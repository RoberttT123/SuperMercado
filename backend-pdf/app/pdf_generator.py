from fpdf import FPDF

def crear_pdf_venta(items, total, numero, cliente):
    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Almacen Gloria", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Nota de Venta: {numero}", ln=True, align='C')
    pdf.cell(0, 10, f"Cliente: {cliente}", ln=True)
    pdf.line(10, 35, 200, 35) # Línea divisoria
    
    # Encabezados de tabla
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(80, 10, "Producto", border=1)
    pdf.cell(30, 10, "Cant.", border=1)
    pdf.cell(40, 10, "Precio", border=1)
    pdf.cell(40, 10, "Subtotal", border=1, ln=True)
    
    # Items
    pdf.set_font("Arial", size=10)
    for item in items:
        # Aquí asumo que 'item' es un diccionario con keys: nombre, cantidad, precio, subtotal
        pdf.cell(80, 10, str(item['nombre']), border=1)
        pdf.cell(30, 10, str(item['cantidad']), border=1)
        pdf.cell(40, 10, f"Bs. {float(item['precio_unitario']):.2f}", border=1)
        pdf.cell(40, 10, f"Bs. {float(item['subtotal']):.2f}", border=1, ln=True)
    
    # Total
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(150, 10, "TOTAL", border=1, align='R')
    pdf.cell(40, 10, f"Bs. {float(total):.2f}", border=1, ln=True)
    
    # Retornamos los bytes en vez de guardar en disco
    # Usamos latin-1 para compatibilidad con caracteres como ñ o tildes
    return pdf.output(dest='S').encode('latin-1')