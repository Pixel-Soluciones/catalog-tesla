"""Configuración de la Base de Datos SQLAlchemy"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL # Importar la URL desde config.py

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Función para obtener una sesión de DB (opcional, pero puede ser útil para dependencias)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 