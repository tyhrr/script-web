# Instalaremos las herramientas necesarias:
# !pip install requests
# !pip install beautifulsoup4
# !pip install pandas
# 
# Nota: Se recomienda instalar las dependencias usando:
# pip install -r requirements.txt

"""
Web Scraper de Glosario Técnico
================================

Script para extraer términos técnicos y sus definiciones del sitio web tugurium.com.
Utiliza scraping concurrente, guardado incremental y manejo robusto de errores.

Autor: Proyecto Web Scraping
Fecha: 2025
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
import time
import random
from requests.exceptions import RequestException
import os

def obtener_detalles(url, max_retries=3):
    """
    Obtiene los detalles adicionales de un término desde su página específica.
    
    Args:
        url (str): URL de la página del término
        max_retries (int): Número máximo de reintentos en caso de error
    
    Returns:
        str: Texto con la información adicional del término o cadena vacía si falla
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            # Pausa aleatoria para simular comportamiento humano
            time.sleep(random.uniform(1, 3))
            
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
            # Retroceso exponencial
            time.sleep(2 ** attempt)
    
    return ""

def procesar_entrada(item):
    """
    Procesa un elemento HTML individual para extraer información del término.
    
    Args:
        item: Elemento BeautifulSoup que contiene la información del término
    
    Returns:
        dict: Diccionario con 'Término', 'Descripciones', 'Información Adicional'
              o None si hay error
    """
    try:
        # Extraer nombre del término
        termino = item.find('a').text.strip()
        
        # Extraer descripción breve
        descripcion_breve = item.find('div').text.strip() if item.find('div') else ""
        
        # Construir URL completa del término
        url_termino = 'http://www.tugurium.com/gti/' + item.find('a')['href']
        
        # Obtener información detallada
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
    """
    Lee un archivo CSV existente o crea un DataFrame vacío si no existe.
    
    Args:
        nombre_archivo (str): Ruta del archivo CSV
    
    Returns:
        pandas.DataFrame: DataFrame con los datos existentes o vacío
    """
    if os.path.exists(nombre_archivo):
        return pd.read_csv(nombre_archivo)
    return pd.DataFrame(columns=['Término', 'Descripciones', 'Información Adicional'])


def guardar_csv_incremental(df, nombre_archivo):
    """
    Guarda datos de forma incremental, evitando duplicados.
    
    Args:
        df (pandas.DataFrame): DataFrame con nuevos datos
        nombre_archivo (str): Ruta del archivo CSV de destino
    """
    df_existente = leer_csv_existente(nombre_archivo)
    df_concatenado = pd.concat([df_existente, df]).drop_duplicates(subset='Término')
    df_concatenado.to_csv(nombre_archivo, index=False)


def obtener_terminos_nuevos(items, df_existente):
    """
    Filtra términos que aún no han sido procesados.
    
    Args:
        items (list): Lista de elementos HTML con términos
        df_existente (pandas.DataFrame): DataFrame con términos ya procesados
    
    Returns:
        list: Lista de términos nuevos para procesar
    """
    terminos_existentes = df_existente['Término'].tolist()
    return [item for item in items if item.find('a').text.strip() not in terminos_existentes]

def scrapeo_progresivo(items, nombre_archivo, batch_size=100):
    """
    Ejecuta el scraping de forma progresiva con guardado incremental.
    
    Args:
        items (list): Lista de elementos HTML con términos a procesar
        nombre_archivo (str): Nombre del archivo CSV de salida
        batch_size (int): Número de términos a procesar antes de guardar
    """
    # Cargar datos existentes y filtrar términos nuevos
    df_existente = leer_csv_existente(nombre_archivo)
    terminos_nuevos = obtener_terminos_nuevos(items, df_existente)

    total_terminos = len(terminos_nuevos)
    print(f"Total de términos nuevos: {total_terminos}")

    if total_terminos == 0:
        print("No hay términos nuevos para procesar.")
        return

    resultados = []
    contador = 0
    start_time = time.time()

    # Procesar términos usando ThreadPoolExecutor para concurrencia
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for resultado in executor.map(procesar_entrada, terminos_nuevos):
            if resultado:
                resultados.append(resultado)
                contador += 1
                
                # Guardar cada batch_size términos procesados
                if contador % batch_size == 0:
                    guardar_csv_incremental(pd.DataFrame(resultados), nombre_archivo)
                    resultados = []  # Limpiar la lista después de guardar
                    print(f"Scraped {contador} out of {total_terminos} terms")

    # Guardar cualquier resultado restante
    if resultados:
        guardar_csv_incremental(pd.DataFrame(resultados), nombre_archivo)

    # Estadísticas finales
    execution_time = time.time() - start_time
    print(f"\nTiempo total de ejecución: {execution_time:.2f} segundos")
    print(f"Número total de entradas procesadas: {contador}")
    print(f"Promedio: {execution_time/contador:.2f} segundos por término" if contador > 0 else "")
    print(f"Archivo guardado como: {nombre_archivo}")

def main():
    """
    Función principal que ejecuta el scraping del glosario.
    
    Configuración actual:
    - Letra: D
    - Archivo de salida: glosario_letra_D.csv
    - Batch size: 100 términos
    """
    # URL para las entradas que comienzan con 'D'
    url = 'http://www.tugurium.com/gti/contenido.php?INI=D'
    
    print("Iniciando scraping del glosario técnico...")
    print(f"URL objetivo: {url}")

    try:
        # Realizar la solicitud a la página principal
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar todas las entradas de términos
        items = soup.select('section.i_link li')
        
        # Aquí podemos limitar las entradas para pruebas si es necesario
        # items = items[:10]  # Descomenta para procesar solo los primeros 10 términos
        
        print(f"Términos encontrados en la página: {len(items)}")

        # Nombre del archivo CSV de salida
        nombre_archivo = 'glosario_letra_D.csv'

        # Ejecutar el scraping progresivo
        scrapeo_progresivo(items, nombre_archivo, batch_size=100)
        
        print("\n¡Scraping completado exitosamente!")
        
    except requests.RequestException as e:
        print(f"Error al acceder a la página principal: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")


if __name__ == "__main__":
    main()
