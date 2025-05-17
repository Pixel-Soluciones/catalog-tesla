from faker import Faker
import random

# Importar desde los nuevos módulos
from database import SessionLocal, engine # engine para Base.metadata.create_all si fuera necesario
from models import Base, Marca, Categoria, Subcategoria, Producto

fake = Faker(['es_ES', 'en_US'])

# Configuración de la Sesión
# SessionLocal ya está definida en models.py, la importamos directamente.

def crear_marcas(db_session, cantidad=5):
    marcas_creadas = []
    nombres_marcas_existentes = {m[0] for m in db_session.query(Marca.nombre).all()}
    for _ in range(cantidad):
        nombre_marca = fake.company()
        while nombre_marca in nombres_marcas_existentes:
            nombre_marca = fake.company()
        
        marca = Marca(nombre=nombre_marca, logo_url=fake.image_url(width=100, height=100))
        db_session.add(marca)
        marcas_creadas.append(marca)
        nombres_marcas_existentes.add(nombre_marca)
    db_session.commit()
    print(f"Creadas {len(marcas_creadas)} marcas.")
    return marcas_creadas

def crear_categorias(db_session, cantidad=3):
    categorias_creadas = []
    nombres_cat_existentes = {c[0] for c in db_session.query(Categoria.nombre).all()}
    nombres_sugeridos = ["Electrónica", "Hogar y Jardín", "Moda y Accesorios", "Deportes", "Libros y Entretenimiento"]
    random.shuffle(nombres_sugeridos)

    for i in range(cantidad):
        if i < len(nombres_sugeridos):
            nombre_cat = nombres_sugeridos[i]
        else:
            nombre_cat = fake.word().capitalize() + " " + fake.word().capitalize()
        
        while nombre_cat in nombres_cat_existentes:
            nombre_cat = fake.word().capitalize() + " " + fake.word().capitalize()

        categoria = Categoria(nombre=nombre_cat, icono=fake.lexify(text="fa-??????"))
        db_session.add(categoria)
        categorias_creadas.append(categoria)
        nombres_cat_existentes.add(nombre_cat)
    db_session.commit()
    print(f"Creadas {len(categorias_creadas)} categorías.")
    return categorias_creadas

def crear_subcategorias(db_session, categorias, subcategorias_por_categoria=2):
    subcategorias_creadas = []
    for categoria_padre in categorias:
        for _ in range(subcategorias_por_categoria):
            nombre_subcat = fake.word().capitalize() + " " + fake.word().capitalize()
            subcat_existente = db_session.query(Subcategoria).filter_by(nombre=nombre_subcat, categoria_id=categoria_padre.id).first()
            if subcat_existente:
                continue
                
            subcategoria = Subcategoria(nombre=nombre_subcat, categoria_id=categoria_padre.id)
            db_session.add(subcategoria)
            subcategorias_creadas.append(subcategoria)
    db_session.commit()
    print(f"Creadas {len(subcategorias_creadas)} subcategorías.")
    return subcategorias_creadas

def crear_productos(db_session, marcas, categorias, subcategorias, cantidad_total=20):
    productos_creados = []
    codigos_producto_existentes = {p[0] for p in db_session.query(Producto.codigo).filter(Producto.codigo.isnot(None)).all()}

    for i in range(cantidad_total):
        nombre_producto = fake.catch_phrase().capitalize()
        if len(nombre_producto) > 250:
            nombre_producto = nombre_producto[:250]
            
        descripcion = fake.text(max_nb_chars=200)
        precio = round(random.uniform(5.99, 2999.99), 2)
        stock = random.randint(0, 100)
        destacado = random.choice([True, False])
        
        codigo = fake.ean(length=13)
        while codigo in codigos_producto_existentes:
            codigo = fake.ean(length=13)

        marca_elegida = random.choice(marcas) if marcas else None
        categoria_elegida = random.choice(categorias) if categorias else None
        
        subcategoria_elegida = None
        if categoria_elegida and subcategorias:
            subcategorias_validas = [s for s in subcategorias if s.categoria_id == categoria_elegida.id]
            if subcategorias_validas:
                subcategoria_elegida = random.choice(subcategorias_validas)
        
        producto = Producto(
            nombre=nombre_producto,
            descripcion=descripcion,
            precio=precio,
            marca_id=marca_elegida.id if marca_elegida else None,
            categoria_id=categoria_elegida.id if categoria_elegida else None,
            subcategoria_id=subcategoria_elegida.id if subcategoria_elegida else None,
            codigo=codigo,
            stock=stock,
            imagen_url=fake.image_url(width=640, height=480),
            destacado=destacado
        )
        if not producto.categoria_id and categoria_elegida:
             producto.categoria_id = categoria_elegida.id
        elif not producto.categoria_id:
            print(f"Advertencia: No se pudo asignar categoría al producto '{nombre_producto}'. Se saltará.")
            continue
            
        db_session.add(producto)
        productos_creados.append(producto)
        codigos_producto_existentes.add(codigo)
        
    db_session.commit()
    print(f"Creados {len(productos_creados)} productos.")
    return productos_creados

def poblar_db():
    # Crea las tablas si no existen (Alembic debería encargarse de esto, pero no hace daño para un script de seed)
    # Base.metadata.create_all(bind=engine) # Comentado ya que Alembic maneja la estructura.

    db = SessionLocal() # Crear una nueva sesión

    try:
        # Limpiar datos existentes (opcional, pero útil para un script de seed)
        # Cuidado: ¡Esto borrará todos los datos de estas tablas!
        respuesta_limpiar = input("¿Deseas limpiar los datos existentes de productos, marcas, categorías y subcategorías? (s/N): ").lower()
        if respuesta_limpiar == 's':
            print("Limpiando tablas...")
            db.query(Producto).delete()
            db.query(Subcategoria).delete()
            db.query(Categoria).delete()
            db.query(Marca).delete()
            db.commit()
            print("Tablas limpiadas.")

        # Crear datos
        marcas = crear_marcas(db, cantidad=7)
        categorias = crear_categorias(db, cantidad=4)
        subcategorias = []
        if categorias:
             subcategorias = crear_subcategorias(db, categorias, subcategorias_por_categoria=3)
        
        # Asegurarnos de tener al menos una categoría si es necesario para los productos
        if not categorias:
            print("No hay categorías, creando una categoría por defecto para los productos.")
            cat_defecto = Categoria(nombre="General", icono="fa-circle")
            db.add(cat_defecto)
            db.commit()
            categorias.append(cat_defecto)

        crear_productos(db, marcas, categorias, subcategorias, cantidad_total=20)
        
        print("\n¡Base de datos poblada exitosamente!")

    except Exception as e:
        print(f"Error al poblar la base de datos: {e}")
        db.rollback() # Revertir cambios en caso de error
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando el script para poblar la base de datos con datos de prueba...")
    poblar_db() 