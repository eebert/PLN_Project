# Proyecto de PLN

Este proyecto es para procesar y analizar datos de lenguaje natural.

## Inicio Rápido

(Instrucciones sobre cómo configurar y ejecutar tu proyecto)

## Estructura del Proyecto

proyecto_pln/
│
├── data/
│   ├── pdf/                  # Almacenar aquí los archivos PDF
│   ├── csv/                  # Almacenar aquí los archivos CSV
│   └── xlsx/                 # Almacenar aquí los archivos XLSX
│
├── notebooks/
│   ├── 01_Download_Process_Speeches.ipynb # Descarga y Lectura de PDFs
│   ├── 02_Text_Processing.ipynb        # Procesamiento de Texto
│   ├── 03_EDA.ipynb                    # Análisis Exploratorio de Datos
│   ├── 04_NER_Basic.ipynb              # Análisis de Entidades Nombradas Básico
│   ├── 05_BERT_Analysis.ipynb          # Análisis Avanzado con BERT
│   ├── 06_RoBERTa_Analysis.ipynb       # Análisis Avanzado con RoBERTa
│   ├── 07_Sentiment_Analysis.ipynb     # Análisis de Sentimientos
│   ├── 08_Visualizations.ipynb         # Visualizaciones
│   └── 09_Main_Analysis.ipynb          # Análisis Principal y Flujo de Trabajo
├── utils/
│   ├── __init__.py
│   ├── pdf_utils.py
│   ├── data_utils.py
│   ├── analysis_utils.py
│   └── visualization_utils.py
│
├── config.py                 # Configuraciones del proyecto
└── requirements.txt          # Dependencias del proyecto


## Descripción de los Notebooks
01_Download_and_Read_PDFs.ipynb: Descarga y lectura inicial de archivos PDF.
02_EDA.ipynb: Análisis exploratorio para entender mejor los datos.
03_Text_Processing.ipynb: Limpieza y preparación del texto para el análisis.
04_NER_Basic.ipynb: Implementación de un análisis básico de entidades nombradas usando herramientas estándar como spaCy o NLTK.
05_BERT_Analysis.ipynb: Uso del modelo BERT para tareas avanzadas de PLN, incluyendo una versión más sofisticada de NER.
06_RoBERTa_Analysis.ipynb: Aplicación del modelo RoBERTa para tareas de PLN, similar a BERT pero explorando las diferencias y ventajas de RoBERTa.
07_Sentiment_Analysis.ipynb: Análisis de sentimientos, que puede ser independiente o complementar los análisis de NER.
08_Visualizations.ipynb: Creación de visualizaciones para interpretar los resultados de tus análisis.
09_Main_Analysis.ipynb: Integración y análisis final, donde combinas los insights y resultados de los notebooks anteriores.

## Consideraciones Finales
Modularidad: La estructura permite trabajar en cada aspecto del proyecto de forma independiente, lo cual facilita la prueba y mantenimiento de cada parte.
Flexibilidad: Se puedes ajustar o expandir la estructura propuesta según las necesidades específicas del proyecto.
Documentación: Se documenta cada notebook claramente, explicando su propósito, el cómo se utiliza y cualquier dependencia o requisito previo necesario.

En general la estructura propuesta proporciona un marco claro y lógico del proyecto de PLN, facilitando la gestión y el desarrollo del proyecto.