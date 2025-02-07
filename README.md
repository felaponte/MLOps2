### Taller 1 - MLOps PUJ

Este proyecto implementa un modelo de predicción de la masa corporal de pingüinos usando FastAPI para la API y Docker para contenerizar la aplicación. Se incluyen las etapas de preprocesamiento, entrenamiento y despliegue del modelo.

## Estructura del Proyecto

```
MLOps_PUJ/
│── FastAPI/                 # Código de la API en FastAPI
│── Docker/                  # Archivos relacionados con Docker
│── modelo_rf.pkl            # Modelo Random Forest entrenado
│── modelo_gb.pkl            # Modelo Gradient Boosting entrenado
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

## Instalación y Configuración

### Clonar el repositorio
```sh
git clone -b mi-version https://github.com/felaponte/MLOps2.git
cd MLOps2
```

### Configurar el entorno virtual (opcional)
```sh
python -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate     # En Windows
```

### Instalar dependencias
```sh
pip install -r requirements.txt
```

---

## Ejecución con Docker

### 1. Construir la imagen Docker
```sh
docker build -t mi-api-pinguinos .
```

### 2. Ejecutar el contenedor
```sh
docker run -p 8989:8989 --name contenedor-api mi-api-pinguinos
```

---

## Uso de la API

### 1️. Verificar el estado de la API
Abre en el navegador:
```
http://localhost:8989/
```
Debe responder:
```json
{"message":"¡API de predicción de pingüinos en funcionamiento!"}
```

### 2️. Hacer una predicción
Ejecuta en la terminal:
```sh
curl -X 'POST'
  'http://localhost:8989/predict'
  -H 'accept: application/json'
  -H 'Content-Type: application/json'
  -d '{
  "Culmen_Length_mm": 45.3,
  "Culmen_Depth_mm": 17.5,
  "Flipper_Length_mm": 200
}'
```

Ejemplo de respuesta:
```json
{"predicted_body_mass": 3814.5}
```

---

## Depuración
Si el contenedor no funciona correctamente, revisa los logs:
```sh
docker logs contenedor-api
```

---

## Contribuciones
Si deseas mejorar este proyecto, crea una **pull request** en la rama `mi-version`.

---


 


