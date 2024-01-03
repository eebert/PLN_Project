# utils/ner_utils.py
import logging
import re
import spacy
from initialize import check_and_download_spacy_model
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from transformers import BertTokenizer, BertForTokenClassification
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline


def is_relevant_entity(entity, label):
    # Ejemplo de criterios ajustados
    if len(entity) <= 2:
        return False  # Excluir entidades muy cortas

    # Tipos específicos que son relevantes en el contexto político
    relevant_types = ["DATE", "MONEY", "LAW", "PERCENT", "PERSON", "ORG", "GPE"]

    if label in relevant_types:
        return True

    # Excluir entidades que contienen números pero no son de tipos específicos relevantes
    if any(char.isdigit() for char in entity) and label not in relevant_types:
        return False

    return True


def extract_context_ner(doc, ent):
    start = max(ent.start - 5, 0)
    end = min(ent.end + 5, len(doc))
    return doc[start : ent.start].text + " [ENTIDAD] " + doc[ent.end : end].text







def normalize_entity(entity):
    # Convertir a minúsculas para estandarizar
    entity = entity.lower()

    # Eliminar artículos y preposiciones comunes al principio
    entity = re.sub(r"^(la |el |los |las |de )", "", entity)

    # Eliminar espacios adicionales
    entity = re.sub(r"\s+", " ", entity).strip()

    # Normalizar acentos y caracteres especiales (opcional)
    # entity = unicodedata.normalize('NFD', entity).encode('ascii', 'ignore').decode('utf-8')

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

