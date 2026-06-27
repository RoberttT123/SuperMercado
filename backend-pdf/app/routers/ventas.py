from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter(prefix="/ventas", tags=["Ventas"])

class ItemVenta(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float
    precio_compra: float
    subtotal: float

class VentaCreate(BaseModel):
    items: List[ItemVenta]
    metodo_pago: str = "efectivo"
    monto_recibido: Optional[float] = None
    descuento: float = 0
    notas: Optional[str] = None
    caja_id: Optional[int] = None

@router.get("/")
def get_ventas():
    result = supabase.table("ventas")\
        .select("*")\
        .order("fecha", desc=True)\
        .limit(100)\
        .execute()
    return result.data

@router.get("/{venta_id}")
def get_venta(venta_id: int):
    venta = supabase.table("ventas").select("*").eq("id", venta_id).execute()
    if not venta.data:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    detalle = supabase.table("detalle_ventas")\
        .select("*, productos(nombre, codigo)")\
        .eq("venta_id", venta_id)\
        .execute()
    return {**venta.data[0], "detalle": detalle.data}

@router.post("/")
def crear_venta(venta: VentaCreate):
    subtotal = sum(item.subtotal for item in venta.items)
    total = subtotal - venta.descuento
    cambio = (venta.monto_recibido - total) if venta.monto_recibido else 0
    numero = f"V-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

    # 1. Crear venta
    nueva_venta = supabase.table("ventas").insert({
        "numero_venta": numero,
        "caja_id": venta.caja_id,
        "subtotal": subtotal,
        "descuento": venta.descuento,
        "total": total,
        "metodo_pago": venta.metodo_pago,
        "monto_recibido": venta.monto_recibido,
        "cambio": cambio,
        "notas": venta.notas,
        "estado": "completada"
    }).execute()

    venta_id = nueva_venta.data[0]["id"]

    for item in venta.items:
        # 2. Insertar detalle
        supabase.table("detalle_ventas").insert({
            "venta_id": venta_id,
            "producto_id": item.producto_id,
            "cantidad": item.cantidad,
            "precio_unitario": item.precio_unitario,
            "precio_compra": item.precio_compra,
            "subtotal": item.subtotal
        }).execute()

        # 3. Descontar stock
        prod = supabase.table("productos").select("stock").eq("id", item.producto_id).execute()
        nuevo_stock = prod.data[0]["stock"] - item.cantidad
        supabase.table("productos").update({"stock": nuevo_stock}).eq("id", item.producto_id).execute()

        # 4. Registrar movimiento
        supabase.table("inventario_movimientos").insert({
            "producto_id": item.producto_id,
            "tipo_movimiento": "egreso",
            "cantidad": item.cantidad,
            "motivo": f"Venta #{numero}"
        }).execute()

    return {
        "success": True,
        "numero_venta": numero,
        "total": total,
        "cambio": cambio,
        "venta_id": venta_id
    }

@router.put("/{venta_id}/anular")
def anular_venta(venta_id: int):
    venta = supabase.table("ventas").select("*").eq("id", venta_id).execute()
    if not venta.data:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    if venta.data[0]["estado"] == "anulada":
        raise HTTPException(status_code=400, detail="La venta ya está anulada")

    # Revertir stock
    detalle = supabase.table("detalle_ventas").select("*").eq("venta_id", venta_id).execute()
    for item in detalle.data:
        prod = supabase.table("productos").select("stock").eq("id", item["producto_id"]).execute()
        nuevo_stock = prod.data[0]["stock"] + item["cantidad"]
        supabase.table("productos").update({"stock": nuevo_stock}).eq("id", item["producto_id"]).execute()

    supabase.table("ventas").update({"estado": "anulada"}).eq("id", venta_id).execute()
    return {"success": True, "mensaje": "Venta anulada y stock revertido"}