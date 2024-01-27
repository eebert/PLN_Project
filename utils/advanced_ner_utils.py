# utils/advanced_ner_utils.py
import pandas as pd
import re
import torch
from utils.ner_utils import normalize_entity, clean_entity


def token_span_to_char_span(doc, start_token_idx, end_token_idx):
    start_char_idx = doc[start_token_idx].idx
    end_char_idx = doc[end_token_idx - 1].idx + len(doc[end_token_idx - 1])
    return start_char_idx, end_char_idx


def perform_ner_basic(sentence_data, model):
    try:
        entity_data = []
        id_ner_entity = 1

        for index, row in sentence_data.iterrows():
            if pd.notna(row["sentence_clean"]):
                id_sentence = row["id_sentence"]
                sentence = str(row["sentence_clean"])

                doc = model(sentence)

                for ent in doc.ents:
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


def find_entity_in_text(text, entity):
    entity_start = text.find(entity)
    entity_end = entity_start + len(entity)
    context = extract_context_sentence(text, entity_start, entity_end)

    if entity_start == -1:
        print(f"\nomitiendo Entidad '{entity}' no encontrada en el texto.")
        print("Contexto:", context)
        print("Oración:", text)
        return None, None
    else:
        return context, entity_start


# Funcion utilizada para NER Basic, BERT y RooBERTa
def extract_context_sentence(text, entity_start, entity_end, window=5):
    # Utilizar expresiones regulares para dividir el texto en palabras y puntuación
    words = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

    start_index = len(re.findall(r"\w+|[^\w\s]", text[:entity_start], re.UNICODE))
    end_index = len(re.findall(r"\w+|[^\w\s]", text[:entity_end], re.UNICODE))

    context_start = max(start_index - window, 0)
    context_end = min(end_index + window, len(words))

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

    normalized_entity = normalize_entity(original_entity)
    cleaned_entity = clean_entity(normalized_entity)
    if cleaned_entity is None:
        return

    context, entity_start = find_entity_in_text(text, original_entity)
    if entity_start is None:
        return

    entities_with_context.append(
        {
            "raw_entity": original_entity,
            "normalized_entity": cleaned_entity,
            "tag": current_label,
            "context": context,
        }
    )


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


def rebuild_entity_from_subtokens_roberta(subtokens, tokenizer):
    entity = ""
    for i, token in enumerate(subtokens):
        decoded_token = tokenizer.decode([token], skip_special_tokens=True)

        if decoded_token.startswith("Ġ"):
            # El prefijo 'Ġ' en RoBERTa indica un nuevo token
            if i != 0:  # No agregues espacio al principio de la entidad
                entity += " "
            decoded_token = decoded_token[1:]  # Elimina el prefijo 'Ġ'
        # No hay necesidad de eliminar el espacio antes de los guiones porque RoBERTa no debería generarlos
        entity += decoded_token

    # Normaliza los guiones después de la reconstrucción
    entity = re.sub(r"\s?-\s?", "-", entity).strip()

    return entity


def rebuild_entity_from_subtokens_bert(subtokens, tokenizer):
    entity = ""
    unk_present = False

    for i, token in enumerate(subtokens):
        decoded_token = tokenizer.decode([token], skip_special_tokens=True)

        if decoded_token == tokenizer.unk_token:
            unk_present = True
            continue

        if decoded_token.startswith("##"):
            # Elimina el prefijo '##' y el espacio anterior si el subtoken es parte de la misma palabra.
            decoded_token = decoded_token[2:]
            if entity and entity[-1] == " ":
                entity = entity[:-1]
        else:
            # Añade un espacio solo si el token anterior no es un guión y el actual no comienza con un guión.
            if entity and not entity[-1] in "-—":
                entity += " "

        entity += decoded_token

    # Normaliza los guiones después de la reconstrucción
    entity = re.sub(r"\s?-\s?", "-", entity).strip()

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