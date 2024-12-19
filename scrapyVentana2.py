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

# Configuración
QUERY = '(ley poder judicial mexico) lang:es until:2024-12-06 since:2023-01-01'

# Verificar la existencia del archivo cookies.json
COOKIES_PATH = r'c:/Users/edgar/OneDrive/Documents/01Proyectos IA/Poder/cookies.json'

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
    # Solicitar al usuario la cantidad de tweets que desea consultar
    try:
        minimum_tweets = int(input("Ingresa la cantidad de tweets que deseas consultar: "))
        if minimum_tweets <= 0:
            raise ValueError("La cantidad debe ser un número positivo.")
    except ValueError as e:
        print(f"Entrada inválida: {e}. Usando 50 tweets por defecto.")
        minimum_tweets = 50

    # Cargar archivo de configuración
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

    # Solicitar al usuario que elija dónde guardar el archivo CSV
    print("Selecciona dónde deseas guardar el archivo CSV:")
    Tk().withdraw()  # Ocultar la ventana principal de tkinter
    file_path = asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Guardar archivo CSV"
    )

    if not file_path:
        print("No se seleccionó ninguna ubicación para guardar el archivo.")
        return

    # Crear el archivo CSV en la ubicación seleccionada
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Tweet_count', 'Username', 'Text', 'Created At', 'Retweets', 'Likes'])

    # Autenticación con X.com (Twitter)
    global client
    client = Client(language='es-MX')

    # Verificar y cargar cookies
    try:
        check_file_exists(COOKIES_PATH)
        client.load_cookies(COOKIES_PATH)  # Usa las cookies existentes
        print(f"Cookies cargadas correctamente desde {COOKIES_PATH}")
    except FileNotFoundError as e:
        print(str(e))
        print("Inicia sesión para generar el archivo cookies.json")
        # Aquí podrías implementar una autenticación con client.login(username, password)

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

            # Guardar tweets en el archivo CSV
            with open(file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(tweet_data)

            # Detenerse si alcanza el límite de tweets
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
