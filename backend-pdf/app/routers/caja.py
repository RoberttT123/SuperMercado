from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from datetime import datetime

router = APIRouter(prefix="/caja", tags=["Caja"])


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

    fecha_apertura = caja.data[0]["fecha_apertura"]

    ventas = supabase.table("ventas")\
        .select("total, metodo_pago, descuento")\
        .eq("caja_id", caja_id)\
        .eq("estado", "completada")\
        .execute()

    total_ingresos = sum(v["total"] for v in ventas.data)
    efectivo = sum(v["total"] for v in ventas.data if v.get("metodo_pago") == "efectivo")
    qr = sum(v["total"] for v in ventas.data if v.get("metodo_pago") in ["qr", "transferencia"])
    tarjeta = sum(v["total"] for v in ventas.data if v.get("metodo_pago") == "tarjeta")

    return {
        "total_transacciones": len(ventas.data),
        "total_ingresos": total_ingresos,
        "efectivo": efectivo,
        "qr": qr,
        "tarjeta": tarjeta
    }


@router.post("/abrir")
def abrir_caja(data: dict):
    # Verificar que no haya una caja abierta
    activa = supabase.table("cajas")\
        .select("id")\
        .eq("estado", "abierta")\
        .execute()
    if activa.data:
        raise HTTPException(status_code=400, detail="Ya hay una caja abierta")

    result = supabase.table("cajas").insert({
        "monto_inicial": data["monto_inicial"],
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

    # Calcular resumen
    ventas = supabase.table("ventas")\
        .select("total, metodo_pago")\
        .eq("caja_id", caja_id)\
        .eq("estado", "completada")\
        .execute()

    total_ventas = sum(v["total"] for v in ventas.data)
    efectivo_ventas = sum(v["total"] for v in ventas.data if v.get("metodo_pago") == "efectivo")
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