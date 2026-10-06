from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from datetime import datetime

router = APIRouter(prefix="/caja", tags=["Caja"])


def _monto_cobrado_ahora(v):
    total = v["total"]
    if v.get("es_credito"):
        return min(v.get("monto_recibido") or 0, total)
    return total


@router.get("/activa")
def get_caja_activa():
    result = supabase.table("cajas")\
        .select("*")\
        .eq("estado", "abierta")\
        .order("fecha_apertura", desc=True)\
        .limit(1)\
        .execute()
    return result.data[0] if result.data else None


@router.get("/historial")
def get_historial():
    result = supabase.table("cajas")\
        .select("*")\
        .eq("estado", "cerrada")\
        .order("fecha_apertura", desc=True)\
        .limit(30)\
        .execute()
    return result.data


@router.get("/{caja_id}/resumen")
def get_resumen_caja(caja_id: int):
    caja = supabase.table("cajas").select("fecha_apertura").eq("id", caja_id).execute()
    if not caja.data:
        raise HTTPException(status_code=404, detail="Caja no encontrada")

    ventas = supabase.table("ventas")\
        .select("total, metodo_pago, descuento, es_credito, monto_recibido")\
        .eq("caja_id", caja_id)\
        .eq("estado", "completada")\
        .execute()

    total_ingresos = sum(v["total"] for v in ventas.data)
    total_credito = sum(
        max(0, v["total"] - (v.get("monto_recibido") or 0))
        for v in ventas.data if v.get("es_credito")
    )

    efectivo = sum(_monto_cobrado_ahora(v) for v in ventas.data if v.get("metodo_pago") == "efectivo")
    qr = sum(_monto_cobrado_ahora(v) for v in ventas.data if v.get("metodo_pago") in ["qr", "transferencia"])
    tarjeta = sum(_monto_cobrado_ahora(v) for v in ventas.data if v.get("metodo_pago") == "tarjeta")

    return {
        "total_transacciones": len(ventas.data),
        "total_ingresos": total_ingresos,
        "total_credito": total_credito,
        "efectivo": efectivo,
        "qr": qr,
        "tarjeta": tarjeta
    }


@router.post("/abrir")
def abrir_caja(data: dict):
    activa = supabase.table("cajas")\
        .select("id")\
        .eq("estado", "abierta")\
        .execute()
    if activa.data:
        raise HTTPException(status_code=400, detail="Ya hay una caja abierta")

    monto = data.get("monto_inicial")
    if isinstance(monto, bool) or not isinstance(monto, (int, float)) or monto < 0:
        raise HTTPException(status_code=400, detail="El monto inicial debe ser 0 o mayor")

    result = supabase.table("cajas").insert({
        "monto_inicial": monto,
        "usuario": data["usuario"],
        "estado": "abierta",
        "fecha_apertura": datetime.utcnow().isoformat()
    }).execute()

    return result.data[0]


@router.post("/cerrar/{caja_id}")
def cerrar_caja(caja_id: int, data: dict):
    caja = supabase.table("cajas").select("*").eq("id", caja_id).execute()
    if not caja.data:
        raise HTTPException(status_code=404, detail="Caja no encontrada")
    if caja.data[0]["estado"] == "cerrada":
        raise HTTPException(status_code=400, detail="La caja ya está cerrada")

    ventas = supabase.table("ventas")\
        .select("total, metodo_pago, es_credito, monto_recibido")\
        .eq("caja_id", caja_id)\
        .eq("estado", "completada")\
        .execute()

    efectivo_ventas = sum(_monto_cobrado_ahora(v) for v in ventas.data if v.get("metodo_pago") == "efectivo")
    monto_esperado = caja.data[0]["monto_inicial"] + efectivo_ventas
    diferencia = data["monto_contado"] - monto_esperado

    result = supabase.table("cajas").update({
        "estado": "cerrada",
        "fecha_cierre": datetime.utcnow().isoformat(),
        "monto_final": data["monto_contado"],
        "monto_esperado": monto_esperado,
        "diferencia": diferencia,
        "notas": data.get("notas", "")
    }).eq("id", caja_id).execute()

    return {
        "success": True,
        "monto_esperado": monto_esperado,
        "monto_contado": data["monto_contado"],
        "diferencia": diferencia
    }