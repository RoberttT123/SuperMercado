from fastapi import APIRouter
from app.supabase_client import supabase
from datetime import timedelta
from app.core.fechas import hoy_bolivia, dia_bolivia, limites_utc, etiqueta_dia

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Todos los "hoy", "ayer" y "este mes" son en hora de Bolivia (ver app/core/fechas.py).


def _ventas_entre(desde, hasta, campos="id, total, fecha"):
    ini, fin = limites_utc(desde, hasta)
    ventas = supabase.table("ventas").select(campos)\
        .gte("fecha", ini).lte("fecha", fin)\
        .eq("estado", "completada").execute().data
    for v in ventas:
        v["_dia"] = dia_bolivia(v["fecha"])
    return ventas


@router.get("/resumen")
def get_resumen():
    hoy = hoy_bolivia()
    ayer = hoy - timedelta(days=1)
    inicio_mes = hoy.replace(day=1)

    # 1. Ventas desde el inicio del mes (o desde ayer, si hoy es día 1) — cubre hoy, ayer y mes en memoria
    ventas = _ventas_entre(min(inicio_mes, ayer), hoy)
    ventas_mes = [v for v in ventas if v["_dia"] >= inicio_mes]
    ventas_hoy = [v for v in ventas if v["_dia"] == hoy]
    ventas_ayer = [v for v in ventas if v["_dia"] == ayer]
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
    hoy = hoy_bolivia()
    ventas = _ventas_entre(hoy - timedelta(days=6), hoy, campos="total, fecha")

    resultado = []
    for i in range(6, -1, -1):
        d = hoy - timedelta(days=i)
        ventas_dia = [v for v in ventas if v["_dia"] == d]
        resultado.append({
            "dia": etiqueta_dia(d),
            "total": sum(v["total"] for v in ventas_dia),
            "cantidad": len(ventas_dia)
        })
    return resultado


@router.get("/top-productos")
def get_top_productos():
    hoy = hoy_bolivia()
    ventas = _ventas_entre(hoy.replace(day=1), hoy, campos="id, fecha")

    if not ventas:
        return []

    venta_ids = [v["id"] for v in ventas]
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