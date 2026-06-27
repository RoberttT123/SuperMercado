from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.supabase_client import supabase

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

# --- ESQUEMAS ---
class ProveedorBase(BaseModel):
    nombre: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(ProveedorBase):
    activo: Optional[bool] = None

# --- RUTAS ---

@router.get("/")
def get_proveedores():
    """Obtiene todos los proveedores activos"""
    result = supabase.table("proveedores").select("*").eq("activo", True).order("nombre").execute()
    return result.data

@router.post("/")
def create_proveedor(proveedor: ProveedorCreate):
    """Crea un nuevo proveedor"""
    result = supabase.table("proveedores").insert(proveedor.model_dump()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear proveedor")
    return result.data[0]

@router.put("/{proveedor_id}")
def update_proveedor(proveedor_id: int, proveedor: ProveedorUpdate):
    """Actualiza un proveedor"""
    data = proveedor.model_dump(exclude_unset=True)
    result = supabase.table("proveedores").update(data).eq("id", proveedor_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return result.data[0]

@router.delete("/{proveedor_id}")
def delete_proveedor(proveedor_id: int):
    """Eliminación lógica (desactivar proveedor)"""
    result = supabase.table("proveedores").update({"activo": False}).eq("id", proveedor_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return {"success": True, "mensaje": "Proveedor desactivado"}