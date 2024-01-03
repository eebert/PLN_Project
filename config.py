import os

# Obtener la ruta del directorio del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Las rutas relativas a BASE_DIR
PDF_DIRECTORY = os.path.join(BASE_DIR, "data", "pdf")
CSV_DIRECTORY = os.path.join(BASE_DIR, "data", "csv")
XLSX_DIRECTORY = os.path.join(BASE_DIR, "data", "xlsx")
TEXT_DIRECTORY = os.path.join(BASE_DIR, "data", "txt")
SPEECH_TYPE = "Independencia"

# --- Configuración Inicial ---

ACCOUNT_NAME = "tfmejm"
ACCOUNT_KEY = "A6HByzBaYzYANlZqqLYtLW4OVSYWDzqnMScFEgoqHTV/7OHgJFCXBsqKc9qHmjQUN8A5/BXnKZfy+AStDC6hlA=="
CONTAINER_NAME = "discursos"
