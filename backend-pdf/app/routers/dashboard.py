from fastapi import APIRouter
from app.supabase_client import supabase
from datetime import datetime, date, timedelta

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def fecha_inicio_fin(dias_atras=0):
    d = date.today() - timedelta(days=dias_atras)
    return f"{d}T00:00:00", f"{d}T23:59:59"


@router.get("/resumen")
def get_resumen():
    hoy_ini, hoy_fin = fecha_inicio_fin(0)
    ayer_ini, ayer_fin = fecha_inicio_fin(1)
    mes_ini = f"{date.today().year}-{date.today().month:02d}-01T00:00:00"
    ahora = datetime.utcnow().isoformat()

    # Ventas hoy
    ventas_hoy = supabase.table("ventas").select("total, metodo_pago")\
        .gte("fecha", hoy_ini).lte("fecha", hoy_fin)\
        .eq("estado", "completada").execute()

    # Ventas ayer
    ventas_ayer = supabase.table("ventas").select("total")\
        .gte("fecha", ayer_ini).lte("fecha", ayer_fin)\
        .eq("estado", "completada").execute()

    # Ventas mes
    ventas_mes = supabase.table("ventas").select("total")\
        .gte("fecha", mes_ini).lte("fecha", ahora)\
        .eq("estado", "completada").execute()

    # Ganancia neta del mes
    venta_ids_mes = [v["id"] for v in supabase.table("ventas")\
        .select("id").gte("fecha", mes_ini).eq("estado", "completada").execute().data]

    ganancia_neta = 0
    if venta_ids_mes:
        detalles = supabase.table("detalle_ventas")\
            .select("subtotal, precio_compra, cantidad")\
            .in_("venta_id", venta_ids_mes).execute()
        ganancia_neta = sum(
            d["subtotal"] - (d.get("precio_compra", 0) * d["cantidad"])
            for d in detalles.data
        )

    # Stock crítico
    productos = supabase.table("productos").select("stock, stock_minimo")\
        .eq("activo", True).execute()
    criticos = sum(1 for p in productos.data if p["stock"] <= p["stock_minimo"])

    total_hoy = sum(v["total"] for v in ventas_hoy.data)
    total_ayer = sum(v["total"] for v in ventas_ayer.data)
    variacion = ((total_hoy - total_ayer) / total_ayer * 100) if total_ayer > 0 else 0

    return {
        "ventas_hoy": total_hoy,
        "transacciones_hoy": len(ventas_hoy.data),
        "ventas_ayer": total_ayer,
        "variacion_hoy": round(variacion, 1),
        "ventas_mes": sum(v["total"] for v in ventas_mes.data),
        "transacciones_mes": len(ventas_mes.data),
        "ganancia_neta_mes": ganancia_neta,
        "productos_criticos": criticos,
    }


@router.get("/ventas-semana")
def get_ventas_semana():
    resultado = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        ini = f"{d}T00:00:00"
        fin = f"{d}T23:59:59"
        ventas = supabase.table("ventas").select("total")\
            .gte("fecha", ini).lte("fecha", fin)\
            .eq("estado", "completada").execute()
        resultado.append({
            "dia": d.strftime("%a %d"),
            "total": sum(v["total"] for v in ventas.data),
            "cantidad": len(ventas.data)
        })
    return resultado


@router.get("/top-productos")
def get_top_productos():
    mes_ini = f"{date.today().year}-{date.today().month:02d}-01T00:00:00"
    ahora = datetime.utcnow().isoformat()

    ventas = supabase.table("ventas").select("id")\
        .gte("fecha", mes_ini).lte("fecha", ahora)\
        .eq("estado", "completada").execute()

    if not ventas.data:
        return []

    venta_ids = [v["id"] for v in ventas.data]
    detalles = supabase.table("detalle_ventas")\
        .select("producto_id, cantidad, subtotal, productos(nombre)")\
        .in_("venta_id", venta_ids).execute()

    agrupado = {}
    for d in detalles.data:
        pid = d["producto_id"]
        nombre = (d.get("productos") or {}).get("nombre", "Desconocido")
        if pid not in agrupado:
            agrupado[pid] = {"nombre": nombre, "unidades": 0, "ingresos": 0}
        agrupado[pid]["unidades"] += d["cantidad"]
        agrupado[pid]["ingresos"] += d["subtotal"]

    return sorted(agrupado.values(), key=lambda x: x["unidades"], reverse=True)[:5]


@router.get("/ultimas-ventas")
def get_ultimas_ventas():
    result = supabase.table("ventas").select("*")\
        .eq("estado", "completada")\
        .order("fecha", desc=True)\
        .limit(5).execute()
    return result.data


@router.get("/stock-critico")
def get_stock_critico():
    result = supabase.table("productos")\
        .select("nombre, stock, stock_minimo, categorias(nombre)")\
        .eq("activo", True).execute()
    criticos = [
        {
            "nombre": p["nombre"],
            "stock": p["stock"],
            "stock_minimo": p["stock_minimo"],
            "categoria": (p.get("categorias") or {}).get("nombre", "—"),
            "faltante": p["stock_minimo"] - p["stock"]
        }
        for p in result.data if p["stock"] <= p["stock_minimo"]
    ]
    return sorted(criticos, key=lambda x: x["stock"])[:5]