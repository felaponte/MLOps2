import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

# 📌 Cargar el dataset
df = pd.read_csv("penguins_lter.csv")

# 📌 Convertir "Date Egg" a día del año (1 a 365), manejando posibles NaN
df["Date Egg"] = pd.to_datetime(df["Date Egg"], errors="coerce").dt.dayofyear
df["Date Egg"].fillna(df["Date Egg"].median(), inplace=True)  # Rellenar con la mediana

# 📌 Eliminar columnas irrelevantes
df.drop(columns=["studyName", "Sample Number", "Individual ID", "Comments"], inplace=True)

# 📌 Manejar valores nulos en columnas numéricas (rellenar con la media)
num_cols = ["Culmen Length (mm)", "Culmen Depth (mm)", "Flipper Length (mm)", "Body Mass (g)", "Delta 15 N (o/oo)", "Delta 13 C (o/oo)"]
for col in num_cols:
    df[col].fillna(df[col].mean(), inplace=True)

# 📌 Manejar valores nulos en columnas categóricas (rellenar con "Desconocido")
cat_cols = ["Species", "Region", "Island", "Stage", "Clutch Completion", "Sex"]
for col in cat_cols:
    df[col].fillna("Desconocido", inplace=True)

# 📌 Convertir variables categóricas en numéricas (One-Hot Encoding)
df = pd.get_dummies(df, columns=cat_cols, drop_first=True)

# 📌 Separar variables predictoras (X) y la variable objetivo (y)
X = df.drop(columns=["Body Mass (g)"])
y = df["Body Mass (g)"]

# 📌 Dividir en conjunto de entrenamiento y prueba (80%-20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 📌 Guardar los datos procesados en archivos CSV para entrenar modelos
X_train.to_csv("X_train.csv", index=False)
X_test.to_csv("X_test.csv", index=False)
y_train.to_csv("y_train.csv", index=False)
y_test.to_csv("y_test.csv", index=False)

print("✅ Preprocesamiento completo. Datos guardados.")
