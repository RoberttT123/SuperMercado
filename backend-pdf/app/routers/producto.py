from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/inventario", tags=["Inventario"])

# Validaciones de entrada (Input Schemas)
class ProductoCreate(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    precio_compra: float = 0
    precio_venta: float = 0
    stock: int = 0
    stock_minimo: int = 5
    unidad: str = "unidad"

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria_id: Optional[int] = None
    precio_compra: Optional[float] = None
    precio_venta: Optional[float] = None
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    activo: Optional[bool] = None

# --- TUS RUTAS ---

@router.get("/productos")
def get_productos():
    # Comunicación directa con Supabase
    result = supabase.table("productos").select("*, categorias(nombre)").eq("activo", True).execute()
    # Procesamiento de la respuesta
    productos = []
    for p in result.data:
        prod = {**p}
        prod["categoria"] = p.get("categorias", {}).get("nombre") if p.get("categorias") else None
        if "categorias" in prod: del prod["categorias"]
        productos.append(prod)
    return productos

@router.post("/productos")
def create_producto(producto: ProductoCreate):
    # .model_dump() es la forma moderna de convertir el esquema a dict
    result = supabase.table("productos").insert(producto.model_dump()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear el producto")
    return result.data[0]

@router.put("/productos/{producto_id}")
def update_producto(producto_id: int, producto: ProductoUpdate):
    # Solo actualizamos los campos que el usuario envió (excluyendo None)
    data = producto.model_dump(exclude_unset=True)
    data["updated_at"] = datetime.utcnow().isoformat()
    
    result = supabase.table("productos").update(data).eq("id", producto_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result.data[0]