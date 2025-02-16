# Usa una imagen base de Python
FROM python:3.9

# Copia todos los archivos del proyecto dentro del contenedor
WORKDIR /app

# Copia solo `api.py` (el código principal de la API)
COPY api.py /app/api.py

# Copia `requirements.txt` primero para optimizar la cache
COPY requirements.txt /app/requirements.txt

# Instala las dependencias de Python desde requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Comando para ejecutar la API con Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8989"]

