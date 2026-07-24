import pandas as pd
import numpy as np

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def filtrado_compras_fisicas(ordenes_sucursales:pd.DataFrame):
    ordenes_filtrado=ordenes_sucursales.rename(
        columns={"monto":"monto_mxn"}
    )
    ordenes_filtrado=ordenes_filtrado.drop(
        columns=["tipo_comprobante","moneda"]
    )
    logger.debug(f"\nREGISTRO VENTAS FISICAS SIMPLIFICADO\n{ordenes_filtrado.head()}")
    return ordenes_filtrado

def nacionalizacion_shopify(ordenes_shopify:pd.DataFrame,cambio_moneda:pd.DataFrame):

    ordenes_shopify["fecha_hora"] = pd.to_datetime(
        ordenes_shopify["fecha_hora"],
        errors="coerce"
    )

    cambio_moneda["fecha_muestra"] = pd.to_datetime(
        cambio_moneda["fecha_muestra"],
        errors="coerce"
    )

    ordenes_shopify = ordenes_shopify.sort_values(
        ["fecha_hora"]
    ).reset_index(drop=True)

    cambio_moneda = cambio_moneda.sort_values(
        ["fecha_muestra"]
    ).reset_index(drop=True)

    shopify_mxn_calculo=pd.merge_asof(
        ordenes_shopify,
        cambio_moneda,
        left_on="fecha_hora",
        right_on="fecha_muestra",
        by="moneda",
        direction="backward"
    ).sort_values(["fecha_hora"]).reset_index(drop=True)

    shopify_mxn_calculo["monto_mxn"] = np.where(
        shopify_mxn_calculo["valor_mxn"].notna(),
        shopify_mxn_calculo["monto"] * shopify_mxn_calculo["valor_mxn"],
        shopify_mxn_calculo["monto"]
    )

    shopify_mxn=shopify_mxn_calculo[[
        'venta_online_id', 
        'fecha_hora', 
        'handle_producto', 
        'cantidad', 
        'monto_mxn']]
    
    return shopify_mxn

def estandarizar_ventas(shopify:pd.DataFrame, fisicas:pd.DataFrame,cambio_moneda:pd.DataFrame):

    shopify_mxn=nacionalizacion_shopify(shopify,cambio_moneda)
    fisicas_filtrado=filtrado_compras_fisicas(fisicas)

    logger.debug(f"\nVENTAS FISICAS SIMPLIFICADO\n{fisicas_filtrado.head()}")
    logger.debug(f"\nVENTAS SHOPIFY MXN\n{shopify_mxn.head()}")

    return shopify_mxn, fisicas_filtrado


def estandarizar_productos_costos(df_productos: pd.DataFrame, df_relaciones: pd.DataFrame) -> tuple[pd.DataFrame]:    

    df_producto_completo = pd.merge(
        df_productos, df_relaciones, 
        how="left",
        on="sku_erp")

    df_producto_completo.insert(
        0,
        "product_id",
        range(1, len(df_producto_completo) + 1)
    )

    df_costos = df_producto_completo[["product_id", "historial_costos"]].copy()
    df_costos = df_costos.explode("historial_costos").reset_index(drop=True)    
    df_costos = pd.concat(
        [
            df_costos[["product_id"]].reset_index(drop=True),
            pd.json_normalize(
                df_costos["historial_costos"]
            )
        ],
        axis=1
    )

    df_producto_completo = df_producto_completo.drop(
        columns=["historial_costos"]
    )

    logger.debug(f"\nPRODUCTOS NUEVO MODELO \n{df_producto_completo}")
    logger.debug(f"\nHISTORIAL DE COSTO POR PRODUCTO\n{df_costos}")

    return df_producto_completo, df_costos

def crear_nuevos_modelos(dataframes: dict[str,pd.DataFrame]):

    #Nuevo frame con los productos completos
    relacion_erp_pos=dataframes.get("relacion_claves_productos")
    info_productos=dataframes.get("info_productos")

    compras_shopify=dataframes.get("compras_shopify")
    compras_sucursales=dataframes.get("compras_sucursales")

    cambio_moneda=dataframes.get("cambio_moneda")

    df_producto, df_costos=estandarizar_productos_costos(info_productos, relacion_erp_pos)

    df_ventas_shopify,df_ventas_fisicas=estandarizar_ventas(compras_shopify,compras_sucursales,cambio_moneda)

    return {
        "df_producto":df_producto, 
        "df_costos":df_costos,
        "df_ventas_shopify":df_ventas_shopify,
        "df_ventas_sucursales":df_ventas_fisicas
    }

