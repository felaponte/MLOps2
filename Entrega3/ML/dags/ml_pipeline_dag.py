from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import joblib
import os

# Configuración de conexión a MySQL
MYSQL_USER = "root"
MYSQL_PASSWORD = "mlops"
# En el docker-compose usaremos el servicio con nombre "mysql" para que Airflow lo reconozca
MYSQL_HOST = "mysql"
MYSQL_DATABASE = "mydb"
CONNECTION_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"

def preprocesamiento():
    engine = create_engine(CONNECTION_URL)
    
    # Leer la tabla original creada previamente (por ejemplo, 'penguins_original')
    df = pd.read_sql_table("penguins_original", engine)
    
    # Transformar "Date Egg" a día del año (1 a 365) y manejar NaN
    df["Date Egg"] = pd.to_datetime(df["Date Egg"], errors="coerce").dt.dayofyear
    df["Date Egg"].fillna(df["Date Egg"].median(), inplace=True)
    
    # Eliminar columnas irrelevantes
    df.drop(columns=["studyName", "Sample Number", "Individual ID", "Comments"], inplace=True)
    
    # Rellenar valores nulos en columnas numéricas
    num_cols = ["Culmen Length (mm)", "Culmen Depth (mm)", "Flipper Length (mm)", "Body Mass (g)", "Delta 15 N (o/oo)", "Delta 13 C (o/oo)"]
    for col in num_cols:
        df[col].fillna(df[col].mean(), inplace=True)
    
    # Rellenar valores nulos en columnas categóricas
    cat_cols = ["Species", "Region", "Island", "Stage", "Clutch Completion", "Sex"]
    for col in cat_cols:
        df[col].fillna("Desconocido", inplace=True)
    
    # One-Hot Encoding para variables categóricas
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
    
    # Seleccionar variables predictoras y objetivo
    X = df[["Culmen Length (mm)", "Culmen Depth (mm)", "Flipper Length (mm)"]]
    y = df["Body Mass (g)"]
    
    # Dividir en entrenamiento y prueba (80%-20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Combinar para guardar en una sola tabla
    train_data = X_train.copy()
    train_data["Body Mass (g)"] = y_train
    test_data = X_test.copy()
    test_data["Body Mass (g)"] = y_test
    
    # Guardar los conjuntos como tablas SQL (reemplazando si existen)
    train_data.to_sql("train_data", con=engine, if_exists="replace", index=False)
    test_data.to_sql("test_data", con=engine, if_exists="replace", index=False)
    
    print("Preprocesamiento completo. Tablas 'train_data' y 'test_data' creadas en MySQL.")

def entrenamiento():
    engine = create_engine(CONNECTION_URL)
    
    # Leer datos preprocesados desde MySQL
    train_data = pd.read_sql_table("train_data", engine)
    test_data = pd.read_sql_table("test_data", engine)
    
    # Separar variables predictoras y objetivo
    X_train = train_data[["Culmen Length (mm)", "Culmen Depth (mm)", "Flipper Length (mm)"]]
    y_train = train_data["Body Mass (g)"].values.ravel()
    X_test = test_data[["Culmen Length (mm)", "Culmen Depth (mm)", "Flipper Length (mm)"]]
    y_test = test_data["Body Mass (g)"].values.ravel()
    
    # Entrenar RandomForestRegressor
    print("Entrenando RandomForestRegressor...")
    rf_model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    rmse_rf = mean_squared_error(y_test, y_pred_rf) ** 0.5
    print(f"RMSE (Random Forest): {rmse_rf}")
    
    # Asegurarse de que exista la carpeta para guardar los modelos
    os.makedirs("/ml_project/data", exist_ok=True)
    joblib.dump(rf_model, "/ml_project/data/modelo_random_forest.pkl")
    
    # Entrenar GradientBoostingRegressor
    print("Entrenando GradientBoostingRegressor...")
    gb_model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)
    gb_model.fit(X_train, y_train)
    y_pred_gb = gb_model.predict(X_test)
    rmse_gb = mean_squared_error(y_test, y_pred_gb) ** 0.5
    print(f"RMSE (Gradient Boosting): {rmse_gb}")
    
    joblib.dump(gb_model, "/ml_project/data/modelo_gradient_boosting.pkl")
    
    print("Comparación de Modelos:")
    print(f"RMSE Random Forest: {rmse_rf}")
    print(f"RMSE Gradient Boosting: {rmse_gb}")
    if rmse_gb < rmse_rf:
        print("¡Gradient Boosting es mejor! Se usará 'modelo_gradient_boosting.pkl'")
    else:
        print("¡Random Forest es mejor! Se usará 'modelo_random_forest.pkl'")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'ml_pipeline',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:
    
    task_preprocesamiento = PythonOperator(
        task_id='preprocesamiento',
        python_callable=preprocesamiento
    )
    
    task_entrenamiento = PythonOperator(
        task_id='entrenamiento',
        python_callable=entrenamiento
    )
    
    task_preprocesamiento >> task_entrenamiento
