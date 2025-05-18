import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
import joblib
import pandas as pd

# Cargar el dataset
df = pd.read_csv("penguins_lter.csv")

# Convertir "Date Egg" a día del año (1 a 365), manejando posibles NaN
df["Date Egg"] = pd.to_datetime(df["Date Egg"], errors="coerce").dt.dayofyear
df["Date Egg"].fillna(df["Date Egg"].median(), inplace=True)  # Rellenar con la mediana

# Eliminar columnas irrelevantes
df.drop(columns=["studyName", "Sample Number", "Individual ID", "Comments"], inplace=True)

# Manejar valores nulos en columnas numéricas (rellenar con la media)
num_cols = ["Culmen Length (mm)", "Culmen Depth (mm)", "Flipper Length (mm)", "Body Mass (g)", "Delta 15 N (o/oo)", "Delta 13 C (o/oo)"]
for col in num_cols:
    df[col].fillna(df[col].mean(), inplace=True)

# Manejar valores nulos en columnas categóricas (rellenar con "Desconocido")
cat_cols = ["Species", "Region", "Island", "Stage", "Clutch Completion", "Sex"]
for col in cat_cols:
    df[col].fillna("Desconocido", inplace=True)

# Convertir variables categóricas en numéricas (One-Hot Encoding)
df = pd.get_dummies(df, columns=cat_cols, drop_first=True)

# Separar variables predictoras (X) y la variable objetivo (y)
X = df[["Culmen Length (mm)", "Culmen Depth (mm)", "Flipper Length (mm)"]]  # Solo columnas relevantes
y = df["Body Mass (g)"]

# Dividir en conjunto de entrenamiento y prueba (80%-20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Cargar los datos preprocesados
y_train = y_train.values.ravel()  # Convertir a 1D
y_test = y_test.values.ravel()

# Entrenar el modelo RandomForestRegressor
print("\n Entrenando RandomForestRegressor...")
rf_model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
rf_model.fit(X_train, y_train)

# Hacer predicciones
y_pred_rf = rf_model.predict(X_test)

# Calcular RMSE
rmse_rf = mean_squared_error(y_test, y_pred_rf) ** 0.5  # Raíz cuadrada para obtener RMSE
print(f" RMSE (Random Forest): {rmse_rf}")

# Guardar el modelo
joblib.dump(rf_model, "app/model.pkl")


# # Entrenar el modelo GradientBoostingRegressor
# print("\n Entrenando GradientBoostingRegressor...")
# gb_model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)
# gb_model.fit(X_train, y_train)

# # Hacer predicciones
# y_pred_gb = gb_model.predict(X_test)

# # Calcular RMSE
# rmse_gb = mean_squared_error(y_test, y_pred_gb)**0.5
# print(f" RMSE (Gradient Boosting): {rmse_gb}")

# # Guardar el modelo
# joblib.dump(gb_model, "modelo_gb.pkl")

# # Comparar resultados
# print("\n Comparación de Modelos:")
# print(f" RMSE Random Forest: {rmse_rf}")
# print(f" RMSE Gradient Boosting: {rmse_gb}")

# if rmse_gb < rmse_rf:
#     print("\n ¡Gradient Boosting es mejor! Usaremos `modelo_gb.pkl`")
# else:
#     print("\n ¡Random Forest es mejor! Usaremos `modelo_rf.pkl`")
