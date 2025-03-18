 ### Taller MLflow

MLflow es una plataforma de código abierto para administrar el ciclo de vida completo del aprendizaje automático. En este proyecto se implementan los siguientes pasos:

1. Instancia de base de datos (MySQL) para almacenar los datos crudos y procesados.
2. Instancia de MLflow (usando MySQL como backend de metadatos, en lugar de SQLite).
3. Instancia de MinIO como almacenamiento de artefactos (reemplazando el servicio de S3).
4. Instancia de JupyterLab para la experimentación, con un notebook donde se entrena un modelo y se registran múltiples ejecuciones (≥20) en MLflow.
5. Registro de modelos en el Model Registry de MLflow, y cambio de etapa a “Production”.
6. API de inferencia (con FastAPI), que carga el modelo directamente desde el Model Registry en producción.

## Estructura del proyecto
```
MLOps2
│── __pycache__
│── 5-MLflow
│   │── API
│   │   │── api.py
│   │   │── docker-compose.yaml
│   │   │── Dockerfile
│   │   │── requirements.txt
│   │
│   │── jupyter-db
│   │   │── .ipynb_checkpoints
│   │   │── docker-compose.yaml
│   │   │── Dockerfile
│   │   │── requirements.txt
│   │    |── mlruns
│   │    |── mlflow_notebook.ipynb
│   │    |── penguins_lter.csv
│   │
│   │── minio
│   │   │── minio
│   │   │   │── .minio.sys
│   │   │   │── mlflows3
│   │   │── docker-compose.yaml
│   │
│   │── mlflow
│   │   │── docker-compose.yaml
│   │   │── mlflow_serv.service
│   │
│   │── Dockerfile
│   │── docker-compose.yaml
│   │── requirements.txt
```
A continuación se detalla para qué sirve cada carpeta/archivo principal:

* API: Contiene el servicio de FastAPI (api.py) para la inferencia del modelo con MLflow.
* jupyter-db: Contiene la definición de un contenedor de MySQL (almacena datos crudos y procesados) y un Dockerfile para levantar JupyterLab y correr el mlflow_notebook.ipynb.
* minio: Define el contenedor de MinIO y su bucket donde se almacenan los artefactos de MLflow.
* mlflow: Define el contenedor o servicio de MLflow Tracking y el archivo mlflow_serv.service que ejemplifica cómo podría configurarse un servicio systemd.
* mlflow_notebook.ipynb: Notebook donde se entrena el modelo, se realizan múltiples ejecuciones (con GridSearchCV), y se registran los resultados en MLflow.
* docker-compose.yaml (varios): Cada uno levanta el servicio correspondiente (API, Jupyter+DB, MinIO, MLflow).

## 1. Base de datos (MySQL)
Para almacenar datos crudos y procesados, usamos un contenedor MySQL. En la carpeta jupyter-db se encuentra un docker-compose.yaml que define:
```
version: '2'
services:
  db:
    image: mysql:latest
    restart: always
    environment:
      MYSQL_DATABASE: 'db_jupyter'
      MYSQL_USER: 'user'
      MYSQL_PASSWORD: 'password'
      MYSQL_ROOT_PASSWORD: 'password'
    ports:
      - '3307:3306'
    volumes:
      - my-db:/var/lib/mysql
    networks:
      - my_network_for_jupyter

volumes:
  my-db:

networks:
  my_network_for_jupyter:
    external: true
```

* Expone el puerto 3307 en la máquina host (que internamente es 3306 en el contenedor).
* Crea la base de datos db_jupyter.
* Usa la variable MYSQL_USER y MYSQL_PASSWORD para autenticar.

En el notebook mlflow_notebook.ipynb, verás que se establece la conexión mysql+pymysql://user:password@db:3306/db_jupyter para cargar y guardar datos.

## 2. Instancia de MLflow (con MySQL)
En la carpeta mlflow, se tiene un docker-compose.yaml donde se define la base de datos para MLflow (otra instancia MySQL) o se podría reutilizar una existente. En este ejemplo, configuramos:

```
version: '2'
services:
  db:
    image: mysql:latest
    restart: always
    environment:
      MYSQL_DATABASE: 'db_mlflow'
      MYSQL_USER: 'user'
      MYSQL_PASSWORD: 'password'
      MYSQL_ROOT_PASSWORD: 'password'
    ports:
      - '3306:3306'
    volumes:
      - my-db:/var/lib/mysql

volumes:
  my-db:

```

Aquí es donde se persisten los metadatos de MLflow (runs, experimentos, parámetros, etc.). En vez de sqlite, usamos MySQL.

Además, está el archivo mlflow_serv.service que muestra cómo podría configurarse MLflow como un servicio de systemd en Linux, con las variables de entorno (MLFLOW_S3_ENDPOINT_URL, AWS_ACCESS_KEY_ID, etc.) para conectar con MinIO. Sin embargo, si prefieres usar contenedores, podrías levantar MLflow directamente con un comando mlflow server ... o escribir otro Dockerfile.

## 3. MinIO
Para el almacenamiento de artefactos (modelos, logs, etc.), se usa MinIO como reemplazo de un servicio S3. Dentro de la carpeta minio, verás un docker-compose.yaml como:
```
version: '2'
services:
  minio:
    container_name: Minio
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=admin
      - MINIO_ROOT_PASSWORD=supersecret
    image: quay.io/minio/minio:latest
    ports:
      - '9000:9000'
      - '9001:9001'
    volumes:
      - ./minio:/data
    restart: unless-stopped
```
* Puerto 9000: API de MinIO (S3-compatible).
* Puerto 9001: Consola web de MinIO.

Ahí puedes crear un bucket llamado mlflows3 y dentro la carpeta artifacts para MLflow. Asegúrate de configurar las variables de entorno en MLflow y Jupyter (MLFLOW_S3_ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY).

## 4. JupyterLab + Notebook de entrenamiento
En la carpeta jupyter-db se encuentra también un Dockerfile para construir un contenedor que instale jupyter y jupyterlab, así como las dependencias (mlflow, boto3, sqlalchemy, etc.). Al levantar este contenedor, podrás acceder a JupyterLab en el puerto 8888 de tu máquina.

Dentro del notebook mlflow_notebook.ipynb se realiza:

1. Carga de datos: Se lee el archivo penguins_lter.csv y se guarda en la base de datos MySQL (db_jupyter).
2. Preprocesamiento: Se generan tablas train_data_X, train_data_y, test_data_X, test_data_y en MySQL.
3. Entrenamiento: Se configuran experimentos en MLflow, se entrenan varios modelos (RandomForest, GradientBoosting) y se hacen GridSearch con ≥20 combinaciones de hiperparámetros.
4. Registro de modelos: Los mejores modelos se guardan y se promueven a “Production” con nombres como Best_random_forest o Best_gradient_boosting.

Ejemplo de instrucción para levantar Jupyter:
```
cd jupyter-db
docker build -t jupyterlab_image .
docker run --name jupyterlab \
  -p 8888:8888 \
  -v $(pwd):/work \
  jupyterlab_image
```
Una vez dentro de JupyterLab, abres mlflow_notebook.ipynb y ejecutas las celdas.

## 5. Registro de modelos en MLflow
Cuando los modelos se entrenan, se registran automáticamente usando la API de MLflow. Si quieres registrarlos manualmente:

```
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()
client.create_registered_model("Best_random_forest")  # Ejemplo
# ...
client.transition_model_version_stage(
    name="Best_random_forest",
    version=1,
    stage="Production"
)
```
Estas acciones también se pueden realizar desde la UI de MLflow (en el puerto 5000), en la sección Model Registry.

## 6. API de inferencia
Para exponer el modelo en un endpoint, se creó una API con FastAPI en la carpeta API. El archivo api.py recibe datos (culmen, flipper, etc.), carga desde mlflow.pyfunc.load_model("models:/<NOMBRE>/Production") y responde la predicción.

Ejecución
El docker-compose.yaml dentro de API luce así:
```
version: '3'
services:
  api_service:
    build: .
    ports:
      - "8989:8989"
    command: ["uv","run","uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8989"]
```
Para levantarlo:
```
cd API
docker compose up -d
```
Luego, puedes probar la API con un curl o herramienta similar:
```
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "Culmen_Length_mm": 45.2,
    "Culmen_Depth_mm": 17.1,
    "Flipper_Length_mm": 201
  }' \
  "http://localhost:8989/predict?modelo_elegir=Best_random_forest"
```
Recibirás un JSON con la predicción, algo como:
```
{
  "modelo usado": "Best_random_forest",
  "predicted_body_mass": 3800.54
}
```
## 7. Cómo levantar todo
Dependiendo de tu preferencia, puedes levantar cada componente por separado:

1. MinIO:
```
cd minio
docker compose up -d
```
* Asegurarte de crear el bucket mlflows3.
2. MLflow:
(O usar systemd con mlflow_serv.service)
O un docker-compose.yaml con un contenedor que ejecute mlflow server --backend-store-uri ....
3. Base de datos Jupyter (MySQL) + JupyterLab:
```
cd jupyter-db
docker compose up -d
```
* Luego, accedes a la URL de Jupyter (puerto 8888).
* Corres mlflow_notebook.ipynb para entrenar y registrar modelos.
4. API:
```
cd API
docker compose up -d
```
* La API estará en http://localhost:8989.

Asegúrate de que cada contenedor pueda “ver” la IP/puerto del resto, configurando las variables de entorno (por ejemplo, MLFLOW_S3_ENDPOINT_URL=http://minio:9000, etc.) según tu red de Docker.

Si decides usar una sola red y un solo docker-compose unificado, podrías simplificar la configuración para que todos los servicios se conecten por nombre de contenedor (por ejemplo, minio:9000, db:3306, etc.).

8. Requisitos cumplidos
* Instancia de BD: MySQL para datos crudos y procesados (carpeta jupyter-db).
* Instancia de MLflow (no SQLite): Usa MySQL como backend (carpeta mlflow).
* Instancia de MinIO: Bucket mlflows3 para artefactos (carpeta minio).
* Instancia de JupyterLab: Notebook que realiza entrenamiento y registra runs en MLflow (≥20 corridas).
* Datos en base de datos: CSV “penguins_lter.csv” se sube a la tabla penguins_original, y luego se procesan a train_data_X, train_data_y etc.
* Modelos registrados en MLflow: Cada experimento con GridSearch produce múltiples runs, se promueve uno a “Production”.
* API de inferencia: api.py (FastAPI) que carga el modelo desde MLflow Model Registry.
