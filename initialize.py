# initialize.py
import subprocess
import nltk
import spacy
import logging
from importlib import reload


def download_nltk_packages():
    required_packages = {"stopwords": "corpora/stopwords", "punkt": "tokenizers/punkt"}
    for package_name, package_path in required_packages.items():
        try:
            nltk.data.find(package_path)
            logging.info(f"El paquete NLTK '{package_name}' ya está instalado.")
        except LookupError:
            logging.info(f"Descargando el paquete NLTK '{package_name}'...")
            nltk.download(package_name)


def set_global_logging():
    reload(logging)
    # Configura el logging a nivel INFO para tu aplicación
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Ajusta el nivel de logging para las bibliotecas de Azure SDK a WARNING para reducir el detalle
    azure_loggers = ["azure", "azure.storage.blob", "azure.core.pipeline.policies"]
    for logger in azure_loggers:
        logging.getLogger(logger).setLevel(logging.WARNING)


set_global_logging()


def check_and_download_spacy_model(model_name):
    try:
        # Intenta cargar el modelo para ver si ya está instalado
        spacy.load(model_name)
        logging.info(f"Modelo spaCy '{model_name}' ya está instalado.")
    except OSError:
        # Si el modelo no está instalado, intenta descargarlo automáticamente
        try:
            logging.info(
                f"Modelo spaCy '{model_name}' no encontrado. Intentando descargar..."
            )
            subprocess.run(
                ["python", "-m", "spacy", "download", model_name], check=True
            )
        except Exception as e:
            # Informar al usuario que necesita realizar la instalación manualmente
            logging.error(
                f"No se pudo descargar automáticamente el modelo '{model_name}'."
            )
            logging.error("Error: " + str(e))
            logging.info(
                "Por favor, instala el modelo spaCy manualmente ejecutando el siguiente comando:"
            )
            logging.info(f"python -m spacy download {model_name}")
            logging.info(
                "Si necesitas derechos de administrador, ejecuta el comando en una terminal con privilegios adecuados."
            )
