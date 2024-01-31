import os

# Obtener la ruta del directorio del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Las rutas relativas a BASE_DIR
# NER
PDF_DIRECTORY = os.path.join(BASE_DIR, "data-NER", "pdf")
CSV_DIRECTORY = os.path.join(BASE_DIR, "data-NER", "csv")
XLSX_DIRECTORY = os.path.join(BASE_DIR, "data-NER", "xlsx")
TEXT_DIRECTORY = os.path.join(BASE_DIR, "data-NER", "txt")
SPEECH_TYPE = "Independencia"

# BoW
PDF_DIRECTORY_BOW = os.path.join(BASE_DIR, "data-BoW", "pdf")
CSV_DIRECTORY_BOW = os.path.join(BASE_DIR, "data-BoW", "csv")
VOCABULARY_DIRECTORY_BOW = os.path.join(BASE_DIR, "data-BoW", "vocabulary")

#EDA
PDF_DIRECTORY_EDA = os.path.join(BASE_DIR, "data-EDA", "pdf")
XLSX_DIRECTORY_EDA = os.path.join(BASE_DIR, "data-EDA", "xlsx")
JSON_DIRECTORY_EDA = os.path.join(BASE_DIR, "data-EDA", "json")

# --- Configuración Inicial ---

ACCOUNT_NAME = "tfmejm"
ACCOUNT_KEY = "A6HByzBaYzYANlZqqLYtLW4OVSYWDzqnMScFEgoqHTV/7OHgJFCXBsqKc9qHmjQUN8A5/BXnKZfy+AStDC6hlA=="
CONTAINER_NAME = "discursos"
