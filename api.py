from fastapi import FastAPI, HTTPException, Query
import joblib
import pandas as pd
from pydantic import BaseModel
import os

# Directorio de volumen con los modelos 
volumen = "./volumen"

#Cargar modelos dinamicamente 
def cargar_modelos():
    modelos = {}
    for filename in os.listdir(volumen):
        if filename.endswith(".pkl"):
            model_name = filename.replace(".pkl", "")  # Remover extension
            modelos[model_name] = joblib.load(os.path.join(volumen, filename))
    return modelos

modelos = cargar_modelos()

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
    return {"message": "¡API de predicción de pingüinos en funcionamiento!", "loaded_models": list(modelos.keys())}

# Ruta para hacer predicciones
@app.post("/predict")
def predict(data: InputData, modelo_elegir: str = Query(None, enum=list(modelos.keys()))):
    
    if modelo_elegir is None:
        raise HTTPException(status_code=400, detail="Por favor especifique un modelo")
    
    if modelo_elegir not in modelos:
        raise HTTPException(status_code=400, detail="Modelo Invalido. Especifique un modelo de los disponibles : {list(modelos.keys())}")
    
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
