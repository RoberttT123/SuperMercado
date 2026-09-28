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

    # 1. Todas las ventas del mes (cubre hoy, ayer y mes en memoria)
    ventas_mes = supabase.table("ventas").select("id, total, fecha")\
        .gte("fecha", mes_ini).lte("fecha", ahora)\
        .eq("estado", "completada").execute().data

    ventas_hoy = [v for v in ventas_mes if hoy_ini <= v["fecha"] <= hoy_fin]
    ventas_ayer = [v for v in ventas_mes if ayer_ini <= v["fecha"] <= ayer_fin]
    venta_ids_mes = [v["id"] for v in ventas_mes]

    # 2. Detalle de ventas del mes — se usa para ganancia neta Y top productos
    ganancia_neta = 0
    top_productos = []
    if venta_ids_mes:
        detalles = supabase.table("detalle_ventas")\
            .select("producto_id, subtotal, precio_compra, cantidad, productos(nombre)")\
            .in_("venta_id", venta_ids_mes).execute().data

        ganancia_neta = sum(d["subtotal"] - (d.get("precio_compra", 0) * d["cantidad"]) for d in detalles)

        agrupado = {}
        for d in detalles:
            pid = d["producto_id"]
            nombre = (d.get("productos") or {}).get("nombre", "Desconocido")
            if pid not in agrupado:
                agrupado[pid] = {"nombre": nombre, "unidades": 0, "ingresos": 0}
            agrupado[pid]["unidades"] += d["cantidad"]
            agrupado[pid]["ingresos"] += d["subtotal"]
        top_productos = sorted(agrupado.values(), key=lambda x: x["unidades"], reverse=True)[:5]

    # 3. Stock crítico — calculado sobre los NIVELES (jaba/caja/paquete), no sobre productos
    niveles = supabase.table("producto_niveles").select("stock, stock_minimo")\
        .eq("activo", True).execute().data
    criticos = sum(1 for n in niveles if n["stock_minimo"] > 0 and n["stock"] <= n["stock_minimo"])

    # 4. Cuentas por cobrar — foto actual, no depende del rango de fechas
    clientes_con_deuda = supabase.table("clientes").select("saldo_pendiente")\
        .gt("saldo_pendiente", 0).eq("activo", True).execute().data
    total_por_cobrar = sum(c["saldo_pendiente"] for c in clientes_con_deuda)

    total_hoy = sum(v["total"] for v in ventas_hoy)
    total_ayer = sum(v["total"] for v in ventas_ayer)
    variacion = ((total_hoy - total_ayer) / total_ayer * 100) if total_ayer > 0 else 0

    return {
        "ventas_hoy": total_hoy,
        "transacciones_hoy": len(ventas_hoy),
        "ventas_ayer": total_ayer,
        "variacion_hoy": round(variacion, 1),
        "ventas_mes": sum(v["total"] for v in ventas_mes),
        "transacciones_mes": len(ventas_mes),
        "ganancia_neta_mes": ganancia_neta,
        "productos_criticos": criticos,
        "top_productos": top_productos,
        "total_por_cobrar": total_por_cobrar,
        "clientes_con_deuda": len(clientes_con_deuda),
    }


@router.get("/ventas-semana")
def get_ventas_semana():
    hoy = date.today()
    hace_6_dias = hoy - timedelta(days=6)
    ini = f"{hace_6_dias}T00:00:00"
    fin = f"{hoy}T23:59:59"

    ventas = supabase.table("ventas").select("total, fecha")\
        .gte("fecha", ini).lte("fecha", fin)\
        .eq("estado", "completada").execute()

    resultado = []
    for i in range(6, -1, -1):
        d = hoy - timedelta(days=i)
        d_str = d.isoformat()
        ventas_dia = [v for v in ventas.data if v["fecha"][:10] == d_str]
        resultado.append({
            "dia": d.strftime("%a %d"),
            "total": sum(v["total"] for v in ventas_dia),
            "cantidad": len(ventas_dia)
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
    result = supabase.table("ventas").select("*, clientes(nombre)")\
        .eq("estado", "completada")\
        .order("fecha", desc=True)\
        .limit(5).execute()

    ventas = []
    for v in result.data:
        row = {**v}
        row["cliente_nombre"] = (v.get("clientes") or {}).get("nombre")
        row.pop("clientes", None)
        ventas.append(row)
    return ventas


@router.get("/stock-critico")
def get_stock_critico():
    result = supabase.table("producto_niveles")\
        .select("nivel, stock, stock_minimo, productos(nombre, categorias(nombre))")\
        .eq("activo", True).execute()

    criticos = []
    for n in result.data:
        if n["stock_minimo"] > 0 and n["stock"] <= n["stock_minimo"]:
            prod = n.get("productos") or {}
            criticos.append({
                "nombre": prod.get("nombre", "Desconocido"),
                "nivel": n["nivel"],
                "stock": n["stock"],
                "stock_minimo": n["stock_minimo"],
                "categoria": (prod.get("categorias") or {}).get("nombre", "—"),
                "faltante": n["stock_minimo"] - n["stock"]
            })
    return sorted(criticos, key=lambda x: x["stock"])[:5]


@router.get("/cuentas-por-cobrar")
def get_cuentas_por_cobrar():
    result = supabase.table("clientes")\
        .select("id, nombre, telefono, saldo_pendiente, limite_credito")\
        .gt("saldo_pendiente", 0).eq("activo", True)\
        .order("saldo_pendiente", desc=True)\
        .limit(5).execute()
    return result.data