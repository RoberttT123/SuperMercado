"""
src/utils/helpers.py
Herramientas reutilizables: moneda, fechas, generación de códigos.
"""

from datetime import datetime, timezone, timedelta
import random
import string

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from dateutil import parser  # Importamos el parser robusto

# Zona horaria de Bolivia (UTC-4)
TZ_BOL = timezone(timedelta(hours=-4))


# ─── Moneda ───────────────────────────────────────────────────────────────────

def fmt_bs(amount: float) -> str:
    """Formatea un número como moneda boliviana. Ej: 12.5 → 'Bs. 12.50'"""
    return f"Bs. {amount:,.2f}"


def fmt_bs_short(amount: float) -> str:
    """Versión corta sin decimales si son ceros. Ej: 12.0 → 'Bs. 12'"""
    if amount == int(amount):
        return f"Bs. {int(amount):,}"
    return fmt_bs(amount)


# ─── Fechas ───────────────────────────────────────────────────────────────────

def now_bolivia() -> datetime:
    """Retorna la fecha/hora actual en Bolivia."""
    return datetime.now(TZ_BOL)


def fmt_fecha(dt: datetime | str) -> str:
    """Formatea fecha como DD/MM/YYYY HH:MM."""
    if isinstance(dt, str):
        try:
            # Usamos isoparse para manejar cualquier formato ISO de Supabase
            dt = parser.isoparse(dt).astimezone(TZ_BOL)
        except Exception:
            return str(dt) # Retorna el string original si no se puede parsear
            
    return dt.strftime("%d/%m/%Y %H:%M")


def fmt_fecha_corta(dt: datetime | str) -> str:
    """Formatea como DD/MM/YYYY."""
    if isinstance(dt, str):
        try:
            dt = parser.isoparse(dt).astimezone(TZ_BOL)
        except Exception:
            return str(dt)
            
    return dt.strftime("%d/%m/%Y")


def fecha_inicio_hoy() -> str:
    """ISO string del inicio del día en Bolivia (para filtros Supabase)."""
    hoy = now_bolivia().replace(hour=0, minute=0, second=0, microsecond=0)
    return hoy.isoformat()


def fecha_fin_hoy() -> str:
    """ISO string del fin del día en Bolivia (para filtros Supabase)."""
    hoy = now_bolivia().replace(hour=23, minute=59, second=59, microsecond=999999)
    return hoy.isoformat()


# ─── Generadores de códigos ───────────────────────────────────────────────────

def generar_numero_venta() -> str:
    """Genera un número de venta único. Ej: V-20250520-A3X9"""
    hoy = now_bolivia().strftime("%Y%m%d")
    sufijo = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"V-{hoy}-{sufijo}"


def generar_numero_compra() -> str:
    """Genera un número de compra único. Ej: C-20250520-B7K2"""
    hoy = now_bolivia().strftime("%Y%m%d")
    sufijo = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"C-{hoy}-{sufijo}"


# ─── Validaciones ─────────────────────────────────────────────────────────────

def validar_precio(precio: float) -> bool:
    return isinstance(precio, (int, float)) and precio >= 0


def calcular_margen(precio_compra: float, precio_venta: float) -> float:
    """Retorna el margen de ganancia en porcentaje."""
    if precio_compra <= 0:
        return 0.0
    return ((precio_venta - precio_compra) / precio_compra) * 100


def calcular_cambio(total: float, recibido: float) -> float:
    """Calcula el cambio. Retorna 0 si no alcanza."""
    return max(0.0, recibido - total)

# ─── PDF ─────────────────────────────────────────────────────────────────────
def generar_pdf_nota_venta(carrito: dict, total: float, numero: str, nombre_cliente: str) -> bytes:
    pdf = FPDF(format="A5")
    pdf.add_page()
    pdf.set_margins(12, 12, 12)

    ancho      = pdf.w - 24
    col_prod   = ancho * 0.45
    col_cant   = ancho * 0.15
    col_precio = ancho * 0.20
    col_sub    = ancho * 0.20

    # Encabezado naranja
    pdf.set_fill_color(255, 107, 43)
    pdf.rect(0, 0, pdf.w, 28, style="F")
    pdf.set_y(6)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, "ALMACEN GLORIA", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Nota de Venta", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    # Info
    pdf.set_y(32)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(ancho / 2, 6, f"N Nota: {numero}", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(ancho / 2, 6, f"Fecha: {now_bolivia().strftime('%d/%m/%Y %H:%M')}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 6, f"Cliente: {nombre_cliente or 'Consumidor final'}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)

    # Separador
    pdf.set_draw_color(255, 107, 43)
    pdf.set_line_width(0.5)
    pdf.line(12, pdf.get_y(), pdf.w - 12, pdf.get_y())
    pdf.ln(3)

    # Encabezado tabla
    pdf.set_fill_color(255, 235, 210)
    pdf.set_text_color(150, 60, 0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(col_prod,   7, "PRODUCTO",  border=0, fill=True)
    pdf.cell(col_cant,   7, "CANT.",     border=0, fill=True, align="C")
    pdf.cell(col_precio, 7, "P.UNIT",    border=0, fill=True, align="R")
    pdf.cell(col_sub,    7, "SUBTOTAL",  border=0, fill=True, align="R",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Filas
    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "", 8)
    fill = False
    for item in carrito.values():
        sub = float(item["cantidad"]) * float(item["precio_venta"])
        pdf.set_fill_color(252, 248, 244) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_prod,   6, str(item["nombre"])[:30],                  border=0, fill=True)
        pdf.cell(col_cant,   6, str(item["cantidad"]),                     border=0, fill=True, align="C")
        pdf.cell(col_precio, 6, f"Bs. {float(item['precio_venta']):.2f}", border=0, fill=True, align="R")
        pdf.cell(col_sub,    6, f"Bs. {sub:.2f}",                         border=0, fill=True, align="R",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        fill = not fill

    pdf.ln(2)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.line(12, pdf.get_y(), pdf.w - 12, pdf.get_y())
    pdf.ln(3)

    # Total
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(255, 107, 43)
    pdf.cell(ancho - col_sub, 8, "TOTAL A PAGAR:", align="R")
    pdf.set_text_color(40, 40, 40)
    pdf.cell(col_sub, 8, f"Bs. {total:.2f}", align="R",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)

    # Pie
    pdf.set_draw_color(255, 107, 43)
    pdf.set_line_width(0.5)
    pdf.line(12, pdf.get_y(), pdf.w - 12, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "Gracias por su compra!", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 5, "Almacen Gloria - su tienda de confianza",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    return bytes(pdf.output())