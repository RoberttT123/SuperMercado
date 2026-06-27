from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.supabase_client import supabase

router = APIRouter(prefix="/categorias", tags=["Categorias"])

# --- ESQUEMAS (Pydantic) ---
class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

# --- RUTAS ---

@router.get("/")
def get_categorias():
    """Obtiene todas las categorías"""
    result = supabase.table("categorias").select("*").order("nombre").execute()
    return result.data

@router.post("/")
def create_categoria(categoria: CategoriaCreate):
    """Crea una nueva categoría"""
    result = supabase.table("categorias").insert(categoria.model_dump()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear la categoría")
    return result.data[0]

@router.put("/{categoria_id}")
def update_categoria(categoria_id: int, categoria: CategoriaUpdate):
    """Actualiza una categoría existente"""
    data = categoria.model_dump(exclude_unset=True)
    result = supabase.table("categorias").update(data).eq("id", categoria_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return result.data[0]

@router.delete("/{categoria_id}")
def delete_categoria(categoria_id: int):
    """Elimina una categoría"""
    result = supabase.table("categorias").delete().eq("id", categoria_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"success": True, "mensaje": "Categoría eliminada"}