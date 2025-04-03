from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sqlalchemy
import pymysql
import mlflow
from mlflow.tracking import MlflowClient
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import mean_squared_error
import os
import requests
import json
import numpy as np
import time
from joblib import parallel_backend

#------------------------------------Drop table--------------------------------------
def truncate_all_tables():
    # Create SQLAlchemy engine directly without using Airflow connections
    engine = sqlalchemy.create_engine("mysql+pymysql://user:password@db-data:3306/db")
    with engine.connect() as conn:
        conn.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # Get all table names from the information_schema
        result = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='db';")
        tables = [row[0] for row in result.fetchall()]
        
        # Truncate each table
        for table in tables:
            #conn.execute(f"TRUNCATE TABLE `{table}`;")
            conn.execute(f"DROP TABLE `{table}`;")
        
        conn.execute("SET FOREIGN_KEY_CHECKS = 1;")


#------------------------------------Load raw data--------------------------------------
def load_data():
    requests.get('http://host.docker.internal/restart_data_generation?group_number=2')
    i = 0
    columnas = ['Elevation', 'Aspect', 'Slope', 'Horizontal_Distance_To_Hydrology', 'Vertical_Distance_To_Hydrology', 'Horizontal_Distance_To_Roadways',
    'Hillshade_9am', 'Hillshade_Noon', 'Hillshade_3pm', 'Horizontal_Distance_To_Fire_Points', 'Wilderness_Area', 'Soil_Type', 'Cover_Type']

    # Crear DataFrame vacío
    df = pd.DataFrame(columns=columnas)

    while i <10:
        try:
            r = requests.get('http://host.docker.internal:80/data?group_number=2')
            d = json.loads(r.content.decode('utf-8'))
            if i == d['batch_number']:
                print("Batch repetido. No se añaden datos")
            else:
                i = d['batch_number']
                print(f"Añadiendo datos batch {i}")
                temp = pd.DataFrame(d['data'], columns=columnas)
                # Concatenate all at once
                df = pd.concat([df, temp], ignore_index=True)


        except requests.exceptions.ConnectionError:
            print("🚫 No se pudo conectar a la API, reintentando...")
        
        if i==10:
            print("Todos los datos han sido guardados")
        else:
            time.sleep(3) 


    engine = sqlalchemy.create_engine("mysql+pymysql://user:password@db-data:3306/db")
    df.to_sql("tipo_de_cubierta_forestal_raw", con=engine, if_exists='replace', index=False)
    
    
#------------------------------------Load transformed data--------------------------------------
def preprocesamiento():
    engine = sqlalchemy.create_engine("mysql+pymysql://user:password@db-data:3306/db")
    
    # Leer la tabla original creada previamente (por ejemplo, 'penguins_original')
    df = pd.read_sql_table("tipo_de_cubierta_forestal_raw", engine)
    
    # Selección de variables predictoras y objetivo
    feature_cols = ['Elevation', 'Aspect', 'Slope', 'Horizontal_Distance_To_Hydrology', 'Vertical_Distance_To_Hydrology', 'Horizontal_Distance_To_Roadways',
    'Hillshade_9am', 'Hillshade_Noon', 'Hillshade_3pm', 'Horizontal_Distance_To_Fire_Points']
    target_col = "Cover_Type"

    X = df[feature_cols]
    y = df[target_col]

    # Dividir en entrenamiento y prueba (80%-20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Convertir X_train, X_test, y_train y y_test a float
    X_train = X_train.astype(float)
    X_test = X_test.astype(float) 
    y_train = y_train.astype(float)
    y_test = y_test.astype(float)
    
    # Guardar los conjuntos como tablas SQL (reemplazando si existen)
    X_train.to_sql("train_data_X", con=engine, if_exists="replace", index=False)
    X_test.to_sql("test_data_X", con=engine, if_exists="replace", index=False)
    y_train.to_sql("train_data_y", con=engine, if_exists="replace", index=False)
    y_test.to_sql("test_data_y", con=engine, if_exists="replace", index=False)
    
    print("Preprocesamiento completo. Tablas 'train_data' y 'test_data' creadas en MySQL.")
    
    
#------------------------------------Training--------------------------------------

def entrenamiento_de_prueba():
    engine = sqlalchemy.create_engine("mysql+pymysql://user:password@db-data:3306/db")
    
    # Separar variables predictoras y objetivo
    X_train = pd.read_sql_table("train_data_X", engine)
    y_train = pd.read_sql_table("train_data_y", engine)
    X_test = pd.read_sql_table("test_data_X", engine)
    y_test = pd.read_sql_table("test_data_y", engine)
    
    y_train = y_train.values.ravel()
    y_test = y_test.values.ravel()
    
    #----------------------------------------Variables de entorno MLFlow--------------------------------
    # connects to the Mlflow tracking server that you started above
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://minio:9000"
    os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'
    mlflow.set_tracking_uri("http://mlflow-service:5000")
    
    #---------------------------------------------------------------------------
    mlflow.set_experiment("mlflow_tracking_tipo_de_cubierta_forestal_proofs")

    mlflow.autolog(log_model_signatures=True, log_input_examples=True)

    # run description (just metadata)
    desc = "the simplest possible example"

    # executes the run
    with mlflow.start_run(run_name="Random_forest_no_params", description=desc) as run:
        # Entrenar RandomForest
        rf_model = RandomForestClassifier()
        rf_model.fit(X_train, y_train)
        
    #---------------------------------
    mlflow.set_experiment("mlflow_tracking_tipo_de_cubierta_forestal_proofs")

    mlflow.autolog(log_model_signatures=True, log_input_examples=True)

    # run description (just metadata)
    desc = "the simplest possible example"

    # executes the run
    with mlflow.start_run(run_name="Gradient_boost_no_params", description=desc) as run:
        # Entrenar GradietBoost
        gb_model = GradientBoostingClassifier()
        gb_model.fit(X_train, y_train)
        
        
def entrenamiento_random_forest():
    engine = sqlalchemy.create_engine("mysql+pymysql://user:password@db-data:3306/db")
    
    # Separar variables predictoras y objetivo
    X_train = pd.read_sql_table("train_data_X", engine)
    y_train = pd.read_sql_table("train_data_y", engine)
    X_test = pd.read_sql_table("test_data_X", engine)
    y_test = pd.read_sql_table("test_data_y", engine)
    
    y_train = y_train.values.ravel()
    y_test = y_test.values.ravel()
    
    #----------------------------------------Variables de entorno MLFlow--------------------------------
    # connects to the Mlflow tracking server that you started above
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://minio:9000"
    os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'
    mlflow.set_tracking_uri("http://mlflow-service:5000")
    
    #---------------------------------
    mlflow.set_experiment("Random_forest_looking_for_the_best_model")

    mlflow.autolog(log_model_signatures=True, log_input_examples=True)

    # run description (just metadata)
    desc = "Random_forest_grid_search"

    params = {
      "n_estimators": [33, 66, 200],
      "max_depth": [2, 4, 6],
      "max_features": [3, 4, 5]
    }

    rf_model = RandomForestClassifier()
    searcher = GridSearchCV(estimator=rf_model, param_grid=params, cv=5, scoring='accuracy', n_jobs=-1)

    with mlflow.start_run(run_name="autolog_with_grid_search") as run:
        searcher.fit(X_train, y_train)


def entrenamiento_gradient_boosting():
    engine = sqlalchemy.create_engine("mysql+pymysql://user:password@db-data:3306/db")
    
    # Separar variables predictoras y objetivo
    X_train = pd.read_sql_table("train_data_X", engine)
    y_train = pd.read_sql_table("train_data_y", engine)
    X_test = pd.read_sql_table("test_data_X", engine)
    y_test = pd.read_sql_table("test_data_y", engine)
    
    y_train = y_train.values.ravel()
    y_test = y_test.values.ravel()
    
    #----------------------------------------Variables de entorno MLFlow--------------------------------
    # connects to the Mlflow tracking server that you started above
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://minio:9000"
    os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'
    mlflow.set_tracking_uri("http://mlflow-service:5000")
       
    #---------------------------------
    mlflow.set_experiment("Gradient_Boosting_looking_for_the_best_model")

    mlflow.autolog(log_model_signatures=True, log_input_examples=True)

    # run description (just metadata)
    desc = "Gradient_Boosting_grid_search"

    param_grid = {
        'n_estimators': [100, 200],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 4, 5],
        'subsample': [0.8, 1.0]
    }

    gb_model = GradientBoostingClassifier()
    searcher = GridSearchCV(estimator=gb_model, param_grid=param_grid, cv=5, scoring='accuracy', n_jobs=-1)

    with mlflow.start_run(run_name="autolog_with_grid_search") as run:
        searcher.fit(X_train, y_train)

#---------------------------------------------------------------------------------------

with DAG(
    dag_id='Pipeline-proyecto2',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    description='Drop tables and Load CSV data into MySQL',
) as dag:

    clear_db = PythonOperator(
        task_id='truncate_all_tables',
        python_callable=truncate_all_tables
    )

    load_task = PythonOperator(
        task_id='load_raw_data',
        python_callable=load_data
    )
    
    load__transformed_task = PythonOperator(
        task_id='load_transformed_data',
        python_callable=preprocesamiento
    )
    
    training1 = PythonOperator(
        task_id='training_modelos_de_prueba',
        python_callable=entrenamiento_de_prueba
    )
    
    training2 = PythonOperator(
        task_id='training_with_random_forest_model',
        python_callable=entrenamiento_random_forest
    )
    
    training3 = PythonOperator(
        task_id='training_with_gradient_boosting_model',
        python_callable=entrenamiento_gradient_boosting
    )
    
    clear_db >> load_task >> load__transformed_task >> [training1, training2, training3] 

