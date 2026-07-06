from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/inventario", tags=["Inventario"])

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
    unidades_por_caja: int = 1

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria_id: Optional[int] = None
    precio_compra: Optional[float] = None
    precio_venta: Optional[float] = None
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    unidades_por_caja: Optional[int] = None
    unidad: Optional[str] = None  # ✅ CAMPO AGREGADO PARA PERMITIR LA ACTUALIZACIÓN


# ── Rutas SIN parámetros dinámicos primero ──────────────────────

@router.get("/productos")
def get_productos():
    result = supabase.table("productos")\
        .select("*, categorias(nombre)")\
        .eq("activo", True)\
        .execute()
    
    productos = []
    for fila_producto in result.data:
        prod = {**fila_producto}
        prod["categoria"] = fila_producto.get("categorias", {}).get("nombre") if fila_producto.get("categorias") else None
        del prod["categorias"]
        productos.append(prod)
    return productos


@router.get("/categorias")
def get_categorias():
    result = supabase.table("categorias").select("*").execute()
    return result.data


# ✅ CRÍTICO: esta ruta ANTES de /productos/{producto_id}
@router.get("/productos/buscar")
def buscar_producto(codigo: Optional[str] = None, nombre: Optional[str] = None):
    if codigo:
        result = supabase.table("productos")\
            .select("*")\
            .eq("codigo", codigo)\
            .eq("activo", True)\
            .execute()
    elif nombre:
        result = supabase.table("productos")\
            .select("*")\
            .ilike("nombre", f"%{nombre}%")\
            .eq("activo", True)\
            .limit(10)\
            .execute()
    else:
        raise HTTPException(status_code=400, detail="Debes enviar codigo o nombre")
    return result.data


# ── Rutas CON parámetros dinámicos después ──────────────────────

@router.post("/productos")
def create_producto(producto: ProductoCreate):
    result = supabase.table("productos").insert(producto.dict()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear producto")
    return result.data[0]


@router.put("/productos/{producto_id}")
def update_producto(producto_id: int, producto: ProductoUpdate):
    data = {k: v for k, v in producto.dict().items() if v is not None}
    data["updated_at"] = datetime.utcnow().isoformat()
    
    result = supabase.table("productos").update(data).eq("id", producto_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result.data[0]


@router.put("/productos/{producto_id}/ajuste-stock")
def ajustar_stock(producto_id: int, data: dict):
    producto_db = supabase.table("productos").select("stock, nombre").eq("id", producto_id).execute()
    if not producto_db.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    stock_actual = producto_db.data[0]["stock"]
    tipo = data.get("tipo", "ajuste")
    cantidad = data["cantidad"]

    if tipo == "ingreso":
        nuevo_stock = stock_actual + cantidad
    elif tipo == "egreso":
        nuevo_stock = stock_actual - cantidad
        if nuevo_stock < 0:
            raise HTTPException(status_code=400, detail="Stock insuficiente")
    else:
        nuevo_stock = cantidad

    supabase.table("productos").update({
        "stock": nuevo_stock,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", producto_id).execute()

    supabase.table("inventario_movimientos").insert({
        "producto_id": producto_id,
        "tipo_movimiento": tipo,
        "cantidad": cantidad,
        "motivo": data.get("motivo", "Ajuste manual")
    }).execute()

    return {"success": True, "stock_anterior": stock_actual, "stock_nuevo": nuevo_stock}


@router.get("/productos/{producto_id}/movimientos")
def get_movimientos(producto_id: int):
    result = supabase.table("inventario_movimientos")\
        .select("*")\
        .eq("producto_id", producto_id)\
        .order("fecha", desc=True)\
        .limit(50)\
        .execute()
    return result.data


@router.post("/compras")
def registrar_compra(data: dict):
    numero = f"C-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
    total = sum(item["subtotal"] for item in data["items"])

    compra = supabase.table("compras").insert({
        "numero_compra": numero,
        "total": total,
        "notas": data.get("notas", ""),
        "estado": "completada",
        "proveedor_id": data.get("proveedor_id")
    }).execute()

    compra_id = compra.data[0]["id"]

    for item in data["items"]:
        supabase.table("detalle_compras").insert({
            "compra_id": compra_id,
            "producto_id": item["productoId"],
            "cantidad": item["cantidad"],
            "precio_unitario": item["precio_unitario"],
            "subtotal": item["subtotal"]
        }).execute()

        producto_db = supabase.table("productos").select("stock").eq("id", item["productoId"]).execute()
        nuevo_stock = producto_db.data[0]["stock"] + item["cantidad"]
        supabase.table("productos").update({"stock": nuevo_stock}).eq("id", item["productoId"]).execute()

        supabase.table("inventario_movimientos").insert({
            "producto_id": item["productoId"],
            "tipo_movimiento": "ingreso",
            "cantidad": item["cantidad"],
            "motivo": f"Compra #{numero}"
        }).execute()

    return {"success": True, "numero_compra": numero, "total": total}