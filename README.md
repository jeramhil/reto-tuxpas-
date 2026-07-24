# Reto Técnico Tuxpas Café Norte

## Nombre: Jeramhil Javier Solis Yari

En este repo está el pipeline diseñado para ingerir los 3 archivos de datos correspondientes a Café Norte y sus movimientos de negocio

## ¿Por qué decidí utilizar python?
Personalmente me parece una herramienta dinámica y adecuada para un manejo por etapas de los datos. Además,suele ser una herramienta útil para portotipado en proyectos a nivel profesionalmente, y ha sido parte de mi portafolio de herramientas para proyectos de todo tipo.

## Respuestas del reto:
Las respuestas a las 4 preguntas de negocio están en un archivo de texto aparte "respuestas.txt"


## Interpretación personal de las 4 preguntas de negocio a responder:

1. Rotación de inventario: calculada como COGS del período sobre el inventario promedio valorizado, respetando los costos históricos vigentes durante los últimos 6 meses tomando en cuenta la variación de costos de los productos.

2. Quiebres de stock: identificación de tiendas y productos con períodos consecutivos de falta de inventario superiores a 3 días durante el último trimestre, tomando como "Quiebre de stock" que al menos 1 producto tuvo cantidad 0 en su registro de inventario.

3. Crecimiento MoM: comparación mensual de las ventas de los canales físico y e-commerce durante los últimos 12 meses, utilizando MXN como moneda común.

4. Margen negativo: identificación de ventas cuyo ingreso fue inferior al COGS correspondiente a la fecha de la transacción, agregando posteriormente el impacto por producto y tienda.


Como hipótesis de análisis, se consideró que las métricas podrían estar relacionadas: un crecimiento de la demanda podría incrementar la rotación, generar presión sobre el inventario y eventualmente contribuir a quiebres de stock o compras con costos variables que afecten la rentabilidad. Esta relación se planteó como hipótesis y no como causalidad asumida.

