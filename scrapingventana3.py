import asyncio
from twikit import Client, TooManyRequests
import time
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint
import os
import json
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename

# Configuración inicial
COOKIES_PATH = r'c:/Users/edgar/OneDrive/Documents/01Proyectos IA/Poder/cookies.json'

# Opciones de temas y consultas
TEMAS = {
    "1": "(ley poder judicial mexico) lang:es until:2024-12-06 since:2023-01-01",
    "2": "(ley de organismos autónomos mexico) lang:es until:2024-12-06 since:2023-01-01"
}

def check_file_exists(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"El archivo {filepath} no existe. Verifica la ruta.")

async def get_tweets(tweets):
    if tweets is None:
        print(f'{datetime.now()} - Obteniendo tweets...')
        tweets = await client.search_tweet(QUERY, product='Top')
    else:
        wait_time = randint(5, 10)
        print(f'{datetime.now()} - Obteniendo siguientes tweets después de {wait_time} segundos...')
        time.sleep(wait_time)
        tweets = await tweets.next()

    return tweets

async def main():
   
    print("Selecciona el tema para hacer el scraping:")
    print("1. Ley del Poder Judicial")
    print("2. Ley de Organismos Autónomos")
    tema = input("Escribe el número correspondiente (1 o 2): ").strip()

    if tema not in TEMAS:
        print("Selección inválida. Por favor elige 1 o 2.")
        return

    global QUERY
    QUERY = TEMAS[tema]
    print(f"Consulta seleccionada: {QUERY}")

    try:
        minimum_tweets = int(input("Ingresa la cantidad de tweets que deseas consultar: "))
        if minimum_tweets <= 0:
            raise ValueError("La cantidad debe ser un número positivo.")
    except ValueError as e:
        print(f"Entrada inválida: {e}. Usando 50 tweets por defecto.")
        minimum_tweets = 50

    config_path = r'c:/Users/edgar/OneDrive/Documents/01Proyectos IA/Poder/config.ini'

    try:
        config = ConfigParser()
        config.read(config_path)

        print("Contenido del archivo config.ini:")
        with open(config_path, 'r', encoding='utf-8') as f:
            print(f.read())

        if 'X' not in config:
            raise ValueError(f"La sección [X] no existe en el archivo {config_path}")

        username = config['X']['username']
        email = config['X']['email']
        password = config['X']['password']

    except FileNotFoundError:
        print(f"El archivo config.ini no se encuentra en la ruta {config_path}")
        return
    except ValueError as e:
        print(str(e))
        return
    
    print("Selecciona dónde deseas guardar el archivo CSV:")
    Tk().withdraw()  
    file_path = asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Guardar archivo CSV"
    )

    if not file_path:
        print("No se seleccionó ninguna ubicación para guardar el archivo.")
        return

    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Tweet_count', 'Username', 'Text', 'Created At', 'Retweets', 'Likes'])

    global client
    client = Client(language='es-MX')

    try:
        check_file_exists(COOKIES_PATH)
        client.load_cookies(COOKIES_PATH) 
        print(f"Cookies cargadas correctamente desde {COOKIES_PATH}")
    except FileNotFoundError as e:
        print(str(e))
        print("Inicia sesión para generar el archivo cookies.json")

    tweet_count = 0
    tweets = None

    # Obtener tweets
    while tweet_count < minimum_tweets:
        try:
            tweets = await get_tweets(tweets)
        except TooManyRequests as e:
            rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
            print(f'{datetime.now()} - Límite de tasa alcanzado. Esperando hasta {rate_limit_reset}')
            wait_time = rate_limit_reset - datetime.now()
            time.sleep(wait_time.total_seconds())
            continue

        if not tweets:
            print(f'{datetime.now()} - No se encontraron más tweets')
            break

        for tweet in tweets:
            tweet_count += 1
            tweet_data = [
                tweet_count, 
                tweet.user.name, 
                tweet.text, 
                tweet.created_at, 
                tweet.retweet_count, 
                tweet.favorite_count
            ]

            with open(file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(tweet_data)

            if tweet_count >= minimum_tweets:
                break

        print(f'{datetime.now()} - Obtenidos {tweet_count} tweets')

    print(f'{datetime.now()} - ¡Completado! Total de tweets obtenidos: {tweet_count}')

# Ejecutar la función principal
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error inesperado: {e}")
