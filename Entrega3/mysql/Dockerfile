FROM mysql:8.0

# Instalar Python y dependencias necesarias para compilar e instalar UV
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates
#------------------------------------INSTALL UV---------------------------------------
# Descargar el instalador de UV
ADD https://astral.sh/uv/install.sh /uv-installer.sh
# Ejecutar el instalador y luego removerlo
RUN sh /uv-installer.sh && rm /uv-installer.sh
# Asegurar que UV esté en el PATH
ENV PATH="/root/.local/bin/:$PATH"
#-------------------------------------------------------------------------------------

# Inicializar un proyecto UV en el directorio /mysql_project
RUN uv init /mysql_project

# Establecer directorio de trabajo
WORKDIR /mysql_project

# Copiar todos los archivos del proyecto (script, entrypoint y dependencias)
COPY . .

# Instalar dependencias de Python utilizando UV
RUN uv add -r requirements.txt

# Dar permisos de ejecución al entrypoint personalizado
RUN chmod +x docker-entrypoint.sh

EXPOSE 3306

# Usar nuestro entrypoint personalizado para iniciar MySQL y ejecutar el script
ENTRYPOINT ["/mysql_project/docker-entrypoint.sh"]
