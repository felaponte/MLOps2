from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import sqlalchemy
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import joblib
import os

#------------------------------------Drop table--------------------------------------
def truncate_all_tables():
    # Create SQLAlchemy engine directly without using Airflow connections
    engine = sqlalchemy.create_engine("mysql+pymysql://user:password@db:3306/db")
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
def load_csv_to_mysql():
    csv_path = '/opt/airflow/files/penguins_lter.csv'
    df = pd.read_csv(csv_path)

    engine = sqlalchemy.create_engine('mysql+pymysql://user:password@db:3306/db')
    df.to_sql("penguins_original", con=engine, if_exists='replace', index=False)
    
    
#------------------------------------Load transformed data--------------------------------------
def preprocesamiento():
    engine = sqlalchemy.create_engine("mysql+pymysql://user:password@db:3306/db")
    
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
    #train_data = X_train.copy()
    #train_data["Body Mass (g)"] = y_train
    #test_data = X_test.copy()
    #test_data["Body Mass (g)"] = y_test
    
    # Guardar los conjuntos como tablas SQL (reemplazando si existen)
    X_train.to_sql("train_data_X", con=engine, if_exists="replace", index=False)
    X_test.to_sql("test_data_X", con=engine, if_exists="replace", index=False)
    y_train.to_sql("train_data_y", con=engine, if_exists="replace", index=False)
    y_test.to_sql("test_data_y", con=engine, if_exists="replace", index=False)
    
    print("Preprocesamiento completo. Tablas 'train_data' y 'test_data' creadas en MySQL.")
    
    
#------------------------------------Training--------------------------------------

def entrenamiento():
    engine = sqlalchemy.create_engine("mysql+pymysql://user:password@db:3306/db")
    
    # Separar variables predictoras y objetivo
    X_train = pd.read_sql_table("train_data_X", engine)
    y_train = pd.read_sql_table("train_data_y", engine)
    X_test = pd.read_sql_table("train_data_X", engine)
    y_test = pd.read_sql_table("train_data_y", engine)
    
    # Entrenar RandomForestRegressor
    print("Entrenando RandomForestRegressor...")
    rf_model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    rmse_rf = mean_squared_error(y_test, y_pred_rf) ** 0.5
    print(f"RMSE (Random Forest): {rmse_rf}")
    
    # Asegurarse de que exista la carpeta para guardar los modelos
    os.makedirs("/opt/airflow/files", exist_ok=True)
    joblib.dump(rf_model, "/opt/airflow/files/modelo_random_forest.pkl")
    
    # Entrenar GradientBoostingRegressor
    print("Entrenando GradientBoostingRegressor...")
    gb_model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)
    gb_model.fit(X_train, y_train)
    y_pred_gb = gb_model.predict(X_test)
    rmse_gb = mean_squared_error(y_test, y_pred_gb) ** 0.5
    print(f"RMSE (Gradient Boosting): {rmse_gb}")
    
    joblib.dump(gb_model, "/opt/airflow/files/modelo_gradient_boosting.pkl")
    
    print("Comparación de Modelos:")
    print(f"RMSE Random Forest: {rmse_rf}")
    print(f"RMSE Gradient Boosting: {rmse_gb}")
    if rmse_gb < rmse_rf:
        print("¡Gradient Boosting es mejor! Se usará 'modelo_gradient_boosting.pkl'")
    else:
        print("¡Random Forest es mejor! Se usará 'modelo_random_forest.pkl'")
#---------------------------------------------------------------------------------------

with DAG(
    dag_id='Complete_pipeline',
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
        task_id='load_raw_csv',
        python_callable=load_csv_to_mysql
    )
    
    load__transformed_task = PythonOperator(
        task_id='load_transformed_csv',
        python_callable=preprocesamiento
    )
    
    training = PythonOperator(
        task_id='training_models',
        python_callable=entrenamiento
    )
    
    
    clear_db >> load_task >> load__transformed_task >> training

