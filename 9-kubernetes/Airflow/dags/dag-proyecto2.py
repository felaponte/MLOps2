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

#------------------------------------Load raw data--------------------------------------
def load_data():
    ## download the dataset
    # Directory of the raw data files
    _data_root = './data/Diabetes'
    # Path to the raw training data
    _data_filepath = os.path.join(_data_root, 'Diabetes.csv')
    # Download data
    os.makedirs(_data_root, exist_ok=True)
    if not os.path.isfile(_data_filepath):
        url = 'https://docs.google.com/uc?export= \download&confirm={{VALUE}}&id=1k5-1caezQ3zWJbKaiMULTGq-3sz6uThC'
        r = requests.get(url, allow_redirects=True, stream=True)
        open(_data_filepath, 'wb').write(r.content)
    df = pd.read_csv("./data/Diabetes/Diabetes.csv")

    engine = sqlalchemy.create_engine("mysql+pymysql://user:password@10.43.101.177:3307/db")
    df.to_sql("db_diabetes_raw", con=engine, if_exists='replace', index=False)
    
    
#------------------------------------Load transformed data--------------------------------------
def preprocesamiento():
    engine1 = sqlalchemy.create_engine("mysql+pymysql://user:password@10.43.101.177:3307/db")
    
    df = pd.read_sql_table("db_diabetes_raw", engine1)
    #Borrando variables con un solo valor, ids, y variables con muchos valores nulos y faltantes
    df_clean =  df.drop(columns=['examide','citoglipton','encounter_id','patient_nbr','max_glu_serum','A1Cresult','weight','race','payer_code'])
    #Borrando variables con más de un 60% de desbalance
    df_clean =  df_clean.drop(columns=['number_outpatient','number_emergency','repaglinide','acarbose','miglitol','troglitazone','tolazamide','glyburide-metformin',
                                  'glipizide-metformin','glimepiride-pioglitazone','metformin-rosiglitazone','metformin-pioglitazone','tolbutamide','metformin',
                                  'acetohexamide','nateglinide','chlorpropamide','glimepiride','pioglitazone','rosiglitazone','glipizide','glyburide','number_inpatient'])
    #Borrando categorías con muchos valores
    df_clean =  df_clean.drop(columns=['diag_1','diag_2','diag_3','medical_specialty'])
    #Borrando categorías muy correlacionadas
    df_clean =  df_clean.drop(columns=['insulin','change'])
    #Muy poca correlación
    df_clean =  df_clean.drop(columns=['gender'])

    df_clean.drop_duplicates(inplace=True)

    midpoints = {"[0-10)": 5, "[10-20)": 15, "[20-30)": 25, "[30-40)": 35, "[40-50)": 45, "[50-60)": 55, "[60-70)": 65, "[70-80)": 75, "[80-90)": 85, "[90-100)": 95}
    df_clean["age"] = df_clean["age"].map(midpoints)

    mapping = {'Yes': 1, 'No': 0}
    df_clean['diabetesMed'] = df_clean['diabetesMed'].map(mapping).astype(int)
    
    # Selección de variables predictoras y objetivo
    X = df_clean.drop(columns=['readmitted'])
    y = df_clean['readmitted']
    
    


    # Dividir en entrenamiento y prueba (80%-20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Guardar los conjuntos como tablas SQL (reemplazando si existen)
    engine2 = sqlalchemy.create_engine("mysql+pymysql://user:password@10.43.101.177:3308/db")
    X_train.to_sql("train_data_X", con=engine2, if_exists="replace", index=False)
    X_test.to_sql("test_data_X", con=engine2, if_exists="replace", index=False)
    y_train.to_sql("train_data_y", con=engine2, if_exists="replace", index=False)
    y_test.to_sql("test_data_y", con=engine2, if_exists="replace", index=False)
    
    print("Preprocesamiento completo. Tablas 'train_data' y 'test_data' creadas en MySQL.")
    
    
#------------------------------------Training--------------------------------------

def entrenamiento_de_prueba():
    engine = sqlalchemy.create_engine("mysql+pymysql://user:password@10.43.101.177:3308/db")
    
    # Separar variables predictoras y objetivo
    X_train = pd.read_sql_table("train_data_X", engine)
    y_train = pd.read_sql_table("train_data_y", engine)
    X_test = pd.read_sql_table("test_data_X", engine)
    y_test = pd.read_sql_table("test_data_y", engine)
    
    y_train = y_train.values.ravel()
    y_test = y_test.values.ravel()
    
    #----------------------------------------Variables de entorno MLFlow--------------------------------
    # connects to the Mlflow tracking server that you started above
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://10.43.101.177:9000"
    os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'
    mlflow.set_tracking_uri("http://10.43.101.177:5000")
    
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
    engine = sqlalchemy.create_engine("mysql+pymysql://user:password@10.43.101.177:3308/db")
    
    # Separar variables predictoras y objetivo
    X_train = pd.read_sql_table("train_data_X", engine)
    y_train = pd.read_sql_table("train_data_y", engine)
    X_test = pd.read_sql_table("test_data_X", engine)
    y_test = pd.read_sql_table("test_data_y", engine)
    
    y_train = y_train.values.ravel()
    y_test = y_test.values.ravel()
    
    #----------------------------------------Variables de entorno MLFlow--------------------------------
    # connects to the Mlflow tracking server that you started above
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://10.43.101.177:9000"
    os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'
    mlflow.set_tracking_uri("http://10.43.101.177:5000")
    
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
    searcher = GridSearchCV(estimator=rf_model, param_grid=params, cv=5, scoring='accuracy', n_jobs=4)

    with mlflow.start_run(run_name="autolog_with_grid_search") as run:
        searcher.fit(X_train, y_train)


def entrenamiento_gradient_boosting():
    engine = sqlalchemy.create_engine("mysql+pymysql://user:password@10.43.101.177:3308/db")
    
    # Separar variables predictoras y objetivo
    X_train = pd.read_sql_table("train_data_X", engine)
    y_train = pd.read_sql_table("train_data_y", engine)
    X_test = pd.read_sql_table("test_data_X", engine)
    y_test = pd.read_sql_table("test_data_y", engine)
    
    y_train = y_train.values.ravel()
    y_test = y_test.values.ravel()
    
    #----------------------------------------Variables de entorno MLFlow--------------------------------
    # connects to the Mlflow tracking server that you started above
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://10.43.101.177:9000"
    os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'
    mlflow.set_tracking_uri("http://10.43.101.177:5000")
       
    #---------------------------------
    mlflow.set_experiment("Gradient_Boosting_looking_for_the_best_model")

    mlflow.autolog(log_model_signatures=True, log_input_examples=True)

    # run description (just metadata)
    desc = "Gradient_Boosting_grid_search"

    param_grid = {
        'n_estimators': [100, 200],
        'learning_rate': [0.01, 0.1],
        'max_depth': [3, 1],
        'subsample': [0.5, 1.0]
    }

    gb_model = GradientBoostingClassifier()
    searcher = GridSearchCV(estimator=gb_model, param_grid=param_grid, cv=3, scoring='accuracy', n_jobs=4)

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
    
    load_task >> load__transformed_task >> [training1, training2, training3] 

