FROM apache/airflow:2.6.0

USER root
# Instalar curl y certificados necesarios para descargar UV
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && apt-get clean

#------------------------------------INSTALL UV---------------------------------------
# Descargar el instalador de UV
ADD https://astral.sh/uv/install.sh /uv-installer.sh
# Ejecutar el instalador y removerlo
RUN sh /uv-installer.sh && rm /uv-installer.sh
# Asegurar que UV esté en el PATH
ENV PATH="/root/.local/bin/:$PATH"
#-------------------------------------------------------------------------------------

# Inicializar un proyecto UV en el directorio /ml_project
RUN uv init /ml_project

WORKDIR /ml_project

# Copiar el archivo de dependencias y los DAGs
COPY requirements.txt .
COPY dags/ ./dags/

# Instalar las dependencias definidas en requirements.txt usando UV
RUN uv add -r requirements.txt

# Cambiar al usuario airflow (el de la imagen oficial)
USER airflow

# La imagen oficial define su entrypoint para iniciar Airflow (scheduler, webserver, etc.)
