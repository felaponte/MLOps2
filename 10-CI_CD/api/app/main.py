from fastapi import FastAPI, HTTPException, Query, Response
import joblib
import pandas as pd
from pydantic import BaseModel
import os
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.concurrency import run_in_threadpool      # Alias de anyio.to_thread.run_sync

# # Cargar ambos modelos
# modelos = {
#     "gradient_boosting": joblib.load("modelo_gb.pkl"),
#     "random_forest": joblib.load("modelo_rf.pkl"),
# }

# Crear una instancia de FastAPI
app = FastAPI()

# Métricas Prometheus
REQUEST_COUNT = Counter('predict_requests_total', 'Total de peticiones de predicción')
REQUEST_LATENCY = Histogram('predict_latency_seconds', 'Tiempo de latencia de predicción')

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
async def predict(data: InputData):
    import time
    import random
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        
        #Uso de modelo elegido
        model = joblib.load("model.pkl")
        if model is None:
            raise HTTPException(status_code=404, detail=f"Modelo '{model}' no disponible.")

        df = pd.DataFrame([data.dict()])
            # Renombrar columnas para que coincidan con `train.py`
        df = df.rename(columns={
            "Culmen_Length_mm": "Culmen Length (mm)",
            "Culmen_Depth_mm": "Culmen Depth (mm)",
            "Flipper_Length_mm": "Flipper Length (mm)"
        })
        pred = await run_in_threadpool(model.predict, df)

    return {"predicted_body_mass": pred[0]}
    
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)