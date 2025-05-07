from fastapi import FastAPI, HTTPException, Query, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.concurrency import run_in_threadpool      # Alias de anyio.to_thread.run_sync
import joblib
import pandas as pd
from pydantic import BaseModel
import os
import mlflow
from mlflow.tracking import MlflowClient
import sklearn

#--------MLFlow-----------
os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://minio:9000"
os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'
    
# connect to mlflow
mlflow.set_tracking_uri("http://mlflow-service:5000")

client = MlflowClient()


# Discover all models already registered in MLflow
list_of_models = [m.name for m in client.search_registered_models()]

if not list_of_models:        # fail fast if registry is empty
    raise RuntimeError("❌  No models found in the MLflow registry.")
    
# 2) Eager-load each model into memory *once*
MODEL_STORE = {               # dict: name ➜ PyFuncModel
    name: mlflow.pyfunc.load_model(f"models:/{name}/production")
    for name in list_of_models
}
print(f"✔  Loaded {len(MODEL_STORE)} models: {', '.join(MODEL_STORE)}")

# ───── FastAPI app ─────
app = FastAPI()

# Métricas Prometheus
REQUEST_COUNT = Counter('predict_requests_total', 'Total de peticiones de predicción')
REQUEST_LATENCY = Histogram('predict_latency_seconds', 'Tiempo de latencia de predicción')

# Definir la estructura de los datos de entrada (Deben coincidir con `train.py`)
class InputData(BaseModel):
    age: int
    admission_type_id: int
    discharge_disposition_id: int
    admission_source_id: int
    time_in_hospital: int
    num_lab_procedures: int
    num_procedures: int
    num_medications: int
    number_diagnoses: int
    diabetesMed: int
        

# ────────────────────────── Routes ──────────────────────────
@app.get("/")
def home():
    return {"message": "¡API de predicción de tipo de cubierta forestal en funcionamiento!"}


@app.get("/models")
def get_models():
    try:
        return {"models": list_of_models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Ruta para hacer predicciones
@app.post("/predict")
async def predict(
    data: InputData,
    modelo_elegir: str = Query(..., enum=list_of_models)  # only valid names
):
    import time
    import random
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        # Look up the already-loaded model
        model = MODEL_STORE.get(modelo_elegir)
        if model is None:
            raise HTTPException(status_code=404, detail=f"Modelo '{modelo_elegir}' no disponible.")

        df = pd.DataFrame([data.dict()])
        pred = await run_in_threadpool(model.predict, df)

    return {"modelo_usado": modelo_elegir, "readmitted": pred[0]}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

