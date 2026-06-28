from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.supabase_client import supabase
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import io

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


class ItemPedido(BaseModel):
    producto_id: int
    cantidad: int
    precio_venta: float


class PedidoCreate(BaseModel):
    cliente: str
    vendedor: Optional[str] = None
    notas: Optional[str] = None
    items: List[ItemPedido]


# ── Rutas SIN parámetros dinámicos PRIMERO ──────────────────────────

@router.get("/")
def get_pedidos(estado: Optional[str] = None):
    query = supabase.table("pedidos").select("*").order("fecha", desc=True)
    if estado:
        query = query.eq("estado", estado)
    return query.execute().data


@router.get("/pendientes")
def get_pedidos_pendientes(vendedor: Optional[str] = None):
    query = supabase.table("pedidos")\
        .select("*")\
        .eq("estado", "pendiente")\
        .order("fecha", desc=True)
    if vendedor:
        query = query.eq("vendedor", vendedor)
    return query.execute().data


# ✅ CRÍTICO: /historial ANTES de /{pedido_id}
@router.get("/historial")
def get_historial(vendedor: Optional[str] = None):
    query = supabase.table("pedidos")\
        .select("*, ventas(numero_venta, total, fecha, metodo_pago)")\
        .order("fecha", desc=True)\
        .limit(100)
    if vendedor:
        query = query.eq("vendedor", vendedor)
    return query.execute().data


@router.post("/")
def crear_pedido(pedido: PedidoCreate):
    numero = f"P-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

    nuevo = supabase.table("pedidos").insert({
        "numero": numero,
        "cliente": pedido.cliente,
        "vendedor": pedido.vendedor,
        "notas": pedido.notas,
        "estado": "pendiente",
        "fecha": datetime.utcnow().isoformat()
    }).execute()

    pedido_id = nuevo.data[0]["id"]

    for item in pedido.items:
        supabase.table("detalle_pedidos").insert({
            "pedido_id": pedido_id,
            "producto_id": item.producto_id,
            "cantidad": item.cantidad,
            "precio_venta": item.precio_venta
        }).execute()

    return {"success": True, "numero": numero, "pedido_id": pedido_id}


# ── Rutas CON parámetros dinámicos DESPUÉS ──────────────────────────

@router.get("/{pedido_id}")
def get_pedido(pedido_id: int):
    pedido = supabase.table("pedidos").select("*").eq("id", pedido_id).execute()
    if not pedido.data:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    detalle = supabase.table("detalle_pedidos")\
        .select("*, productos(nombre, codigo, precio_venta)")\
        .eq("pedido_id", pedido_id)\
        .execute()

    return {**pedido.data[0], "items": detalle.data}


@router.put("/{pedido_id}/cancelar")
def cancelar_pedido(pedido_id: int):
    pedido = supabase.table("pedidos").select("estado").eq("id", pedido_id).execute()
    if not pedido.data:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.data[0]["estado"] != "pendiente":
        raise HTTPException(status_code=400, detail="Solo se pueden cancelar pedidos pendientes")

    supabase.table("pedidos").update({"estado": "cancelado"}).eq("id", pedido_id).execute()
    return {"success": True}


@router.put("/{pedido_id}/entregar")
def entregar_pedido(pedido_id: int, data: dict):
    pedido = supabase.table("pedidos").select("*").eq("id", pedido_id).execute()
    if not pedido.data:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    numero_venta = f"V-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
    items = data.get("items", [])
    total = sum(i["subtotal"] for i in items)

    nueva_venta = supabase.table("ventas").insert({
        "numero_venta": numero_venta,
        "subtotal": total,
        "descuento": 0,
        "total": total,
        "metodo_pago": data.get("metodo_pago", "efectivo"),
        "monto_recibido": data.get("monto_recibido", total),
        "cambio": data.get("monto_recibido", total) - total,
        "notas": f"Pedido {pedido.data[0]['numero']}",
        "estado": "completada"
    }).execute()

    venta_id = nueva_venta.data[0]["id"]

    for item in items:
        supabase.table("detalle_ventas").insert({
            "venta_id": venta_id,
            "producto_id": item["producto_id"],
            "cantidad": item["cantidad"],
            "precio_unitario": item["precio_venta"],
            "precio_compra": item.get("precio_compra", 0),
            "subtotal": item["subtotal"]
        }).execute()

        prod = supabase.table("productos").select("stock").eq("id", item["producto_id"]).execute()
        nuevo_stock = prod.data[0]["stock"] - item["cantidad"]
        supabase.table("productos").update({"stock": nuevo_stock}).eq("id", item["producto_id"]).execute()

        supabase.table("inventario_movimientos").insert({
            "producto_id": item["producto_id"],
            "tipo_movimiento": "egreso",
            "cantidad": item["cantidad"],
            "motivo": f"Venta pedido {pedido.data[0]['numero']}"
        }).execute()

    supabase.table("pedidos").update({
        "estado": "entregado",
        "venta_id": venta_id
    }).eq("id", pedido_id).execute()

    return {"success": True, "numero_venta": numero_venta, "total": total, "venta_id": venta_id}

@router.put("/{pedido_id}/editar")
def editar_pedido(pedido_id: int, data: dict):
    """
    data: {
        "notas": str (opcional),
        "items": [{ producto_id, cantidad, precio_venta }]
    }
    """
    pedido = supabase.table("pedidos").select("estado").eq("id", pedido_id).execute()
    if not pedido.data:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.data[0]["estado"] != "pendiente":
        raise HTTPException(status_code=400, detail="Solo se pueden editar pedidos pendientes")

    # Actualizar notas si vienen
    update_data = {}
    if "notas" in data:
        update_data["notas"] = data["notas"]
    if update_data:
        supabase.table("pedidos").update(update_data).eq("id", pedido_id).execute()

    # Borrar items anteriores y reemplazar con los nuevos
    supabase.table("detalle_pedidos").delete().eq("pedido_id", pedido_id).execute()

    for item in data.get("items", []):
        supabase.table("detalle_pedidos").insert({
            "pedido_id": pedido_id,
            "producto_id": item["producto_id"],
            "cantidad": item["cantidad"],
            "precio_venta": item["precio_venta"]
        }).execute()

    return {"success": True, "mensaje": "Pedido actualizado"}
@router.get("/{pedido_id}/pdf")
def descargar_pdf_pedido(pedido_id: int):
    from fpdf import FPDF

    pedido = supabase.table("pedidos").select("*").eq("id", pedido_id).execute()
    if not pedido.data:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    p = pedido.data[0]

    detalle = supabase.table("detalle_pedidos")\
        .select("*, productos(nombre)")\
        .eq("pedido_id", pedido_id).execute()

    pdf = FPDF(format="A5")
    pdf.add_page()
    pdf.set_margins(12, 12, 12)

    pdf.set_fill_color(255, 107, 43)
    pdf.rect(0, 0, pdf.w, 28, style="F")
    pdf.set_y(6)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, "ALMACEN GLORIA", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Hoja de Pedido", ln=True, align="C")

    pdf.set_y(32)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 6, f"N° Pedido: {p['numero']}", ln=True)
    pdf.cell(0, 6, f"Cliente: {p['cliente']}", ln=True)
    pdf.cell(0, 6, f"Vendedor: {p.get('vendedor', '—')}", ln=True)
    pdf.cell(0, 6, f"Fecha: {p['fecha'][:10]}", ln=True)
    if p.get("notas"):
        pdf.cell(0, 6, f"Notas: {p['notas']}", ln=True)
    pdf.ln(3)

    ancho = pdf.w - 24
    pdf.set_fill_color(255, 235, 210)
    pdf.set_text_color(150, 60, 0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(ancho * 0.6, 7, "PRODUCTO", fill=True)
    pdf.cell(ancho * 0.2, 7, "CANT.", fill=True, align="C")
    pdf.cell(ancho * 0.2, 7, "P. VENTA", fill=True, align="R", ln=True)

    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "", 8)
    for d in detalle.data:
        nombre = (d.get("productos") or {}).get("nombre", "—")
        pdf.cell(ancho * 0.6, 6, nombre[:30])
        pdf.cell(ancho * 0.2, 6, str(d["cantidad"]), align="C")
        pdf.cell(ancho * 0.2, 6, f"Bs. {d['precio_venta']:.2f}", align="R", ln=True)

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "Pedido pendiente de entrega — Almacen Gloria", ln=True, align="C")

    buffer = io.BytesIO(pdf.output())
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=pedido_{p['numero']}.pdf"}
    )