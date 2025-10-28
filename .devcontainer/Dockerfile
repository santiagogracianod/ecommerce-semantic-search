FROM mcr.microsoft.com/devcontainers/python:3.12

# Instalar herramientas adicionales necesarias
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean


RUN python3 -m pip install --upgrade pip

# Instalar dependencias del proyecto
# COPY backend/requirements.txt /tmp/requirements.txt
# RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Configuración de usuario
USER vscode