#!/bin/sh

# Nombre del contenedor
CONTAINER_NAME="app"

# Verificar si el contenedor ya existe y eliminarlo
if sudo podman ps -a --format "{{.Names}}" | grep -Eq "^${CONTAINER_NAME}$"; then
  echo "El contenedor '${CONTAINER_NAME}' ya existe. Eliminando..."
  sudo podman rm -f "${CONTAINER_NAME}"
fi

# Ejecutar el contenedor con los montajes y configuración de entorno
sudo podman run -it --name "${CONTAINER_NAME}" --user root \
  -v /home/sabishi/tiktok/text2speech:/app \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  localhost/freebsd-app:latest /bin/sh

