# Usa una imagen base de Python
FROM python:3.9

# Copia todos los archivos del proyecto dentro del contenedor
COPY . .

# Instala las dependencias de Python desde requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Comando para ejecutar la API con Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8989"]

