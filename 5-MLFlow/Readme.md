### Taller MLflow

MLflow es una plataforma de código abierto para administrar el ciclo de vida completo del aprendizaje automático. En este proyecto se implementan los siguientes pasos:

1. Instancia de base de datos (MySQL) para almacenar los datos crudos y procesados.
2. Instancia de MLflow (usando MySQL como backend de metadatos, en lugar de SQLite).
3. Instancia de MinIO como almacenamiento de artefactos (reemplazando el servicio de S3).
4. Instancia de JupyterLab para la experimentación, con un notebook donde se entrena un modelo y se registran múltiples ejecuciones (≥20) en MLflow.
5. Registro de modelos en el Model Registry de MLflow, y cambio de etapa a “Production”.
6. API de inferencia (con FastAPI), que carga el modelo directamente desde el Model Registry en producción.

## 0. Acceso y ubicación del proyecto en la máquina virtual

# 1. Entrar a la máquina virtual:
```
ssh estudiante@10.43.101.162
```
# 2. Ir a la carpeta del proyecto:
```
cd /home/estudiante/Documents/MLOps2/5_MLFlow
```
## Estructura del proyecto
```
MLOps2

5-MLflow/
│   │── API/
│   │   │── api.py
│   │   │── docker-compose.yaml
│   │   │── Dockerfile
│   │   │── requirements.txt
│   │
│   │── jupyter-db/
│   │   │── .ipynb_checkpoints/
|   |   |── mlruns/0/
│   │   │── docker-compose.yaml
│   │   │── Dockerfile
│   │   │── requirements.txt 
│   │   |── mlflow_notebook.ipynb
│   │   |── penguins_lter.csv
│   │
│   │── minio/
│   │   │── minio/
│   │   │   │── .minio.sys/
│   │   │   │── mlflows3/artifacts/
│   │   │── docker-compose.yaml
│   │
│   │── mlflow/
│   │   │── docker-compose.yaml
│   │   │── mlflow_serv.service
│   │── Readme.md
```
A continuación se detalla para qué sirve cada carpeta/archivo principal:

* API: Contiene el servicio de FastAPI (api.py) para la inferencia del modelo con MLflow.
* jupyter-db: Contiene la definición de un contenedor de MySQL (almacena datos crudos y procesados) y un Dockerfile para levantar JupyterLab y correr el mlflow_notebook.ipynb.
* minio: Define el contenedor de MinIO y su bucket donde se almacenan los artefactos de MLflow.
* mlflow: Define el contenedor o servicio de MLflow Tracking y el archivo mlflow_serv.service que ejemplifica cómo podría configurarse un servicio systemd.
* mlflow_notebook.ipynb: Notebook donde se entrena el modelo, se realizan múltiples ejecuciones (con GridSearchCV), y se registran los resultados en MLflow.
* docker-compose.yaml (varios): Cada uno levanta el servicio correspondiente (API, Jupyter+DB, MinIO, MLflow).

### 1. Carpeta jupyter-db
En esta carpeta se define un archivo docker-compose.yaml para ejecutar:

* MinIO (puertos 9000 y 9001).
* MySQL para almacenar datos crudos y procesados (puerto 3307).

# Pasos para levantar
```
cd jupyter-db
docker compose up -d
```
* MinIO quedará disponible en:
  * Puerto 9000 (API S3-compatible).
  * Puerto 9001 (Consola web de administración).
* MySQL quedará disponible en puerto 3307 en la máquina host (internamente 3306 en el contenedor).

Dentro de MinIO, crear un bucket llamado mlflows3 y dentro de este la carpeta artifacts para almacenar la información (artefactos) procedente de los modelos de MLflow.
Se agrega la carpeta minio (como volumen) para que allí se almacenen los datos de MinIO de manera persistente.

Esta carpeta contiene un Dockerfile y un requirements.txt para ejecutar un contenedor de JupyterLab en el puerto 8888. Dentro de este contenedor se corre el notebook de experimentos.

# Pasos para construir y correr el contenedor de Jupyter
```
cd Jupyter
docker build -t jupyterlab .
docker run -it --name jupyterlab --rm \
  -e TZ=America/Bogota \
  -p 8888:8888 \
  -v $PWD:/work \
  jupyterlab:latest
```
Cambia -v $PWD:/work según tu ruta, si lo deseas.

# Contenido principal
* Archivo experiments.ipynb (o mlflow_notebook.ipynb):
1. Carga de archivo penguin.csv (datos raw) a la base de datos MySQL.
2. Preprocesamiento y guardado de datos procesados en la misma base de datos MySQL.
3. Ejecución de experimentos con Random Forest y Gradient Boosting.
4. Registro de los resultados en MLflow (con artefactos en MinIO).
5. Ejemplo de inferencia usando los modelos que se han pasado a etapa “Production” en MLflow.
* penguins_lter.csv: Archivo raw que se utiliza para crear la base de datos en MySQL desde Jupyter.

Nota: Para marcar un modelo como “Production”, normalmente se hace desde la UI de MLflow (puerto 5000) o programáticamente. Asegúrate de que el experiments.ipynb tenga las credenciales correctas de MinIO y MLflow.

### 2. Carpeta mlflow
Aquí se define el archivo docker-compose.yaml para un servicio MySQL que almacenará la metadata de MLflow (runs, experimentos, etc.). Después de levantar este contenedor, podremos usar MLflow con MySQL como backend (en lugar de SQLite).

# Pasos para levantar MySQL de MLflow
```
cd mlflow
sudo docker compose up -d
```
Se recomienda levantar primero este contenedor antes de iniciar el servicio MLflow propiamente dicho.

# Servicio systemd para MLflow
En la misma carpeta encontrarás el archivo mlflow_serv.service, que sirve para configurar MLflow como un servicio de Linux (usando systemd). Requiere que se tengan instaladas las dependencias:

```
pip install mlflow awscli boto3
```
# Comandos para habilitar y levantar el servicio MLflow
```
sudo systemctl daemon-reload
sudo systemctl enable /home/estudiante/Documents/MLOps2/Entrega4_mlflow/mlflow/mlflow_serv.service
sudo systemctl start mlflow_serv.service
sudo systemctl status mlflow_serv.service
```
Este servicio desplegará MLflow en el puerto 5000. Asegúrate de cambiar la ruta en caso de que difiera de la carpeta donde realmente está el archivo .service.

### 3. Carpeta minio
Aquí se detalla el docker-compose.yaml que inicia MinIO de manera separada (puertos 9000 y 9001). Si ya lo estás levantando desde jupyter-db/docker-compose.yaml, asegúrate de no duplicar contenedores de MinIO. En algunos casos se maneja en una sola carpeta, en otros se mantiene separado.

### 4. Carpeta API (FastAPI)
Contiene un docker-compose.yaml para desplegar el servicio de FastAPI a partir del Dockerfile, junto con instalación de las dependencias (uv, MLflow, etc.).

# Archivos principales
* api.py:
 * Se conecta con MLflow (Model Registry) para cargar el modelo en producción (p. ej. models:/Best_random_forest/Production).
 * Expone un endpoint /predict donde envías los datos del pingüino (longitud de pico, etc.) y devuelve la masa corporal estimada.
 * Se deben cambiar las IP y puertos dependiendo del entorno (en las variables de entorno o directamente en el código).
# Ejecución de la API
```
cd API
docker compose up -d
```
Por defecto, se expone en el puerto 8989.

Para probar la API:

1. Accede a http://127.0.0.1:8989/docs en tu navegador.
2. Verifica que aparezcan los modelos registrados y prueba el endpoint /predict.

### 5. Flujo de ejecución general
# 1. Levantar MinIO y MySQL de datos:
```
cd jupyter-db
docker compose up -d
```
* Crear el bucket mlflows3 en la consola de MinIO (puerto 9001) y la carpeta artifacts (http://<TU_IP>:9001).

# 2. Levantar MySQL para MLflow:
```
cd ../mlflow
sudo docker compose up -d
```
# 3. Levantar MLflow (si se desea con systemd):
```
sudo systemctl daemon-reload
sudo systemctl enable /path/a/tu/mlflow_serv.service
sudo systemctl start mlflow_serv.service
```
* Asegúrate de haber instalado mlflow, awscli, boto3.
* MLflow quedará expuesto en puerto 5000.
# 4. Levantar JupyterLab (también en jupyter-db, si no lo has hecho):
```
cd ../Jupyter
docker build -t jupyterlab .
docker run -it --name jupyterlab --rm \
  -e TZ=America/Bogota \
  -p 8888:8888 \
  -v $PWD:/work \
  jupyterlab:latest
```
* Dentro de Jupyter, abrir experiments.ipynb (o mlflow_notebook.ipynb), cargar datos, entrenar, registrar runs en MLflow.
* Promocionar el mejor modelo a “Production” (desde la UI de MLflow en http://<TU_IP>:5000 o programáticamente).

# 5. Levantar la API: 
para despliegue de servicio API a partir de Dockerfile con instalación de requerimientos con UV.

```
cd ../API
docker compose up -d
```
* Probar en http://127.0.0.1:8989/docs.

### 6. Requisitos cumplidos
* Instancia de BD: MySQL para datos crudos y procesados (carpeta jupyter-db).
* Instancia de MLflow (no SQLite): Usa MySQL como backend (carpeta mlflow).
* Instancia de MinIO: Bucket mlflows3 para artefactos (carpeta minio).
* Instancia de JupyterLab: Notebook que realiza entrenamiento y registra runs en MLflow (≥20 corridas).
* Datos en base de datos: CSV “penguins_lter.csv” se sube a la tabla penguins_original, y luego se procesan a train_data_X, train_data_y etc.
* Modelos registrados en MLflow: Cada experimento con GridSearch produce múltiples runs, se promueve uno a “Production”.
* API de inferencia: api.py (FastAPI) que carga el modelo desde MLflow Model Registry.
