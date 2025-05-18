# Usa una imagen base de Python
FROM python:3.10

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de la carpeta local /app a la carpeta /app del contenedor
COPY . /app

# Instala las dependencias de Python desde requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Expone el puerto que usará la API
EXPOSE 8989

# Comando para ejecutar la API con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8989"]

