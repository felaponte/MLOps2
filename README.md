### Taller 1 - MLOps PUJ

Este proyecto implementa un modelo de predicción de la masa corporal de pingüinos usando FastAPI para la API y Docker para contenerizar la aplicación. Se incluyen las etapas de preprocesamiento, entrenamiento y despliegue del modelo.

## Estructura del Proyecto

```
MLOps_PUJ/
│── FastAPI/                 # Código de la API en FastAPI
│── Docker/                  # Archivos relacionados con Docker
│── modelo_entrenado.pkl     # 1° Modelo Random Forest Regressor entrenado 
|── modelo_rf.pkl            # 2° Modelo Random Forest entrenado después de prerpocesamiento
│── modelo_gb.pkl            # 2° Modelo Gradient Boosting entrenado después de prerpocesamiento
│── train.py                 # Script de entrenamiento del modelo
│── preprocesamiento.py      # Preprocesamiento de datos
│── api.py                   # Implementación de la API con FastAPI
│── requirements.txt         # Dependencias necesarias
│── Dockerfile               # Dockerfile para contenerizar la API
│── X_train.csv / y_train.csv # Datos de entrenamiento
│── X_test.csv / y_test.csv   # Datos de prueba
│── README.md                # Documentación del proyecto
```
# Tecnologías Utilizadas

- Python 3.9
- FastAPI
- Scikit-Learn
- Joblib
- Pandas & NumPy
- Docker

---
# Desarrollo del taller

## 1. Clonar el Repositorio
Se clonó el repositorio original donde se encontraba la estructura base del taller
```
git clone https://github.com/CristianDiazAlvarez/MLOPS_PUJ.git
cd MLOPS_PUJ/Niveles/0
```
## 2. Preparación del entorno
Se configuró un ambiente virtual en conda
```
conda create --name mlops python=3.9 -y
conda activate mlops
```
- Se crea un entorno llamado mlops con Python 3.9.
- Se activa el entorno para instalar dependencias sin afectar el sistema

## 3. Instalación de dependencias
Dentro del entorno virtual, se instalaron las librerías necesarias:
pip install -r requirements.txt
- Se usó un archivo requirements.txt para instalar las librerías necesarias como FastAPI, scikit-learn, numpy, etc.
- Esto garantiza que el entorno tenga las mismas dependencias en cualquier máquina.

## 4. Preprocesamiento de Datos

- Se cargó el dataset penguins_lter.csv
- Se manejaron valores nulos y se realizó One-Hot Encoding para variables categóricas.
- Se dividieron los datos en entrenamiento y prueba.

## 5. Entrenamiento del Modelo

- Se probaron varios modelos: RandomForestRegressor y GradientBoostingRegressor.
- Se evaluaron con RMSE, seleccionando el mejor modelo (modelo_entrenado.pkl).

## 6. Creación de la API con FastAPI

Se definió la API con FastAPI, exponiendo un endpoint POST /predict.
```
@app.post("/predict")
def predict(data: InputData):
    resultado = modelo.predict([[data.Culmen_Length_mm, data.Culmen_Depth_mm, data.Flipper_Length_mm]])
    return {"predicted_body_mass": resultado[0]}
```
## 7. Dockerización de la API
Se creó un Dockerfile con la siguiente configuración:
```
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8989"]
```
Se construyo la imagen y se ejecutó el contenedor:

## 8. Construir la imagen Docker
```sh
docker build -t mi-api-pinguinos .
```
## 9. Ejecutar el contenedor
```sh
docker run -p 8989:8989 --name contenedor-api mi-api-pinguinos
```
## 10. Uso de la API
- Se verificó la API en http://localhost:8989
- Se probó una predicción con curl:
curl -X 'POST' 'http://localhost:8989/predict' \
     -H 'Content-Type: application/json' \
     -d '{"Culmen_Length_mm": 45.3, "Culmen_Depth_mm": 17.5, "Flipper_Length_mm": 200}'

  Ejemplo de respuesta:
```json
{"predicted_body_mass": 3814.5}
```
## 11. Subida a GitHub

Se configuró el repositorio y se creó la rama taller_1 para no afectar main

## 12. Conclusiones

- Se logró implementar una API funcional para predecir la masa corporal de los pingüinos.
- Se desplegó en un contenedor Docker y se verificó su funcionamiento.