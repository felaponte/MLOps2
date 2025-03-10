#!/bin/bash
# Iniciar MySQL en background utilizando el entrypoint original
/usr/local/bin/docker-entrypoint.sh mysqld &

# Esperar a que MySQL esté disponible
until mysqladmin ping -h 127.0.0.1 --silent; do
    echo "Esperando a que MySQL inicie..."
    sleep 2
done

echo "MySQL está listo. Ejecutando script de inicialización..."

# Ejecutar el script de inicialización usando UV
uv run python3 /mysql_project/init_table.py

# Esperar al proceso de mysqld para mantener el contenedor activo
wait
