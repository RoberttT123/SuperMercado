"""
src/utils/helpers.py
Herramientas reutilizables: moneda, fechas, generación de códigos.
"""

from datetime import datetime, timezone, timedelta
import random
import string
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