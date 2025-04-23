FROM python:3.8-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY requirements.txt /app
COPY main.py /app
COPY data.py /app
# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt
# Comando para cargar el template y luego ejecutar Streamlit
CMD ["streamlit", "run", "/app/main.py"]