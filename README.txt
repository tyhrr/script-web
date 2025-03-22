PRIMERA PARTE

Para abordar esta tarea de scraping y extracción de un glosario en formato CSV desde el sitio web, se detalla paso a paso el proceso con todas las consideraciones técnicas. Trabajaremos con Python y la librería BeautifulSoup para extraer el contenido HTML, y utilizaremos Pandas para manipular los datos y generar el CSV.

Paso 1: Análisis del sitio web

El primer paso es analizar cómo están organizados los datos en el sitio web. En el caso de http://www.tugurium.com/gti/termino.php?Tr=cast, parece que cada término del glosario tiene una URL con un identificador único en el parámetro Tr.

Así que necesitamos entender:

Cómo se generan esos parámetros.

Si hay una lista maestra de términos o si debes iterar a través de combinaciones posibles.

Esto también incluye inspeccionar la estructura del HTML para identificar dónde se encuentran los términos y sus traducciones.

SEGUNDA PARTE


!pip install requests
!pip install beautifulsoup4
!pip install pandas

requests: Para hacer las peticiones HTTP y descargar las páginas.

BeautifulSoup4: Para procesar el HTML y extraer los datos.

Pandas: Para almacenar los resultados en un CSV.


Tercera parte

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
