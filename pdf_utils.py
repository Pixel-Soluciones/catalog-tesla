"""Utilidades para la generación de PDFs con ReportLab."""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas # Importar canvas
from reportlab.lib.colors import grey, black # Importar black y otros colores si es necesario
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

# Estilo para las entradas del índice
STYLE_INDEX_ENTRY = ParagraphStyle('IndexEntry',
                                 parent=STYLES['Normal'],
                                 fontSize=10,
                                 leading=14,
                                 spaceBefore=4,
                                 leftIndent=0.2*inch
                                 )

# --- Estilos para la tabla de producto ---
STYLE_PROD_LABEL = ParagraphStyle('ProdLabel', parent=STYLES['Normal'], fontSize=9, alignment=0) # Izquierda
STYLE_PROD_VALUE = ParagraphStyle('ProdValue', parent=STYLES['Normal'], fontSize=9, alignment=0)
STYLE_PROD_H2_TABLE = ParagraphStyle('ProdH2Table', parent=STYLES['h2'], fontSize=13, spaceBefore=0, spaceAfter=6)
STYLE_PROD_DESC = ParagraphStyle('ProdDesc', parent=STYLES['Normal'], fontSize=9, leading=11)
# --- Fin estilos para la tabla de producto ---

# --- Funciones para encabezado y pie de página ---
def header_canvas(canvas_obj, doc):
    """Dibuja el encabezado en cada página."""
    canvas_obj.saveState()
    canvas_obj.setFont('Helvetica', 10) # Puedes cambiar la fuente
    canvas_obj.setFillColor(grey) # Color gris para el texto
    
    # Texto del encabezado (a 0.4 pulgadas del borde superior de la página)
    y_text_header = doc.pagesize[1] - 0.4 * inch
    canvas_obj.drawString(doc.leftMargin, y_text_header, "Tesla SAS - Catálogo de Productos")
    
    # Línea decorativa debajo del encabezado (a 0.6 pulgadas del borde superior de la página)
    y_line_header = doc.pagesize[1] - 0.6 * inch
    canvas_obj.line(doc.leftMargin, y_line_header, 
                  doc.width + doc.leftMargin, y_line_header)
    canvas_obj.restoreState()

def footer_canvas(canvas_obj, doc):
    """Dibuja el pie de página y la numeración en cada página."""
    canvas_obj.saveState()
    canvas_obj.setFont('Helvetica', 8) # Fuente más pequeña para el pie
    canvas_obj.setFillColor(grey)
    # Pie de página "Tesla SAS"
    canvas_obj.drawString(doc.leftMargin, 0.5 * inch, "Tesla SAS")
    # Numeración de página
    page_num_text = f"Página {doc.page}"
    canvas_obj.drawRightString(doc.width + doc.leftMargin, 0.5 * inch, page_num_text)
    canvas_obj.restoreState()
# --- Fin de funciones para encabezado y pie de página ---

def generar_elemento_producto(producto_obj: models.Producto, doc) -> List:
    """
    Crea una Tabla de ReportLab para un solo producto.
    """
    
    bookmark_anchor = None
    if producto_obj.codigo:
        bookmark_anchor = f"prod_{producto_obj.codigo.replace(' ', '_')}"

    # Nombre del producto con ancla
    nombre_texto = producto_obj.nombre or 'Nombre no disponible'
    if bookmark_anchor:
        nombre_texto_render = f'<a name="{bookmark_anchor}"/>{nombre_texto}'
    else:
        nombre_texto_render = nombre_texto
    
    p_nombre = Paragraph(nombre_texto_render, STYLE_PROD_H2_TABLE)

    # --- Datos para la tabla del producto ---
    # [ (Etiqueta, Valor), (Etiqueta, Valor), ... ]
    # El valor puede ser un Paragraph o un string simple que se convertirá a Paragraph
    product_details_data = []

    # Imagen (placeholder por ahora)
    img_placeholder = Paragraph("[Imagen omitida]", STYLE_SMALL)
    # product_details_data.append([img_placeholder, ' ']) # Ocupar dos celdas, o SPAN

    # Marca
    marca_str = producto_obj.marca.nombre if producto_obj.marca else "N/A"
    product_details_data.append([Paragraph("<b>Marca:</b>", STYLE_PROD_LABEL), Paragraph(marca_str, STYLE_PROD_VALUE)])

    # Categoría y Subcategoría
    cat_text = producto_obj.categoria.nombre if producto_obj.categoria else "N/A"
    if producto_obj.subcategoria:
        cat_text += f" > {producto_obj.subcategoria.nombre}"
    product_details_data.append([Paragraph("<b>Categoría:</b>", STYLE_PROD_LABEL), Paragraph(cat_text, STYLE_PROD_VALUE)])
    
    # Código de producto
    if producto_obj.codigo:
        product_details_data.append([Paragraph("<b>Código:</b>", STYLE_PROD_LABEL), Paragraph(producto_obj.codigo, STYLE_PROD_VALUE)])

    # Descripción
    descripcion_texto = producto_obj.descripcion or 'Descripción no disponible.'
    if len(descripcion_texto) > 250: # Un poco más largo para la tabla
        descripcion_texto = descripcion_texto[:247] + "..."
    # La descripción ocupará ambas columnas
    p_descripcion = Paragraph(descripcion_texto, STYLE_PROD_DESC)
    # product_details_data.append([p_descripcion, ' ']) # Span en TableStyle

    # Precio y Stock
    precio_str = f"${producto_obj.precio:.2f}" if producto_obj.precio is not None else "N/A"
    stock_str = str(producto_obj.stock) if producto_obj.stock is not None else "N/A"
    product_details_data.append([Paragraph("<b>Precio:</b>", STYLE_PROD_LABEL), Paragraph(precio_str, STYLE_PROD_VALUE)])
    product_details_data.append([Paragraph("<b>Stock:</b>", STYLE_PROD_LABEL), Paragraph(stock_str, STYLE_PROD_VALUE)])

    # Si es destacado
    destacado_str = "<i>-- Producto Destacado --</i>" if producto_obj.destacado else ""
    p_destacado = Paragraph(destacado_str, STYLE_SMALL)
    # product_details_data.append([p_destacado, ' ']) # Span en TableStyle

    # --- Construcción de la Tabla del Producto ---
    # Primero el nombre del producto, luego la tabla de detalles, luego la descripción, luego destacado.
    # Esto es un poco más complejo que una sola tabla, podríamos anidar o usar múltiples tablas/flowables.
    # Por simplicidad inicial, intentaremos una tabla principal con SPAN.

    # Definición de la tabla de producto
    # Columna 0 para etiquetas, Columna 1 para valores
    # La imagen y descripción necesitarán SPAN
    table_data = [
        [p_nombre, None],  # Nombre del producto, ocupa 2 columnas
        [img_placeholder, None], # Placeholder imagen, ocupa 2 columnas
    ]
    table_data.extend(product_details_data) # Añadir filas de marca, categoría, código, precio, stock
    table_data.append([p_descripcion, None]) # Descripción, ocupa 2 columnas
    if producto_obj.destacado:
        table_data.append([p_destacado, None]) # Destacado, ocupa 2 columnas

    # Anchos de columna (aproximados, ajusta según necesidad)
    # La suma debe ser menor o igual al ancho disponible en la página.
    # doc.width es el ancho total del frame donde fluye el contenido.
    # Para calcular el ancho disponible: available_width = doc.width
    # (asumiendo que la tabla no tiene sus propios márgenes izquierdo/derecho significativos más allá del padding)
    # Si leftMargin y rightMargin de SimpleDocTemplate son inch/2, y pagesize es letter (8.5 inch)
    # doc.width = 8.5*inch - 2*(inch/2) = 7.5*inch.
    # Sin embargo, `doc.width` ya considera los márgenes del documento, así que podemos usarlo.
    
    # Ajustar los anchos de columna. Por ejemplo, 1.5 inch para etiquetas, resto para valores.
    # Esto necesita estar definido antes de crear la tabla si no se quiere el auto-ajuste.
    available_width = doc.width # Este es el ancho del frame de SimpleDocTemplate
    col_widths = [1.5*inch, available_width - 1.5*inch - 0.1*inch] # 0.1 para un pequeño margen

    product_table = Table(table_data, colWidths=col_widths)

    ts_product = TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        
        # Estilo para el nombre del producto (primera fila)
        ('SPAN', (0,0), (1,0)), # El nombre (p_nombre) ocupa de col 0 a col 1 en la fila 0
        ('ALIGN', (0,0), (0,0), 'CENTER'), # Centrar el nombre del producto
        ('BOTTOMPADDING', (0,0), (0,0), 10), # Más espacio después del nombre

        # Estilo para la imagen (segunda fila)
        ('SPAN', (0,1), (1,1)), # Placeholder de imagen ocupa de col 0 a col 1 en la fila 1
        ('ALIGN', (0,1), (0,1), 'CENTER'),
        ('BOTTOMPADDING', (0,1), (0,1), 6),

        # Las filas de detalles (marca, categoría, etc.) comienzan después del nombre e imagen
        # Si product_details_data tiene N items, van de fila 2 a 2+N-1
        # Las etiquetas en la primera columna, valores en la segunda.
        # ('GRID', (0,2), (-1,-1), 0.5, grey), # Grid para todas las celdas de detalles y abajo

        # Estilo para la descripción (después de los detalles)
        # Si hay N items en product_details_data, la descripción está en la fila 2+N
        # El índice de la fila de descripción será len(product_details_data) + 2 (por nombre e imagen)
        # Esta es una forma de hacerlo dinámico, pero requiere calcular 'desc_row_idx'
        # desc_row_idx = 2 + len(product_details_data)
        # ('SPAN', (0, desc_row_idx), (1, desc_row_idx)),
        # ('BOTTOMPADDING', (0, desc_row_idx), (0, desc_row_idx), 6),

        # Estilo para el destacado (última fila si existe)
        # if producto_obj.destacado:
        #     destacado_row_idx = desc_row_idx + 1
        #     ('SPAN', (0, destacado_row_idx), (1, destacado_row_idx)),
        #     ('ALIGN', (0, destacado_row_idx), (0, destacado_row_idx), colors.darkgrey),
        #     ('TOPPADDING', (0, destacado_row_idx), (0, destacado_row_idx), 6)
    ])

    # Calcular dinámicamente los SPANs para descripción y destacado
    # Fila del nombre: 0
    # Fila de la imagen: 1
    # Filas de detalles: desde 2 hasta 2 + len(product_details_data) - 1
    current_row_idx = 2 + len(product_details_data)
    
    # Span para descripción
    ts_product.add('SPAN', (0, current_row_idx), (1, current_row_idx))
    ts_product.add('BOTTOMPADDING', (0, current_row_idx), (0, current_row_idx), 6)
    current_row_idx +=1

    # Span y estilo para destacado si existe
    if producto_obj.destacado:
        ts_product.add('SPAN', (0, current_row_idx), (1, current_row_idx))
        ts_product.add('ALIGN', (0, current_row_idx), (0, current_row_idx), 'CENTER')
        # ts_product.add('TEXTCOLOR', (0, current_row_idx), (0, current_row_idx), colors.darkgrey) # No funciona bien con <p><i>
        ts_product.add('TOPPADDING', (0, current_row_idx), (0, current_row_idx), 6)

    product_table.setStyle(ts_product)
    
    # Devolver la tabla y un spacer después
    # La función generar_catalogo_pdf_completo espera una lista de flowables de esta función.
    return [product_table, Spacer(1, 0.3*inch)]

def generar_catalogo_pdf_completo(nombre_archivo: str, productos_list_objs: List[models.Producto]):
    """
    Genera el archivo PDF del catálogo.
    """
    doc = SimpleDocTemplate(nombre_archivo, pagesize=letter,
                            rightMargin=inch/2, leftMargin=inch/2,
                            topMargin=inch, # Aumentar margen superior para el encabezado
                            bottomMargin=inch) # Aumentar margen inferior para el pie

    story = []

    # --- INICIO: Generación del Índice ---
    story.append(Paragraph("Índice del Catálogo", STYLE_HEADING1))
    story.append(Spacer(1, 0.2*inch))

    if not productos_list_objs:
        story.append(Paragraph("No hay productos para mostrar en el índice.", STYLE_NORMAL))
    else:
        index_table_data = []
        
        for producto_obj in productos_list_objs:
            nombre_producto = producto_obj.nombre or "Producto sin nombre"
            # Asumimos que producto_obj.codigo es solo el número.
            # Si necesitara limpieza (ej. quitar "Código: "), se haría aquí.
            codigo_producto_num = producto_obj.codigo or "N/A" 
            
            bookmark_anchor_ref = None
            if producto_obj.codigo: # Usar producto_obj.codigo para el ancla
                bookmark_anchor_ref = f"prod_{producto_obj.codigo.replace(' ', '_')}"

            # Formato: Nombre - CODIGO_EN_AZUL
            texto_indice_contenido = f'{nombre_producto} - <font color="blue">{codigo_producto_num}</font>'

            if bookmark_anchor_ref:
                texto_indice_html = f'<a href="#{bookmark_anchor_ref}">{texto_indice_contenido}</a>'
                p_texto_indice = Paragraph(texto_indice_html, STYLE_INDEX_ENTRY)
            else:
                # Sin ancla, solo el texto formateado
                p_texto_indice = Paragraph(texto_indice_contenido, STYLE_INDEX_ENTRY)
            
            index_table_data.append([p_texto_indice]) # Una sola celda por fila
        
        if index_table_data:
            # Tabla con una sola columna, usando el ancho disponible del documento
            index_table = Table(index_table_data, colWidths=[doc.width]) 
            
            # Estilo de tabla simplificado para una sola columna
            ts_index = TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                # LEFTPADDING es 0 porque STYLE_INDEX_ENTRY ya maneja la sangría del párrafo.
                ('LEFTPADDING', (0,0), (-1,-1), 0), 
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3), # Espacio entre entradas del índice
                # ('GRID', (0,0), (-1,-1), 0.5, grey) # Descomentar para ver bordes
            ])
            index_table.setStyle(ts_index)
            story.append(index_table)
        
    story.append(PageBreak()) # Salto de página después del índice
    # --- FIN: Generación del Índice ---

    # Título del catálogo principal (opcional, podría eliminarse si el índice es suficiente)
    # story.append(Paragraph("Catálogo de Productos", STYLE_HEADING1))
    # story.append(Spacer(1, 0.3*inch))

    if not productos_list_objs:
        # Esta parte podría estar redundante si ya se manejó en el índice,
        # pero se deja por si el índice y el catálogo principal pueden tener diferentes condiciones.
        story.append(Paragraph("No hay productos para mostrar.", STYLE_NORMAL))
    else:
        for i, producto_obj in enumerate(productos_list_objs):
            print(f"Añadiendo producto al PDF: {producto_obj.nombre}")
            story.extend(generar_elemento_producto(producto_obj, doc))
            if (i + 1) % 4 == 0 and (i+1) < len(productos_list_objs):
                 story.append(PageBreak())

    print(f"Construyendo PDF: {nombre_archivo}...")
    try:
        doc.build(story, onFirstPage=lambda c, d: (header_canvas(c, d), footer_canvas(c, d)), 
                  onLaterPages=lambda c, d: (header_canvas(c, d), footer_canvas(c, d)))
        print(f"PDF '{nombre_archivo}' generado exitosamente.")
    except Exception as e:
        print(f"Error al generar el PDF: {e}")
        # Considerar relanzar la excepción o manejarla de forma más específica si es necesario 