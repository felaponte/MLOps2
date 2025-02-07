import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
import joblib

# 📌 Cargar los datos preprocesados
X_train = pd.read_csv("X_train.csv")
X_test = pd.read_csv("X_test.csv")
y_train = pd.read_csv("y_train.csv").values.ravel()  # Convertir a 1D
y_test = pd.read_csv("y_test.csv").values.ravel()

# 📌 Entrenar el modelo RandomForestRegressor
print("\n🌲 Entrenando RandomForestRegressor...")
rf_model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
rf_model.fit(X_train, y_train)

# 📌 Hacer predicciones
y_pred_rf = rf_model.predict(X_test)

# 📌 Calcular RMSE
rmse_rf = mean_squared_error(y_test, y_pred_rf) ** 0.5  # Raíz cuadrada para obtener RMSE
print(f"📊 RMSE (Random Forest): {rmse_rf}")

# 📌 Guardar el modelo
joblib.dump(rf_model, "modelo_rf.pkl")


# 📌 Entrenar el modelo GradientBoostingRegressor
print("\n🚀 Entrenando GradientBoostingRegressor...")
gb_model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)
gb_model.fit(X_train, y_train)

# 📌 Hacer predicciones
y_pred_gb = gb_model.predict(X_test)

# 📌 Calcular RMSE
rmse_gb = mean_squared_error(y_test, y_pred_gb)**0.5
print(f"📊 RMSE (Gradient Boosting): {rmse_gb}")

# 📌 Guardar el modelo
joblib.dump(gb_model, "modelo_gb.pkl")

# 📌 Comparar resultados
print("\n📌 Comparación de Modelos:")
print(f"✅ RMSE Random Forest: {rmse_rf}")
print(f"✅ RMSE Gradient Boosting: {rmse_gb}")

if rmse_gb < rmse_rf:
    print("\n🏆 ¡Gradient Boosting es mejor! Usaremos `modelo_gb.pkl`")
else:
    print("\n🏆 ¡Random Forest es mejor! Usaremos `modelo_rf.pkl`")
