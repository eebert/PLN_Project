# analysis_eda.py
import logging
from utils.file_utils import read_excel_file
from utils.visualization_utils import (
    create_histogram,
    create_wordcloud,
    create_bar_chart,
    create_countplot,
    create_boxplot
)

# Función para cargar y describir los datos
def load_and_describe_data(file_path):
    logging.info(f"Cargando datos desde {file_path}...")
    df = read_excel_file(file_path)
    logging.info("Datos cargados con éxito.")
    logging.info("Descripción de los datos:")
    logging.info(df.describe())
    return df

# Función para realizar EDA específico de los discursos
def analyze_speeches(df_speeches):
    logging.info("Análisis de los datos de los discursos...")
    # Aquí se pueden agregar análisis específicos para los discursos, como la creación de histogramas, nubes de palabras, etc.
    # Por ejemplo:
    create_histogram(df_speeches['text_raw'].str.split().str.len(), "Histograma de la Longitud de los Discursos", "Número de Palabras", "Frecuencia")

# Función para realizar EDA específico de las oraciones
def analyze_sentences(df_sentences):
    logging.info("Análisis de los datos de las oraciones...")
    # Similar a analyze_speeches, aquí se agregarían los análisis y visualizaciones para las oraciones.

# Función para visualizar la información
def visualize_data(df_speeches, df_sentences):
    logging.info("Creando visualizaciones de los datos...")
    # Llama a las funciones de visualización de datos aquí.

# Funciones adicionales para análisis más detallados pueden ser agregadas aquí.
