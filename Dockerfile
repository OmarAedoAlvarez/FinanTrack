# Usa una imagen base oficial de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de tu proyecto al contenedor
COPY . /app/

# Instalar las dependencias del proyecto
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exponer el puerto 8000 para acceder a la aplicación Django
EXPOSE 8000

# Ejecutar el servidor de desarrollo de Django cuando el contenedor se inicie
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
