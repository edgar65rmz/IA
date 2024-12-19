import os
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.simpledialog as simpledialog
from PyPDF2 import PdfReader
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np

# Configuración de directorio de salida
output_dir = r"C:\Users\edgar\OneDrive\Documents\ollamaIA\scraping\metodo"
os.makedirs(output_dir, exist_ok=True)

# Funciones para extracción de texto
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_csv(file_path, column_name):
    data = pd.read_csv(file_path)
    text = " ".join(data[column_name].astype(str))
    return text

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text

# Función para generar embeddings
def generate_embeddings(text, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    sentences = text.split(".")  # Dividir texto en oraciones
    embeddings = model.encode(sentences)
    return embeddings

# Función para procesar archivos
def process_file(file_path, file_type, column_name=None):
    # Extraer texto según el tipo de archivo
    if file_type == "pdf":
        text = extract_text_from_pdf(file_path)
    elif file_type == "csv":
        if not column_name:
            raise ValueError("Se requiere 'column_name' para archivos CSV.")
        text = extract_text_from_csv(file_path, column_name)
    elif file_type == "txt":
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError("Tipo de archivo no soportado.")
    
    # Generar embeddings
    embeddings = generate_embeddings(text)
    return text, embeddings

# Función para guardar embeddings y texto original en texto plano
def save_embeddings_as_text(embeddings, text, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        flattened_embeddings = " ".join(" ".join(map(str, emb)) for emb in embeddings)
        file.write(flattened_embeddings + "\n")
        file.write(text)

# Función para procesar múltiples archivos seleccionados
def process_and_save_files(file_paths, csv_column_name=None):
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == ".pdf":
                text, embeddings = process_file(file_path, "pdf")
            elif file_ext == ".csv":
                if not csv_column_name:
                    raise ValueError(f"Para procesar {file_name}, se requiere una columna especificada.")
                text, embeddings = process_file(file_path, "csv", column_name=csv_column_name)
            elif file_ext == ".txt":
                text, embeddings = process_file(file_path, "txt")
            else:
                print(f"Tipo de archivo no soportado: {file_name}")
                continue

            # Guardar embeddings y texto original como texto plano
            output_file = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_embeddings.txt")
            save_embeddings_as_text(embeddings, text, output_file)
            print(f"Embeddings y texto guardados en: {output_file}")
        
        except Exception as e:
            print(f"Error procesando {file_name}: {e}")

# Interfaz gráfica con Tkinter
def open_file_dialog():
    # Abrir ventana de selección de archivos
    file_paths = filedialog.askopenfilenames(
        title="Selecciona los archivos",
        filetypes=[
            ("Archivos soportados", "*.pdf *.csv *.txt"),
            ("Archivos PDF", "*.pdf"),
            ("Archivos CSV", "*.csv"),
            ("Archivos TXT", "*.txt")
        ]
    )
    
    if file_paths:
        # Pedir columna si hay un CSV
        csv_column_name = None
        if any(path.endswith(".csv") for path in file_paths):
            csv_column_name = simpledialog.askstring(
                "Nombre de la columna",
                "Por favor, introduce el nombre de la columna para procesar CSV:"
            )
        
        # Procesar archivos
        process_and_save_files(file_paths, csv_column_name)
        messagebox.showinfo("Éxito", "Los archivos se han procesado y los embeddings se han guardado como texto plano.")
    else:
        messagebox.showwarning("Sin selección", "No seleccionaste ningún archivo.")

# Configuración de la ventana principal
def main():
    root = tk.Tk()
    root.title("Procesador de Archivos y Embeddings")

    # Tamaño y posición de la ventana
    root.geometry("400x200")
    root.resizable(False, False)

    # Etiqueta de bienvenida
    label = tk.Label(root, text="Procesador de Archivos Embeddings", font=("Arial", 16))
    label.pack(pady=20)

    # Botón para abrir el diálogo de selección
    button = tk.Button(root, text="Cargar Archivos", command=open_file_dialog, font=("Arial", 12))
    button.pack(pady=20)

    # Iniciar el bucle de la ventana
    root.mainloop()

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
