"""
src/services/caja_service.py
Lógica de negocio para apertura, cierre y arqueo de caja.
"""

from src.database.connection import get_supabase
from src.utils.helpers import now_bolivia, fecha_inicio_hoy, fecha_fin_hoy


# ─── Consultas de estado ──────────────────────────────────────────────────────

def get_caja_abierta() -> dict | None:
    """
    Retorna la caja actualmente abierta o None si no hay ninguna.
    """
    db  = get_supabase()
    res = (
        db.table("cajas")
        .select("*")
        .eq("estado", "abierta")
        .order("fecha_apertura", desc=True)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


def get_historial_cajas(limite: int = 30) -> list[dict]:
    """Retorna el historial de cajas cerradas."""
    db  = get_supabase()
    res = (
        db.table("cajas")
        .select("*")
        .eq("estado", "cerrada")
        .order("fecha_apertura", desc=True)
        .limit(limite)
        .execute()
    )
    return res.data or []


# ─── Apertura ─────────────────────────────────────────────────────────────────

def abrir_caja(monto_inicial: float, usuario: str = "Admin") -> dict:
    """
    Abre una nueva caja.
    Lanza ValueError si ya existe una caja abierta.
    """
    if get_caja_abierta():
        raise ValueError("⚠️ Ya existe una caja abierta. Ciérrala antes de abrir una nueva.")

    db  = get_supabase()
    res = (
        db.table("cajas")
        .insert({
            "monto_inicial": monto_inicial,
            "usuario":       usuario,
            "estado":        "abierta",
        })
        .execute()
    )
    return res.data[0]


# ─── Cierre ───────────────────────────────────────────────────────────────────

def cerrar_caja(caja_id: int, monto_final: float, notas: str = "") -> dict:
    """
    Cierra la caja indicada y calcula el arqueo.
    """
    db = get_supabase()

    # Total de ventas en efectivo durante esta caja
    ventas_res = (
        db.table("ventas")
        .select("total")
        .eq("caja_id",    caja_id)
        .eq("estado",     "completada")
        .eq("metodo_pago","efectivo")
        .execute()
    )
    total_ventas_efectivo = sum(v["total"] for v in (ventas_res.data or []))

    # Recuperar monto inicial
    caja_res = db.table("cajas").select("monto_inicial").eq("id", caja_id).single().execute()
    monto_inicial = caja_res.data["monto_inicial"]

    monto_esperado = monto_inicial + total_ventas_efectivo
    diferencia     = monto_final - monto_esperado

    res = (
        db.table("cajas")
        .update({
            "fecha_cierre":   now_bolivia().isoformat(),
            "monto_final":    monto_final,
            "monto_esperado": monto_esperado,
            "diferencia":     diferencia,
            "estado":         "cerrada",
            "notas":          notas,
        })
        .eq("id", caja_id)
        .execute()
    )
    return res.data[0]


# ─── Resumen del día ──────────────────────────────────────────────────────────

def get_resumen_caja(caja_id: int) -> dict:
    """
    Calcula el resumen de ventas para una caja específica.
    """
    db  = get_supabase()
    res = (
        db.table("ventas")
        .select("total, metodo_pago, estado")
        .eq("caja_id", caja_id)
        .eq("estado",  "completada")
        .execute()
    )
    ventas = res.data or []

    resumen = {
        "total_transacciones": len(ventas),
        "total_ingresos":      sum(v["total"] for v in ventas),
        "efectivo":            sum(v["total"] for v in ventas if v["metodo_pago"] == "efectivo"),
        "qr":                  sum(v["total"] for v in ventas if v["metodo_pago"] == "qr"),
        "tarjeta":             sum(v["total"] for v in ventas if v["metodo_pago"] == "tarjeta"),
    }
    return resumen