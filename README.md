# Proyecto Generador de Catálogo de Productos en PDF

Este proyecto permite generar un catálogo de productos en formato PDF a partir de una base de datos PostgreSQL, utilizando Python, SQLAlchemy, Alembic para migraciones, y ReportLab para la generación del PDF.

## Requisitos Previos

*   **Python:** Versión 3.8 o superior.
*   **Pip:** El gestor de paquetes de Python.
*   **Docker y Docker Compose:** Para ejecutar la base de datos PostgreSQL en un contenedor. Asegúrate de que Docker Desktop (o tu motor de Docker) esté en ejecución.
*   **Git:** Para clonar el repositorio (si aplica).

## 1. Configuración Inicial del Proyecto

### 1.1. Clonar el Repositorio (Opcional)
Si has obtenido el código como un archivo zip, descomprímelo. Si es un repositorio Git:
```bash
git clone <url_del_repositorio>
cd <nombre_del_directorio_del_proyecto>
```

### 1.2. Crear un Entorno Virtual (Recomendado)
Es una buena práctica trabajar dentro de un entorno virtual:
```bash
python -m venv venv
```
Activa el entorno virtual:
*   En Windows (cmd): `venv\Scripts\activate`
*   En Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
*   En macOS/Linux: `source venv/bin/activate`

### 1.3. Instalar Dependencias
Instala todas las librerías necesarias listadas en `requirements.txt`:
```bash
pip install -r requirements.txt
```
Las dependencias principales incluyen:
*   `sqlalchemy`: ORM para interactuar con la base de datos.
*   `psycopg2-binary`: Adaptador de PostgreSQL para Python.
*   `alembic`: Herramienta de migración de bases de datos para SQLAlchemy.
*   `reportlab`: Librería para la creación de PDFs.
*   `Faker`: Para generar datos de prueba.

## 2. Configuración y Manejo de la Base de Datos

### 2.1. Iniciar la Base de Datos PostgreSQL con Docker
El proyecto utiliza Docker Compose para gestionar el servicio de PostgreSQL.
Asegúrate de que Docker esté en ejecución y luego ejecuta:
```bash
docker-compose up -d
```
Esto iniciará un contenedor PostgreSQL con el nombre `postgres_catalog_db`. Los datos se persistirán en un volumen de Docker llamado `postgres_data`.

**Configuración de la Conexión:**
*   La configuración de la base de datos (usuario, contraseña, host, puerto, nombre de la BD) se encuentra en `config.py` y es utilizada por la aplicación.
*   Alembic también utiliza esta configuración a través de `alembic/env.py`, que lee `DATABASE_URL` desde `config.py`. El archivo `alembic.ini` tiene una URL de fallback, pero la de `config.py` tiene precedencia.
*   Por defecto, las credenciales son:
    *   Usuario: `catalog_user`
    *   Contraseña: `password`
    *   Base de datos: `catalog_db`
    *   Host: `localhost`
    *   Puerto: `5432`

### 2.2. Aplicar Migraciones de la Base de Datos
Una vez que la base de datos esté en ejecución, necesitas crear la estructura de tablas. Alembic gestiona esto.
Para aplicar todas las migraciones y llevar la base de datos a su estado más reciente:
```bash
# En PowerShell, si tienes problemas de codificación con alembic.ini:
# $env:ALEMBIC_INI_ENCODING='utf-8' 
python -m alembic upgrade head
```
Esto creará las tablas `marcas`, `categorias`, `subcategorias`, y `productos` en tu base de datos `catalog_db`.

### 2.3. Poblar la Base de Datos con Datos Semilla (Opcional)
Para llenar la base de datos con datos de ejemplo generados por Faker, ejecuta el script `seed_db.py`:
```bash
python seed_db.py
```
El script te preguntará si deseas limpiar los datos existentes antes de insertar nuevos registros. Esto es útil para comenzar con un conjunto de datos limpio cada vez.

## 3. Generación del Catálogo PDF

Para generar el catálogo en PDF con los datos actuales de la base de datos, ejecuta el script principal:
```bash
python main.py
```
El archivo PDF generado se guardará en la raíz del proyecto. El nombre del archivo por defecto es `catalogo_productos_final.pdf`, según se define en `config.py` (`PDF_FILENAME`).

## 4. Modificación y Desarrollo

### 4.1. Modificar los Modelos de Datos
Si necesitas cambiar la estructura de la base de datos (por ejemplo, añadir una nueva tabla o una columna a una tabla existente):
1.  **Edita los modelos:** Realiza los cambios necesarios en las clases definidas en `models.py`.
2.  **Genera una nueva migración:** Una vez que hayas modificado los modelos, Alembic puede generar automáticamente un script de migración que refleje estos cambios.
    ```bash
    # $env:ALEMBIC_INI_ENCODING='utf-8' # Si es necesario en PowerShell
    python -m alembic revision --autogenerate -m "Un mensaje descriptivo de tus cambios"
    ```
    Esto creará un nuevo archivo de script en la carpeta `alembic/versions/`.
3.  **Revisa el script de migración:** Es **crucial** revisar el script generado para asegurarte de que los cambios son los que esperas. Alembic hace un buen trabajo, pero siempre es bueno verificar.
4.  **Aplica la nueva migración:**
    ```bash
    # $env:ALEMBIC_INI_ENCODING='utf-8' # Si es necesario en PowerShell
    python -m alembic upgrade head
    ```

### 4.2. Configurar y Personalizar el PDF
La lógica para la generación del PDF se encuentra principalmente en `pdf_utils.py`.

*   **Contenido y Estructura:** La función `generar_pdf_catalogo` en `pdf_utils.py` es el punto de partida. Aquí se define cómo se recuperan los datos, cómo se itera sobre ellos y qué información de cada producto se incluye.
*   **Estilos:** ReportLab permite una personalización detallada de estilos (fuentes, tamaños, colores, márgenes, etc.). Puedes definir y aplicar `ParagraphStyle` para los textos, configurar `TableStyle` para las tablas, y controlar el layout general usando Platypus Flowables (como `Paragraph`, `Image`, `Table`, `Spacer`, `PageBreak`).
    *   Busca dentro de `pdf_utils.py` cómo se definen los estilos y se aplican a los elementos del PDF.
*   **Imágenes:** Actualmente, el manejo de imágenes desde URLs externas puede ser problemático y está comentado. Si deseas incluir imágenes, deberás:
    1.  Asegurarte de que las URLs de las imágenes sean válidas y accesibles.
    2.  Descomentar y ajustar la lógica de descarga o incrustación de imágenes en `pdf_utils.py`. Puede ser necesario usar la librería `requests` para descargar imágenes y luego pasarlas a ReportLab, o manejar errores si las imágenes no se pueden cargar.
*   **Nombre del archivo PDF:** Se puede cambiar modificando la variable `PDF_FILENAME` en `config.py`.
*   **Plantilla y Layout:** Para cambios más avanzados en el layout (cabeceras, pies de página, numeración), puedes explorar las capacidades de `canvas` de ReportLab o usar plantillas de página (`PageTemplate`) dentro del `BaseDocTemplate`.

## 5. Solución de Problemas Comunes

*   **Error `ModuleNotFoundError`:** Asegúrate de tener el entorno virtual activado y de haber instalado todas las dependencias con `pip install -r requirements.txt`.
*   **Error de conexión a la base de datos (`OperationalError`):**
    *   Verifica que el contenedor Docker de PostgreSQL (`postgres_catalog_db`) esté en ejecución (`docker ps`). Si no, inícialo con `docker-compose up -d`.
    *   Confirma que la configuración en `config.py` (host, puerto, usuario, contraseña, nombre de la BD) sea correcta y coincida con la configuración de tu servicio PostgreSQL.
*   **Alembic: `Target database is not up to date` o `Can't locate revision identified by ...`:**
    *   Esto usualmente significa una inconsistencia entre los scripts de migración en tu sistema de archivos (`alembic/versions/`) y el estado registrado en la tabla `alembic_version` de la base de datos.
    *   Asegúrate de aplicar todas las migraciones (`python -m alembic upgrade head`) antes de generar una nueva.
    *   En casos extremos, si estás seguro de que quieres empezar de cero con las migraciones (¡esto puede implicar pérdida de datos si la BD no está vacía!), podrías necesitar:
        1.  Eliminar todos los archivos en `alembic/versions/`.
        2.  Eliminar o truncar la tabla `alembic_version` en tu base de datos.
        3.  Generar una nueva revisión inicial: `python -m alembic revision --autogenerate -m "Creacion inicial"`.
        4.  Aplicarla: `python -m alembic upgrade head`.
*   **Alembic: Problemas de codificación en Windows/PowerShell (`UnicodeDecodeError` al leer `alembic.ini`):**
    *   Ejecuta los comandos de Alembic precedidos por `$env:ALEMBIC_INI_ENCODING='utf-8'; `, por ejemplo:
        `$env:ALEMBIC_INI_ENCODING='utf-8'; python -m alembic upgrade head`
    *   Alternativamente, asegúrate de que `alembic.ini` esté guardado con codificación UTF-8.

## 6. Detener la Base de Datos
Para detener el contenedor de PostgreSQL:
```bash
docker-compose down
```
Si solo quieres detenerlo sin eliminar los recursos (para un reinicio rápido después):
```bash
docker-compose stop db 
```
Y para iniciarlo de nuevo:
```bash
docker-compose start db
```

---
Esta documentación debería ayudarte a poner en marcha y trabajar con el proyecto. 