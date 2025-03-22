PRIMERA PARTE

Para abordar esta tarea de scraping y extracción de un glosario en formato CSV desde el sitio web, se detalla paso a paso el proceso con todas las consideraciones técnicas. Trabajaremos con Python y la librería BeautifulSoup para extraer el contenido HTML, y utilizaremos Pandas para manipular los datos y generar el CSV.

Paso 1: Análisis del sitio web

El primer paso es analizar cómo están organizados los datos en el sitio web. En el caso de http://www.tugurium.com/gti/termino.php?Tr=cast, parece que cada término del glosario tiene una URL con un identificador único en el parámetro Tr.

Así que necesitamos entender:

Cómo se generan esos parámetros.

Si hay una lista maestra de términos o si debes iterar a través de combinaciones posibles.

Esto también incluye inspeccionar la estructura del HTML para identificar dónde se encuentran los términos y sus traducciones.

Este script está diseñado para realizar un proceso de web scraping en paralelo para obtener términos de un sitio web, procesarlos y almacenarlos incrementalmente en un archivo CSV. A continuación, desgloso punto por punto los *features, herramientas utilizadas y el procedimiento detallado del código:

 1.  Imports (Librerías utilizadas)
   - requests: Para hacer peticiones HTTP y obtener el contenido de las páginas web.
   - BeautifulSoup de `bs4`: Para analizar y extraer datos estructurados del HTML.
   - pandas: Para manipular y almacenar datos en formato CSV.
   - concurrent.futures: Para ejecutar múltiples tareas en paralelo utilizando threads.
   - time** y **random: Para manejar pausas y retardos en el scraping, así como medición de tiempos.
   - os: Para manejar la existencia de archivos en el sistema.
   - requests.exceptions.RequestException: Para manejar errores específicos relacionados con las solicitudes HTTP.

 2. Función: `obtener_detalles(url, max_retries=3)
   - Propósito: Extraer detalles adicionales de una página específica (por cada término) y manejar errores en las solicitudes.
   - Características:
   - Establece un encabezado `User-Agent` para evitar restricciones automáticas del sitio web.
   - Retardo aleatorio: Implementa una pausa entre 1 y 3 segundos para simular comportamiento humano y evitar ser bloqueado por el servidor.
     - Intentos con retroceso exponencial: Intenta hasta 3 veces obtener los datos de la página en caso de error. Si falla, aplica un retraso incremental (`2^attempt`).
     - BeautifulSoup: Analiza el HTML de la página y busca una sección específica (`section.desc`) que contiene la información adicional del término.
     - Manejo de errores: Si falla después de 3 intentos, retorna una cadena vacía.

  3. Función: `procesar_entrada(item)`
   - Propósito: Procesar cada término encontrado en la página principal y extraer tanto su definición breve como su detalle completo.
     -Características:
      - Extrae el nombre del término y una descripción breve de los elementos HTML.
      - Construye la URL completa de la página del término.
      - Llama a la función `obtener_detalles()` para obtener información adicional de la página específica del término.
      - Retorna un diccionario con las tres piezas de información: **Término**, **Descripciones**, **Información Adicional**.
      - **Manejo de errores**: En caso de cualquier error, retorna `None` para evitar que el programa se detenga.

  4. Función: `leer_csv_existente(nombre_archivo)`
   - Propósito**: Leer el archivo CSV ya existente, si es que está presente, para no duplicar términos en futuros scrapes.
   - Características:
     - Utiliza `pandas` para leer el archivo CSV y si no existe, retorna un DataFrame vacío con columnas predefinidas.
     - Esto permite que el script sea incremental y no vuelva a procesar términos ya guardados.

  5. Función: `guardar_csv_incremental(df, nombre_archivo)`
   - propósito: Guardar los nuevos términos extraídos al archivo CSV, de manera incremental.
   - Características:
     - Lee los datos ya existentes en el archivo CSV.
     - Concatena los nuevos datos con los existentes y elimina duplicados utilizando `drop_duplicates()` basado en el término.
     - Guarda los datos actualizados en el CSV, asegurando que no se pierda el progreso.

   6. Función: `obtener_terminos_nuevos(items, df_existente)`
   - Propósito: Comparar los términos extraídos del sitio con los ya presentes en el CSV para evitar procesarlos de nuevo.
   - Características:
     - Crea una lista de términos ya procesados del CSV.
     - Retorna una lista de términos que aún no han sido procesados.

   7. Función: `scrapeo_progresivo(items, nombre_archivo, batch_size=100)`
   - Propósito: Controlar el flujo del scraping en bloques o "batches" de tamaño definido, para evitar sobrecargas y asegurar el guardado incremental de los datos.
   - Características:
     - Primero lee el CSV existente y filtra los términos que aún no han sido procesados.
     - Imprime el número total de términos nuevos a procesar.
     - Utiliza un **ThreadPoolExecutor** con 5 threads para procesar las entradas en paralelo y mejorar la eficiencia.
     - Almacena los resultados en una lista y los guarda al CSV cada 100 términos (controlado por `batch_size`), evitando que se pierda el progreso.
     - Imprime el progreso a medida que avanza (cada vez que se procesan 100 términos) y el tiempo total al finalizar.

   8. Ejecución del scraping
   - URL base: Se hace una solicitud a la página principal de términos que empiezan con la letra "D".
   - BeautifulSoup analiza el HTML y encuentra todos los términos dentro de la sección `'section.i_link li'`.
   - Se define el archivo CSV de salida como `'glosario_letra_D.csv'`.

   9. Concurrente y Progresivo
   - El scraping se realiza en bloques (batches) con concurrencia mediante threads.
   - Guarda el progreso en intervalos regulares para evitar perder datos en caso de error.
   - Verifica los términos que ya fueron procesados, optimizando el flujo y evitando duplicados.

   Features y Herramientas clave:
- Concurrent scraping: Ejecuta la extracción de múltiples términos en paralelo para mejorar la eficiencia.
- Progreso incremental: Guarda los resultados progresivamente, lo que permite evitar la pérdida de datos en caso de fallo.
- Retry y retroceso exponencial: Gestión de errores con múltiples intentos y pausas entre cada intento.
- Filtrado de términos existentes: Asegura que el scraping no repita términos ya procesados.
