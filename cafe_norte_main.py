import pandas as pd

import logging

from estandarizacion.lectura_archivos import cargar_archivos_originales
from estandarizacion.normalizacion_dataframes import normalizar_dataframes
from estandarizacion.creacion_nuevas_relaciones import crear_nuevos_modelos

from statements.orden_calculos import statements_main

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    #Cargar los archivos de datos originales
    datos_recibidos_df=cargar_archivos_originales(
        ["ecommerce_orders.parquet",
         "sales.csv", 
         "inventory.json"]
    )
    if not datos_recibidos_df:
        logger.error("No se pudieron cargar los archivos de datos")
        return False

    #Normalizar las columnas para empatar estructuras
    df_normalizados=normalizar_dataframes(datos_recibidos_df)
    if not df_normalizados:
        logger.error("No se pudieron normalizar los dataframes")
        return False
    
    #Crear modelos simplificados
    modelos_simplificados=crear_nuevos_modelos(df_normalizados)
    if not modelos_simplificados:
        logger.error("No se crearon los nuevos modelos necesarios")
        return False

    modelo_final={
        "df_sucursales":df_normalizados["info_sucursales"],
        "df_inventario":df_normalizados["inventario"],
        "df_erp_pos":df_normalizados["relacion_claves_productos"],
        **modelos_simplificados
    }
    
    logger.debug(f"\nMODELOS DATOS FINAL\n{modelo_final.keys()}")

    resultado_calculos=statements_main(modelo_final)



if __name__ == "__main__":
    main()