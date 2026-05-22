"""
src/services/ventas_service.py
Lógica de negocio para el Punto de Venta: procesar carrito y guardar ventas.
"""

from src.database.connection import get_supabase
from src.utils.helpers import generar_numero_venta, fecha_inicio_hoy, fecha_fin_hoy


def _get_producto_por_id(producto_id: int) -> dict | None:
    """Helper interno para no importar desde inventario_service y evitar circular imports."""
    db  = get_supabase()
    res = (
        db.table("productos")
        .select("id, nombre, stock, precio_compra")
        .eq("id", producto_id)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


def _decrementar_stock(producto_id: int, cantidad: int) -> None:
    prod = _get_producto_por_id(producto_id)
    if not prod:
        raise ValueError(f"Producto ID {producto_id} no encontrado.")
    if prod["stock"] < cantidad:
        raise ValueError(
            f"Sin stock para '{prod['nombre']}'. "
            f"Disponible: {prod['stock']}, solicitado: {cantidad}."
        )
    db = get_supabase()
    db.table("productos").update({"stock": prod["stock"] - cantidad}).eq("id", producto_id).execute()


# ── Procesar venta ─────────────────────────────────────────────────────────────

def procesar_venta(
    carrito:        list,
    caja_id:        int,
    metodo_pago:    str   = "efectivo",
    descuento:      float = 0.0,
    monto_recibido: float = 0.0,
    notas:          str   = "",
) -> dict:
    """
    Guarda la venta completa en Supabase y descuenta el stock.

    carrito: lista de dicts con {producto_id, cantidad, precio_unitario, precio_compra}
    Retorna el dict de la venta creada.
    """
    if not carrito:
        raise ValueError("El carrito está vacío.")

    db           = get_supabase()
    numero_venta = generar_numero_venta()
    subtotal     = sum(i["cantidad"] * i["precio_unitario"] for i in carrito)
    total        = max(0.0, subtotal - descuento)
    cambio       = max(0.0, monto_recibido - total) if metodo_pago == "efectivo" else 0.0

    # Validar stock de todos los items antes de guardar
    for item in carrito:
        prod = _get_producto_por_id(item["producto_id"])
        if not prod:
            raise ValueError(f"Producto ID {item['producto_id']} no encontrado.")
        if prod["stock"] < item["cantidad"]:
            raise ValueError(
                f"Sin stock para '{prod['nombre']}'. "
                f"Disponible: {prod['stock']}, solicitado: {item['cantidad']}."
            )

    # Insertar cabecera de venta
    venta_res = (
        db.table("ventas")
        .insert({
            "numero_venta":   numero_venta,
            "caja_id":        caja_id,
            "subtotal":       subtotal,
            "descuento":      descuento,
            "total":          total,
            "metodo_pago":    metodo_pago,
            "monto_recibido": monto_recibido if metodo_pago == "efectivo" else total,
            "cambio":         cambio,
            "notas":          notas,
            "estado":         "completada",
        })
        .execute()
    )
    venta = venta_res.data[0]

    # Insertar detalle y descontar stock
    detalles = []
    for item in carrito:
        detalles.append({
            "venta_id":        venta["id"],
            "producto_id":     item["producto_id"],
            "cantidad":        item["cantidad"],
            "precio_unitario": item["precio_unitario"],
            "precio_compra":   item["precio_compra"],
            "subtotal":        item["cantidad"] * item["precio_unitario"],
        })
        _decrementar_stock(item["producto_id"], item["cantidad"])

    db.table("detalle_ventas").insert(detalles).execute()
    return venta


# ── Anular venta ──────────────────────────────────────────────────────────────

def anular_venta(venta_id: int) -> None:
    """Marca una venta como anulada y restaura el stock."""
    db = get_supabase()
    det_res = (
        db.table("detalle_ventas")
        .select("producto_id, cantidad")
        .eq("venta_id", venta_id)
        .execute()
    )
    for item in (det_res.data or []):
        prod = _get_producto_por_id(item["producto_id"])
        if prod:
            db.table("productos").update(
                {"stock": prod["stock"] + item["cantidad"]}
            ).eq("id", item["producto_id"]).execute()

    db.table("ventas").update({"estado": "anulada"}).eq("id", venta_id).execute()


# ── Consultas ─────────────────────────────────────────────────────────────────

def get_ventas_del_dia() -> list:
    """Retorna todas las ventas del día actual en Bolivia."""
    db  = get_supabase()
    res = (
        db.table("ventas")
        .select("*")
        .gte("fecha", fecha_inicio_hoy())
        .lte("fecha", fecha_fin_hoy())
        .order("fecha", desc=True)
        .execute()
    )
    return res.data or []


def get_detalle_venta(venta_id: int) -> list:
    """Retorna el detalle de una venta con nombres de productos."""
    db  = get_supabase()
    res = (
        db.table("detalle_ventas")
        .select("*, productos(nombre, codigo)")
        .eq("venta_id", venta_id)
        .execute()
    )
    return res.data or []


def get_ventas_por_rango(fecha_inicio: str, fecha_fin: str) -> list:
    """Retorna ventas completadas entre dos fechas (ISO strings)."""
    db  = get_supabase()
    res = (
        db.table("ventas")
        .select("*")
        .gte("fecha", fecha_inicio)
        .lte("fecha", fecha_fin)
        .eq("estado", "completada")
        .order("fecha", desc=True)
        .execute()
    )
    return res.data or []


def get_resumen_ventas(fecha_inicio: str, fecha_fin: str) -> dict:
    """Calcula métricas agregadas de ventas para un rango de fechas."""
    ventas = get_ventas_por_rango(fecha_inicio, fecha_fin)

    if not ventas:
        return {
            "total_transacciones": 0,
            "ingresos_totales":    0.0,
            "descuentos":          0.0,
            "ticket_promedio":     0.0,
            "efectivo":            0.0,
            "qr":                  0.0,
            "tarjeta":             0.0,
        }

    return {
        "total_transacciones": len(ventas),
        "ingresos_totales":    sum(v["total"]     for v in ventas),
        "descuentos":          sum(v["descuento"] for v in ventas),
        "ticket_promedio":     sum(v["total"]     for v in ventas) / len(ventas),
        "efectivo":            sum(v["total"] for v in ventas if v["metodo_pago"] == "efectivo"),
        "qr":                  sum(v["total"] for v in ventas if v["metodo_pago"] == "qr"),
        "tarjeta":             sum(v["total"] for v in ventas if v["metodo_pago"] == "tarjeta"),
    }


def get_productos_mas_vendidos(fecha_inicio: str, fecha_fin: str, limite: int = 10) -> list:
    """Top N productos más vendidos en el rango con ganancia neta."""
    ventas = get_ventas_por_rango(fecha_inicio, fecha_fin)
    if not ventas:
        return []

    venta_ids = [v["id"] for v in ventas]
    db = get_supabase()

    # Traer detalle de todas esas ventas
    det_res = (
        db.table("detalle_ventas")
        .select("cantidad, subtotal, precio_compra, precio_unitario, producto_id, productos(id, nombre, codigo)")
        .in_("venta_id", venta_ids)
        .execute()
    )
    rows = det_res.data or []

    # Agrupar por producto
    agregado: dict = {}
    for r in rows:
        prod = r.get("productos") or {}
        pid  = prod.get("id") or r.get("producto_id")
        if not pid:
            continue
        if pid not in agregado:
            agregado[pid] = {
                "producto_id": pid,
                "nombre":  prod.get("nombre", f"Producto {pid}"),
                "codigo":  prod.get("codigo", ""),
                "unidades": 0,
                "ingresos": 0.0,
                "ganancia": 0.0,
            }
        agregado[pid]["unidades"] += r["cantidad"]
        agregado[pid]["ingresos"] += r["subtotal"]
        agregado[pid]["ganancia"] += r["subtotal"] - r["cantidad"] * r["precio_compra"]

    return sorted(agregado.values(), key=lambda x: x["unidades"], reverse=True)[:limite]