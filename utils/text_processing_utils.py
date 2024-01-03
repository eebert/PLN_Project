# utils/text_processing.py
import os
import re
import string
import nltk
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from initialize import download_nltk_packages
from utils.file_utils import extract_metadata_from_filename, read_txt_file

# Llama a download_nltk_packages para asegurarte de que los paquetes necesarios estén disponibles
download_nltk_packages()

spanish_stopwords = set(nltk.corpus.stopwords.words("spanish"))


def clean_text(text):
    """
    Realiza la limpieza a nivel de texto completo.
    Esta limpieza se aplica después de extraer el texto del PDF y antes de convertirlo en un archivo de texto plano.
    Se enfoca en eliminar elementos no deseados como texto entre paréntesis y números.
    """
    text = re.sub(r"\(.*?\)", "", text)  # Elimina texto entre paréntesis
    #text = re.sub(r"\d+", "", text)  # Elimina números
    return text


def clean_sentence(sentence):
    """
    Realiza la limpieza a nivel de oración.
    Esta limpieza se aplica después de dividir el texto en oraciones.
    Se enfoca en eliminar stopwords y puntuación para simplificar cada oración.
    """
    words = word_tokenize(sentence)
    cleaned_sentence = " ".join(
        word for word in words if word.isalpha() or word.istitle() and word.lower() not in spanish_stopwords
    )
    # No elimina la puntuación aquí si tu modelo de NER la necesita
    return cleaned_sentence


def clean_sentences(sentences):
    """Limpia cada oración en una lista de oraciones."""
    return [clean_sentence(sentence) for sentence in sentences]


def split_sentences(text):
    """Divide el texto en oraciones."""
    return sent_tokenize(text.strip())


def process_speeches(text_directory):
    """
    Procesa los archivos de texto guardados y crea una lista de discursos.
    Args:
        text_directory (str): El directorio donde se almacenan los archivos de texto.
    Returns:
        list: Una lista de diccionarios con la información de los discursos.
    """
    id_speech = 1
    speech_data = []

    for txt_file in os.listdir(text_directory):
        if txt_file.lower().endswith(".txt"):
            txt_path = os.path.join(text_directory, txt_file)
            raw_text = read_txt_file(txt_path)

            if raw_text:
                # Aquí se asume que el nombre del archivo PDF original tiene el formato adecuado para extraer los metadatos
                year, president, country = extract_metadata_from_filename(txt_file)

                speech_data.append(
                    {
                        "id_speech": id_speech,
                        "file_name": txt_file.replace(
                            ".txt", ".pdf"
                        ),  # El nombre del archivo PDF original
                        "file_name_txt": txt_file,  # El nombre del archivo TXT
                        "year": year,
                        "president": president,
                        "country": country,
                        "speech_type": "Independencia",
                        "text_raw": raw_text,  # El texto sin procesar extraído del archivo TXT
                    }
                )
                id_speech += 1

    return speech_data


def process_sentence(speech_data):
    """
    Procesa cada discurso en el conjunto de datos proporcionado, dividiéndolos en oraciones y realizando limpieza de texto.
    Args:
        speech_data (DataFrame): Un DataFrame que contiene los datos de los discursos, incluyendo el texto crudo de cada discurso.
    Returns:
        list: Una lista de diccionarios, donde cada diccionario contiene información sobre una oración individual, incluyendo su identificador, el texto crudo, el texto limpio, y las longitudes de las oraciones antes y después de la limpieza.
    """
    id_sentence = 1
    sentence_data = []

    for index, speech in speech_data.iterrows():
        cleaned_text = clean_text(
            speech["text_raw"]
        )  # Limpieza del texto completo del discurso
        sentences = sent_tokenize(cleaned_text)  # Dividir el texto limpio en oraciones
        for sentence_number, original_sentence in enumerate(sentences, start=1):
            cleaned_sentence = clean_sentence(
                original_sentence
            )  # Limpieza a nivel de oración
            sentence_data.append(
                {
                    "id_sentence": id_sentence,
                    "id_speech": speech["id_speech"],
                    "sentence_number": sentence_number,
                    "sentence_raw": original_sentence,
                    "sentence_clean": cleaned_sentence,
                    "sentence_length_raw": len(original_sentence.split()),
                    "sentence_length_clean": len(cleaned_sentence.split()),
                }
            )
            id_sentence += 1

    return sentence_data
