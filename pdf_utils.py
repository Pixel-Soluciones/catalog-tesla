"""Utilidades para la generación de PDFs con ReportLab."""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from typing import List

# Importar modelos para type hinting, si es necesario acceder a atributos específicos
import models # Accederemos como models.Producto

# Estilos (se podrían personalizar más)
STYLES = getSampleStyleSheet()
STYLE_NORMAL = STYLES['Normal']
STYLE_HEADING1 = STYLES['h1']
STYLE_HEADING2 = STYLES['h2']
STYLE_SMALL = getSampleStyleSheet()['Normal']
STYLE_SMALL.fontSize = 8
STYLE_SMALL.leading = 10 # Espacio entre líneas para texto pequeño

def generar_elemento_producto(producto_obj: models.Producto) -> List:
    """
    Crea los elementos de ReportLab para un solo producto (objeto SQLAlchemy).
    """
    elementos_producto = []

    # Nombre del producto
    elementos_producto.append(Paragraph(producto_obj.nombre or 'Nombre no disponible', STYLE_HEADING2))
    elementos_producto.append(Spacer(1, 0.1*inch))

    # --- SECCIÓN DE IMAGEN COMENTADA TEMPORALMENTE (COMO ESTABA ANTES) ---
    # imagen_flowable = None
    # if producto_obj.imagen_url:
    #     try:
    #         img_temp = Image(producto_obj.imagen_url, width=1.5*inch, height=1.5*inch, kind='bound')
    #         img_temp.hAlign = 'LEFT'
    #         imagen_flowable = img_temp
    #     except Exception as e:
    #         pass 
    # if imagen_flowable:
    #     elementos_producto.append(imagen_flowable)
    #     elementos_producto.append(Spacer(1, 0.1*inch))
    # else:
    #     placeholder_text = f"<i>[No se pudo cargar imagen para: {producto_obj.nombre}]</i>" 
    #     if not producto_obj.imagen_url:
    #         placeholder_text = "<i>[No hay URL de imagen]</i>"
    #     elementos_producto.append(Paragraph(placeholder_text, STYLE_SMALL))
    #     elementos_producto.append(Spacer(1, 0.05*inch))
    elementos_producto.append(Paragraph("[Imagen omitida temporalmente]", STYLE_SMALL))
    elementos_producto.append(Spacer(1, 0.1*inch))
    # --- FIN DE SECCIÓN DE IMAGEN COMENTADA ---
    
    # Marca
    if producto_obj.marca:
        elementos_producto.append(Paragraph(f"<b>Marca:</b> {producto_obj.marca.nombre}", STYLE_NORMAL))
    else:
        elementos_producto.append(Paragraph("<b>Marca:</b> N/A", STYLE_NORMAL))
    elementos_producto.append(Spacer(1, 0.05*inch))

    # Categoría y Subcategoría
    cat_text = "<b>Categoría:</b> "
    cat_text += producto_obj.categoria.nombre if producto_obj.categoria else "N/A"
    if producto_obj.subcategoria:
        cat_text += f" > {producto_obj.subcategoria.nombre}"
    elementos_producto.append(Paragraph(cat_text, STYLE_NORMAL))
    elementos_producto.append(Spacer(1, 0.05*inch))
    
    # Código de producto
    if producto_obj.codigo:
        elementos_producto.append(Paragraph(f"<b>Código:</b> {producto_obj.codigo}", STYLE_NORMAL))
        elementos_producto.append(Spacer(1, 0.05*inch))

    # Descripción
    descripcion_texto = producto_obj.descripcion or 'Descripción no disponible.'
    if len(descripcion_texto) > 150: # Acortar descripciones largas para el PDF
        descripcion_texto = descripcion_texto[:147] + "..."
    elementos_producto.append(Paragraph(descripcion_texto, STYLE_NORMAL))
    elementos_producto.append(Spacer(1, 0.1*inch))

    # Precio y Stock
    precio_stock_text = f"<b>Precio:</b> ${producto_obj.precio:.2f}" if producto_obj.precio is not None else "<b>Precio:</b> N/A"
    if producto_obj.stock is not None:
        precio_stock_text += f"  |  <b>Stock:</b> {producto_obj.stock}"
    elementos_producto.append(Paragraph(precio_stock_text, STYLE_NORMAL))
    
    # Si es destacado
    if producto_obj.destacado:
        elementos_producto.append(Spacer(1, 0.05*inch))
        elementos_producto.append(Paragraph("<i>-- Producto Destacado --</i>", STYLE_SMALL))

    elementos_producto.append(Spacer(1, 0.3*inch)) # Espacio después de cada producto
    return elementos_producto

def generar_catalogo_pdf_completo(nombre_archivo: str, productos_list_objs: List[models.Producto]):
    """
    Genera el archivo PDF del catálogo.
    """
    doc = SimpleDocTemplate(nombre_archivo, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=inch/2, bottomMargin=inch/2)
    story = []

    # Título del catálogo
    story.append(Paragraph("Catálogo de Productos", STYLE_HEADING1))
    story.append(Spacer(1, 0.3*inch))

    if not productos_list_objs:
        story.append(Paragraph("No hay productos para mostrar.", STYLE_NORMAL))
    else:
        for i, producto_obj in enumerate(productos_list_objs):
            print(f"Añadiendo producto al PDF: {producto_obj.nombre}")
            story.extend(generar_elemento_producto(producto_obj))
            if (i + 1) % 4 == 0 and (i+1) < len(productos_list_objs):
                 story.append(PageBreak())

    print(f"Construyendo PDF: {nombre_archivo}...")
    try:
        doc.build(story)
        print(f"PDF '{nombre_archivo}' generado exitosamente.")
    except Exception as e:
        print(f"Error al generar el PDF: {e}")
        # Considerar relanzar la excepción o manejarla de forma más específica si es necesario 