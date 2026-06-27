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
    """Registra una compra completa con actualización de stock"""
    numero = f"C-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
    total = sum(item.subtotal for item in compra.items)

    # 1. Insertar cabecera de compra
    compra_res = supabase.table("compras").insert({
        "numero_compra": numero,
        "proveedor_id": compra.proveedor_id,
        "total": total,
        "notas": compra.notas,
        "estado": "completada"
    }).execute()
    
    compra_id = compra_res.data[0]["id"]

    # 2. Procesar items
    for item in compra.items:
        # Insertar detalle
        supabase.table("detalle_compras").insert({
            "compra_id": compra_id,
            "producto_id": item.producto_id,
            "cantidad": item.cantidad,
            "precio_unitario": item.precio_unitario,
            "subtotal": item.subtotal
        }).execute()

        # Actualizar Stock
        prod = supabase.table("productos").select("stock").eq("id", item.producto_id).execute()
        nuevo_stock = prod.data[0]["stock"] + item.cantidad
        supabase.table("productos").update({"stock": nuevo_stock}).eq("id", item.producto_id).execute()

        # Registrar Movimiento
        supabase.table("inventario_movimientos").insert({
            "producto_id": item.producto_id,
            "tipo_movimiento": "ingreso",
            "cantidad": item.cantidad,
            "motivo": f"Compra #{numero}"
        }).execute()

    return {"success": True, "numero_compra": numero, "total": total}