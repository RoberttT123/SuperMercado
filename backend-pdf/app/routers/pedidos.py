from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.supabase_client import supabase
from app.core.fechas import ahora_bolivia, texto_fecha
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import io

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


class ItemPedido(BaseModel):
    producto_id: int
    nivel_id: int
    cantidad: int
    precio_venta: float


class PedidoCreate(BaseModel):
    cliente: str
    cliente_id: Optional[int] = None
    vendedor: Optional[str] = None
    notas: Optional[str] = None
    items: List[ItemPedido]


def _adjuntar_cliente_registrado(filas: list) -> list:
    for f in filas:
        f["cliente_registrado"] = f.get("clientes")
        f.pop("clientes", None)
    return filas


# ── Rutas SIN parámetros dinámicos PRIMERO ──────────────────────────

@router.get("/")
def get_pedidos(estado: Optional[str] = None):
    query = supabase.table("pedidos")\
        .select("*, clientes(nombre, saldo_pendiente, limite_credito)")\
        .order("fecha", desc=True)
    if estado:
        query = query.eq("estado", estado)
    return _adjuntar_cliente_registrado(query.execute().data)


@router.get("/pendientes")
def get_pedidos_pendientes(vendedor: Optional[str] = None):
    query = supabase.table("pedidos")\
        .select("*, clientes(nombre, saldo_pendiente, limite_credito)")\
        .eq("estado", "pendiente")\
        .order("fecha", desc=True)
    if vendedor:
        query = query.eq("vendedor", vendedor)
    return _adjuntar_cliente_registrado(query.execute().data)


@router.get("/historial")
def get_historial(vendedor: Optional[str] = None):
    query = supabase.table("pedidos")\
        .select("*, ventas(numero_venta, total, fecha, metodo_pago), clientes(nombre, saldo_pendiente, limite_credito)")\
        .order("fecha", desc=True)\
        .limit(100)
    if vendedor:
        query = query.eq("vendedor", vendedor)
    return _adjuntar_cliente_registrado(query.execute().data)


@router.post("/")
def crear_pedido(pedido: PedidoCreate):
    numero = f"P-{ahora_bolivia().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

    nuevo = supabase.table("pedidos").insert({
        "numero": numero,
        "cliente": pedido.cliente,
        "cliente_id": pedido.cliente_id,
        "vendedor": pedido.vendedor,
        "notas": pedido.notas,
        "estado": "pendiente",
        "fecha": datetime.utcnow().isoformat()
    }).execute()

    pedido_id = nuevo.data[0]["id"]

    detalle_rows = [{
        "pedido_id": pedido_id,
        "producto_id": item.producto_id,
        "nivel_id": item.nivel_id,
        "cantidad": item.cantidad,
        "precio_venta": item.precio_venta
    } for item in pedido.items]
    if detalle_rows:
        supabase.table("detalle_pedidos").insert(detalle_rows).execute()

    return {"success": True, "numero": numero, "pedido_id": pedido_id}


@router.get("/{pedido_id}/pdf")
def descargar_pdf_pedido(pedido_id: int):
    from fpdf import FPDF

    pedido = supabase.table("pedidos").select("*").eq("id", pedido_id).execute()
    if not pedido.data:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    p = pedido.data[0]

    detalle = supabase.table("detalle_pedidos")\
        .select("*, productos(nombre), producto_niveles(nivel)")\
        .eq("pedido_id", pedido_id).execute()

    pdf = FPDF(format="A5")
    pdf.add_page()
    pdf.set_margins(12, 12, 12)

    pdf.set_fill_color(255, 107, 43)
    pdf.rect(0, 0, pdf.w, 28, style="F")
    pdf.set_y(6)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, "ALMACEN CORI", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Hoja de Pedido", ln=True, align="C")

    pdf.set_y(32)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 6, f"N. Pedido: {p['numero']}", ln=True)
    pdf.cell(0, 6, f"Cliente: {p['cliente']}", ln=True)
    pdf.cell(0, 6, f"Vendedor: {p.get('vendedor', '-')}", ln=True)
    pdf.cell(0, 6, f"Fecha: {texto_fecha(p['fecha'], con_hora=True)}", ln=True)
    if p.get("notas"):
        pdf.cell(0, 6, f"Notas: {p['notas']}", ln=True)
    pdf.ln(3)

    ancho = pdf.w - 24
    pdf.set_fill_color(255, 235, 210)
    pdf.set_text_color(150, 60, 0)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(ancho * 0.45, 7, "PRODUCTO", fill=True)
    pdf.cell(ancho * 0.2, 7, "NIVEL", fill=True, align="C")
    pdf.cell(ancho * 0.15, 7, "CANT.", fill=True, align="C")
    pdf.cell(ancho * 0.2, 7, "P. VENTA", fill=True, align="R", ln=True)

    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "", 8)
    for d in detalle.data:
        nombre = (d.get("productos") or {}).get("nombre", "-")
        nivel_nombre = (d.get("producto_niveles") or {}).get("nivel", "-")
        pdf.cell(ancho * 0.45, 6, nombre[:24])
        pdf.cell(ancho * 0.2, 6, nivel_nombre, align="C")
        pdf.cell(ancho * 0.15, 6, str(d["cantidad"]), align="C")
        pdf.cell(ancho * 0.2, 6, f"Bs. {d['precio_venta']:.2f}", align="R", ln=True)

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "Pedido pendiente de entrega - Almacen Cori", ln=True, align="C")

    buffer = io.BytesIO(pdf.output())
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=pedido_{p['numero']}.pdf"}
    )


@router.get("/{pedido_id}/nota-venta")
def nota_venta_pdf(pedido_id: int):
    from fpdf import FPDF

    pedido_result = supabase.table("pedidos").select("*").eq("id", pedido_id).execute()
    if not pedido_result.data:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    p = pedido_result.data[0]

    if not p.get("venta_id"):
        raise HTTPException(status_code=400, detail="Este pedido aun no tiene venta asociada")

    venta_result = supabase.table("ventas").select("*").eq("id", p["venta_id"]).execute()
    if not venta_result.data:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    v = venta_result.data[0]

    detalle = supabase.table("detalle_ventas")\
        .select("*, productos(nombre), producto_niveles(nivel)")\
        .eq("venta_id", p["venta_id"]).execute()

    pdf = FPDF(format="A5")
    pdf.add_page()
    pdf.set_margins(12, 12, 12)
    ancho = pdf.w - 24

    pdf.set_fill_color(255, 107, 43)
    pdf.rect(0, 0, pdf.w, 30, style="F")
    pdf.set_y(6)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, "ALMACEN CORI", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Nota de Venta", ln=True, align="C")

    pdf.set_y(34)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("Helvetica", "", 8)

    col = ancho / 2
    metodo_display = "CREDITO" if v.get("es_credito") else v['metodo_pago'].upper()
    pdf.cell(col, 6, f"N. Venta: {v['numero_venta']}")
    pdf.cell(col, 6, f"Fecha: {texto_fecha(v['fecha'], con_hora=True)}", ln=True, align="R")
    pdf.cell(col, 6, f"N. Pedido: {p['numero']}")
    pdf.cell(col, 6, f"Metodo: {metodo_display}", ln=True, align="R")

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(40, 40, 40)
    cliente = p.get("cliente") or "Consumidor final"
    pdf.cell(0, 7, f"Cliente: {cliente}", ln=True)
    if p.get("vendedor"):
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Vendedor: {p['vendedor']}", ln=True)
    pdf.ln(2)

    pdf.set_draw_color(255, 107, 43)
    pdf.set_line_width(0.5)
    pdf.line(12, pdf.get_y(), pdf.w - 12, pdf.get_y())
    pdf.ln(3)

    pdf.set_fill_color(255, 235, 210)
    pdf.set_text_color(150, 60, 0)
    pdf.set_font("Helvetica", "B", 8)
    col_prod   = ancho * 0.36
    col_nivel  = ancho * 0.17
    col_cant   = ancho * 0.13
    col_precio = ancho * 0.17
    col_sub    = ancho * 0.17
    pdf.cell(col_prod,  7, "PRODUCTO",  fill=True)
    pdf.cell(col_nivel, 7, "NIVEL",     fill=True, align="C")
    pdf.cell(col_cant,  7, "CANT.",     fill=True, align="C")
    pdf.cell(col_precio,7, "P.UNIT.",   fill=True, align="R")
    pdf.cell(col_sub,   7, "SUBTOTAL",  fill=True, align="R", ln=True)

    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "", 8)
    fill = False
    for d in detalle.data:
        nombre = (d.get("productos") or {}).get("nombre", "-")
        nivel_nombre = (d.get("producto_niveles") or {}).get("nivel", "-")
        sub = float(d["subtotal"])
        pdf.set_fill_color(252, 248, 244) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_prod,  6, nombre[:22],                          fill=True)
        pdf.cell(col_nivel, 6, nivel_nombre,                         fill=True, align="C")
        pdf.cell(col_cant,  6, str(d["cantidad"]),                   fill=True, align="C")
        pdf.cell(col_precio,6, f"Bs. {float(d['precio_unitario']):.2f}", fill=True, align="R")
        pdf.cell(col_sub,   6, f"Bs. {sub:.2f}",                    fill=True, align="R", ln=True)
        fill = not fill

    pdf.ln(2)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.line(12, pdf.get_y(), pdf.w - 12, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(255, 107, 43)
    pdf.cell(ancho - col_sub, 8, "TOTAL PAGADO:", align="R")
    pdf.set_text_color(40, 40, 40)
    pdf.cell(col_sub, 8, f"Bs. {float(v['total']):.2f}", align="R", ln=True)

    if v.get("es_credito"):
        pagado = float(v.get("monto_recibido") or 0)
        pendiente = max(0.0, float(v["total"]) - pagado)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(ancho - col_sub, 6, "Pagado ahora:", align="R")
        pdf.cell(col_sub, 6, f"Bs. {pagado:.2f}", align="R", ln=True)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(ancho - col_sub, 6, "Queda a credito:", align="R")
        pdf.cell(col_sub, 6, f"Bs. {pendiente:.2f}", align="R", ln=True)
    elif v.get("cambio") and float(v["cambio"]) > 0:
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(ancho - col_sub, 6, "Cambio:", align="R")
        pdf.cell(col_sub, 6, f"Bs. {float(v['cambio']):.2f}", align="R", ln=True)

    pdf.ln(5)
    pdf.set_draw_color(255, 107, 43)
    pdf.set_line_width(0.5)
    pdf.line(12, pdf.get_y(), pdf.w - 12, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "Gracias por su compra!", ln=True, align="C")
    pdf.cell(0, 5, "Almacen Cori - Su tienda de confianza", ln=True, align="C")

    buffer = io.BytesIO(pdf.output())
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=nota_venta_{v['numero_venta']}.pdf"}
    )


@router.get("/{pedido_id}")
def get_pedido(pedido_id: int):
    pedido = supabase.table("pedidos")\
        .select("*, clientes(nombre, saldo_pendiente, limite_credito)")\
        .eq("id", pedido_id).execute()
    if not pedido.data:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    detalle = supabase.table("detalle_pedidos")\
        .select("*, productos(nombre, codigo, precio_venta), producto_niveles(nivel, precio_venta, precio_compra, stock)")\
        .eq("pedido_id", pedido_id)\
        .execute()

    resultado = _adjuntar_cliente_registrado(pedido.data)[0]
    return {**resultado, "items": detalle.data}


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
    """
    data: {
      metodo_pago, monto_recibido, es_credito (bool),
      items: [{ producto_id, nivel_id, cantidad, precio_venta, precio_compra?, subtotal }]
    }
    """
    pedido = supabase.table("pedidos").select("*").eq("id", pedido_id).execute()
    if not pedido.data:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    p = pedido.data[0]

    es_credito = data.get("es_credito", False)
    cliente_id = p.get("cliente_id")

    if es_credito:
        if not cliente_id:
            raise HTTPException(status_code=400, detail="Este pedido no está vinculado a un cliente registrado, no se puede entregar a crédito")
        cliente = supabase.table("clientes").select("limite_credito").eq("id", cliente_id).execute()
        if not cliente.data or (cliente.data[0]["limite_credito"] or 0) <= 0:
            raise HTTPException(status_code=400, detail="Este cliente no tiene línea de crédito habilitada")

    numero_venta = f"V-{ahora_bolivia().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
    items = data.get("items", [])
    total = sum(i["subtotal"] for i in items)
    monto_recibido = data.get("monto_recibido", total)

    cambio = 0
    if monto_recibido and not es_credito:
        cambio = monto_recibido - total

    nueva_venta = supabase.table("ventas").insert({
        "numero_venta": numero_venta,
        "subtotal": total,
        "descuento": 0,
        "total": total,
        "metodo_pago": data.get("metodo_pago", "efectivo"),
        "monto_recibido": monto_recibido,
        "cambio": cambio,
        "notas": f"Pedido {p['numero']}",
        "estado": "completada",
        "cliente_id": cliente_id,
        "es_credito": es_credito
    }).execute()

    venta_id = nueva_venta.data[0]["id"]

    detalle_rows = [{
        "venta_id": venta_id,
        "producto_id": item["producto_id"],
        "nivel_id": item["nivel_id"],
        "cantidad": item["cantidad"],
        "precio_unitario": item["precio_venta"],
        "precio_compra": item.get("precio_compra", 0),
        "subtotal": item["subtotal"]
    } for item in items]
    if detalle_rows:
        supabase.table("detalle_ventas").insert(detalle_rows).execute()

    items_json = [{"nivel_id": item["nivel_id"], "cantidad": item["cantidad"]} for item in items]
    if items_json:
        supabase.rpc("procesar_venta_niveles", {"p_items": items_json}).execute()

    if es_credito and cliente_id:
        saldo_credito = max(0, total - monto_recibido)
        if saldo_credito > 0:
            supabase.rpc("registrar_cargo_cliente", {
                "p_cliente_id": cliente_id,
                "p_monto": saldo_credito,
                "p_motivo": f"Pedido entregado {p['numero']}",
                "p_venta_id": venta_id
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
        "items": [{ producto_id, nivel_id, cantidad, precio_venta }]
    }
    """
    pedido = supabase.table("pedidos").select("estado").eq("id", pedido_id).execute()
    if not pedido.data:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.data[0]["estado"] != "pendiente":
        raise HTTPException(status_code=400, detail="Solo se pueden editar pedidos pendientes")

    update_data = {}
    if "notas" in data:
        update_data["notas"] = data["notas"]
    if update_data:
        supabase.table("pedidos").update(update_data).eq("id", pedido_id).execute()

    supabase.table("detalle_pedidos").delete().eq("pedido_id", pedido_id).execute()

    items = data.get("items", [])
    if items:
        detalle_rows = [{
            "pedido_id": pedido_id,
            "producto_id": item["producto_id"],
            "nivel_id": item["nivel_id"],
            "cantidad": item["cantidad"],
            "precio_venta": item["precio_venta"]
        } for item in items]
        supabase.table("detalle_pedidos").insert(detalle_rows).execute()

    return {"success": True, "mensaje": "Pedido actualizado"}