from fastapi import FastAPI
import joblib
import os

app = FastAPI()

# Ruta al modelo compartido (se supone que se encuentra en la carpeta compartida /models)
MODEL_PATH = "/models/mimodelo.pkl"

# Carga el modelo si existe
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None

@app.get("/")
def root():
    return {"message": "API de ML funcionando", "modelo_cargado": model is not None}

@app.get("/predict")
def predict(value: float):
    if model is None:
        return {"error": "Modelo no cargado"}
    prediction = model.predict([[value]])
    return {"prediction": float(prediction[0])}
