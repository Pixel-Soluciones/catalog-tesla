"""Funciones CRUD (Create, Read, Update, Delete) para la base de datos."""

from sqlalchemy.orm import Session, joinedload
from typing import List

import models # Importar todos los modelos para evitar importaciones circulares y para referencia

def obtener_productos_con_relaciones(db: Session) -> List[models.Producto]:
    """
    Obtiene la lista de todos los productos de la base de datos con sus relaciones 
    (marca, categoría, subcategoría) cargadas eficientemente.
    """
    print("Obteniendo todos los productos con sus relaciones...")
    try:
        productos = (
            db.query(models.Producto)
            .options(
                joinedload(models.Producto.marca),
                joinedload(models.Producto.categoria),
                joinedload(models.Producto.subcategoria)
            )
            .order_by(models.Producto.id) # Opcional: ordenar los productos
            .all()
        )
        print(f"Se encontraron {len(productos)} productos.")
        return productos
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        return []

# Aquí se podrían añadir más funciones CRUD en el futuro:
# def obtener_producto_por_id(db: Session, producto_id: int) -> models.Producto | None:
#     ...
# def crear_producto(db: Session, producto_data: dict) -> models.Producto:
#     ...
# def actualizar_producto(db: Session, producto_id: int, producto_data: dict) -> models.Producto | None:
#     ...
# def eliminar_producto(db: Session, producto_id: int) -> bool:
#     ... 