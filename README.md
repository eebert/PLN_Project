# Proyecto de PLN

Este proyecto es para procesar y analizar datos de lenguaje natural.

## Inicio Rápido

(Instrucciones sobre cómo configurar y ejecutar tu proyecto)

## Estructura de Implementación

PLN_Project/
│
├── data/
│	├── pdf/                  						# Contiene los archivos PDF originales de los discursos descargados del Bucket.
│   		├── speech_01.pdf 					# Ejemplo de archivo de discurso en formato PDF.
│   		├── ...
│
│	├── txt/                  						# Almacena los archivos de texto procesados a partir de los PDFs.
│   		├── speech_01.txt  					# Ejemplo de archivo de texto de un discurso procesado.
│   	├── ...
│
│	├── xlsx/                 						# Contiene archivos Excel con datos estructurados y resultados de análisis.
│   	├── speech.xlsx       						# Datos de discursos procesados y almacenados en formato Excel.
│    	├── sentence.xlsx     						# Datos de oraciones extraídas de los discursos para análisis.
│    	├── ner_entity.xlsx   						# Entidades identificadas a través del análisis NER básico.
│    	├── bert_entity.xlsx  						# Entidades identificadas con el modelo BERT.
│    	├── roberta_entity.xlsx 						# Entidades identificadas con el modelo RoBERTa.
│    	└── sentiment.xlsx    						# Resultados del análisis de sentimientos.
│
│├── notebooks-NER/
│   ├── 01_Download_Process_Speeches.ipynb 		# Descarga y procesamiento de discursos
│   ├── 02_Text_Processing.ipynb           			# Limpieza y tokenización del texto
│   ├── 03_PRE_Analysis.ipynb                        		# PRE - Análisis Exploratorio de Datos
│   ├── 04_NER_Basic.ipynb                  				# Reconocimiento de Entidades Nombradas (NER) básico
│   ├── 05_BERT_Analysis.ipynb              			# Análisis NER con modelo BERT
│   ├── 06_RoBERTa_Analysis.ipynb           			# Análisis NER con modelo RoBERTa
│   ├── 07_Sentiment_Analysis.ipynb         			# Análisis de Sentimientos
│   ├── 08_Script_BD_Process.ipynb             			# Integración de datos y almacenamiento en base de datos
│   ├── 09_Visualization.ipynb             				# Permite la visualizacion de los datos como etapa inicial
│   └── 10_Main_Execution. ipynb                   		# Ejecuión de todos los notebooks.
│
│├── notebook-EDA/
│   ├── 01_Load_Structured_Database_Tokenization.ipynb    # Carga y tokenización DB
│   ├── 02_Coneixonsql_EDA_Distribution.ipynb          # Análisis distribución datos SQL
│   ├── 03_Coneixonsql_EDA_Entity.ipynb                    # Exploración entidades DB
│   ├── 04_Coneixonsql_EDA_Tokenization.ipynb         # Análisis tokenización DB
│   └── 05_Coneixonsql_EDA_Valuation.ipynb             	# Valoración datos DB
│
├── utils/
│   ├── __init__.py
│   ├── file_utils.py             						# Funciones para manejar archivos
│   ├── text_processing_utils.py  					# Funciones de preprocesamiento de texto
│   ├── ner_utils.py              						# Funciones para NER básico y avanzado
│   ├── sentiment_utils.py        					# Funciones para análisis de sentimientos
│   └── visualization_utils.py    					# Funciones para generar visualizaciones
│
├── config.py                    						# Configuración global del proyecto
└── README.md                 						# Documentación general del proyecto

## Descripción de los Notebooks

Notebook-NER

01_Download_Process_Speeches.ipynb: Inicia el flujo de trabajo descargando y procesando los archivos PDF para extraer los textos.
02_Text_Processing.ipynb: Continúa con el procesamiento del texto, preparándolo para el análisis.
03_PRE_Analysis.ipynb: Explora los datos para obtener una comprensión inicial y detectar patrones o anomalías.
04_NER_Basic.ipynb: Realiza un análisis básico de NER utilizando herramientas como spaCy.
05_BERT_Analysis.ipynb: Avanza hacia un análisis NER más sofisticado con el modelo BERT.
06_RoBERTa_Analysis.ipynb: Explora el uso de RoBERTa, un modelo similar a BERT pero con diferencias clave.
07_Sentiment_Analysis.ipynb: Evalúa el tono emocional de los discursos a través del análisis de sentimientos.
08_Main_Analysis.ipynb: Combina todos los análisis individuales para formar un entendimiento comprensivo y cohesivo.
09_Visualization.ipynb: Permite la visualizacion de los datos como etapa inicial
10_Script_BD_Process.ipynb: Integra datos de archivo excel a un almacenamiento fisico en BD


Notebook-EDA
01_Load_Structured_Database_Tokenization.ipynb: Carga y tokenización inicial de la base de datos para preparación de análisis.
02_Coneixonsql_EDA_Distribution.ipynb: Identifica patrones y anomalías en la distribución de datos de la base SQL.
03_Coneixonsql_EDA_Entity.ipynb: Explora y evalúa entidades en la base de datos por importancia y frecuencia.
04_Coneixonsql_EDA_Tokenization.ipynb: Análisis detallado de la estructura y frecuencia de tokens en la base de datos.
05_Coneixonsql_EDA_Valuation.ipynb: Valora la calidad de datos y sugiere mejoras para análisis precisos.
06_Main_Analysis.ipynb: Sintetiza análisis previos en un informe integrado y comprensivo.

## Consideraciones Adicionales

- **Modularidad:** Cada componente del proyecto es independiente, lo que facilita la prueba y el mantenimiento del código.
- **Flexibilidad:** La estructura es flexible y puede ajustarse o expandirse para satisfacer las necesidades del proyecto.
- **Documentación:** Se proporciona documentación clara para cada notebook, describiendo su propósito y requisitos.

La estructura y la documentación detallada ayudan a gestionar y desarrollar el proyecto de manera eficiente, promoviendo la claridad y la reproducibilidad del análisis.
