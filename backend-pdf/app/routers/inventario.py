from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter(prefix="/inventario", tags=["Inventario"])


# --- ESQUEMAS ---

class PresentacionInput(BaseModel):
    nombre: str
    unidades_base: int
    precio_venta: float
    precio_compra: float = 0
    orden: int = 0


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
    presentaciones: List[PresentacionInput] = []


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria_id: Optional[int] = None
    precio_compra: Optional[float] = None
    precio_venta: Optional[float] = None
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    unidad: Optional[str] = None
    activo: Optional[bool] = None
    presentaciones: Optional[List[PresentacionInput]] = None


# ── Rutas SIN parámetros dinámicos primero ──────────────────────

@router.get("/productos")
def get_productos():
    result = supabase.table("productos")\
        .select("*, categorias(nombre)")\
        .eq("activo", True)\
        .execute()

    productos, ids = [], []
    for fila_producto in result.data:
        prod = {**fila_producto}
        prod["categoria"] = fila_producto.get("categorias", {}).get("nombre") if fila_producto.get("categorias") else None
        prod.pop("categorias", None)
        productos.append(prod)
        ids.append(fila_producto["id"])

    # 1 sola query extra: TODAS las presentaciones de TODOS los productos
    presentaciones_map = {}
    if ids:
        pres = supabase.table("producto_presentaciones")\
            .select("*")\
            .in_("producto_id", ids)\
            .eq("activo", True)\
            .order("orden")\
            .execute().data
        for pr in pres:
            presentaciones_map.setdefault(pr["producto_id"], []).append(pr)

    for prod in productos:
        prod["presentaciones"] = presentaciones_map.get(prod["id"], [])

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

    productos = result.data
    ids = [p["id"] for p in productos]

    # También traemos presentaciones aquí — el POS las necesita para mostrar precios por mayor
    presentaciones_map = {}
    if ids:
        pres = supabase.table("producto_presentaciones")\
            .select("*")\
            .in_("producto_id", ids)\
            .eq("activo", True)\
            .order("orden")\
            .execute().data
        for pr in pres:
            presentaciones_map.setdefault(pr["producto_id"], []).append(pr)

    for prod in productos:
        prod["presentaciones"] = presentaciones_map.get(prod["id"], [])

    return productos


# ── Rutas CON parámetros dinámicos después ──────────────────────

@router.post("/productos")
def create_producto(producto: ProductoCreate):
    data = producto.model_dump(exclude={"presentaciones"})
    result = supabase.table("productos").insert(data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear producto")

    nuevo = result.data[0]

    if producto.presentaciones:
        rows = [{
            "producto_id": nuevo["id"],
            "nombre": p.nombre,
            "unidades_base": p.unidades_base,
            "precio_venta": p.precio_venta,
            "precio_compra": p.precio_compra,
            "orden": p.orden
        } for p in producto.presentaciones]
        supabase.table("producto_presentaciones").insert(rows).execute()
        nuevo["presentaciones"] = rows
    else:
        nuevo["presentaciones"] = []

    return nuevo


@router.put("/productos/{producto_id}")
def update_producto(producto_id: int, producto: ProductoUpdate):
    data = producto.model_dump(exclude={"presentaciones"}, exclude_unset=True)
    data["updated_at"] = datetime.utcnow().isoformat()

    result = supabase.table("productos").update(data).eq("id", producto_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Si vino la lista de presentaciones, se reemplaza completa (simple y sin ambigüedad)
    if producto.presentaciones is not None:
        supabase.table("producto_presentaciones").delete().eq("producto_id", producto_id).execute()
        if producto.presentaciones:
            rows = [{
                "producto_id": producto_id,
                "nombre": p.nombre,
                "unidades_base": p.unidades_base,
                "precio_venta": p.precio_venta,
                "precio_compra": p.precio_compra,
                "orden": p.orden
            } for p in producto.presentaciones]
            supabase.table("producto_presentaciones").insert(rows).execute()

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
    """
    data: {
        "proveedor_id": int | None,
        "notas": str,
        "items": [{ "productoId": int, "cantidad": int, "precio_unitario": float, "subtotal": float }]
    }
    """
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

    # 1 sola llamada: inserta TODO el detalle de una vez
    detalle_rows = [{
        "compra_id": compra_id,
        "producto_id": item["productoId"],
        "cantidad": item["cantidad"],
        "precio_unitario": item["precio_unitario"],
        "subtotal": item["subtotal"]
    } for item in data["items"]]
    supabase.table("detalle_compras").insert(detalle_rows).execute()

    # 1 sola llamada: suma stock + registra movimientos de TODOS los productos
    items_json = [{"producto_id": item["productoId"], "cantidad": item["cantidad"]} for item in data["items"]]
    supabase.rpc("procesar_compra", {"p_items": items_json}).execute()

    return {"success": True, "numero_compra": numero, "total": total}