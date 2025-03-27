FROM python:3.9-slim

# Crear directorio de trabajo
WORKDIR /mlflow

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copiar requirements y archivos
COPY requirements.txt .

# Instalar requerimientos
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto del servidor de MLflow
EXPOSE 5000

# Comando por defecto
CMD ["mlflow", "server"]
