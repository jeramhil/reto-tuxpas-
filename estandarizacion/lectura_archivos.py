import pandas as pd

import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RUTA_ARCHIVOS: str = "./datos/"

def dividir_json_inventario(inventario: dict)-> list[pd.DataFrame]:
    #Independizar la información de cada sucursal física
    registro_sucursales=inventario.get("tiendas_info", [])
    df_sucursales = pd.DataFrame(registro_sucursales)

    registro_productos = inventario["catalogo"]["productos"]
    df_productos = pd.DataFrame(registro_productos)

    relacion_claves_productos = inventario.get("sku_mappings", [])
    df_relacion_erp_pos = pd.DataFrame(relacion_claves_productos)

    #Independizar historial de inventario por producto y sucursal
    registro_inventario = inventario.get("snapshots", [])
    df_inventario = pd.DataFrame(registro_inventario)

    logger.debug(f"Información de sucursales: {df_sucursales.columns}")
    logger.debug(f"Información de productos: {df_productos.columns}")
    logger.debug(f"Relación de claves de productos: {df_relacion_erp_pos.columns}")
    logger.debug(f"Historial de inventario: {df_inventario.columns}")

    return [df_sucursales, df_productos, df_relacion_erp_pos, df_inventario]

def cargar_archivos_originales(lista_archivos: list[str]) -> dict[str,pd.DataFrame]:

    nuevos_dataframes = {}

    for archivo in lista_archivos:
        try:
            if archivo.endswith(".csv"):
                compras_sucursales = pd.read_csv(f"{RUTA_ARCHIVOS}{archivo}")
                nuevos_dataframes["compras_sucursales"] = compras_sucursales
                logger.debug(f"Columnas extraidas de registro de compras físicas:\n{compras_sucursales.columns}")

            elif archivo.endswith(".parquet"):
                ordenes_shopify = pd.read_parquet(f"{RUTA_ARCHIVOS}{archivo}")
                nuevos_dataframes["compras_shopify"] = ordenes_shopify
                logger.debug(f"Columnas extraidas de registro de ordenes de shopify:\n{ordenes_shopify.columns}")

            elif archivo.endswith(".json"):   
                with open(f"{RUTA_ARCHIVOS}{archivo}", "r") as file:
                    
                    inventario = json.load(file)
                    info_sucursales, info_productos, relacion_claves_productos, historico_inventario = dividir_json_inventario(inventario)
                    
                    nuevos_dataframes["info_sucursales"] = info_sucursales
                    nuevos_dataframes["info_productos"] = info_productos
                    nuevos_dataframes["relacion_claves_productos"] = relacion_claves_productos
                    nuevos_dataframes["inventario"] = historico_inventario

            else:
                logger.warning(f"El archivo {archivo} no es de un formato válido para la carga de datos")
                continue
            
        except FileNotFoundError:
            logger.error(f"El archivo {archivo} no se encontró")

        except Exception:
            logger.exception(f"Ocurrió un error al cargar el archivo: {archivo}.")

    nuevos_dataframes["cambio_moneda"]=pd.read_csv(f"{RUTA_ARCHIVOS}{"exchange_rates.csv"}")

    return nuevos_dataframes

def main() -> None:
    datos_recibidos=cargar_archivos_originales(["ecommerce_orders.parquet","sales.csv", "inventory.json"])

if __name__ == "__main__":
    main()