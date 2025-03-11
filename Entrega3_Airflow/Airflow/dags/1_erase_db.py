from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sqlalchemy

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

with DAG(
    dag_id='clear_mysql_database_direct',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    description='Truncate all tables in MySQL without using Airflow connection',
) as dag:
    
    clear_db = PythonOperator(
        task_id='truncate_all_tables',
        python_callable=truncate_all_tables
    )

