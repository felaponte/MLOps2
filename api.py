from fastapi import FastAPI, HTTPException, Query
import joblib
import pandas as pd
from pydantic import BaseModel

# Cargar ambos modelos
modelos = {
    "gradient_boosting": joblib.load("modelo_gb.pkl"),
    "random_forest": joblib.load("modelo_rf.pkl"),
}

# Crear una instancia de FastAPI
app = FastAPI()

# Definir la estructura de los datos de entrada (Deben coincidir con `train.py`)
class InputData(BaseModel):
    Culmen_Length_mm: float
    Culmen_Depth_mm: float
    Flipper_Length_mm: float

# Ruta de prueba
@app.get("/")
def home():
    return {"message": "¡API de predicción de pingüinos en funcionamiento!"}

# Ruta para hacer predicciones
@app.post("/predict")
def predict(data: InputData, modelo_elegir: str = Query("gradient_boosting", enum=["gradient_boosting", "random_forest"])):
    
    if modelo_elegir not in modelos:
        raise HTTPException(status_code=400, detail="Invalid model type. Choose 'gradient_boosting' or 'random_forest'.")
    
    # Convertir los datos de entrada en un DataFrame y asegurarse de que coinciden con el modelo
    df = pd.DataFrame([data.dict()])

    # Renombrar columnas para que coincidan con `train.py`
    df = df.rename(columns={
        "Culmen_Length_mm": "Culmen Length (mm)",
        "Culmen_Depth_mm": "Culmen Depth (mm)",
        "Flipper_Length_mm": "Flipper Length (mm)"
    })

    #Uso de modelo elegido

    modelo = modelos[modelo_elegir]

    # Hacer la predicción
    prediction = modelo.predict(df)[0]

    return {"modelo usado": modelo_elegir, "predicted_body_mass": prediction}
