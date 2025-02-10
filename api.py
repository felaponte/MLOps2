from fastapi import FastAPI
import joblib
import pandas as pd
from pydantic import BaseModel

# Cargar el modelo entrenado
modelo = joblib.load("modelo_entrenado.pkl")

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
def predict(data: InputData):
    # Convertir los datos de entrada en un DataFrame y asegurarse de que coinciden con el modelo
    df = pd.DataFrame([data.dict()])

    # Renombrar columnas para que coincidan con `train.py`
    df = df.rename(columns={
        "Culmen_Length_mm": "Culmen Length (mm)",
        "Culmen_Depth_mm": "Culmen Depth (mm)",
        "Flipper_Length_mm": "Flipper Length (mm)"
    })

    # Hacer la predicción
    prediction = modelo.predict(df)[0]

    return {"predicted_body_mass": prediction}
