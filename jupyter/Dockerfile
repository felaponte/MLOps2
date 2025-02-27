FROM python:3.9

# Directorio de trabajo dentro del contenedor
WORKDIR /home/jovyan/work

# Copia el archivo de dependencias
COPY requirements.txt ./

# Actualiza pip e instala las dependencias
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expone el puerto 8888 (JupyterLab)
EXPOSE 8888

# Comando para iniciar JupyterLab sin token
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''"]