from fastapi import FastAPI, HTTPException, Query
import joblib
import pandas as pd
from pydantic import BaseModel
import os

# Specify the folder you want to search
folder_path = "./data"

# List comprehension to filter for .pkl files
pkl_files = [os.path.splitext(file)[0] for file in os.listdir(folder_path) if file.endswith('.pkl')]

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
def predict(data: InputData, modelo_elegir: str = Query("-",enum=pkl_files)):
    
    if len(pkl_files)==0:
        raise HTTPException(status_code=400, detail="No hay modelos para usar.")
    
    # Convertir los datos de entrada en un DataFrame y asegurarse de que coinciden con el modelo
    df = pd.DataFrame([data.dict()])

    # Renombrar columnas para que coincidan con `train.py`
    df = df.rename(columns={
        "Culmen_Length_mm": "Culmen Length (mm)",
        "Culmen_Depth_mm": "Culmen Depth (mm)",
        "Flipper_Length_mm": "Flipper Length (mm)"
    })

    #Uso de modelo elegido
    modelo = joblib.load("./data/"+modelo_elegir+".pkl")

    # Hacer la predicción
    prediction = modelo.predict(df)[0]

    return {"modelo usado": modelo_elegir, "predicted_body_mass": prediction}
