import os
import pandas as pd
from sqlalchemy import create_engine

# Configuración de conexión usando variables de entorno
user = "root"
password = os.environ.get("MYSQL_ROOT_PASSWORD", "mlops")
host = "127.0.0.1"  # Dentro del contenedor usamos localhost
db = os.environ.get("MYSQL_DATABASE", "mydb")

# Construir la URL de conexión para SQLAlchemy
connection_url = f"mysql+pymysql://{user}:{password}@{host}/{db}"
engine = create_engine(connection_url)

# Ruta del CSV en el volumen montado (se espera que montes ./data en /mysql_project/data)
csv_path = "/mysql_project/data/penguins_lter.csv"

if os.path.exists(csv_path):
    print(f"Leyendo archivo CSV desde {csv_path}")
    df = pd.read_csv(csv_path)
    # Crear o reemplazar la tabla 'penguins_original' en la base de datos
    df.to_sql('penguins_original', con=engine, if_exists='replace', index=False)
    print("Tabla 'penguins_original' creada exitosamente en MySQL.")
else:
    print(f"Archivo {csv_path} no encontrado. Verifica que exista en el volumen montado.")
