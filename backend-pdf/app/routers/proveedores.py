from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])


class ProveedorCreate(BaseModel):
    nombre: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None


class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None


@router.get("/")
def get_proveedores():
    result = supabase.table("proveedores")\
        .select("*")\
        .order("nombre")\
        .execute()
    return result.data


@router.get("/{proveedor_id}")
def get_proveedor(proveedor_id: int):
    result = supabase.table("proveedores")\
        .select("*")\
        .eq("id", proveedor_id)\
        .execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return result.data[0]


@router.get("/{proveedor_id}/compras")
def get_compras_proveedor(proveedor_id: int):
    result = supabase.table("compras")\
        .select("*")\
        .eq("proveedor_id", proveedor_id)\
        .order("fecha", desc=True)\
        .limit(20)\
        .execute()
    return result.data


@router.post("/")
def create_proveedor(proveedor: ProveedorCreate):
    result = supabase.table("proveedores")\
        .insert(proveedor.dict())\
        .execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear proveedor")
    return result.data[0]


@router.put("/{proveedor_id}")
def update_proveedor(proveedor_id: int, proveedor: ProveedorUpdate):
    data = {k: v for k, v in proveedor.dict().items() if v is not None}
    result = supabase.table("proveedores")\
        .update(data)\
        .eq("id", proveedor_id)\
        .execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return result.data[0]


@router.delete("/{proveedor_id}")
def desactivar_proveedor(proveedor_id: int):
    result = supabase.table("proveedores")\
        .update({"activo": False})\
        .eq("id", proveedor_id)\
        .execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return {"success": True, "mensaje": "Proveedor desactivado"}