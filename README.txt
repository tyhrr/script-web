*PRIMERA PARTE*

Para abordar esta tarea de scraping y extracción de un glosario en formato CSV desde el sitio web, se detalla paso a paso el proceso con todas las consideraciones técnicas. Trabajaremos con Python y la librería BeautifulSoup para extraer el contenido HTML, y utilizaremos Pandas para manipular los datos y generar el CSV.

Paso 1: Análisis del sitio web

El primer paso es analizar cómo están organizados los datos en el sitio web. En el caso de http://www.tugurium.com/gti/termino.php?Tr=cast, parece que cada término del glosario tiene una URL con un identificador único en el parámetro Tr.

Así que necesitamos entender:

Cómo se generan esos parámetros.

Si hay una lista maestra de términos o si debes iterar a través de combinaciones posibles.

Esto también incluye inspeccionar la estructura del HTML para identificar dónde se encuentran los términos y sus traducciones.

*SEGUNDA PARTE*

Configuracion del entorno:



#Instalaremos las herramientas necesarias:
!pip install requests
!pip install beautifulsoup4
!pip install pandas

requests: Para hacer las peticiones HTTP y descargar las páginas.

BeautifulSoup4: Para procesar el HTML y extraer los datos.

Pandas: Para almacenar los resultados en un CSV.


*Tercera parte*

Montamos nuestro código:

import requests
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
import time
import random
from requests.exceptions import RequestException
import os

def obtener_detalles(url, max_retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(1, 3))  # Espera aleatoria entre 1 y 3 segundos
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            detalle = soup.select_one('section.desc')
            if detalle:
                return detalle.text.strip()
            return ""
        except RequestException as e:
            print(f"Error al obtener {url}: {e}. Intento {attempt + 1} de {max_retries}")
            if attempt == max_retries - 1:
                print(f"No se pudo obtener {url} después de {max_retries} intentos")
                return ""
            time.sleep(2 ** attempt)  # Retroceso exponencial
    return ""

def procesar_entrada(item):
    try:
        termino = item.find('a').text.strip()
        descripcion_breve = item.find('div').text.strip() if item.find('div') else ""
        url_termino = 'http://www.tugurium.com/gti/' + item.find('a')['href']
        detalle_definicion = obtener_detalles(url_termino)
        return {
            'Término': termino,
            'Descripciones': descripcion_breve,
            'Información Adicional': detalle_definicion
        }
    except Exception as e:
        print(f"Error al procesar entrada: {e}")
        return None

def leer_csv_existente(nombre_archivo):
    if os.path.exists(nombre_archivo):
        return pd.read_csv(nombre_archivo)
    return pd.DataFrame(columns=['Término', 'Descripciones', 'Información Adicional'])

def guardar_csv_incremental(df, nombre_archivo):
    df_existente = leer_csv_existente(nombre_archivo)
    df_concatenado = pd.concat([df_existente, df]).drop_duplicates(subset='Término')
    df_concatenado.to_csv(nombre_archivo, index=False)

def obtener_terminos_nuevos(items, df_existente):
    terminos_existentes = df_existente['Término'].tolist()
    return [item for item in items if item.find('a').text.strip() not in terminos_existentes]

def scrapeo_progresivo(items, nombre_archivo, batch_size=100):
    df_existente = leer_csv_existente(nombre_archivo)
    terminos_nuevos = obtener_terminos_nuevos(items, df_existente)

    total_terminos = len(terminos_nuevos)
    print(f"Total de términos nuevos: {total_terminos}")

    resultados = []
    contador = 0
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for resultado in executor.map(procesar_entrada, terminos_nuevos):
            if resultado:
                resultados.append(resultado)
                contador += 1
                if contador % batch_size == 0:
                    guardar_csv_incremental(pd.DataFrame(resultados), nombre_archivo)
                    resultados = []  # Limpiar la lista después de guardar
                    print(f"Scraped {contador} out of {total_terminos} terms")

    # Guardar cualquier resultado restante después de que termine el scraping
    if resultados:
        guardar_csv_incremental(pd.DataFrame(resultados), nombre_archivo)

    print(f"\nTiempo total de ejecución: {time.time() - start_time} segundos")
    print(f"\nNúmero total de entradas procesadas: {contador}")

# URL para las entradas que comienzan con 'D'
url = 'http://www.tugurium.com/gti/contenido.php?INI=D'

# Realizar la solicitud a la página
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Encontrar todas las entradas
items = soup.select('section.i_link li')

# Aqui podemos limitar las entradas de ser necesario para detener el script en caso de necesitar hacer pruebas
items = items[:]

# Nombre del archivo CSV
nombre_archivo = 'glosario_letra_D.csv'

# Ejecutar el scrapeo progresivo
scrapeo_progresivo(items, nombre_archivo, batch_size=100)


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
