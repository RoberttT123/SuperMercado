"""
src/services/inventario_service.py
Lógica de negocio para productos, stock y registro de compras.
"""

from src.database.connection import get_supabase
from src.utils.helpers import generar_numero_compra


# ─── Categorías ───────────────────────────────────────────────────────────────

def get_categorias() -> list[dict]:
    db  = get_supabase()
    res = db.table("categorias").select("*").order("nombre").execute()
    return res.data or []


# ─── Productos ────────────────────────────────────────────────────────────────

def buscar_producto_por_codigo(codigo: str) -> dict | None:
    """Busca un producto por código de barras (escaneo). Retorna None si no existe."""
    db  = get_supabase()
    res = (
        db.table("productos")
        .select("*, categorias(nombre)")
        .eq("codigo", codigo.strip())
        .eq("activo", True)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


def buscar_productos(termino: str = "", categoria_id: int | None = None) -> list[dict]:
    """
    Busca productos por nombre o código.
    Opcionalmente filtra por categoría.
    """
    db    = get_supabase()
    query = db.table("productos").select("*, categorias(nombre)").eq("activo", True)

    if termino:
        # Supabase usa ilike para búsqueda case-insensitive
        query = query.or_(f"nombre.ilike.%{termino}%,codigo.ilike.%{termino}%")
    if categoria_id:
        query = query.eq("categoria_id", categoria_id)

    res = query.order("nombre").execute()
    return res.data or []


def get_todos_productos() -> list[dict]:
    db  = get_supabase()
    res = (
        db.table("productos")
        .select("*, categorias(nombre)")
        .order("nombre")
        .execute()
    )
    return res.data or []


def get_producto_por_id(producto_id: int) -> dict | None:
    db  = get_supabase()
    res = (
        db.table("productos")
        .select("*, categorias(nombre)")
        .eq("id", producto_id)
        .single()
        .execute()
    )
    return res.data


def crear_producto(datos: dict) -> dict:
    """
    Crea un nuevo producto.
    datos debe incluir: codigo, nombre, precio_compra, precio_venta, stock.
    """
    db  = get_supabase()
    res = db.table("productos").insert(datos).execute()
    return res.data[0]


def actualizar_producto(producto_id: int, datos: dict) -> dict:
    db  = get_supabase()
    res = (
        db.table("productos")
        .update(datos)
        .eq("id", producto_id)
        .execute()
    )
    return res.data[0]


def desactivar_producto(producto_id: int) -> None:
    db = get_supabase()
    db.table("productos").update({"activo": False}).eq("id", producto_id).execute()


# ─── Stock ────────────────────────────────────────────────────────────────────

def get_stock_critico() -> list[dict]:
    """Retorna productos con stock <= stock_mínimo."""
    db  = get_supabase()
    res = (
        db.table("productos")
        .select("*, categorias(nombre)")
        .eq("activo", True)
        .execute()
    )
    productos = res.data or []
    return [p for p in productos if p["stock"] <= p["stock_minimo"]]


def actualizar_stock(producto_id: int, nueva_cantidad: int) -> None:
    """Sobreescribe el stock de un producto."""
    db = get_supabase()
    db.table("productos").update({"stock": nueva_cantidad}).eq("id", producto_id).execute()


def incrementar_stock(producto_id: int, cantidad: int) -> None:
    """Incrementa el stock de un producto en N unidades."""
    prod = get_producto_por_id(producto_id)
    if not prod:
        raise ValueError(f"Producto ID {producto_id} no encontrado.")
    nuevo_stock = prod["stock"] + cantidad
    actualizar_stock(producto_id, nuevo_stock)


def decrementar_stock(producto_id: int, cantidad: int) -> None:
    """Reduce el stock tras una venta. Lanza ValueError si no hay suficiente."""
    prod = get_producto_por_id(producto_id)
    if not prod:
        raise ValueError(f"Producto ID {producto_id} no encontrado.")
    if prod["stock"] < cantidad:
        raise ValueError(
            f"Stock insuficiente para '{prod['nombre']}'. "
            f"Disponible: {prod['stock']}, solicitado: {cantidad}."
        )
    actualizar_stock(producto_id, prod["stock"] - cantidad)


# ─── Registro de Compras ──────────────────────────────────────────────────────

def registrar_compra(items: list[dict], proveedor_id: int | None = None, notas: str = "") -> dict:
    """
    Registra una compra e incrementa el stock.

    items: lista de dicts con {producto_id, cantidad, precio_unitario}
    """
    db             = get_supabase()
    numero_compra  = generar_numero_compra()
    total          = sum(i["cantidad"] * i["precio_unitario"] for i in items)

    # Insertar cabecera
    compra_res = (
        db.table("compras")
        .insert({
            "numero_compra": numero_compra,
            "proveedor_id":  proveedor_id,
            "total":         total,
            "notas":         notas,
        })
        .execute()
    )
    compra = compra_res.data[0]

    # Insertar detalle y actualizar stock
    detalles = []
    for item in items:
        detalles.append({
            "compra_id":      compra["id"],
            "producto_id":    item["producto_id"],
            "cantidad":       item["cantidad"],
            "precio_unitario":item["precio_unitario"],
            "subtotal":       item["cantidad"] * item["precio_unitario"],
        })
        # Actualizar precio de compra en el producto y aumentar stock
        incrementar_stock(item["producto_id"], item["cantidad"])
        db.table("productos").update(
            {"precio_compra": item["precio_unitario"]}
        ).eq("id", item["producto_id"]).execute()

    db.table("detalle_compras").insert(detalles).execute()
    return compra