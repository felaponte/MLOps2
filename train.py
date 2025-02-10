import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib  # Para guardar el modelo entrenado

# Cargar los datos desde el archivo CSV
df = pd.read_csv("penguins_lter.csv")

# Mostrar las primeras filas para revisar la estructura
print("Primeras filas del dataset:")
print(df.head())

# Verificar las columnas del dataset
print("\nColumnas del dataset:")
print(df.columns)

# Eliminar filas con valores nulos
df = df.dropna()

# Seleccionar las columnas relevantes
X = df[["Culmen Length (mm)", "Culmen Depth (mm)", "Flipper Length (mm)"]]  # Solo columnas relevantes
y = df["Body Mass (g)"]  # Variable de salida

# Dividir en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenar un modelo de Machine Learning
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluar el modelo
y_pred = model.predict(X_test)
rmse = mean_squared_error(y_test, y_pred) ** 0.5  # Raíz cuadrada para obtener RMSE
print(f"\n RMSE del modelo: {rmse}")

# Guardar el modelo entrenado
joblib.dump(model, "modelo_entrenado.pkl")
print("Modelo guardado como 'modelo_entrenado.pkl'")
