import requests
from bs4 import BeautifulSoup
from googlesearch import search
import urllib3
import time
import tkinter as tk
from tkinter import simpledialog, filedialog

# Deshabilitar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Temas predefinidos con sufijo "Noticias"
TEMAS = {
    "1": "Ley del Poder Judicial Noticias",
    "2": "Ley de Organismos Autónomos Noticias"
}

def get_google_links(query, num_results=5, offset=0):
    """
    Obtiene una lista de enlaces de resultados de búsqueda en Google.
    La biblioteca `googlesearch` no admite paginación directamente, 
    por lo que simulamos el manejo de bloques mediante `offset`.
    """
    all_links = list(search(query, num_results=num_results * 10))  # Obtener más resultados y paginar manualmente
    return all_links[offset:offset + num_results]

def scrape_web_pages(links):
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
            file.write(f"Título: {item['title']}\n")
            file.write(f"Link: {item['link']}\n")
            file.write(f"Contenido:\n{item['content']}\n")
            file.write("\n" + "-"*80 + "\n\n")
    print(f"Archivo de texto generado: {output_filename}")

if __name__ == "__main__":
    # Seleccionar tema
    print("Selecciona el tema para hacer el scraping:")
    print("1. Ley del Poder Judicial Noticias")
    print("2. Ley de Organismos Autónomos Noticias")
    tema = input("Escribe el número correspondiente (1 o 2): ").strip()

    if tema not in TEMAS:
        print("Selección inválida. Por favor elige 1 o 2.")
        exit()

    query = TEMAS[tema]
    tema_nombre = query.replace(" ", "_")  # Usar el nombre del tema en los archivos
    print(f"Consulta seleccionada: {query}")

    # Crear ventana de Tkinter
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal

    # Solicitar ruta donde guardar los archivos
    txt_path = filedialog.askdirectory(title="Seleccione la carpeta para guardar los archivos de texto")
    if not txt_path:
        print("No se seleccionó ninguna carpeta. Saliendo...")
        exit()

    print("Realizando scraping, por favor espere...")
    total_pages = 50
    pages_per_cycle = 5
    offset = 0
    cycle = 1

    while offset < total_pages:
        print(f"Iniciando ciclo {cycle}...")

        # Obtener los enlaces para el bloque actual
        links = get_google_links(query, num_results=pages_per_cycle, offset=offset)

        # Extraer contenido de las páginas web
        scraped_data = scrape_web_pages(links)

        # Generar archivo de texto para este bloque
        output_filename = f"{txt_path}/{tema_nombre}_bloque_{cycle}.txt"
        generate_txt(scraped_data, output_filename)

        offset += pages_per_cycle
        cycle += 1

        if offset < total_pages:
            print(f"Esperando 2 minutos antes del próximo ciclo...")
            time.sleep(10)  # Esperar 2 minutos
        else:
            print("Proceso completado. Se han buscado 50 páginas.")
