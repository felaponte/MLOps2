from fastapi import FastAPI, HTTPException, Query
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

# List all registered models using search_registered_models
registered_models = client.search_registered_models()

list_of_models=[]
# Print the names of the models
for model in registered_models:
    print(list_of_models.append(model.name))

# Crear una instancia de FastAPI
app = FastAPI()

# Definir la estructura de los datos de entrada (Deben coincidir con `train.py`)
class InputData(BaseModel):
    Elevation: float
    Aspect: float
    Slope: float
    Horizontal_Distance_To_Hydrology: float
    Vertical_Distance_To_Hydrology: float
    Horizontal_Distance_To_Roadways: float
    Hillshade_9am: float
    Hillshade_Noon: float
    Hillshade_3pm: float
    Horizontal_Distance_To_Fire_Points: float

# Ruta de prueba
@app.get("/")
def home():
    return {"message": "¡API de predicción de tipo de cubierta forestal en funcionamiento!"}

# Ruta para hacer predicciones
@app.post("/predict")
def predict(data: InputData, modelo_elegir: str = Query("-",enum=list_of_models)):
    
    if len(list_of_models)==0:
        raise HTTPException(status_code=400, detail="No hay modelos para usar.")
    
    # Convertir los datos de entrada en un DataFrame y asegurarse de que coinciden con el modelo
    df = pd.DataFrame([data.dict()])

    
    model_production_uri = "models:/{model_name}/production".format(model_name=modelo_elegir)

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(model_uri=model_production_uri)

    # Hacer la predicción
    prediction = loaded_model.predict(df.iloc[0].to_frame().T)[0]

    return {"modelo usado": modelo_elegir, "Cover_Type": prediction}
    
