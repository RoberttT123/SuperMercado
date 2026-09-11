from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
from app.supabase_client import supabase

router = APIRouter(prefix="/compras", tags=["Compras"])

# --- ESQUEMAS ---
class ItemCompra(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float

class CompraCreate(BaseModel):
    proveedor_id: int
    items: List[ItemCompra]
    notas: Optional[str] = None

# --- RUTAS ---

@router.get("/")
def get_compras():
    """Historial de compras"""
    result = supabase.table("compras").select("*, proveedores(nombre)").order("fecha", desc=True).limit(50).execute()
    return result.data

@router.post("/")
def registrar_compra(compra: CompraCreate):
    numero = f"C-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
    total = sum(item.subtotal for item in compra.items)

    compra_res = supabase.table("compras").insert({
        "numero_compra": numero,
        "proveedor_id": compra.proveedor_id,
        "total": total,
        "notas": compra.notas,
        "estado": "completada"
    }).execute()
    compra_id = compra_res.data[0]["id"]

    # 1 sola llamada: inserta TODO el detalle de una vez
    detalle_rows = [{
        "compra_id": compra_id,
        "producto_id": item.producto_id,
        "cantidad": item.cantidad,
        "precio_unitario": item.precio_unitario,
        "subtotal": item.subtotal
    } for item in compra.items]
    supabase.table("detalle_compras").insert(detalle_rows).execute()

    # 1 sola llamada: suma stock + registra movimientos de TODOS los productos
    items_json = [{"producto_id": item.producto_id, "cantidad": item.cantidad} for item in compra.items]
    supabase.rpc("procesar_compra", {"p_items": items_json}).execute()

    return {"success": True, "numero_compra": numero, "total": total}