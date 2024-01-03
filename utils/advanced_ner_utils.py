# utils/advanced_ner_utils.py
import pandas as pd
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
from utils.ner_utils import extract_context_ner, is_relevant_entity, normalize_entity


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
    context = (
        " ".join(words[context_start:start_index])
        + " [ENTIDAD] "
        + " ".join(words[end_index:context_end])
    )

    return context


def add_entity_to_list(
    current_entity_tokens,
    tokenizer,
    text,
    entities_with_context,
    current_label,
    model_type,
):
    # Reconstruir la entidad a partir de los subtokens
    if model_type == "roberta":
        original_entity = rebuild_entity_from_subtokens_roberta(current_entity_tokens, tokenizer)
    elif model_type == "bert":
        original_entity = rebuild_entity_from_subtokens_bert(current_entity_tokens, tokenizer)
    else:
        raise ValueError("model_type debe ser 'roberta' o 'bert'")

    normalized_entity = normalize_entity(original_entity)
    entity_start = text.find(original_entity)
    entity_end = entity_start + len(original_entity)

    # Verificar que la entidad no se haya agregado previamente
    if not any(d["raw_entity"] == original_entity and d['tag'] == current_label for d in entities_with_context):
        if entity_start != -1:
            context = extract_context_sentence(text, entity_start, entity_end)
            entities_with_context.append(
                {
                    "raw_entity": original_entity,
                    "normalized_entity": normalized_entity,
                    "tag": current_label,
                    "context": context,
                }
            )
        else:
            print(f"Entidad '{original_entity}' no encontrada en el texto.")



def rebuild_entity_from_subtokens_roberta(subtokens, tokenizer):
    # Reconstruir entidades a partir de subtokens
    entity = ""
    for token in subtokens:
        decoded_token = tokenizer.decode([token], skip_special_tokens=True)
        if decoded_token.startswith("Ġ"):
            entity += " " + decoded_token[1:]
        else:
            entity += decoded_token
    return entity.strip()


def rebuild_entity_from_subtokens_bert(subtokens, tokenizer):
    # Reconstruir entidades a partir de subtokens
    entity = ""
    for token in subtokens:
        decoded_token = tokenizer.decode([token], skip_special_tokens=True)
        if decoded_token.startswith("##"):
            entity += decoded_token[2:]
        else:
            entity += " " + decoded_token
    return entity.strip()

def check_and_add_entity(current_entity_tokens, tokenizer, text, entities_with_context, current_label, model_type):
    if current_entity_tokens:
        add_entity_to_list(
            current_entity_tokens, tokenizer, text, entities_with_context, current_label, model_type
        )


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
                    check_and_add_entity(current_entity_tokens, tokenizer, text, entities_with_context, current_label, model_type)
                    current_entity_tokens = [token]
                    current_label = label.split("-")[-1]
                elif label.startswith("I-") and current_label is not None:
                    current_entity_tokens.append(token)
            else:
                check_and_add_entity(current_entity_tokens, tokenizer, text, entities_with_context, current_label, model_type)
                current_entity_tokens = []
                current_label = None

        check_and_add_entity(current_entity_tokens, tokenizer, text, entities_with_context, current_label, model_type)

        return entities_with_context
    
    except ValueError as ve:
        print(f"Error de validación: {ve}")
        # Aquí podrías decidir si devolver una lista vacía, None o re-lanzar la excepción.
        return []
    except Exception as e:
        print(f"Se produjo un error al realizar NER con BERT: {e}")
        # Manejo de otros errores inesperados.
        return []

def process_sentences_and_extract_entities(
    sentence_data, tokenizer, model, perform_ner_function, model_name
):
    total_sentences = len(sentence_data)
    print_interval = max(total_sentences // 10, 1)

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
    id_entity = 1  # Inicia el ID de entidad

    for index, row in sentence_data.iterrows():
        if index % print_interval == 0:
            print(
                f"Procesando: {index}/{total_sentences} oraciones ({(index/total_sentences)*100:.2f}%)"
            )

        sentence = row["sentence_clean"]
        if isinstance(sentence, str) and sentence.strip():
            id_sentence = row["id_sentence"]
            entities = perform_ner_function(sentence, tokenizer, model)

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
        current_entity_tokens = []
        current_label = None

        for idx, pred in enumerate(outputs.logits[0]):
            label = model.config.id2label[pred.argmax().item()]
            token = tokens.input_ids[0][idx]

            if label != "O":
                if label.startswith("B-"):
                    check_and_add_entity(current_entity_tokens, tokenizer, text, entities_with_context, current_label, model_type)
                    current_entity_tokens = [token]
                    current_label = label.split("-")[-1]
                elif label.startswith("I-") and current_label is not None:
                    current_entity_tokens.append(token)
            else:
                check_and_add_entity(current_entity_tokens, tokenizer, text, entities_with_context, current_label, model_type)
                current_entity_tokens = []
                current_label = None

        check_and_add_entity(current_entity_tokens, tokenizer, text, entities_with_context, current_label, model_type)

        return entities_with_context
    
    except ValueError as ve:
        print(f"Error de validación: {ve}")
        # Aquí podrías decidir si devolver una lista vacía, None o re-lanzar la excepción.
        return []
    except Exception as e:
        print(f"Se produjo un error al realizar NER con BERT: {e}")
        # Manejo de otros errores inesperados.
        return []



def print_entities(entities):
    for entity, entity_type in entities:
        print(f"{entity}: {entity_type}")




def perform_ner_basic(sentence_data, model):
    entity_data = []
    id_ner_entity = 1

    for index, row in sentence_data.iterrows():
        if pd.notna(row["sentence_clean"]):  # Verifica que sentence_clean no sea NaN
            id_sentence = row["id_sentence"]
            sentence = str(row["sentence_clean"])  # Convierte a string

            doc = model(sentence)

            for ent in doc.ents:
                if is_relevant_entity(ent.text, ent.label_):
                    context = extract_context_ner(doc, ent)
                    # Obtener la entidad normalizada
                    normalized_entity = normalize_entity(ent.text)
                    entity_row = {
                        "id_ner_entity": id_ner_entity,
                        "id_sentence": id_sentence,
                        "context": context,
                        "tag": ent.label_,
                        "raw_entity": ent.text,
                        "entity": normalized_entity,  # Agregar la entidad normalizada
                        "entity_cluster": None,  # Se llenará más adelante con el clustering
                    }

                    entity_data.append(entity_row)
                    id_ner_entity += 1

    return entity_data