# utils/text_processing.py
import os
import re
from utils.file_utils import extract_metadata_from_filename, read_txt_file


# Realiza la limpieza de data a nivel de Texto Completo.
def clean_text(text):
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


# Realiza la limpieza de data a nivel de oración.
def clean_sentence(sentence):
    sentence = re.sub(r"\s+", " ", sentence).strip()  # Elimina espacios extra
    sentence = re.sub(
        r"\s*-\s*", "-", sentence
    )  # Eliminar espacios alrededor de los guiones
    return sentence


# Procesa los archivos de texto guardados y crea una lista de discursos.
def process_speeches(text_directory):
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


# Procesa cada discurso en el conjunto de datos proporcionado, dividiéndolos en oraciones y realizando limpieza de texto.
def process_sentence(speech_data, model):
    id_sentence = 1
    sentence_data = []

    for index, speech in speech_data.iterrows():
        cleaned_text = clean_text(
            speech["text_raw"]
        )  # Limpieza a nivel texto completo del discurso
        doc = model(cleaned_text)  # Procesar el texto con spaCy para obtener oraciones
        sentences = [sent.text.strip() for sent in doc.sents]

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
