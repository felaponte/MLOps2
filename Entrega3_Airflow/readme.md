### Taller 3 Airflow - MLOps PUJ

Este proyecto implementa un modelo de predicción de la masa corporal de pingüinos. Para este objetivo se implementarán 3 servicios con docker. El primer contenedor es una conexión a una instancia sql donde vamos a mantener nuestras tablas para el preprocesamiento y el entrenamiento del modelo.
El segundo contenedor ejecuta una instancia de Airflow la cual tiene un dag con las siguientes tareas:
    1 Borra los archivos
    2 Carga archivos a mysql
    3 Preprocesamiento del dataset como tabla importada de mysql
    4 Entrenamiento de modelos y carga de estos al volumen.
Finalmente tenemos un tercer servicio para despliegue de la Api que nos va permitir realizar la inferencia.

## Consideraciones Generales
- Para la instalación de dependencias en Airflow se uso PIP. No fue posible usar UV ya que necesitaba un usuario root para conectarse a mySQL, y como el usuario que requería Airflow en el Dockerfile se definía como Airflow y cuando se ejecuta cualquier conexión a mysql, obteníamos errores. Con PIP se evitó trabajar con usuario Root y solo el definido en el Dockerfile de Airflow como user=Airflow
- Se deben definir variables de entorno para que Airflow permita la conexión al volumen. Las variables son las siguientes:
                 echo -e "AIRFLOW_UID=$(id -u)" > .env
                 echo -e "AIRFLOW_PROJ_DIR=./Airflow" >> .env
- Se ajustó el directorio de build en el docker compose.yaml para que se basara en el Dockerfile personalizado por nosotros.            

## Estructura del Proyecto

```
Entrega3_Airflow/
├── Airflow/    # Todo lo de Airflow (dags, logs, plugins)
| ├─ dags/
│   ├── 3.py
| ├─ files/   # Volumen donde se van a guardar los modelos para alimentar el API.
│   ├── penguins_lter.csv
| ├─ Dockerfile
| ├─ Requirements.txt 
├── API/
│     ├── api.py
│     ├── Dockerfile  (si necesitas construir una imagen personalizada para la API)
│     └── requirements.txt
|
|── docker-compose.yaml
│── .env
└── README.md
```
# Tecnologías Utilizadas
- Python 3.9
- FastAPI
- Scikit-Learn
- Joblib
- Pandas & NumPy
- Docker
- Jupyter y Jupyter notebook
- UV
- PIP
- Mysql
- PostgresSQL
- Airflow
---
# Instrucciones

## 1. Clonar el Repositorio
Se clona el repositorio
```
git clone https://github.com/felaponte/MLOps2.git
cd MLOps2
cd Entrega3_Airflow
```
## 2. Estableciemiento variables de entorno
Se debe ejecutar los siguientes dos comandos para definir las variables de entorno para Airflow
```
echo -e "AIRFLOW_UID=$(id -u)" > .env
echo -e "AIRFLOW_PROJ_DIR=./Airflow" >> .env
```
## 3. Creación de las imágenes 
Se inician todos los servicios.
```
sudo docker compose up --build 
```
El primer servicio va crear una instancia mysql en el puerto 3086. 
El segundo servicio es una instancia de Airflow con un dag que tiene 4 task. El dag se debe ejecutar de manera manual. Los procesos son los siguientes: 
    - Borrar contenido base de datos
    - Cargar datos de penguins a la base de datos en mysql como una tabla.
    - Realizar preprocesamiento para entrenamiento de modelo con la tabla del paso anterior y carga las tablas de train y test para X y y.
    - Realiza entrenamiento de modelo usando las tablas generadas anteriormente y guarda los modelos entrenados como archivos .pkl en el volumen.
El tercer serviciova a desplegar la API en el puerto 8989 donde vamos a poder hacer la inferencia con los modelos entrenados del paso anterior.
Esta API reconoce los archivos .pkl que fueron entrenados anteriormente. Es necesario escoger el modelo a usar y pasarle los parámetros "Culmen_Length_mm", "Culmen_Depth_mm", "Flipper_Length_mm" para poder realizar la inferencia.



