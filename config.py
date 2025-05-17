"""Configuraciones de la Aplicación"""

import os

# Configuración de la Base de Datos
# Se podría usar os.getenv para leer de variables de entorno en producción
DB_USER = os.getenv("DB_USER", "catalog_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password") # Asegúrate que coincida con docker-compose.yml
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "catalog_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configuración del PDF
PDF_FILENAME = "catalogo_productos_final.pdf"

# Otras configuraciones
IMG_DIR = "img" 