# utils/ner_utils.py
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import unicodedata
import pandas as pd

def clean_entity(entity):
    if not entity.strip():
        return None

    if len(entity) == 1:
        return None

    # Omite entidades con solo caracteres no alfanuméricos
    if re.match(r"^\W+$", entity):  #
        return None

    # Eliminar espacios antes de los signos de puntuación
    entity = re.sub(r"\s([,;.!?])", r"\1", entity)

    return entity.strip()


def normalize_entity(entity):
    #entity = entity.lower()
    entity = re.sub(r"\s+", " ", entity).strip()  # Elimina Espacios Adicionales
    entity = re.sub(r"\s*[-—]\s*", "-", entity)  # Normaliza guiones y em-dashes.
    # Elimina Preposiciones al inicio
    #entity = re.sub( r"^(la |el |los |las |de )", "", entity ) 
    # Normaliza acentos y caracteres especiales a su forma más simple
    #entity = unicodedata.normalize('NFD', entity)
    # Codifica en ASCII y decodifica de nuevo a UTF-8, eliminando caracteres que no son ASCII
    #entity = entity.encode('ascii', 'ignore').decode('utf-8')

    return entity


def cluster_entities(entity_data, num_clusters=10):
    # Convertir las entidades a vectores TF-IDF
    vectorizer = TfidfVectorizer()
    entity_texts = [entity["entity"] for entity in entity_data]
    X = vectorizer.fit_transform(entity_texts)

    # Verificar si hay suficientes muestras para el número de clusters deseado
    if X.shape[0] < num_clusters:
        print(
            f"No se puede realizar clustering con {num_clusters} clusters porque solo hay {X.shape[0]} muestras."
        )
        # Opción 1: Devolver los datos sin modificar
        return entity_data
        # Opción 2: Ajustar el número de clusters al número de muestras
        # num_clusters = X.shape[0]

    # Aplicar K-means para agrupar entidades similares
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(X)

    # Asignar el cluster a cada entidad en el conjunto de datos
    for i, entity in enumerate(entity_data):
        entity["entity_cluster"] = kmeans.labels_[i]
    return entity_data



def process_sentences_and_extract_entities(
    sentence_data, tokenizer, model, perform_ner_function, model_name
):
    # Se Calcula el numero total de oraciones y define los intervalos de impresión
    total_sentences = len(sentence_data)
    print_interval = max(total_sentences // 10, 1)

    # Creación del DataFrame donde se almacerpa las entidades extraidas
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
    id_entity = 1 

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
