# utils/text_processing.py
import os
import re
from utils.file_utils import extract_metadata_from_filename, read_txt_file


def clean_text(text):
    """
    Realiza la limpieza a nivel de texto completo.
    Esta limpieza se aplica después de extraer el texto del PDF y antes de convertirlo en un archivo de texto plano.
    Se enfoca en eliminar elementos no deseados como texto entre paréntesis y números, pero conservando caracteres especiales como acentos y ñ.
    """
    text = re.sub(r"[\•\−\–\—\―]", "-", text)  # Normaliza guiones
    text = re.sub(
        r"(\w)-\s*\n\s*(\w)", r"\1\2", text
    )  # Une palabras divididas por salto de línea
    text = re.sub(r"\n+", " ", text)  # Reemplaza múltiples saltos de línea con espacio
    text = re.sub(r"\s+", " ", text)  # Normaliza espacios
    # text = re.sub(r"\(.*?\)", "", text)                        # Elimina texto entre paréntesis
    text = re.sub(
        r"\s*\([A-ZÁÉÍÓÚÑÜ]+\)\s*\.?", " ", text
    )  # Eliminar anotaciones (APLAUSOS) y puntuación adyacente
    text = re.sub(
        r"[^\w\sáéíóúÁÉÍÓÚñÑüÜ.,;!?¡¿-]", "", text
    )  # Conserva letras (incluyendo acentos y "ñ"), números, espacios y caracteres comunes

    return text.strip()


def clean_sentence(sentence):
    """
    Realiza la limpieza a nivel de oración.
    Se enfoca en normalizar el texto sin eliminar información contextual crucial.
    """
    # Normalizar espacios (eliminar espacios extra)
    sentence = re.sub(r"\s+", " ", sentence).strip()

    # Eliminar espacios alrededor de los guiones (ajustado para coincidir con normalize_entity)
    sentence = re.sub(r"\s*-\s*", "-", sentence)

    # Otras normalizaciones (como convertir a minúsculas) pueden ir aquí si son necesarias
    # sentence = sentence.lower()

    return sentence



# def clean_sentences(sentences):
#    """Limpia cada oración en una lista de oraciones."""
#    return [clean_sentence(sentence) for sentence in sentences]


# def split_sentences(text):
#    """Divide el texto en oraciones."""
#    return sent_tokenize(text.strip())


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
                year, president, country = extract_metadata_from_filename(txt_file)

                speech_data.append(
                    {
                        "id_speech": id_speech,
                        "file_name": txt_file.replace(".txt", ".pdf"),
                        "file_name_txt": txt_file,
                        "year": year,
                        "president": president,
                        "country": country,
                        "speech_type": "Independencia",
                        "text_raw": raw_text,
                    }
                )
                id_speech += 1

    return speech_data


def process_sentence(speech_data, model):
    """
    Procesa cada discurso en el conjunto de datos proporcionado, dividiéndolos en oraciones y realizando limpieza de texto.
    Args:
        speech_data (DataFrame): Un DataFrame que contiene los datos de los discursos, incluyendo el texto crudo de cada discurso.
        model (spacy.Language): Modelo de spaCy para la segmentación de oraciones.
    Returns:
        list: Una lista de diccionarios, donde cada diccionario contiene información sobre una oración individual.
    """
    id_sentence = 1
    sentence_data = []

    for index, speech in speech_data.iterrows():
        cleaned_text = clean_text(
            speech["text_raw"]
        )  # Limpieza a nive texto completo del discurso
        doc = model(cleaned_text)  # Procesar el texto con spaCy para obtener oraciones
        sentences = [sent.text.strip() for sent in doc.sents]

        for sentence_number, original_sentence in enumerate(sentences, start=1):
            if clean_sentence:
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
