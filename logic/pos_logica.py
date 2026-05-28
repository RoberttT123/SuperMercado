from services.supabase_client import supabase
import uuid

def obtener_productos():
    try:
        # Traemos solo los activos
        response = supabase.table("productos").select("*").eq("activo", True).execute()
        return response.data
    except Exception as e:
        print(f"Error: {e}")
        return []

def registrar_venta(carrito, total_venta):
    try:
        # 1. Crear la cabecera de la venta
        # Usamos un numero_venta único
        numero_venta = str(uuid.uuid4())[:8].upper()
        
        venta_data = {
            "numero_venta": numero_venta,
            "total": total_venta,
            "subtotal": total_venta,
            "estado": "completada"
        }
        
        res_venta = supabase.table("ventas").insert(venta_data).execute()
        venta_id = res_venta.data[0]['id']
        
        # 2. Insertar cada producto en detalle_ventas
        for item in carrito:
            detalle = {
                "venta_id": venta_id,
                "producto_id": item['id'],
                "cantidad": 1, 
                "precio_unitario": item['precio_venta'],
                "precio_compra": item['precio_compra'], # Importante para ganancia
                "subtotal": item['precio_venta']
            }
            supabase.table("detalle_ventas").insert(detalle).execute()
            
        return True
    except Exception as e:
        print(f"Error al registrar venta: {e}")
        return False