from fastapi import APIRouter
from app.supabase_client import supabase
from datetime import datetime, date

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.get("/ventas-diarias")
def ventas_diarias():
    hoy = date.today().isoformat()
    result = supabase.table("ventas")\
        .select("*")\
        .gte("fecha", f"{hoy}T00:00:00")\
        .lte("fecha", f"{hoy}T23:59:59")\
        .eq("estado", "completada")\
        .execute()

    total = sum(v["total"] for v in result.data)
    return {
        "fecha": hoy,
        "cantidad_ventas": len(result.data),
        "total": total,
        "ventas": result.data
    }

@router.get("/stock-critico")
def stock_critico():
    result = supabase.table("productos")\
        .select("id, codigo, nombre, stock, stock_minimo")\
        .eq("activo", True)\
        .execute()
    criticos = [p for p in result.data if p["stock"] <= p["stock_minimo"]]
    return {"cantidad": len(criticos), "productos": criticos}

@router.get("/resumen")
def resumen_general():
    productos = supabase.table("productos").select("stock, precio_venta, precio_compra, activo").execute()
    activos = [p for p in productos.data if p["activo"]]

    ventas_mes = supabase.table("ventas")\
        .select("total")\
        .gte("fecha", f"{datetime.now().year}-{datetime.now().month:02d}-01")\
        .eq("estado", "completada")\
        .execute()

    return {
        "total_productos": len(activos),
        "valor_inventario": sum(p["stock"] * p["precio_compra"] for p in activos),
        "ventas_mes": sum(v["total"] for v in ventas_mes.data),
        "cantidad_ventas_mes": len(ventas_mes.data)
    }