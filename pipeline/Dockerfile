FROM python:3.9

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de dependencias
COPY requirements.txt ./

# Actualiza pip e instala las dependencias
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia el archivo principal de la API
COPY main.py ./

# Expone el puerto 80 (interno del contenedor)
EXPOSE 80

# Comando para iniciar la API con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
