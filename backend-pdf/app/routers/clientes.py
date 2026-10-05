from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from app.core.auth import SOLO_GESTION
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/clientes", tags=["Clientes"])


class ClienteCreate(BaseModel):
    nombre: str
    nit_ci: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    limite_credito: float = 0


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    nit_ci: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    limite_credito: Optional[float] = None
    activo: Optional[bool] = None


class AbonoInput(BaseModel):
    monto: float
    motivo: Optional[str] = "Abono a cuenta"


# ── Rutas SIN parámetros dinámicos primero ──────────────────────

@router.get("/")
def get_clientes(solo_con_deuda: bool = False):
    query = supabase.table("clientes").select("*").eq("activo", True).order("nombre")
    if solo_con_deuda:
        query = query.gt("saldo_pendiente", 0)
    return query.execute().data


@router.get("/buscar")
def buscar_cliente(nombre: str):
    return supabase.table("clientes")\
        .select("*")\
        .ilike("nombre", f"%{nombre}%")\
        .eq("activo", True)\
        .limit(10)\
        .execute().data


@router.post("/")
def crear_cliente(cliente: ClienteCreate):
    result = supabase.table("clientes").insert(cliente.model_dump()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear cliente")
    return result.data[0]


# ── Rutas CON parámetros dinámicos después ──────────────────────

@router.get("/{cliente_id}")
def get_cliente(cliente_id: int):
    result = supabase.table("clientes").select("*").eq("id", cliente_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return result.data[0]


@router.put("/{cliente_id}")
def actualizar_cliente(cliente_id: int, cliente: ClienteUpdate):
    data = cliente.model_dump(exclude_unset=True)
    result = supabase.table("clientes").update(data).eq("id", cliente_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return result.data[0]


@router.delete("/{cliente_id}", dependencies=SOLO_GESTION)
def desactivar_cliente(cliente_id: int):
    result = supabase.table("clientes").update({"activo": False}).eq("id", cliente_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"success": True}


@router.get("/{cliente_id}/movimientos")
def get_movimientos_cliente(cliente_id: int):
    return supabase.table("cliente_movimientos")\
        .select("*, ventas(numero_venta)")\
        .eq("cliente_id", cliente_id)\
        .order("fecha", desc=True)\
        .execute().data


@router.post("/{cliente_id}/abono")
def registrar_abono(cliente_id: int, abono: AbonoInput):
    cliente = supabase.table("clientes").select("saldo_pendiente").eq("id", cliente_id).execute()
    if not cliente.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    supabase.rpc("registrar_abono_cliente", {
        "p_cliente_id": cliente_id,
        "p_monto": abono.monto,
        "p_motivo": abono.motivo
    }).execute()

    nuevo = supabase.table("clientes").select("saldo_pendiente").eq("id", cliente_id).execute()
    return {"success": True, "saldo_pendiente": nuevo.data[0]["saldo_pendiente"]}