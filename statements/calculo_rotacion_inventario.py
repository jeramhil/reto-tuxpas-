import pandas as pd

import logging

from .calculo_margen_productos import calcular_margenes_producto

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




def calcular_rotacion_inventario(valor_promedio_inventario:pd.DataFrame,cogs_completo:pd.DataFrame, productos:pd.DataFrame):

    inventario_product_id=valor_promedio_inventario.merge(
        productos[["sku_erp","product_id","nombre_producto"]],
        on="sku_erp",
        how="left"
    )

    tabla_rotacion=inventario_product_id.merge(
        cogs_completo,
        on="product_id",
        how="left"
    )

    tabla_rotacion["rotacion_inventario"]=(
        tabla_rotacion["cogs_total"]/tabla_rotacion["inventario_promedio_mxn"]
    )

    tabla_rotacion=tabla_rotacion.drop(
        columns={"cogs_total","inventario_promedio_mxn"}
    ).sort_values(
        ["rotacion_inventario"],
        ascending=True
    ).reset_index(drop=True)

    #RESPUESTA PREGUNTA 1

    rotacion_inventario_producto=tabla_rotacion.head(10)
    logger.debug(f"\n{rotacion_inventario_producto}")

    return rotacion_inventario_producto

def calcular_cogs_producto(cogs_shopify:pd.DataFrame,cogs_fisicas:pd.DataFrame):
    cogs_shopify=cogs_shopify.sort_values(
        ["product_id","fecha_hora"]
    ).reset_index(drop=True)

    cogs_fisicas=cogs_fisicas.sort_values(
            ["product_id","fecha_hora"]
    ).reset_index(drop=True)

    cogs_canales = pd.concat(
        [
            cogs_shopify.assign(canal="ecommerce"),
            cogs_fisicas.assign(canal="fisico")
        ],
        ignore_index=True
    )

    cogs_por_producto = (
        cogs_canales
        .groupby("product_id", as_index=False)
        .agg(
            cogs_total=("cogs", "sum")
        )
    )
    logger.debug(f"\n{cogs_por_producto}")

    return cogs_por_producto

def calcular_cogs_fisicas(fisicas_reconciliado:pd.DataFrame,costos_historico_df:pd.DataFrame):
    fisicas_reconciliado = fisicas_reconciliado.sort_values(
            ["fecha_hora","product_id"]
        ).reset_index(drop=True)

    fisicas_valorizado = pd.merge_asof(
        fisicas_reconciliado,
        costos_historico_df,
        left_on="fecha_hora",
        right_on="fecha_vigencia",
        by="product_id",
        direction="backward"
    ).sort_values(["product_id","fecha_hora"]).reset_index(drop=True)

    fisicas_valorizado=fisicas_valorizado.drop(
            columns=["proveedor","fecha_vigencia","venta_fisica_id","product_id_extraido"]
        )
    
    fisicas_valorizado["cogs"]=(
        fisicas_valorizado["costo_mxn"]*fisicas_valorizado["cantidad"]
    )

    calcular_margenes_producto(fisicas_valorizado)
    
    return fisicas_valorizado

def calcular_cogs_shopify(shopify_reconciliado:pd.DataFrame,costos_historico_df:pd.DataFrame):
    shopify_valorizado = pd.merge_asof(
        shopify_reconciliado,
        costos_historico_df,
        left_on="fecha_hora",
        right_on="fecha_vigencia",
        by="product_id",
        direction="backward"
    ).sort_values(["product_id","fecha_hora"]).reset_index(drop=True)

    shopify_valorizado=shopify_valorizado.drop(
        columns=["proveedor","fecha_vigencia","venta_online_id"]
    )

    shopify_valorizado["cogs"]=(
        shopify_valorizado["costo_mxn"]*shopify_valorizado["cantidad"]
    )

    logger.debug(f"\n{shopify_valorizado}")

    return shopify_valorizado

def completar_registros_sucursales(fisicos_product_id:pd.DataFrame,info_productos:pd.DataFrame):

    
    fisicos_product_id["product_id_extraido"] = (
        fisicos_product_id["sku_pos"]
        .str.extract(r"(\d+)$")[0]
        .astype("Int64")
    )

    ventas_fisicas_sin_producto = fisicos_product_id[
            fisicos_product_id["product_id"].isna()
        ].copy()
    

    auditoria_pos = ventas_fisicas_sin_producto.merge(
        info_productos[
            [
                "product_id",
                "sku_erp",
                "nombre_producto"
            ]
        ].rename(
            columns={
                "product_id": "product_id_maestro"
            }
        ),
        left_on="product_id_extraido",
        right_on="product_id_maestro",
        how="left"
    )

    auditoria_pos["id_valido"] = (
        auditoria_pos["product_id_maestro"].notna()
    )

    auditoria_pos = auditoria_pos[
        [
            "sku_pos",
            "product_id_extraido",
            "product_id_maestro",
            "sku_erp",
            "nombre_producto",
            "id_valido"
        ]
    ].drop_duplicates()

    logger.debug(f"\n{auditoria_pos.head(10)}")

    ids_validos = auditoria_pos.loc[
        auditoria_pos["id_valido"],
        "product_id_maestro"
    ].dropna().unique()

    mask_reconciliacion = (
        fisicos_product_id["product_id"].isna()
        & fisicos_product_id["product_id_extraido"].isin(ids_validos)
    )

    fisicos_product_id.loc[
        mask_reconciliacion,
        "product_id"
    ] = fisicos_product_id.loc[
        mask_reconciliacion,
        "product_id_extraido"
    ]

    return fisicos_product_id

def completar_registros_shopify(shopify_product_id:pd.DataFrame,info_productos:pd.DataFrame):
    # 1. Extraer ID implícito del handle
    shopify_product_id["product_id_extraido"] = (
        shopify_product_id["handle_producto"]
        .str.extract(r"-(\d+)$")[0]
        .astype("Int64")
    )

    # 2. Solo considerar los registros sin product_id
    candidatos = shopify_product_id[
        shopify_product_id["product_id"].isna()
    ].copy()

    # 3. Relacionar contra el catálogo maestro
    auditoria_reconciliacion = candidatos.merge(
        info_productos[
            [
                "product_id",
                "sku_erp",
                "nombre_producto"
            ]
        ].rename(
            columns={
                "product_id": "product_id_maestro"
            }
        ),
        left_on="product_id_extraido",
        right_on="product_id_maestro",
        how="left"
    )

    # 4. Validar que el ID extraído existe en el maestro
    auditoria_reconciliacion["id_valido"] = (
        auditoria_reconciliacion["product_id_maestro"].notna()
    )

    ids_validos = auditoria_reconciliacion.loc[
        auditoria_reconciliacion["id_valido"],
        "product_id_maestro"
    ].dropna().unique()

    mask_reconciliacion = (
        shopify_product_id["product_id"].isna()
        & shopify_product_id["product_id_extraido"].isin(ids_validos)
    )

    shopify_product_id.loc[
        mask_reconciliacion,
        "product_id"
    ] = shopify_product_id.loc[
        mask_reconciliacion,
        "product_id_extraido"
    ]

    shopify_product_id=shopify_product_id.drop(
        columns=["product_id_extraido"]
    )

    return shopify_product_id

def preparar_df_ventas(shopify:pd.DataFrame,fisicas:pd.DataFrame,costos_historico:pd.DataFrame,info_productos:pd.DataFrame):
    shopify_product_id = shopify.merge(
        info_productos[
            ["handle_producto", "product_id"]
        ],
        on="handle_producto",
        how="left"
    )

    fisicos_product_id = fisicas.merge(
            info_productos[
                ["sku_pos", "product_id"]
            ],
            on="sku_pos",
            how="left"
    )
    
    shopify_product_id["fecha_hora"] = pd.to_datetime(
        shopify_product_id["fecha_hora"],
        errors="coerce"
    )

    fisicos_product_id["fecha_hora"] = pd.to_datetime(
        fisicos_product_id["fecha_hora"],
        errors="coerce"
    )

    costos_historico["fecha_vigencia"] = pd.to_datetime(
        costos_historico["fecha_vigencia"],
        errors="coerce"
    )

    shopify_product_id["product_id"] = (
        shopify_product_id["product_id"]
        .astype("Int64")
    )
    fisicos_product_id["product_id"] = (
        fisicos_product_id["product_id"]
        .astype("Int64")
    )

    costos_historico["product_id"] = (
        costos_historico["product_id"]
        .astype("Int64")
    )

    return shopify_product_id,fisicos_product_id,costos_historico

def asignar_costo_venta(shopify:pd.DataFrame,fisicas:pd.DataFrame,costos_historico:pd.DataFrame,info_productos:pd.DataFrame):

    shopify_product_id,fisicos_product_id,costos_historico_df=preparar_df_ventas(shopify,fisicas,costos_historico,info_productos)

    shopify_reconciliado=completar_registros_shopify(shopify_product_id,info_productos)

    fisicas_reconciliado=completar_registros_sucursales(fisicos_product_id,info_productos)

    costos_historico_df = costos_historico_df.sort_values(
        ["fecha_vigencia","product_id"]
    ).reset_index(drop=True)

    cogs_shopify=calcular_cogs_shopify(shopify_reconciliado,costos_historico_df)
    cogs_fisicas=calcular_cogs_fisicas(fisicas_reconciliado,costos_historico_df)

    cogs_totales=calcular_cogs_producto(cogs_shopify,cogs_fisicas)

    return cogs_totales

def asignar_costo_producto_inv_nacional(inventario_nacional:pd.DataFrame,costos_historico:pd.DataFrame,info_productos:pd.DataFrame):

    inventario_con_producto = inventario_nacional.merge(
        info_productos[
            ["product_id", "sku_erp"]
        ],
        on="sku_erp",
        how="left"
    )

    inventario_con_producto["fecha_snapshot"] = pd.to_datetime(
        inventario_con_producto["fecha_snapshot"],
        errors="coerce"
    )

    costos_historico["fecha_vigencia"] = pd.to_datetime(
        costos_historico["fecha_vigencia"],
        errors="coerce"
    )

    inventario_con_producto = inventario_con_producto.sort_values(
        ["fecha_snapshot","product_id"]
    ).reset_index(drop=True)

    costos_historico = costos_historico.sort_values(
        ["fecha_vigencia","product_id"]
    ).reset_index(drop=True)

    inventario_valorizado = pd.merge_asof(
        inventario_con_producto,
        costos_historico,
        left_on="fecha_snapshot",
        right_on="fecha_vigencia",
        by="product_id",
        direction="backward"
    ).sort_values(["sku_erp","fecha_snapshot"]).reset_index(drop=True)


    inventario_valorizado["costo_nacional_mxn"]=(
        inventario_valorizado["costo_mxn"]*inventario_valorizado["stock_nacional_dia"]
    )
    inventario_valorizado.rename(
        columns={
            "costo_mxn":"costo_unitario_mxn",
            "fecha_vigencia":"costo_vigente_desde"
        },inplace=True
    )

    inventario_valorizado = inventario_valorizado.drop(
        columns=["proveedor","costo_vigente_desde","fecha_inicio_6m","fecha_max_producto"]
    )

    inventario_promedio_nacional = (
        inventario_valorizado
        .groupby("sku_erp", as_index=False)
        .agg(
            inventario_promedio_mxn=(
                "costo_nacional_mxn",
                "mean"
            )
        )
    )
    return inventario_valorizado, inventario_promedio_nacional

def calcular_inventario_nacional_diario(inventario_analisis:pd.DataFrame):
    
    inventario_nacional=inventario_analisis[
            ["fecha_snapshot","sku_erp","cantidad_en_stock","fecha_max_producto","fecha_inicio_6m"]
    ]

    inventario_nacional["cantidad_en_stock"] = pd.to_numeric(
        inventario_nacional["cantidad_en_stock"],
        errors="coerce"
    )

    inventario_nacional["stock_nacional_dia"] = (
        inventario_nacional
        .groupby(["sku_erp","fecha_snapshot"])["cantidad_en_stock"].transform("sum")
    )

    inventario_nacional=inventario_nacional[
        ["sku_erp","fecha_snapshot","stock_nacional_dia","fecha_inicio_6m","fecha_max_producto"]
        ].drop_duplicates().reset_index(drop=True)

    #logger.info(f"\n{inventario_nacional}")

    return inventario_nacional

def limitar_registros_por_fecha(df_completo:pd.DataFrame,llave_fecha:str,meses_analisis:int):
    #Recibo número de meses a tomar desde el último registro hacia atrás

    df_completo[llave_fecha]=pd.to_datetime(df_completo[llave_fecha])

    df_orden_producto=(
        df_completo.sort_values(
                ["sku_erp",llave_fecha]).reset_index(drop=True)
    )

    df_orden_producto["fecha_max_producto"] = (
        df_orden_producto
        .groupby("sku_erp")["fecha_snapshot"]
        .transform("max")
    )

    df_orden_producto["fecha_inicio_6m"] = (
        df_orden_producto["fecha_max_producto"]-pd.DateOffset(months=meses_analisis)
    )
    
    df_ultimos_6_meses = df_orden_producto[
        df_orden_producto["fecha_snapshot"]>=df_orden_producto["fecha_inicio_6m"]
    ].copy()
    
    return df_ultimos_6_meses

def calcular_rotacion_inventario_main(inventario: pd.DataFrame, 
                                 info_productos: pd.DataFrame, 
                                 historial_costos: pd.DataFrame,
                                 ventas_shopify:pd.DataFrame,
                                 ventas_sucursales:pd.DataFrame) -> pd.DataFrame:
    """
    Dentro de los últimos 6 meses
    Qué 10 productos 
    tienen la mayor rotación de inventario

    """

    meses_analisis=6

    inventario_analisis=limitar_registros_por_fecha(inventario,"fecha_snapshot",meses_analisis)
    
    inventario_nacional_diario=calcular_inventario_nacional_diario(inventario_analisis)

    inventario_nacional_valorizado, valor_promedio_inventario=asignar_costo_producto_inv_nacional(
                                                                            inventario_nacional_diario,
                                                                            historial_costos,
                                                                            info_productos)

    cogs_completo=asignar_costo_venta(ventas_shopify,
                          ventas_sucursales,
                          historial_costos,
                          info_productos)

    rotacion_inventario=calcular_rotacion_inventario(valor_promedio_inventario,
                                                     cogs_completo,
                                                     info_productos)


    return rotacion_inventario

