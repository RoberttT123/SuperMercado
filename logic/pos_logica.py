from services.supabase_client import supabase
from datetime import datetime


def obtener_productos():
    try:
        response = (
            supabase.table("productos")
            .select("*")
            .eq("activo", True)
            .order("nombre")
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"[pos_logica] Error al obtener productos: {e}")
        return []


def obtener_ultimas_ventas(limite: int = 10):
    try:
        response = (
            supabase.table("ventas")
            .select("*")
            .order("created_at", desc=True)
            .limit(limite)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"[pos_logica] Error al obtener historial: {e}")
        return []


def registrar_venta(carrito: list, total_venta: float, cliente: str = "") -> int | None:
    try:
        numero_venta = datetime.now().strftime("V%Y%m%d%H%M%S")

        venta_data = {
            "numero_venta": numero_venta,
            "subtotal":     total_venta,
            "total":        total_venta,
            "descuento":    0,
            "estado":       "completada",
            "metodo_pago":  "efectivo",
        }
        res_venta = supabase.table("ventas").insert(venta_data).execute()
        if not res_venta.data:
            return None

        venta_id = res_venta.data[0]["id"]

        detalle = []
        for item in carrito:
            cantidad = int(item.get("cantidad") or 1)
            precio_u = float(item["precio_venta"])
            detalle.append({
                "venta_id":        venta_id,
                "producto_id":     item["id"],
                "cantidad":        cantidad,
                "precio_unitario": precio_u,
                "precio_compra":   float(item.get("precio_compra") or 0),
                "subtotal":        round(precio_u * cantidad, 2),
            })
        supabase.table("detalle_ventas").insert(detalle).execute()

        # Descontar stock
        for item in carrito:
            cantidad = int(item.get("cantidad") or 1)
            res_stock = (
                supabase.table("productos")
                .select("stock")
                .eq("id", item["id"])
                .single()
                .execute()
            )
            stock_actual = int(res_stock.data.get("stock") or 0)
            supabase.table("productos").update(
                {"stock": max(0, stock_actual - cantidad)}
            ).eq("id", item["id"]).execute()

        return venta_id

    except Exception as e:
        print(f"[pos_logica] Error al registrar venta: {e}")
        return None

def obtener_detalle_venta(venta_id: int) -> tuple[dict, str]:
    try:
        # 1. Buscar cliente en pedidos (sin tocar tabla ventas)
        nombre_cliente = ""
        try:
            res_pedido = (
                supabase.table("pedidos")
                .select("cliente")
                .eq("venta_id", venta_id)
                .maybe_single()
                .execute()
            )
            if res_pedido.data:
                nombre_cliente = res_pedido.data.get("cliente") or ""
        except Exception:
            pass  # Si no hay pedido vinculado, se queda vacío

        # 2. Detalle de productos
        res = (
            supabase.table("detalle_ventas")
            .select("cantidad, precio_unitario, productos(nombre)")
            .eq("venta_id", venta_id)
            .execute()
        )

        if not res.data:
            return {}, nombre_cliente

        detalle: dict = {}
        for item in res.data:
            prod_info = item.get("productos") or {}
            nombre_prod = prod_info.get("nombre", "Producto desconocido")
            detalle[str(nombre_prod)] = {
                "nombre":       nombre_prod,
                "cantidad":     int(item["cantidad"]),
                "precio_venta": float(item["precio_unitario"]),
            }

        return detalle, nombre_cliente

    except Exception as e:
        print(f"[pos_logica] Error en obtener_detalle_venta: {e}")
        return {}, ""