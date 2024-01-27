# utils/file_utils.py
import os
import logging
from requests.exceptions import Timeout, RequestException
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from config import ACCOUNT_NAME, ACCOUNT_KEY, CONTAINER_NAME, PDF_DIRECTORY
import re
import pdfplumber
import pandas as pd


# Asegura que el directorio para un archivo dado exista, creándolo si es necesario.
def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


# Inicializa y retorna un cliente de Azure Blob Storage.
def initialize_blob_client():
    connect_str = f"DefaultEndpointsProtocol=https;AccountName={ACCOUNT_NAME};AccountKey={ACCOUNT_KEY};EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    return blob_service_client.get_container_client(CONTAINER_NAME)


# Descarga un blob de Azure Blob Storage y lo guarda en una ruta local.
def download_blob(blob_client, blob_name, file_path):
    ensure_directory_exists(file_path)
    try:
        response = blob_client.download_blob(blob_name)
        with open(file_path, "wb") as pdf_file:
            pdf_file.write(response.readall())
        return True
    except Timeout:
        logging.warning(f"Timeout occurred while downloading {blob_name}")
    except RequestException as e:
        logging.error(f"Failed to download {blob_name}: {e}")
    return False


def download_all_pdf_files_from_pdf_directory(blob_client):
    pdf_files = []
    existing_files = []
    downloaded_files = []

    blobs_list = blob_client.list_blobs()
    for blob in blobs_list:
        local_pdf_name = os.path.basename(blob.name)
        file_path = os.path.join(PDF_DIRECTORY, local_pdf_name)

        if not os.path.exists(file_path):
            if download_blob(blob_client, blob.name, file_path):
                downloaded_files.append(local_pdf_name)
            else:
                logging.error(f"Failed to download {local_pdf_name}")
        else:
            existing_files.append(local_pdf_name)

        pdf_files.append(local_pdf_name)

    # Logging summaries at the end
    if existing_files:
        logging.info(f"Existing files skipped: {existing_files}")
    if downloaded_files:
        logging.info(f"Downloaded files: {downloaded_files}")

    return pdf_files


# Lee el contenido de texto de un archivo PDF, aplicando un recorte si se especifica.
def read_pdf_file(pdf_path, apply_crop=False, crop_area=(0, 100, 600, 700)):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if apply_crop:
                    cropped_page = page.crop(crop_area)
                    text += cropped_page.extract_text() or ""
                else:
                    text += page.extract_text() or ""
        return text, os.path.basename(pdf_path)
    except pdfplumber.exceptions.PDFSyntaxError as e:
        logging.error(
            f"Archivo PDF corrupto o con formato incorrecto ({pdf_path}): {e}"
        )
        return None, None
    except Exception as e:
        logging.error(f"Error al leer el archivo PDF ({pdf_path}): {e}")
        return None, None


# Lee el contenido de texto de un archivo TXT.
def read_txt_file(txt_path):
    try:
        with open(txt_path, "r", encoding="utf-8") as txt_file:
            return txt_file.read()
    except FileNotFoundError:
        logging.error(f"Error: el archivo TXT no existe ({txt_path})")
        return None
    except Exception as e:
        logging.error(f"Error al leer el archivo TXT ({txt_path}): {e}")
        return None


# Lee el contenido de un archivo Excel y lo devuelve como un DataFrame de pandas.
def read_excel_file(excel_path):
    try:
        return pd.read_excel(excel_path)
    except FileNotFoundError:
        logging.error(f"Error: el archivo Excel no existe ({excel_path})")
        return None
    except Exception as e:
        logging.error(f"Error al leer el archivo Excel ({excel_path}): {e}")
        return None


def write_txt_file(content, file_path):
    ensure_directory_exists(file_path)
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
    except Exception as e:
        logging.error(f"Error al escribir en el archivo ({file_path}): {e}")


# Extrae el texto de un archivo PDF.
def extract_text_from_pdf(pdf_path):
    raw_text, _ = read_pdf_file(pdf_path)
    return raw_text


# Guarda texto en un archivo.
def save_text_to_file(text, file_path):
    write_txt_file(text, file_path)


# Procesa todos los archivos PDF en un directorio, guardando su texto en archivos de texto.
def process_pdfs_in_directory_to_txt(
    pdf_directory, txt_directory, recreate_existing_files=False
):
    text_files = []
    created_files = []
    skipped_files = []

    for pdf_file in os.listdir(pdf_directory):
        if pdf_file.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, pdf_file)
            txt_file_path = os.path.join(
                txt_directory, os.path.splitext(pdf_file)[0] + ".txt"
            )
            txt_file_name = os.path.basename(txt_file_path)

            if not os.path.exists(txt_file_path) or recreate_existing_files:
                raw_text = extract_text_from_pdf(pdf_path)
                if raw_text is not None:
                    save_text_to_file(raw_text, txt_file_path)
                    created_files.append(txt_file_name)
            else:
                skipped_files.append(txt_file_name)

            text_files.append(txt_file_name)

    if created_files:
        logging.info(f"Created text files: {created_files}")
    if skipped_files:
        logging.info(f"Existing text files skipped: {skipped_files}")

    return text_files


# Extrae metadatos a partir del nombre del archivo.
def extract_metadata_from_filename(filename):
    country = filename.split("_")[0]
    year_match = re.search(r"\d{4}", filename)
    year = year_match.group() if year_match else "Desconocido"
    president_match = re.search(r"(?<=\d{4}_)\w+", filename)
    president = president_match.group() if president_match else "Desconocido"
    return year, president, country


# Guarda un DataFrame de pandas en un archivo Excel.
def save_df_to_excel(df, excel_dir, excel_filename):
    ensure_directory_exists(os.path.join(excel_dir, excel_filename))
    path = os.path.join(excel_dir, excel_filename)
    df.to_excel(path, index=False)
    logging.info(f"DataFrame guardado en {path}")


# Guarda datos en un archivo Excel. Los datos pueden ser de discursos, oraciones, entidades, etc.
def save_data_to_excel(data, xlsx_directory, filename):
    if isinstance(data, list):
        data = pd.DataFrame(data)
    save_df_to_excel(data, xlsx_directory, filename)
