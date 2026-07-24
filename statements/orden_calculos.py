import pandas as pd

import logging
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from .calculo_rotacion_inventario import calcular_rotacion_inventario_main
from .calculo_quiebres_stock import calcular_quiebres_stock
from .calculo_MoM_canales import calcular_MoM_canales



def statements_main(modelos_dict:dict):
    logger.debug(f"\n{modelos_dict.keys()}")

    df_producto=modelos_dict["df_producto"]
    df_sucursales=modelos_dict['df_sucursales'] 
    df_inventario=modelos_dict['df_inventario']  
    df_erp_pos=modelos_dict['df_erp_pos'] 
    df_producto=modelos_dict['df_producto']
    df_costos=modelos_dict['df_costos'] 
    df_ventas_shopify=modelos_dict['df_ventas_shopify']
    df_ventas_sucursales=modelos_dict[ 'df_ventas_sucursales']

    #1. Top 10 SKUs por rotación de inventario en los últimos 6 meses.
    respuesta_1=calcular_rotacion_inventario_main(
        df_inventario,
        df_producto,
        df_costos,
        df_ventas_shopify,
        df_ventas_sucursales
    )
	#2. Tiendas con quiebres de stock de más de 3 días en el último trimestre.
    respuesta_2=calcular_quiebres_stock(
        df_inventario,
        df_sucursales
    )
	#3. Crecimiento mes a mes (MoM) de ventas por canal (físico vs e-commerce) en el último año.

    respuesta_3=calcular_MoM_canales(
        df_ventas_shopify,
        df_ventas_sucursales
    )
   
    logger.debug(f"\n1.Top 10 SKUs por rotación de inventario en los últimos 6 meses:\n\n{respuesta_1}"
                f"\n\n2.Tiendas con quiebres de stock de más de 3 días en el último trimestre: \n\n{respuesta_2}"
                f"\n\n3.Crecimiento mes a mes (MoM) de ventas por canal (físico vs e-commerce) en el último año:\n\n{respuesta_3}")

    return 