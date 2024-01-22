# utils/advanced_ner_utils.py
import pandas as pd
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from utils.ner_utils import (
    extract_context_ner,
    is_relevant_entity,
    normalize_entity,
)


def extract_context_sentence(text, entity_start, entity_end, window=5):
    # Utilizar expresiones regulares para dividir el texto en palabras y puntuación
    words = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

    # Encontrar los índices de inicio y fin de la entidad en términos de palabras
    start_index = len(re.findall(r"\w+|[^\w\s]", text[:entity_start], re.UNICODE))
    end_index = len(re.findall(r"\w+|[^\w\s]", text[:entity_end], re.UNICODE))

    # Calcular los índices de inicio y fin del contexto
    context_start = max(start_index - window, 0)
    context_end = min(end_index + window, len(words))

    # Reconstruir el contexto
    context_pieces = (
        words[context_start:start_index] + ["[ENTIDAD]"] + words[end_index:context_end]
    )
    context = " ".join(context_pieces)
    # Eliminar espacios antes de signos de puntuación
    context = re.sub(r"\s([?.!,;:])", r"\1", context)

    return context


def add_entity_to_list(
    current_entity_tokens,
    tokenizer,
    text,
    entities_with_context,
    current_label,
    model_type,
):
    if not current_entity_tokens:
        return

    # Reconstruir la entidad a partir de subtokens
    if model_type == "roberta":
        original_entity = rebuild_entity_from_subtokens_roberta(
            current_entity_tokens, tokenizer
        )
    elif model_type == "bert":
        original_entity = rebuild_entity_from_subtokens_bert(
            current_entity_tokens, tokenizer
        )
    else:
        raise ValueError("El tipo de modelo debe ser 'roberta' o 'bert'")

    # Normalizar la entidad
    normalized_entity = normalize_entity(original_entity)

    # Limpiar la entidad normalizada
    cleaned_entity = clean_entity(normalized_entity)
    if cleaned_entity is None:
        return

    # Intentar encontrar la entidad original en el texto para obtener su ubicación exacta
    entity_start = text.find(original_entity)
    entity_end = entity_start + len(original_entity)

    # Si no se encuentra la entidad, imprimir el error y el contexto usando la entidad original
    if entity_start == -1:
        print(f"\nEntidad '{original_entity}' no encontrada en el texto.")
        context = extract_context_sentence(
            text,
            text.find(original_entity),
            text.find(original_entity) + len(original_entity),
        )
        print("Contexto:", context)
        print("Oración:", text)
        print(
            f"Omitiendo la adición de la entidad '{original_entity}' ya que no se encontró en el texto."
        )
        return

    # Extraer el contexto para la entidad encontrada
    context = extract_context_sentence(text, entity_start, entity_end)

    # Verificar si la entidad ya ha sido agregada
    if any(
        d["raw_entity"] == original_entity and d["tag"] == current_label
        for d in entities_with_context
    ):
        return  # Evitar agregar duplicados

    # Agregar la entidad con su contexto
    entities_with_context.append(
        {
            "raw_entity": original_entity,
            "normalized_entity": cleaned_entity,
            "tag": current_label,
            "context": context,
        }
    )


def rebuild_entity_from_subtokens_roberta(subtokens, tokenizer):
    entity = ""
    for i, token in enumerate(subtokens):
        decoded_token = tokenizer.decode([token], skip_special_tokens=True)
        if i == 0:
            entity = decoded_token
        elif decoded_token.startswith("Ġ"):
            entity += " " + decoded_token[1:]
        else:
            entity += decoded_token

    entity = entity.replace(" - ", "-").replace(" — ", "—").strip()
    return entity

    return entity.strip()


def rebuild_entity_from_subtokens_bert(subtokens, tokenizer):
    entity = ""
    unk_present = False

    for i, token in enumerate(subtokens):
        decoded_token = tokenizer.decode([token], skip_special_tokens=True)

        if decoded_token == tokenizer.unk_token:
            unk_present = True
            continue

        if decoded_token.startswith("##"):
            decoded_token = decoded_token[2:]
            if entity and entity[-1] == " ":
                entity = entity[
                    :-1
                ]  # Elimina el espacio si el siguiente subtoken es parte de la misma palabra
        else:
            if (
                entity
                and not decoded_token.startswith(("-", "—"))
                and not entity[-1].endswith(("-", "—"))
            ):
                entity += " "  # Añade espacio solo si no estamos tratando con un guión

        entity += decoded_token

    # Normalizar los guiones para que coincidan con el uso en el texto
    entity = entity.replace(" - ", "-").replace(" — ", "—").strip()

    return entity


def perform_ner_with_roberta(text, tokenizer, model, model_type="roberta"):
    try:
        if not isinstance(text, str) or not text.strip():
            return []

        tokens = tokenizer.encode_plus(
            text, return_tensors="pt", truncation=True, max_length=512
        )

        with torch.no_grad():
            outputs = model(**tokens)

        entities_with_context = []
        current_entity_tokens = []
        current_label = None

        for idx, pred in enumerate(outputs.logits[0]):
            label = model.config.id2label[pred.argmax().item()]
            token = tokens.input_ids[0][idx]

            if label != "O":
                if label.startswith("B-") or label.startswith("S-"):
                    if current_entity_tokens:
                        add_entity_to_list(
                            current_entity_tokens,
                            tokenizer,
                            text,
                            entities_with_context,
                            current_label,
                            model_type,
                        )
                    current_entity_tokens = [token]
                    current_label = label.split("-")[-1]
                elif label.startswith("I-") or label.startswith("E-"):
                    current_entity_tokens.append(token)
            else:
                if current_entity_tokens:
                    add_entity_to_list(
                        current_entity_tokens,
                        tokenizer,
                        text,
                        entities_with_context,
                        current_label,
                        model_type,
                    )
                    current_entity_tokens = []
                    current_label = None

        if current_entity_tokens:
            add_entity_to_list(
                current_entity_tokens,
                tokenizer,
                text,
                entities_with_context,
                current_label,
                model_type,
            )

        return entities_with_context

    except ValueError as ve:
        print(f"Error de validación: {ve}")
        return []
    except Exception as e:
        print(f"Se produjo un error al realizar NER con RoBERTa: {e}")
        return []


def process_sentences_and_extract_entities(
    sentence_data, tokenizer, model, perform_ner_function, model_name
):
    # Calcula el numero total de oraciones y define los intervalos de impresión
    total_sentences = len(sentence_data)
    print_interval = max(total_sentences // 10, 1)

    # Se crea el DataFrame donde se almacerpa las entidades extraidas
    entities_df = pd.DataFrame(
        columns=[
            f"id_{model_name}_entity",
            "id_sentence",
            "context",
            "tag",
            "raw_entity",
            "entity",
            "entity_cluster",
        ]
    )
    id_entity = 1  # Se inicializa la varianle de entidad del flujo

    # Realiza la iteracion entre todas las oraciones
    for index, row in sentence_data.iterrows():
        # Se verifica el intervalo de impresion para mostrar el progreso
        if index % print_interval == 0:
            print(
                f"Procesando: {index}/{total_sentences} oraciones ({(index/total_sentences)*100:.2f}%)"
            )

        sentence = row["sentence_clean"]  # Se obtiene la oracion actual
        if isinstance(sentence, str) and sentence.strip():
            id_sentence = row["id_sentence"]  # Se obtiene el id de la oracion

            # Funcien generiaca para la recepcion de entidades
            entities = perform_ner_function(sentence, tokenizer, model)

            # Itera a travez de las entidades extraidas
            for entity_info in entities:
                entities_df.loc[len(entities_df.index)] = {
                    f"id_{model_name}_entity": id_entity,
                    "id_sentence": id_sentence,
                    "context": entity_info["context"],
                    "tag": entity_info["tag"],
                    "raw_entity": entity_info["raw_entity"],
                    "entity": entity_info["normalized_entity"],
                    "entity_cluster": None,
                }
                id_entity += 1

    print("Procesamiento completado.")
    return entities_df


def perform_ner_with_bert(text, tokenizer, model, model_type="bert"):
    try:
        if not isinstance(text, str) or not text.strip():
            return []

        tokens = tokenizer.encode_plus(
            text, return_tensors="pt", truncation=True, max_length=512
        )

        with torch.no_grad():
            outputs = model(**tokens)

        entities_with_context = []
        current_entity_tokens = (
            []
        )  # Lista temporal para acumular tokens de la entidad actual
        current_label = None

        for idx, pred in enumerate(outputs.logits[0]):
            label = model.config.id2label[pred.argmax().item()]
            token = tokens.input_ids[0][idx]

            if label != "O":  # Verifica si es una entidad
                if label.startswith("B-"):  # Comienzo de Entidad
                    current_entity_tokens = [token]
                    current_label = label.split("-")[
                        -1
                    ]  # Extracción del tipo de entidad
                elif label.startswith("I-") and current_label is not None:
                    # Continúa acumulando tokens de la entidad actual
                    current_entity_tokens.append(token)
            else:
                if current_entity_tokens:
                    # Si hay tokens en la entidad actual, la procesamos y la agregamos
                    add_entity_to_list(
                        current_entity_tokens,
                        tokenizer,
                        text,
                        entities_with_context,
                        current_label,
                        model_type,
                    )
                    current_entity_tokens = []  # Reiniciamos la lista de tokens
                    current_label = None

        if current_entity_tokens:
            # Procesamos la entidad final si aún quedan tokens
            add_entity_to_list(
                current_entity_tokens,
                tokenizer,
                text,
                entities_with_context,
                current_label,
                model_type,
            )

        return entities_with_context

    except ValueError as ve:
        print(f"Error de validación: {ve}")
        return []
    except Exception as e:
        print(f"Se produjo un error al realizar NER con BERT RoBERTa: {e}")
        return []


def print_entities(entities):
    for entity, entity_type in entities:
        print(f"{entity}: {entity_type}")


def token_span_to_char_span(doc, start_token_idx, end_token_idx):
    start_char_idx = doc[start_token_idx].idx
    end_char_idx = doc[end_token_idx - 1].idx + len(doc[end_token_idx - 1])
    return start_char_idx, end_char_idx


def perform_ner_basic(sentence_data, model):
    try:
        entity_data = []
        id_ner_entity = 1

        for index, row in sentence_data.iterrows():
            if pd.notna(
                row["sentence_clean"]
            ):  # Verifica que sentence_clean no sea NaN
                id_sentence = row["id_sentence"]
                sentence = str(row["sentence_clean"])

                doc = model(sentence)

                for ent in doc.ents:
                    if is_relevant_entity(ent.text, ent.label_):
                        start_char_idx, end_char_idx = token_span_to_char_span(
                            doc, ent.start, ent.end
                        )
                        context = extract_context_sentence(
                            doc.text, start_char_idx, end_char_idx
                        )
                        normalized_entity = normalize_entity(ent.text)
                        entity_row = {
                            "id_ner_entity": id_ner_entity,
                            "id_sentence": id_sentence,
                            "context": context,
                            "tag": ent.label_,
                            "raw_entity": ent.text,
                            "entity": normalized_entity,
                            "entity_cluster": None,
                        }

                        entity_data.append(entity_row)
                        id_ner_entity += 1

        return entity_data
    except ValueError as ve:
        print(f"Error de validación: {ve}")
        return []
    except Exception as e:
        print(f"Se produjo un error al realizar NER Basic: {e}")
        return []


def clean_entity(entity):
    # Eliminar entidades que son espacios en blanco
    if not entity.strip():
        return None

    # Omitir caracteres únicos (opcional, basado en tu dominio)
    if len(entity) == 1:
        return None

    # Omitir entidades con solo caracteres no alfanuméricos (opcional, basado en tu dominio)
    if re.match(r"^\W+$", entity):
        return None

    # Eliminar espacios antes de los signos de puntuación
    entity = re.sub(r"\s([,;.!?])", r"\1", entity)

    # Devolver la entidad limpia
    return entity.strip()
