USE DB_TablesPLN

DROP TABLE dbo.DimDiscursos

-- Crear tabla de valores �nicos
CREATE TABLE dbo.DimDiscursos (
  --Id int IDENTITY NOT NULL,
  id_speech int PRIMARY KEY,
  Nombre_pdf varchar(50) NOT NULL,
  year int,
  president_name varchar(20) NOT NULL,
  country varchar(20) NOT NULL,
  speech_type varchar(20) NOT NULL
);

INSERT INTO dbo.DimDiscursos (id_speech, Nombre_pdf, year, president_name, country, speech_type)

SELECT  distinct 
	   s.[id_speech]
      ,s.[file_name] AS Nombre_pdf
      ,s.[year]
      ,s.[president]
      ,s.[country]
      ,s.[speech_type]
FROM dbo.[speech] s;

USE DB_TablesPLN

DROP TABLE dbo.DimTokenizacion

-- Crear tabla de valores unicos
CREATE TABLE dbo.DimTokenizacion (
	F1 varchar(50),
	--id_speech int,
    NombreArchivo varchar(50),
    Pais varchar(50),
    Ano int,
    NombrePresidente varchar(50),
    ApellidoPresidente varchar(50),
    Palabras varchar(max),
    ConteoPalabras int,
    PalabraLematizada varchar(max),
    Sentimiento float
);

INSERT INTO dbo.DimTokenizacion 
SELECT   
	t.[F1],
	--s.id_speech,
	t.[Nombre archivo],
	t.[Pa�s],
	t.[A�o],
	t.[Nombre Presidente],
	t.[Apellido Presidente],
	t.[palabras],
	t.[conteo_palabras],
	t.[palabra_lematizada],
	t.[sentimiento]

FROM dbo.[Tokenizacion] t
INNER JOIN  dbo.[speech] s ON [Nombre Archivo] = s.[file_name];

USE DB_TablesPLN

IF NOT EXISTS (
    SELECT *
    FROM sys.tables
    WHERE name = 'dbo.DimEntity'
)--entity
BEGIN

DROP TABLE dbo.DimEntity;

    -- Crear tabla con todas las columnas del SELECT
    CREATE TABLE dbo.DimEntity (
        --id_speech int,
        file_name varchar(50),
        year int,
        president_name varchar(50),
        country varchar(50),
        speech_type varchar(50),
		[text_raw] varchar(max),
        id_sentence int,
        sentence_number int,
        sentence varchar(max),
        clean_sentence varchar(max),
        sentence_length int,
        sentence_length_clean int,
        id_entity int,
        model varchar(max),
		context varchar(max),
		raw_entity varchar(max),
		entity  varchar(max),
        tag varchar(50),
        entity_cluster int,
        descripcion_tag varchar(max),
        tag_spanish varchar(50),
		id_sentiment int,
		sentiment_score float,
		sentiment_category varchar(50)
    );
END;

-- Insertar datos en la tabla, ya sea nueva o existente
INSERT INTO dbo.DimEntity
SELECT 
    --S.[id_speech],
    S.[file_name],
    S.[year],
    S.[president],
    S.[country],
    S.[speech_type],
	S.[text_raw],
    SS.[id_sentence],
    SS.[sentence_number],
    SS.[sentence_raw],
    SS.[sentence_clean],
    SS.[sentence_length_raw],
	SS.[sentence_length_clean],
    SE.[id_entity],
    SE.[model],
    SE.[context],
    SE.[raw_entity],
    SE.[entity],
    SE.[tag],
    SE.[entity_cluster],
    TG.[description],
    TG.[tag_spanish],
	ST.[id_sentiment],
    ST.[sentiment_score],
	ST.[sentiment_category]
FROM [dbo].[Speech] S
LEFT JOIN [dbo].[sentence] SS ON S.[id_speech] = SS.[id_speech]
LEFT JOIN [dbo].[entity] SE ON SE.[id_sentence] = SS.[id_sentence]
LEFT JOIN [dbo].[ner_tag] TG ON SE.[tag] = TG.[tag]
LEFT JOIN [dbo].[Sentiment] ST ON ST.[id_sentence] = SS.[id_sentence];

USE DB_TablesPLN

IF NOT EXISTS (
    SELECT *
    FROM sys.tables
    WHERE name = 'dbo.DimValoracion'
)--entity
BEGIN

DROP TABLE dbo.DimValoracion;

-- Crear tabla nueva
CREATE TABLE dbo.DimValoracion (
	--Discursos varchar(50),
	--id_speech int,
    Fecha date,
    Presidente varchar(50),
    Orden int,
    Discurso varchar(max),
    Oracion varchar(max),
	TextoProcesado varchar(max),
    PalabrasEliminadas varchar(max),
    Clasificacion varchar(50),
    Valoracion float,
    Clasificacion2 varchar(50),
    Valoracion2 float,
    PalabrasFrecuentes varchar(max),
    PalabrasFrecuentes2 varchar(max)
);

-- Insertar datos en la tabla
INSERT INTO dbo.DimValoracion
SELECT 
	--concat(s.id_speech,TP.[Discurso]) AS Discursos,
	--s.id_speech,
	TP.[Fecha],
    TP.[Presidente],
    TP.[Orden],
    TP.[Discurso],
    TP.[Oracion],
    TP.[TextoProcesado],
    TP.[PalabrasEliminadas],
    TP.[Clasificacion],
    TP.[Valoracion],
    TP.[Clasificacion2],
    TP.[Valoracion2],
    TP.[PalabrasFrecuentes],
    TP.[PalabrasFrecuentes2]
FROM [dbo].[valoracion_discurso] TP
INNER JOIN  [dbo].[Speech] s ON TP.[Discurso] = s.[file_name];
end;
USE DB_TablesPLN

IF NOT EXISTS (
    SELECT *
    FROM sys.tables
    WHERE name = 'dbo.DimDistribucionPal'
)--entity
BEGIN

DROP TABLE dbo.DimDistribucionPal;

-- Crear tabla nueva
CREATE TABLE dbo.DimDistribucionPal (
	nombre_discurso varchar(50),
    topico varchar(50),
    palabras varchar(50),
    porcentajes float,
);
-- Insertar datos en la tabla
INSERT INTO dbo.DimDistribucionPal
SELECT 
	DP.[nombre_discurso]
   ,DP.[topico]
   ,DP.[palabras]
   ,DP.[porcentajes]
FROM [dbo].[distribucion_palabras_topicos_tidy] DP
END;

USE DB_TablesPLN

DROP TABLE dbo.FactDiscursos

-- Crear tabla de valores �nicos
CREATE TABLE dbo.FactDiscursos (
  Id int IDENTITY NOT NULL,
  NombreArchivo varchar(50),
  Discurso varchar(50), 
  nombre_discurso varchar(50), 
  file_name varchar(50),
  id_speech int,
  --Discursos varchar(50),
  --id_sentence int,
  --id_entity int,
  --tag varchar(50)
);

INSERT INTO dbo.FactDiscursos (NombreArchivo, Discurso, nombre_discurso, file_name, id_speech)--, id_sentence, id_entity, tag)
SELECT  distinct 
	    
	t.[Nombre Archivo], 
	rt.[Discurso],
	rt.[Discurso] AS nombre_discurso,
	s.[file_name],
	s.[id_speech]
	--concat(s.id_speech,s.[file_name]) AS Discursos
	--ss.[id_sentence],
	--se.[id_entity],
	--se.[tag]

FROM [dbo].[Tokenizacion] t
LEFT JOIN [dbo].[valoracion_discurso]  rt ON t.[Nombre Archivo] = rt.[Discurso]
INNER JOIN [dbo].[Speech] s ON t.[Nombre Archivo] = s.[file_name]
INNER JOIN [dbo].[sentence] ss ON s.[id_speech] = ss.[id_speech]
INNER JOIN [dbo].[entity] se ON se.[id_sentence] = ss.[id_sentence]
;
END;