"""Punto de entrada principal para la aplicación de generación de catálogos."""

import os

# Importar configuraciones y utilidades necesarias
from config import PDF_FILENAME, IMG_DIR
from database import SessionLocal, get_db # Usaremos SessionLocal directamente o get_db si se prefiere como dependencia
import crud
import pdf_utils

def run_catalog_generation():
    """
    Orquesta la generación del catálogo de productos.
    """
    print("Iniciando generador de catálogos...")
    
    # Crear sesión de base de datos
    # Opción 1: Usar SessionLocal directamente
    db = SessionLocal()
    
    # Opción 2: Usar el generador get_db (más común con FastAPI, pero usable aquí)
    # db_generator = get_db()
    # db = next(db_generator)

    productos_con_relaciones = []
    try:
        # 1. Obtener productos de la base de datos
        productos_con_relaciones = crud.obtener_productos_con_relaciones(db)
    except Exception as e:
        print(f"Error durante la obtención de datos: {e}")
        # Considerar si se debe continuar o no
    finally:
        db.close() # Asegurarse de cerrar la sesión

    if productos_con_relaciones:
        # 2. Generar PDF
        pdf_utils.generar_catalogo_pdf_completo(PDF_FILENAME, productos_con_relaciones)
    else:
        print("No se encontraron productos para generar el catálogo o la conexión/consulta falló.")

if __name__ == "__main__":
    # Crear directorio de imágenes si no existe (si se planea usar imágenes locales)
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)
        print(f"Directorio '{IMG_DIR}' creado/verificado (para imágenes locales).")

    run_catalog_generation() 