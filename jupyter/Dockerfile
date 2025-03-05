FROM python:3.9

# Directorio de trabajo dentro del contenedor
WORKDIR /home/jovyan/work

# Copia el archivo de dependencias
COPY requirements.txt ./

# 1) Instala dependencias base
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 2) Instala las extensiones/paquetes requeridos para Facets y Beam Interactive
RUN pip install --no-cache-dir apache-beam[interactive] facets-overview

# 3) (Opcional) Instala la extensión de ipywidgets en JupyterLab
#RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager

# Expone el puerto 8888 (JupyterLab)
EXPOSE 8888

# Comando para iniciar JupyterLab sin token
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''"]
