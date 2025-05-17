import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

# Importar Base desde database.py
from database import Base 

# DATABASE_URL, engine, SessionLocal ya no se definen aquí.

class Marca(Base):
    __tablename__ = "marcas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    logo_url = Column(String(255), nullable=True)

    productos = relationship("Producto", back_populates="marca")

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    icono = Column(String(255), nullable=True)

    subcategorias = relationship("Subcategoria", back_populates="categoria_padre")
    productos = relationship("Producto", back_populates="categoria")

class Subcategoria(Base):
    __tablename__ = "subcategorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)

    categoria_padre = relationship("Categoria", back_populates="subcategorias")
    productos = relationship("Producto", back_populates="subcategoria")

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(10, 2), nullable=False)
    
    marca_id = Column(Integer, ForeignKey("marcas.id"), nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    subcategoria_id = Column(Integer, ForeignKey("subcategorias.id"), nullable=True)
    
    codigo = Column(String(50), unique=True, nullable=True, index=True)
    stock = Column(Integer, default=0)
    imagen_url = Column(String(255), nullable=True)
    destacado = Column(Boolean, default=False)
    
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizado = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    marca = relationship("Marca", back_populates="productos")
    categoria = relationship("Categoria", back_populates="productos")
    subcategoria = relationship("Subcategoria", back_populates="productos")

# No es necesario if __name__ == "__main__": para crear tablas aquí,
# Alembic y el script de seed se encargan de ello. 