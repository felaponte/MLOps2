# Usa una imagen base de Python
FROM apache/airflow:2.6.0

# Copia el archivo de requirements (dentro del contexto del usuario airflow)
COPY requirements.txt /tmp/requirements.txt

# Instala los paquetes
RUN pip install --no-cache-dir -r /tmp/requirements.txt

CMD ["ls", "-l"]
