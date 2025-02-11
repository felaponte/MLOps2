import pandas as pd

# Cargar el dataset
df = pd.read_csv('penguins_lter.csv')

# Mostrar las primeras filas
print("\n Primeras filas del dataset:")
print(df.head())

# Verificar columnas
print("\n Columnas del dataset:")
print(df.columns)

# Revisar valores nulos
print("\n Valores nulos en cada columna:")
print(df.isnull().sum())

# Mostrar estadísticas del dataset
print("\n Estadísticas del dataset:")
print(df.describe())
