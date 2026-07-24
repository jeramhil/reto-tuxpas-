import pandas as pd

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def asignar_info_sucursales(lista_sucursales_quiebre:list[str],info_sucursales:pd.DataFrame)->pd.DataFrame:
    
    sucursales_quiebres_trimestral=info_sucursales[
            info_sucursales["sucursal_id"].isin(lista_sucursales_quiebre)

        ][
            ["sucursal_id", "ciudad"]
            ].sort_values(
                ["ciudad","sucursal_id"]
            ).reset_index(drop=True)

    sucursales_por_ciudad=(
        sucursales_quiebres_trimestral
            .groupby("ciudad", as_index=False)
            .agg(
                sucursales=("sucursal_id", lambda x: ", ".join(x))
            )
    )
    
    #RESPUESTA PREGUNTA 2
    #logger.info(f"\nSUCURSALES CON QUIEBRES >3 DIAS (ULTIMO TRIMESTRE)\n{sucursales_por_ciudad}")

    return sucursales_por_ciudad

    

def calcular_quiebres_stock(inventario_historico:pd.DataFrame,info_sucursales:pd.DataFrame)->list[str]:

    inventario_historico["fecha_snapshot"]= pd.to_datetime(inventario_historico['fecha_snapshot'])
    
    fin_trimestre=inventario_historico["fecha_snapshot"].max()
    inicio_trimestre = fin_trimestre - pd.DateOffset(months=3)
    
    inventario_trimestral = inventario_historico[
        (inventario_historico["fecha_snapshot"] >= inicio_trimestre) &
        (inventario_historico["fecha_snapshot"] <= fin_trimestre)
    ]
        
    """
    registros_quiebres = inventario_trimestral[
        (inventario_trimestral["cantidad_en_stock"]==0) |
        (inventario_trimestral["cantidad_en_stock"].eq("N/A")) |
        (inventario_trimestral["cantidad_en_stock"].isna())
    ]
    """
    registros_quiebres = inventario_trimestral[
        (inventario_trimestral["cantidad_en_stock"].eq(0)) 
    ]

    quiebres_por_tienda_historico=(
        registros_quiebres[
            ["fecha_snapshot", "sucursal_id"]
        ]
        .drop_duplicates()
        .sort_values(
            ["sucursal_id" , "fecha_snapshot"]
        )
    )

    quiebres_por_tienda_historico["dias_ultimo_quiebre"] = quiebres_por_tienda_historico["fecha_snapshot"].diff().dt.days
    quiebres_por_tienda_historico["no_consecutivo"] = quiebres_por_tienda_historico["dias_ultimo_quiebre"]!=1
    quiebres_por_tienda_historico["grupo"] = (quiebres_por_tienda_historico['no_consecutivo']).cumsum()

    quiebres_por_tienda_registro = (
        quiebres_por_tienda_historico
            .groupby(
                ["sucursal_id", "grupo"]
            )
            .agg(
                fecha_inicio=("fecha_snapshot", "min"),
                fecha_fin=("fecha_snapshot", "max"),
                duracion_quiebre=("fecha_snapshot", "count")
            )
            .reset_index()
    )

    quiebres_mayores=(
        quiebres_por_tienda_registro[
            quiebres_por_tienda_registro["duracion_quiebre"]>=4
        ]
    )

    lista_sucursales=(
        quiebres_mayores["sucursal_id"].unique()
    )

    return asignar_info_sucursales(lista_sucursales,info_sucursales)
