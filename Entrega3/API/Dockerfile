# Usa una imagen base de Python
FROM python:3.9

#------------------------------------INSTALL UV---------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"
#-------------------------------------------------------------------------------------

# Inicializa un proyecto UV en el directorio 'api'
RUN uv init api

WORKDIR api

# Copia todos los archivos del proyecto dentro del contenedor
COPY . .

# Instala las dependencias definidas en requirements.txt usando UV
RUN uv add -r requirements.txt

CMD ["ls", "-l"]

