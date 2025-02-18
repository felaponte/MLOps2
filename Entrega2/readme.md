<<<<<<< HEAD

=======
### Taller 2 - MLOps PUJ

Este proyecto implementa un modelo de predicción de la masa corporal de pingüinos usando FastAPI para la API y Docker para contenerizar la aplicación. Se utilizó UV para hacer la gestión de dependencias. Y mediante Se incluyen las etapas de preprocesamiento, entrenamiento y delo.

## Estructura del Proyecto

```
Entrega2/
│── docker-compose.yaml        # Archivo de docker compose
│── README.md                  # Documentación del proyecto
│── API/                       # Carpeta con los archivos del servicio de API
│──── api.py                   # Implementación de la API con FastAPI
│──── requirements.txt         # Dependencias necesarias para la API
│──── Dockerfile               # Dockerfile para contenerizar la API
│── ML/                        # Carpeta con los archivos del servicio de ML
│──── preprocesamiento.ipynb   # Notebook de preprocesamiento de datos que generan los archivos de entrenamiento y prueba
│──── entrenar_modelos.ipynb   # Notebook de entrenamiento de modelos que generan los archivos .pkl de Random Forest y Gradient Boostng
│──── requirements.txt         # Dependencias necesarias para el modelo de ML
│──── Dockerfile               # Dockerfile para contenerizar el modelo de ML
│──── penguins_iter.csv        # Data inicial
│── data/                      # Volumen de datos NO volátiles
│──── X_train.csv & y_train.csv      # Datos de entrenamiento que son generados por el notebook preprocesamiento.ipynb
│──── X_test.csv & y_test.csv        # Datos de prueba que son generados por el notebook preprocesamiento.ipynb
|──── modelo_random_forest.pkl       # Modelo Random Forest entrenado después del preprocesamiento que es generado por el notebook entrenar_modelos.ipynb.
│──── modelo_gradient_boosting.pkl   # Modelo Gradient Boosting entrenado después del preprocesamiento que es generado por el notebook entrenar_modelos.ipynb.

```
# Tecnologías Utilizadas

- Python 3.9
- FastAPI
- Scikit-Learn
- Joblib
- Pandas & NumPy
- Docker
- Jupyter y Jupyter notebook
- UV

---
# Instrucciones

## 1. Clonar el Repositorio
Se clona el repositorio
```
git clone https://github.com/felaponte/MLOps2.git
cd MLOps2
cd Entrega2
```
## 2. Preparación del entorno
Se configuró un ambiente virtual en conda
```
conda create --name mlops python=3.9 -y
conda activate mlops
```

sudo docker compose up --build ml_service

- Se crea un entorno llamado mlops con Python 3.9.
- Se activa el entorno para instalar dependencias sin afectar el sistema

## 3. Instalación de dependencias
Dentro del entorno virtual, se instalaron las librerías necesarias:
pip install -r requirements.txt
- Se usó un archivo requirements.txt para instalar las librerías necesarias como FastAPI, scikit-learn, numpy, etc.
- Esto garantiza que el entorno tenga las mismas dependencias en cualquier máquina.

