import pandas as pd

import logging
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



def calcular_MoM_canales(ventas_shopify:pd.DataFrame,ventas_sucursales:pd.DataFrame):

    #logger.info(f"\n{ventas_sucursales.head()}")

    ventas_shopify["fecha_hora"]=pd.to_datetime(ventas_shopify["fecha_hora"])
    ventas_sucursales["fecha_hora"]=pd.to_datetime(ventas_sucursales["fecha_hora"])

    ventas_mensuales_shopify = (
        ventas_shopify
        .groupby(
            ventas_shopify["fecha_hora"].dt.to_period("M")
        )["monto_mxn"]
        .sum()
        .reset_index()
    )

    ventas_mensuales_sucursales = (
        ventas_sucursales
        .groupby(
            ventas_sucursales["fecha_hora"].dt.to_period("M")
        )["monto_mxn"]
        .sum()
        .reset_index()
    )    

    ventas_mensuales_shopify['mes_anterior'] = ventas_mensuales_shopify['monto_mxn'].shift(1)
    ventas_mensuales_shopify['dif_absoluta'] = ventas_mensuales_shopify['monto_mxn'] - ventas_mensuales_shopify['mes_anterior']
    ventas_mensuales_shopify['MoM_ecommerce '] = (ventas_mensuales_shopify['dif_absoluta'] / ventas_mensuales_shopify['mes_anterior']) * 100

    ventas_mensuales_sucursales['mes_anterior'] = ventas_mensuales_sucursales['monto_mxn'].shift(1)
    ventas_mensuales_sucursales['dif_absoluta'] = ventas_mensuales_sucursales['monto_mxn'] - ventas_mensuales_sucursales['mes_anterior']
    ventas_mensuales_sucursales['MoM_fisico'] = (ventas_mensuales_sucursales['dif_absoluta'] / ventas_mensuales_sucursales['mes_anterior']) * 100

    ventas_mensuales_shopify.drop(
        columns={"mes_anterior","monto_mxn","dif_absoluta"},
        inplace=True
    )

    ventas_mensuales_sucursales.drop(
        columns={"mes_anterior","monto_mxn","dif_absoluta"},
        inplace=True
    )

    fecha_maxima = ventas_mensuales_sucursales["fecha_hora"].max()
    fecha_inicio = fecha_maxima - 12

    ventas_mensuales_global = (
        ventas_mensuales_sucursales[
            ventas_mensuales_sucursales["fecha_hora"].between(
                fecha_inicio,
                fecha_maxima
            )
        ]
        .merge(
            ventas_mensuales_shopify,
            on="fecha_hora",
            how="left"
        ).rename(
                columns={"fecha_hora":"mes"})
    )
    
    return ventas_mensuales_global