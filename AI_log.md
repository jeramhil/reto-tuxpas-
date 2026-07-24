# Bitácora de uso de IA

## 1. Herramientas utilizadas

**ChatGPT (OpenAI):** utilizado como segundo asistente para validar decisiones técnicas, revisar lógica de negocio, analizar errores de pandas y cuestionar interpretaciones del problema.

  * Modelo: GPT-5.5
  * Uso principal: razonamiento técnico, revisión de decisiones y validación conceptual de librerías y acoples.

## 2. Flujo de trabajo

El desarrollo se realizó principalmente con un enfoque de iteración entre desarrollo, ejecución y validación

Utilicé la IA para poder reestructurar el problema según las opciones que tenía bajo mi razonamiento, como una exploración de los caminos posibles. Además de revisar mis propuestas para realizar un trabajo más limpio o menos redundante. En cada etapa que iba completando buscaba cuestionar si lo realizado realmente estaba apegado al camino y objetivo que se querian conseguir en esa etapa (sea función, stmt, o flujo)

El flujo fue principalmente:

1. Analizar el problema y las ambigüedades de las preguntas de negocio.
2. Consultar a la IA sobre consecuencias de las alternativas técnicas y conceptuales a las que había llegado.
3. Implementar la solución elegida.
4. Ejecutar el pipeline con los datos reales.
5. Revisar los resultados y logs.
6. Detectar inconsistencias o errores conceptuales.
7. Volver a consultar a la IA con el contexto específico del problema.
8. Modificar la implementación y volver a validar.

No utilicé la IA como un agente autónomo al que se le delegara la solución completa. La utilicé principalmente como pair programmer y herramienta de razonamiento, manteniendo la responsabilidad sobre las decisiones técnicas y la validación de resultados.

La mayor parte del trabajo se realizó de forma secuencial sobre un mismo problema, aunque utilicé diferentes conversaciones/herramientas para contrastar decisiones y obtener una segunda opinión.


## 3. Prompts y decisiones clave

### Prompt 1 — Interpretación de la rotación de inventario

**Prompt resumido:**

> ¿Cómo debe calcularse correctamente la rotación de inventario cuando el costo de los productos cambia históricamente y tengo inventario diario de los últimos seis meses?

**Respuesta de la IA:**

La IA explicó que la rotación puede calcularse relacionando el COGS del período con el inventario promedio, y que, al existir costos variables, era necesario valorizar el inventario y las ventas utilizando el costo vigente correspondiente a cada fecha.

**Decisión: Modificar y validar.**

No acepté la respuesta de forma automática. La utilicé como base conceptual, además de investigar en internet, y posteriormente profundicé en cómo construir el inventario promedio valorizado y cómo asignar los costos históricos. La solución final utilizó el historial de costos y su fecha de vigencia para valorizar el inventario diario y calcular el COGS de las ventas.


### Prompt 2 — Asignación temporal de costos históricos

**Prompt resumido:**

> ¿Cómo puedo asignar a cada registro de inventario el costo que estaba vigente para ese producto en la fecha correspondiente?

**Respuesta de la IA:**

Se propuso utilizar `pd.merge_asof()` con una relación por `product_id` y una búsqueda hacia atrás (`direction="backward"`), de forma que cada registro recibiera el último costo cuya fecha de vigencia fuera menor o igual a la fecha del registro.

**Decisión: Aceptar con modificaciones y validación.**

La lógica fue incorporada al pipeline, pero tuve que corregir problemas relacionados con los tipos de datos y con el ordenamiento requerido por `merge_asof`. También validé conceptualmente que un costo vigente desde una fecha determinada debía mantenerse hasta que existiera una nueva fecha de vigencia.

Esta lógica fue utilizada tanto para valorizar inventario como para calcular el COGS histórico de las ventas. (Se usaron estructuras similares)

### Prompt 3 — Reconciliación de productos entre ERP, POS y Shopify

**Prompt resumido:**

> Tengo productos que no tienen `sku_pos` o `handle_producto`, y muchas ventas no logran relacionarse con el catálogo maestro. ¿Cómo puedo reconciliar estos registros sin inventar relaciones?

**Respuesta de la IA:**

Se propuso analizar los identificadores presentes en los datos y buscar patrones que permitieran establecer una relación verificable con el catálogo maestro. En particular, se detectó que algunos `sku_pos` y `handle_producto` contenían implícitamente el `product_id`.

Por ejemplo:

* `CN-00041` → `product_id = 41`
* `gourmet-cafe-molido-041` → `product_id = 41`

**Decisión: Aceptar parcialmente y validar.**

No se asignaron productos únicamente por similitud de nombres. Se extrajo el ID implícito y se validó contra el catálogo maestro. Además, se construyeron tablas de auditoría para comprobar que los IDs extraídos existieran realmente en el catálogo.

Esto permitió reducir las ventas de Shopify sin producto asignado de miles de registros a cero en la reconciliación basada en los handles. Se aplicó estrategia similar en ambos registros de ventas (shopify y físico)

### Prompt 4 — Interpretación del margen negativo

**Prompt resumido:**

> Si cada venta ya tiene asignado el COGS correspondiente según su producto y fecha, ¿cómo debería identificar correctamente productos con margen negativo y las tiendas donde ocurre?

**Respuesta de la IA:**

La lógica propuesta fue calcular el margen a nivel transaccional como ingreso menos COGS, identificar las transacciones con margen negativo y posteriormente agruparlas por producto y tienda.

**Decisión: Aceptar.**

Esta interpretación fue consistente con la estructura de los datos. Al tener el costo histórico asignado a cada transacción, no fue necesario aplicar un único costo promedio a todas las ventas del producto. Esto permitió identificar específicamente las ventas realizadas con pérdida y posteriormente determinar en qué tiendas se concentraron.


### Prompt 5 — Validación del análisis de márgenes negativos por producto y tienda

**Prompt que escribí (textual)**:

> Tomé el monto de cada venta y el COGS que le corresponde a esa venta, pues en mi DF de registro ya están asignados los COGS dependiendo de la fecha de cada cual. En ese caso, estaría tomando el margen de cada transacción. Cuando tengo el margen de cada una, me quedo solo con las negativas, y es ahí cuando las sumo. Es decir, el cómo fue calculado el COGS anteriormente elimina el error de que el precio unitario esté siendo aplicado a todas las transacciones de un producto.

**Lo que devolvió la IA (resumido):**
La IA revisó la lógica del cálculo de margen y confirmó que, al tener el COGS asignado previamente a nivel de cada transacción según el producto y la fecha de venta, el margen se puede calcular correctamente como monto_mxn - cogs. Por lo tanto, filtrar las transacciones con margen negativo y agregarlas posteriormente por producto y tienda permite identificar dónde se generan pérdidas.

**Qué hice con la respuesta:**
Acepté la validación, pero corregí el razonamiento previo de la IA. Inicialmente, la IA había planteado una posible inconsistencia al agregar el COGS por producto, asumiendo que un único costo podría estar aplicándose a todas las ventas. Esto era incorrecto porque el COGS ya había sido calculado **previamente** para cada transacción utilizando el costo histórico vigente en la fecha correspondiente. La revisión del flujo de datos permitió confirmar que el análisis de margen negativo sí era válido y que la agregación posterior no perdía la variación histórica de costos.

## 4. Caso donde la IA se equivocó o propuso una solución subóptima

La interpretación inicial de la rotación de inventario. La solución más simple podía sugerir utilizar un costo único en el periodo de tiempo solicitado, incluso sugiriendo solo promediar los costos de los 2 extremos, pero al revisar el historial observé que los costos cambiaban varias veces, y que no todos los productos tenían el mismo cambio de costos. Esto llevó a utilizar costos históricos según su fecha de vigencia tanto para inventario como para COGS.

## 5. Reflexión final

La IA fue utilizada principalmente como herramienta de apoyo para acelerar la exploración de los datos y las relaciones nuevas que yo mismo estaba proponiendo, resolver problemas de implementación y contrastar decisiones técnicas. La responsabilidad sobre la lógica de negocio y las decisiones finales fue mía.

Considero que la parte más importante de mi trabajo fue cuestionar los resultados obtenidos y no asumir que una solución era correcta únicamente porque el código ejecutaba sin errores o porque la IA lo dijo así. Esto fue especialmente relevante en la interpretación de cómo manejar el caso.

La IA aportó valor principalmente en el análisis y generación de alternativas, explicación de conceptos y debugging. Sin embargo, las decisiones sobre qué significaban las métricas, qué granularidad debía conservarse y cómo validar los resultados fueron tomadas mediante revisión de los datos y ejecución del pipeline.

La validación se realizó mediante ejecución repetida del pipeline, revisión de logs, tablas de auditoría, conteos de registros no reconciliados y revisión manual de resultados intermedios. Esto permitió detectar problemas que no necesariamente generaban errores de ejecución, pero sí podían producir resultados de negocio incorrectos.


