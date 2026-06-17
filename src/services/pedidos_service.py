from datetime import datetime
from typing import Optional
from services.supabase_client import supabase


def generar_numero_pedido() -> str:
    return datetime.now().strftime("P%Y%m%d%H%M%S")

def guardar_pedido(nombre_cliente: str, vendedor: str, items: dict, notas: str = "") -> Optional[dict]:
    """
    Guarda un pedido y su detalle en Supabase.
    items = { producto_id: { nombre, cantidad, precio_venta, ... } }
    Retorna el pedido creado o None si falla.
    """
    try:
        numero = generar_numero_pedido()

        # 1. Insertar cabecera del pedido
        pedido_data = {
            "numero":   numero,
            "cliente":  nombre_cliente,
            "vendedor": vendedor,
            "estado":   "pendiente",
            "notas":    notas,
        }
        res_pedido = supabase.table("pedidos").insert(pedido_data).execute()
        if not res_pedido.data:
            return None

        pedido = res_pedido.data[0]
        pedido_id = pedido["id"]

        # 2. Insertar detalle
        detalle = [
            {
                "pedido_id":   pedido_id,
                "producto_id": int(pid),
                "cantidad":    item["cantidad"],
                "precio_venta": item["precio_venta"],
            }
            for pid, item in items.items()
        ]
        supabase.table("detalle_pedidos").insert(detalle).execute()

        return pedido

    except Exception as e:
        print(f"[pedidos_service] Error al guardar pedido: {e}")
        return None

def obtener_pedidos_pendientes(vendedor: Optional[str] = None) -> list:

    """
    Retorna pedidos con estado 'pendiente'.
    Si se pasa vendedor, filtra por él.
    """
    try:
        query = supabase.table("pedidos").select("*").eq("estado", "pendiente").order("created_at", desc=True)
        if vendedor:
            query = query.eq("vendedor", vendedor)
        res = query.execute()
        return res.data or []
    except Exception as e:
        print(f"[pedidos_service] Error al obtener pedidos: {e}")
        return []


def obtener_detalle_pedido(pedido_id: int) -> list:
    """
    Retorna el detalle de un pedido con info del producto.
    """
    try:
        res = (
            supabase.table("detalle_pedidos")
            .select("*, productos(nombre, precio_venta, stock)")
            .eq("pedido_id", pedido_id)
            .execute()
        )
        return res.data or []
    except Exception as e:
        print(f"[pedidos_service] Error al obtener detalle: {e}")
        return []


def marcar_pedido_entregado(pedido_id: int, venta_id: Optional[int] = None) -> bool:
    try:
        # Tipamos el dict explícitamente para que acepte str e int
        data: dict[str, object] = {"estado": "entregado"}
        if venta_id is not None:
            data["venta_id"] = venta_id

        res = supabase.table("pedidos").update(data).eq("id", pedido_id).execute()
        return bool(res.data)
    except Exception as e:
        print(f"[pedidos_service] Error al marcar entregado: {e}")
        return False

def cancelar_pedido(pedido_id: int) -> bool:
    try:
        res = supabase.table("pedidos").update({"estado": "cancelado"}).eq("id", pedido_id).execute()
        return bool(res.data)
    except Exception as e:
        print(f"[pedidos_service] Error al cancelar pedido: {e}")
        return False
    
