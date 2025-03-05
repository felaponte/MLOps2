# Proyecto 1 MLOPS: Ambiente de Desarrollo con Docker y JupyterLab


---

## Resumen del proyecto:

Este proyecto consiste en la creación de un entorno de desarrollo para Machine Learning capaz de ingerir, validar y transformar datos, al tiempo que se demuestra el versionado de código y del ambiente (mediante Docker y Docker Compose). Se utiliza Docker para garantizar reproducibilidad y se implementa un pipeline con TFX. El dataset utilizado es una versión modificada del conjunto de datos **Tipo de Cubierta Forestal**, enfocado en predecir el tipo de cobertura forestal mediante variables cartográficas.

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
│  │  └─ data_transformed.csv      # CSV final 
│  └─ readme.md
│
│  ├─pipeline/
│  ├─ CsvExampleGen/
│  ├─ ExampleValidator/
│  ├─ ImportSchemaGen/
│  ├─ SchemaGen/
│  ├─ StatisticsGen/
│  ├─ Transform/
│  ├─ metadata.sqlite              # Base de datos 
│  └─ ...
├─ ML/
│  ├─ notebooks/
│  ├─ preprocesamiento.ipynb       # Notebook principal de ingesta, validación, transform 
│  ├─ census_constants.py          # Ejemplo de constantes para la función de preprocesamiento
│  ├─ census_transform.py          # Ejemplo de preprocessing_fn
│
│  └─ covertype_train.csv          # CSV original
│
├─ docker-compose.yml
├─ Dockerfile
├─ requirements.txt
└─ readme.md                       
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
git clone -b proyecto1_version_santiago https://github.com/felaponte/MLOps2.git

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

