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


def ensure_directory_exists(file_path):
    """
    Asegura que el directorio para un archivo dado exista, creándolo si es necesario.

    Args:
        file_path (str): Ruta del archivo.
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def initialize_blob_client():
    """
    Inicializa y retorna un cliente de Azure Blob Storage.

    Returns:
        BlobServiceClient: Cliente de Azure Blob Storage.
    """
    connect_str = f"DefaultEndpointsProtocol=https;AccountName={ACCOUNT_NAME};AccountKey={ACCOUNT_KEY};EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    return blob_service_client.get_container_client(CONTAINER_NAME)


def download_blob(blob_client, blob_name, file_path):
    """
    Descarga un blob de Azure Blob Storage y lo guarda en una ruta local.

    Args:
        blob_client (BlobServiceClient): Cliente de Azure Blob Storage.
        blob_name (str): Nombre del blob a descargar.
        file_path (str): Ruta del archivo local para guardar el blob.

    Returns:
        bool: True si la descarga fue exitosa, False de lo contrario.
    """
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


def read_pdf_file(pdf_path, apply_crop=False, crop_area=(0, 100, 600, 700)):
    """
    Lee el contenido de texto de un archivo PDF, aplicando un recorte si se especifica.

    Args:
        pdf_path (str): Ruta del archivo PDF a leer.
        apply_crop (bool, optional): Si se aplica el recorte.
        crop_area (tuple, optional): Área para extraer el texto (x0, y0, x1, y1), solo si apply_crop es True.

    Returns:
        tuple: Texto extraído del PDF y el nombre del archivo, o (None, None) si hay un error.
    """
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


def read_txt_file(txt_path):
    """
    Lee el contenido de texto de un archivo TXT.
    Args:
        txt_path (str): Ruta del archivo TXT a leer.
    Returns:
        str: Texto extraído del archivo TXT, o None si el archivo no existe o hay un error.
    """
    try:
        with open(txt_path, "r", encoding="utf-8") as txt_file:
            return txt_file.read()
    except FileNotFoundError:
        logging.error(f"Error: el archivo TXT no existe ({txt_path})")
        return None
    except Exception as e:
        logging.error(f"Error al leer el archivo TXT ({txt_path}): {e}")
        return None

def read_excel_file(excel_path):
    """
    Lee el contenido de un archivo Excel y lo devuelve como un DataFrame de pandas.
    
    Args:
        excel_path (str): Ruta del archivo Excel a leer.
    
    Returns:
        pandas.DataFrame: DataFrame con los datos leídos, o None si el archivo no existe o hay un error.
    """
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


def extract_text_from_pdf(pdf_path):
    """
    Extrae el texto de un archivo PDF.

    Args:
        pdf_path (str): Ruta del archivo PDF.

    Returns:
        str: Texto extraído del PDF.
    """
    raw_text, _ = read_pdf_file(pdf_path)
    return raw_text


def save_text_to_file(text, file_path):
    """
    Guarda texto en un archivo.

    Args:
        text (str): Texto a guardar.
        file_path (str): Ruta del archivo donde se guardará el texto.
    """
    write_txt_file(text, file_path)


def process_pdfs_in_directory_to_txt(
    pdf_directory, txt_directory, recreate_existing_files=False
):
    """
    Procesa todos los archivos PDF en un directorio, guardando su texto en archivos de texto.

    Args:
        pdf_directory (str): Ruta al directorio que contiene los archivos PDF.
        txt_directory (str): Ruta al directorio donde se guardarán los archivos .txt.
        recreate_existing_files (bool): Si es True, se recrearán archivos .txt existentes.
    """
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


def extract_metadata_from_filename(filename):
    """Extrae metadatos a partir del nombre del archivo."""
    country = filename.split("_")[0]
    year_match = re.search(r"\d{4}", filename)
    year = year_match.group() if year_match else "Desconocido"
    president_match = re.search(r"(?<=\d{4}_)\w+", filename)
    president = president_match.group() if president_match else "Desconocido"
    return year, president, country





def save_df_to_excel(df, excel_dir, excel_filename):
    """
    Guarda un DataFrame de pandas en un archivo Excel.

    Args:
        df (pandas.DataFrame): DataFrame a guardar.
        excel_dir (str): Directorio donde se guardará el archivo Excel.
        excel_filename (str): Nombre del archivo Excel.

    Returns:
        None
    """
    ensure_directory_exists(os.path.join(excel_dir, excel_filename))
    path = os.path.join(excel_dir, excel_filename)
    df.to_excel(path, index=False)
    logging.info(f"DataFrame guardado en {path}")



def save_data_to_excel(data, xlsx_directory, filename):
    """
    Guarda datos en un archivo Excel. Los datos pueden ser de discursos, oraciones, entidades, etc.

    Args:
        data (list or pandas.DataFrame): Datos a guardar. Si es una lista, se convertirá en DataFrame.
        xlsx_directory (str): Directorio para guardar el archivo Excel.
        filename (str): Nombre del archivo Excel.

    Returns:
        None
    """
    if isinstance(data, list):
        data = pd.DataFrame(data)
    save_df_to_excel(data, xlsx_directory, filename)

