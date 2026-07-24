import pandas as pd

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def calcular_margenes_producto(compras_sucursales_con_costo:pd.DataFrame):

    compras_sucursales_con_costo["margen"]=(
            compras_sucursales_con_costo["monto_mxn"]-compras_sucursales_con_costo["cogs"]
    )

    fecha_max = compras_sucursales_con_costo["fecha_hora"].max()
    fecha_inicio = fecha_max - pd.DateOffset(months=12)

    compras_sucursales_12m = compras_sucursales_con_costo[
        (compras_sucursales_con_costo["fecha_hora"] >= fecha_inicio)
        & (compras_sucursales_con_costo["fecha_hora"] <= fecha_max)
    ].copy()

    ventas_negativas = compras_sucursales_12m[
        compras_sucursales_12m["margen"] < 0
    ].copy()

    resultado_4= (
        ventas_negativas
        .groupby(
            ["product_id", "sku_pos"]
        )
        .agg(
            margen_negativo_total=("margen", "sum"),
            tiendas=("sucursal_id", lambda x: sorted(x.unique()))
        )
        .reset_index()
    )

    auditoria_margen = (
        compras_sucursales_con_costo
        .groupby(["product_id", "sucursal_id"])
        .agg(
            transacciones=("product_id", "size"),
            ingresos_totales=("monto_mxn", "sum"),
            cogs_total=("cogs", "sum"),
            margen_total=("margen", "sum"),
            compras_en_perdida=(
                "margen",
                lambda x: (x < 0).sum()
            )
        )
        .reset_index()
    )
    detalle_4 = auditoria_margen[
        auditoria_margen["margen_total"] < 0
    ].copy()


    logger.info(f"\n\n4.Productos con margen negativo y en qué tiendas ocurren:\n\n{resultado_4}"
                #f"\n{detalle_4}"    
                )
    
    return
    