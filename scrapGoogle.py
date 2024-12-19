import requests
from bs4 import BeautifulSoup
from googlesearch import search
import urllib3
import tkinter as tk
from tkinter import simpledialog, filedialog

# Deshabilitar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_google_links(query):
    links = []
    for url in search(query, num_results=5):
        links.append(url)
    return links

def scrape_web_pages(query):
    links = get_google_links(query)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    scraped_data = []
    for link in links:
        try:
            page_response = requests.get(link, headers=headers, timeout=10, verify=False)
            page_soup = BeautifulSoup(page_response.text, "html.parser")
            title = page_soup.title.string.strip() if page_soup.title else "No Title"
            paragraphs = page_soup.find_all("p")
            text = " ".join([p.get_text().strip() for p in paragraphs[:5] if p.get_text().strip()])
            if text:
                scraped_data.append({"title": title, "link": link, "content": text})
        except Exception as e:
            print(f"Error scraping {link}: {e}")
    return scraped_data

def generate_txt(data, output_filename):
    with open(output_filename, "w", encoding="utf-8") as file:
        for item in data:
            # Escribir título
            file.write(f"Título: {item['title']}\n")
            # Escribir enlace
            file.write(f"Link: {item['link']}\n")
            # Escribir contenido
            file.write(f"Contenido:\n{item['content']}\n")
            file.write("\n" + "-"*80 + "\n\n")  # Separador entre entradas
    print(f"Archivo de texto generado: {output_filename}")

if __name__ == "__main__":
    # Crear ventana de Tkinter
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal

    # Solicitar término de búsqueda
    query = simpledialog.askstring("Término de búsqueda", "Ingrese el término de búsqueda:")
    if not query:
        print("No se ingresó un término de búsqueda. Saliendo...")
        exit()

    # Solicitar nombre del archivo
    txt_name = simpledialog.askstring("Nombre del archivo de texto", "Ingrese el nombre del archivo de texto (sin extensión):")
    if not txt_name:
        print("No se ingresó un nombre para el archivo. Saliendo...")
        exit()

    # Solicitar ruta donde guardar el archivo
    txt_path = filedialog.askdirectory(title="Seleccione la carpeta para guardar el archivo de texto")
    if not txt_path:
        print("No se seleccionó ninguna carpeta. Saliendo...")
        exit()

    # Crear la ruta completa del archivo
    full_path = f"{txt_path}/{txt_name}.txt"

    print("Realizando scraping, por favor espere...")
    scraped_data = scrape_web_pages(query)
    if scraped_data:
        generate_txt(scraped_data, full_path)
    else:
        print("No se encontró información relevante.")
