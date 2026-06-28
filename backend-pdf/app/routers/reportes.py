from fastapi import APIRouter
from app.supabase_client import supabase
from datetime import datetime, date

router = APIRouter(prefix="/reportes", tags=["Reportes"])


def get_ventas_en_rango(inicio: str, fin: str):
    return supabase.table("ventas")\
        .select("*")\
        .gte("fecha", f"{inicio}T00:00:00")\
        .lte("fecha", f"{fin}T23:59:59")\
        .eq("estado", "completada")\
        .execute()


@router.get("/ventas/resumen")
def resumen_ventas(inicio: str, fin: str):
    result = get_ventas_en_rango(inicio, fin)
    ventas = result.data

    ingresos = sum(v["total"] for v in ventas)
    descuentos = sum(v.get("descuento") or 0 for v in ventas)
    cantidad = len(ventas)

    return {
        "total_transacciones": cantidad,
        "ingresos_totales": ingresos,
        "descuentos": descuentos,
        "ticket_promedio": ingresos / cantidad if cantidad > 0 else 0,
        "efectivo": sum(v["total"] for v in ventas if v.get("metodo_pago") == "efectivo"),
        "qr": sum(v["total"] for v in ventas if v.get("metodo_pago") in ["qr", "transferencia"]),
        "tarjeta": sum(v["total"] for v in ventas if v.get("metodo_pago") == "tarjeta"),
    }


@router.get("/ventas/lista")
def lista_ventas(inicio: str, fin: str):
    result = supabase.table("ventas")\
        .select("*")\
        .gte("fecha", f"{inicio}T00:00:00")\
        .lte("fecha", f"{fin}T23:59:59")\
        .order("fecha", desc=True)\
        .execute()
    return result.data


@router.get("/ventas/top-productos")
def top_productos(inicio: str, fin: str):
    ventas = get_ventas_en_rango(inicio, fin)
    if not ventas.data:
        return []

    venta_ids = [v["id"] for v in ventas.data]
    detalles = supabase.table("detalle_ventas")\
        .select("*, productos(codigo, nombre)")\
        .in_("venta_id", venta_ids)\
        .execute()

    # Agrupar por producto
    agrupado = {}
    for d in detalles.data:
        prod = d.get("productos") or {}
        pid = d["producto_id"]
        if pid not in agrupado:
            agrupado[pid] = {
                "codigo": prod.get("codigo", "—"),
                "nombre": prod.get("nombre", "Desconocido"),
                "unidades": 0,
                "ingresos": 0,
                "ganancia": 0
            }
        agrupado[pid]["unidades"] += d["cantidad"]
        agrupado[pid]["ingresos"] += d["subtotal"]
        costo = d.get("precio_compra", 0) * d["cantidad"]
        agrupado[pid]["ganancia"] += d["subtotal"] - costo

    resultado = sorted(agrupado.values(), key=lambda x: x["unidades"], reverse=True)
    return resultado[:20]


@router.get("/stock-critico")
def stock_critico():
    result = supabase.table("productos")\
        .select("codigo, nombre, stock, stock_minimo, categorias(nombre)")\
        .eq("activo", True)\
        .execute()

    criticos = []
    for p in result.data:
        if p["stock"] <= p["stock_minimo"]:
            criticos.append({
                "codigo": p["codigo"],
                "nombre": p["nombre"],
                "categoria": (p.get("categorias") or {}).get("nombre", "—"),
                "stock": p["stock"],
                "minimo": p["stock_minimo"],
                "faltante": p["stock_minimo"] - p["stock"]
            })
    return criticos


@router.get("/rentabilidad")
def rentabilidad(inicio: str, fin: str):
    ventas = get_ventas_en_rango(inicio, fin)
    if not ventas.data:
        return {"ganancia_neta": 0}

    venta_ids = [v["id"] for v in ventas.data]
    detalles = supabase.table("detalle_ventas")\
        .select("subtotal, precio_compra, cantidad")\
        .in_("venta_id", venta_ids)\
        .execute()

    ganancia = sum(
        d["subtotal"] - (d.get("precio_compra", 0) * d["cantidad"])
        for d in detalles.data
    )
    return {"ganancia_neta": ganancia}