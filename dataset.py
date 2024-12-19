import pandas as pd
import PyPDF2
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

# Función para leer archivos CSV
def leer_csv(archivo):
    try:
        df = pd.read_csv(archivo)
        return df
    except Exception as e:
        print(f"Error al leer el archivo CSV {archivo}: {e}")
        return pd.DataFrame()

# Función para leer archivos TXT
def leer_txt(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            texto = f.readlines()
        return pd.DataFrame({"Text": [line.strip() for line in texto if line.strip()]})
    except Exception as e:
        print(f"Error al leer el archivo TXT {archivo}: {e}")
        return pd.DataFrame()

# Función para leer archivos PDF
def leer_pdf(archivo):
    try:
        with open(archivo, "rb") as f:
            lector_pdf = PyPDF2.PdfReader(f)
            texto = []
            for pagina in lector_pdf.pages:
                texto.append(pagina.extract_text())
        return pd.DataFrame({"Text": texto})
    except Exception as e:
        print(f"Error al leer el archivo PDF {archivo}: {e}")
        return pd.DataFrame()

# Construir dataset
def construir_dataset():
    print("Selecciona los archivos para construir el dataset (.csv, .txt, .pdf):")
    Tk().withdraw()  # Oculta la ventana principal de tkinter
    archivos = askopenfilenames(
        filetypes=[("Archivos soportados", "*.csv;*.txt;*.pdf")],
        title="Seleccionar archivos"
    )

    if not archivos:
        print("No se seleccionaron archivos.")
        return pd.DataFrame()

    dataset = pd.DataFrame()
    for archivo in archivos:
        if archivo.endswith(".csv"):
            df = leer_csv(archivo)
        elif archivo.endswith(".txt"):
            df = leer_txt(archivo)
        elif archivo.endswith(".pdf"):
            df = leer_pdf(archivo)
        else:
            print(f"Tipo de archivo no soportado: {archivo}")
            continue

        if not df.empty:
            df["Fuente"] = archivo  # Agregar la fuente del archivo
            dataset = pd.concat([dataset, df], ignore_index=True)
    
    return dataset

# Guardar dataset en un archivo CSV
def guardar_dataset(dataset, nombre_archivo="dataset.csv"):
    try:
        dataset.to_csv(nombre_archivo, index=False, encoding="utf-8")
        print(f"Dataset guardado exitosamente como {nombre_archivo}")
    except Exception as e:
        print(f"Error al guardar el dataset: {e}")

# Programa principal para construir y guardar el dataset
def main():
    dataset = construir_dataset()
    if not dataset.empty:
        guardar_dataset(dataset)

if __name__ == "__main__":
    main()
