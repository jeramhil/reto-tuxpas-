import pandas as pd

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalizar_shopify(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    df.rename(columns={"order_id":"venta_online_id", 
                        "fecha":"fecha_hora", 
                        "product_handle":"handle_producto",
                        "amount":"monto",
                        "currency":"moneda",
                        "customer_name":"nombre_cliente", 
                        "customer_email":"email_cliente", 
                        "customer_rfc":"rfc_cliente", 
                        "shipping_city":"ciudad_envio",
                        "shipping_address":"direccion_envio"}, inplace=True)
    return df

def normalizar_venta_fisica(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    df.rename(columns={"venta_id":"venta_fisica_id", 
                       "tienda_id":"sucursal_id",
                       "sku":"sku_pos"}, inplace=True)
    return df

def normalizar_productos(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    df.rename(columns={"nombre":"nombre_producto",
                       "categoria":"categoria_producto",
                       "cost_history":"historial_costos",
                       "sku_erp":"sku_erp"}, inplace=True)
    return df

def normalizar_sucursales(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    df.rename(columns={"tienda_id":"sucursal_id", 
                       "timezone":"zona_horaria"}, inplace=True)
    return df

def normalizar_relaciones(df:pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    df.rename(columns={"handle":"handle_producto"}, inplace=True)
    return df

def normalizar_inventario(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    df.rename(columns={"fecha":"fecha_snapshot", 
                       "tienda_id":"sucursal_id"}, inplace=True)
    return df

def normalizar_monedas(df:pd.DataFrame)-> pd.DataFrame:
    df.columns = df.columns.str.lower()
    df.rename(columns={"fecha":"fecha_muestra",
                        "currency":"moneda", 
                        "rate_to_mxn":"valor_mxn"}, inplace=True)
    return df

def normalizar_dataframes(dataframes: dict[str,pd.DataFrame]) -> dict[str,pd.DataFrame]:
    #Debo normalizar los dataframes para que tengan la misma estructura y puedan ser comparados entre sí
    
    df_shopify=normalizar_shopify(dataframes['compras_shopify'])
    df_venta_fisica=normalizar_venta_fisica(dataframes['compras_sucursales'])
    
    df_sucursales=normalizar_sucursales(dataframes['info_sucursales'])
    df_productos=normalizar_productos(dataframes['info_productos'])
    
    df_relaciones=normalizar_relaciones(dataframes['relacion_claves_productos'])
    df_inventario=normalizar_inventario(dataframes['inventario'])

    df_moneda=normalizar_monedas(dataframes["cambio_moneda"])
    
    return {
        "compras_shopify": df_shopify,
        "compras_sucursales": df_venta_fisica,
        "info_sucursales": df_sucursales,
        "info_productos": df_productos,
        "relacion_claves_productos": df_relaciones,
        "inventario": df_inventario,
        "cambio_moneda":df_moneda
    }

def main() -> None:
    #Busco normalizar las estructuras de los dataframes útiles
    
    pass

if __name__ == "__main__":
    main()