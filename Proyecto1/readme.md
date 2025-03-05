# Proyecto 1 MLOPS: Ambiente de Desarrollo con Docker y JupyterLab


---

## Resumen del proyecto:

Este proyecto consiste en la creación de un entorno de desarrollo para Machine Learning capaz de ingerir, validar y transformar datos, al tiempo que se demuestra el versionado de código y del ambiente (mediante Docker y Docker Compose). Se utiliza Docker para garantizar reproducibilidad y se implementa un pipeline con TensorFlow Extended (TFX). El dataset utilizado es una versión modificada del conjunto de datos **Tipo de Cubierta Forestal**, enfocado en predecir el tipo de cobertura forestal mediante variables cartográficas.

Se construye una canalización de datos que abarca:

* Ingesta del conjunto de datos.
* Validación y estadísticas (ExampleValidator, StatisticsGen).
* Creación y curación de un esquema (SchemaGen, ImportSchemaGen).
* Manejo de entornos (TRAINING, SERVING).
* Preprocesado y transformación (Transform).
* Gestión de metadatos (ML Metadata).
* Seguimiento de la procedencia de los datos.
* Versión de código y ambiente de desarrollo (usando Git y contenedores Docker)

---
## Estructura del repositorio

```bash
Proyecto_1/
├─ data/
│  ├─ dataset/
│     └─ data_transformed.csv      # CSV final 
│  
│
│  ├─pipeline/
│  ├─ CsvExampleGen/
│  ├─ ExampleValidator/
│  ├─ ImportSchemaGen/
│  ├─ SchemaGen/
│  ├─ StatisticsGen/
│  ├─ Transform/
│  ├─ metadata.sqlite              # DB de metadatos de ML
│  └─ ...
├─ ML/
│  ├── Dockerfile                  # Definición de la imagen base de Python + TFX 
│  ├── requirements.txt            # Librerías Python necesarias
│  └── notebooks/                  # Scripts .py y Notebooks .ipynb
│     ├─ preprocesamiento.ipynb       # Notebook principal de ingesta, validación, transform 
│     ├─ census_constants.py          # Ejemplo de constantes para la función de preprocesamiento
│     ├─ census_transform.py          # Ejemplo de preprocessing_fn
│
│     └─ covertype_train.csv          # CSV original
│
├─ docker-compose.yml                 #Orquestación de contenedores
└─ readme.md                          # Este archivo de documentación
```

---
En este repositorio encontrarás los siguientes archivos principales para ejecutar el ambiente de desarrollo:

* ML/

    *Dockerfile*: Parte esencial para construir la imagen del contenedor. Está basada en Python 3.9 y realiza los siguientes pasos:

    Actualiza la imagen base y descarga la utilidad de línea de comandos uv (por Astral.sh).

    Crea un directorio de trabajo ml_project.

    Copia los archivos del proyecto al contenedor y agrega las dependencias listadas en requirements.txt.

    Expone el puerto 8888, que usaremos para JupyterLab.
* *requirements.txt*: Contiene las librerías de Python necesarias para este proyecto (tales como Jupyter, scikit-learn, TFX, entre otras). Estas se instalan al construir la imagen de Docker.
* *notebooks/*: Carpeta en la cual se ubican los archivos Jupyter Notebook (.ipynb) y scripts Python que constituyen el pipeline (por ejemplo, archivos de configuración, scripts de procesamiento, etc.). Este directorio se mapea dentro del contenedor, de modo que los cambios locales se reflejen inmediatamente en el entorno de Docker.
* data/
    dataset/: Guarda los archivos CSV u otros formatos de datos (por ejemplo, covertype_train.csv). Estos datos se comparten con el contenedor para ser ingeridos y procesados por la canalización TFX.
* pipeline/
Contiene los artefactos generados por TensorFlow Extended (TFX), como salidas de CsvExampleGen, StatisticsGen, etc. También se incluye la base de datos de metadatos (metadata.sqlite) que registra la procedencia de los datos, esquemas y ejecuciones.
* docker-compose.yml: Orquesta el servicio “ml_service”.
    Construye la imagen a partir del Dockerfile en la carpeta ML/.
    Publica el puerto 8888 para acceder a JupyterLab desde el host.
    Define los volúmenes locales que se montan en el contenedor (./data y ML/notebooks), permitiendo la persistencia de la información y la edición de los notebooks en tiempo real.
    Ejecuta el comando de JupyterLab al iniciar el contenedor, de forma que se pueda acceder vía navegador en http://localhost:8888.

## Requisitos Previos
- Docker y Docker Compose instalados.
- Cuenta en GitHub (para clonar el repositorio).

## Pasos para levantar el entorno

1. Clonar el repositorio o descargarlo en tu máquina local

```bash
git clone https://github.com/felaponte/MLOps2.git

cd MLOps2/Proyecto1

```
2. Construir la imagen
Desde la raíz del proyecto, donde se encuentra el docker-compose.yml:

```bash

docker-compose build

```
Esto leerá el Dockerfile y descargará/instalará las dependencias definidas en requirements.txt.

3. Levantar el contenedor en segundo plano

```bash
docker-compose up -d
```
4. Verificar contenedor en ejecución

```bash
docker ps
```
Debería ver el contenedor en ejecución.

##  Acceso a JupyterLab

Una vez que el contenedor está arriba, abre tu navegador y navega a:

http://localhost:8888

(o la IP/puerto que hayas configurado).
Si pide un token, revisa el log que imprime Docker Compose o la consola del contenedor (docker logs NOMBRE_CONTENEDOR) para copiarlo.

## Uso de la carpeta notebooks/

* Dentro del contenedor, la carpeta notebooks/ se sincroniza con el host.

* Allí se ubica el notebook principal (preprocesamiento.ipynb) donde se ejecutan los componentes TFX:
    1. CsvExampleGen
    2. StatisticsGen
    3. SchemaGen + curación con TFDV
    4. ImportSchemaGen (opcional)
    5. Transform (donde defines preprocessing_fn)
    6. ExampleValidator
    7. Exploración de ML Metadata
    
Todas estas ejecuciones se reflejan en la carpeta pipeline/.
---
## Uso del Volumen y Persistencia

* El docker-compose.yml mapea:
    * ./data:/ml_project/data
    * ./ML/notebooks:/ml_project/notebooks
* Esto significa que cualquier cambio en local dentro de la carpeta data/ o ML/notebooks/ será visible en el contenedor, y viceversa.
---
## Limpieza

Para detener y eliminar contenedor(s) y red asociada, ejecuta:
```bash
docker-compose down
```

Si deseas eliminar también la imagen creada:

```bash
docker-compose down --rmi all
```

---
## Notas Adicionales

* El pipeline usa TensorFlow Extended (TFX) y sus componentes (CsvExampleGen, StatisticsGen, SchemaGen, ExampleValidator, Transform, etc.) para crear un flujo reproducible de datos y metadatos de ML.
* El archivo metadata.sqlite registra la procedencia de los artefactos. Puedes inspeccionarlo para entender qué data se ha procesado y en qué etapas.
* Si necesitas agregar más dependencias, edita ML/requirements.txt y reconstruye:

```bash
docker-compose build
docker-compose up -d
```
## ¡Listo!

Con este entorno, podrás ejecutar notebooks de TFX para:

1. Ingerir y validar datos.
2. Generar estadísticas y esquemas.
3. Preprocesar, transformar y crear features.
4. Rastrear metadatos (MLMD).
