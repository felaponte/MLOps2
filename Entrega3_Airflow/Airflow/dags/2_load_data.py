from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import sqlalchemy

def load_csv_to_mysql():
    csv_path = '/opt/airflow/files/penguins_lter.csv'
    df = pd.read_csv(csv_path)

    engine = sqlalchemy.create_engine('mysql+pymysql://user:password@db:3306/db')
    df.to_sql('my_table', con=engine, if_exists='replace', index=False)

with DAG(
    dag_id='load_csv_to_mysql',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    description='Load CSV data into MySQL',
) as dag:

    load_task = PythonOperator(
        task_id='load_csv',
        python_callable=load_csv_to_mysql
    )

