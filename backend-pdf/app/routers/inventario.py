from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

router = APIRouter(prefix="/inventario", tags=["Inventario"])


class NivelInput(BaseModel):
    nivel: str
    contiene: Optional[str] = None
    cantidad_contenida: Optional[int] = None
    precio_compra: float = 0
    precio_venta: float = 0
    stock: int = 0
    stock_minimo: int = 0
    orden: int = 0


class NivelUpdate(BaseModel):
    contiene: Optional[str] = None
    cantidad_contenida: Optional[int] = None
    precio_compra: Optional[float] = None
    precio_venta: Optional[float] = None
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    orden: Optional[int] = None
    activo: Optional[bool] = None


class ProductoCreate(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    niveles: List[NivelInput] = []


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria_id: Optional[int] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


def _adjuntar_niveles(productos: list) -> list:
    ids = [p["id"] for p in productos]
    niveles_map = {}
    if ids:
        niveles = supabase.table("producto_niveles").select("*")\
            .in_("producto_id", ids).eq("activo", True).order("orden").execute().data
        for n in niveles:
            niveles_map.setdefault(n["producto_id"], []).append(n)
    for p in productos:
        p["niveles"] = niveles_map.get(p["id"], [])
    return productos


@router.get("/productos")
def get_productos():
    result = supabase.table("productos").select("*, categorias(nombre)").eq("activo", True).execute()
    productos = []
    for fila in result.data:
        prod = {**fila}
        prod["categoria"] = fila.get("categorias", {}).get("nombre") if fila.get("categorias") else None
        prod.pop("categorias", None)
        productos.append(prod)
    return _adjuntar_niveles(productos)


@router.get("/categorias")
def get_categorias():
    return supabase.table("categorias").select("*").execute().data


@router.get("/productos/buscar")
def buscar_producto(codigo: Optional[str] = None, nombre: Optional[str] = None):
    if codigo:
        result = supabase.table("productos").select("*").eq("codigo", codigo).eq("activo", True).execute()
    elif nombre:
        result = supabase.table("productos").select("*").ilike("nombre", f"%{nombre}%").eq("activo", True).limit(10).execute()
    else:
        raise HTTPException(status_code=400, detail="Debes enviar codigo o nombre")
    return _adjuntar_niveles(result.data)


@router.post("/productos")
def create_producto(producto: ProductoCreate):
    data = producto.model_dump(exclude={"niveles"})
    result = supabase.table("productos").insert(data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear producto")
    nuevo = result.data[0]

    if producto.niveles:
        rows = [{
            "producto_id": nuevo["id"], "nivel": n.nivel, "contiene": n.contiene,
            "cantidad_contenida": n.cantidad_contenida, "precio_compra": n.precio_compra,
            "precio_venta": n.precio_venta, "stock": n.stock, "stock_minimo": n.stock_minimo,
            "orden": n.orden
        } for n in producto.niveles]
        nuevo["niveles"] = supabase.table("producto_niveles").insert(rows).execute().data
    else:
        nuevo["niveles"] = []
    return nuevo


@router.put("/productos/{producto_id}")
def update_producto(producto_id: int, producto: ProductoUpdate):
    data = producto.model_dump(exclude_unset=True)
    result = supabase.table("productos").update(data).eq("id", producto_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return result.data[0]


@router.post("/productos/{producto_id}/niveles")
def agregar_nivel(producto_id: int, nivel: NivelInput):
    existe = supabase.table("productos").select("id").eq("id", producto_id).execute()
    if not existe.data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    row = {
        "producto_id": producto_id, "nivel": nivel.nivel, "contiene": nivel.contiene,
        "cantidad_contenida": nivel.cantidad_contenida, "precio_compra": nivel.precio_compra,
        "precio_venta": nivel.precio_venta, "stock": nivel.stock, "stock_minimo": nivel.stock_minimo,
        "orden": nivel.orden
    }
    return supabase.table("producto_niveles").insert(row).execute().data[0]


@router.put("/niveles/{nivel_id}")
def editar_nivel(nivel_id: int, nivel: NivelUpdate):
    data = nivel.model_dump(exclude_unset=True)
    result = supabase.table("producto_niveles").update(data).eq("id", nivel_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Nivel no encontrado")
    return result.data[0]


@router.delete("/niveles/{nivel_id}")
def eliminar_nivel(nivel_id: int):
    result = supabase.table("producto_niveles").update({"activo": False}).eq("id", nivel_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Nivel no encontrado")
    return {"success": True}


@router.put("/niveles/{nivel_id}/ajuste-stock")
def ajustar_stock_nivel(nivel_id: int, data: dict):
    nivel_db = supabase.table("producto_niveles").select("stock, producto_id").eq("id", nivel_id).execute()
    if not nivel_db.data:
        raise HTTPException(status_code=404, detail="Nivel no encontrado")

    stock_actual = nivel_db.data[0]["stock"]
    producto_id = nivel_db.data[0]["producto_id"]
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

    supabase.table("producto_niveles").update({"stock": nuevo_stock}).eq("id", nivel_id).execute()
    supabase.table("inventario_movimientos").insert({
        "producto_id": producto_id, "nivel_id": nivel_id, "tipo_movimiento": tipo,
        "cantidad": cantidad, "motivo": data.get("motivo", "Ajuste manual")
    }).execute()

    return {"success": True, "stock_anterior": stock_actual, "stock_nuevo": nuevo_stock}


@router.get("/productos/{producto_id}/movimientos")
def get_movimientos(producto_id: int):
    return supabase.table("inventario_movimientos")\
        .select("*, producto_niveles(nivel)")\
        .eq("producto_id", producto_id)\
        .order("fecha", desc=True).limit(50).execute().data


@router.post("/compras")
def registrar_compra(data: dict):
    numero = f"C-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
    total = sum(item["subtotal"] for item in data["items"])

    compra = supabase.table("compras").insert({
        "numero_compra": numero, "total": total, "notas": data.get("notas", ""),
        "estado": "completada", "proveedor_id": data.get("proveedor_id")
    }).execute()
    compra_id = compra.data[0]["id"]

    nivel_ids = [item["nivel_id"] for item in data["items"]]
    niveles_info = supabase.table("producto_niveles").select("id, producto_id").in_("id", nivel_ids).execute().data
    nivel_a_producto = {n["id"]: n["producto_id"] for n in niveles_info}

    detalle_rows = [{
        "compra_id": compra_id,
        "producto_id": nivel_a_producto.get(item["nivel_id"]),
        "nivel_id": item["nivel_id"],
        "cantidad": item["cantidad"],
        "precio_unitario": item["precio_unitario"],
        "subtotal": item["subtotal"]
    } for item in data["items"]]
    supabase.table("detalle_compras").insert(detalle_rows).execute()

    items_json = [{"nivel_id": item["nivel_id"], "cantidad": item["cantidad"]} for item in data["items"]]
    supabase.rpc("procesar_compra_niveles", {"p_items": items_json}).execute()

    return {"success": True, "numero_compra": numero, "total": total}


@router.get("/compras/{compra_id}/detalle")
def get_detalle_compra(compra_id: int):
    result = supabase.table("detalle_compras")\
        .select("*, productos(nombre, codigo), producto_niveles(nivel)")\
        .eq("compra_id", compra_id)\
        .execute()

    items = []
    for d in result.data:
        prod = d.get("productos") or {}
        nivel = d.get("producto_niveles") or {}
        items.append({
            "nombre": prod.get("nombre", "Desconocido"),
            "codigo": prod.get("codigo"),
            "nivel": nivel.get("nivel"),
            "cantidad": d["cantidad"],
            "precio_unitario": d["precio_unitario"],
            "subtotal": d["subtotal"]
        })
    return items