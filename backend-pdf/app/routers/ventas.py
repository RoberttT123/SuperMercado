from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.supabase_client import supabase
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import io

router = APIRouter(prefix="/ventas", tags=["Ventas"])


class ItemVenta(BaseModel):
    producto_id: int
    nivel_id: int
    cantidad: int
    precio_unitario: float
    precio_compra: float
    subtotal: float


class VentaCreate(BaseModel):
    items: List[ItemVenta]
    metodo_pago: str = "efectivo"
    monto_recibido: Optional[float] = None
    descuento: float = 0
    notas: Optional[str] = None
    caja_id: Optional[int] = None
    cliente_id: Optional[int] = None
    es_credito: bool = False


# ── Rutas SIN parámetros dinámicos PRIMERO ──────────────────────────

@router.get("/")
def get_ventas(caja_id: Optional[int] = None, limit: int = 100):
    query = supabase.table("ventas")\
        .select("*")\
        .order("fecha", desc=True)\
        .limit(limit)
    if caja_id:
        query = query.eq("caja_id", caja_id)
    return query.execute().data


@router.post("/")
def crear_venta(venta: VentaCreate):
    # Validaciones de crédito ANTES de crear nada
    if venta.es_credito:
        if not venta.cliente_id:
            raise HTTPException(status_code=400, detail="Debes seleccionar un cliente para vender a crédito")
        cliente = supabase.table("clientes").select("limite_credito").eq("id", venta.cliente_id).execute()
        if not cliente.data or (cliente.data[0]["limite_credito"] or 0) <= 0:
            raise HTTPException(status_code=400, detail="Este cliente no tiene línea de crédito habilitada")

    subtotal = sum(item.subtotal for item in venta.items)
    total = subtotal - venta.descuento

    # El "cambio" solo aplica a ventas normales en efectivo, no a ventas a crédito
    cambio = 0
    if venta.monto_recibido and not venta.es_credito:
        cambio = venta.monto_recibido - total

    numero = f"V-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"

    # 1. Crear venta
    nueva_venta = supabase.table("ventas").insert({
        "numero_venta": numero,
        "caja_id": venta.caja_id,
        "subtotal": subtotal,
        "descuento": venta.descuento,
        "total": total,
        "metodo_pago": venta.metodo_pago,
        "monto_recibido": venta.monto_recibido,
        "cambio": cambio,
        "notas": venta.notas,
        "estado": "completada",
        "cliente_id": venta.cliente_id,
        "es_credito": venta.es_credito
    }).execute()

    if not nueva_venta.data:
        raise HTTPException(status_code=500, detail="Error al crear la venta")

    venta_id = nueva_venta.data[0]["id"]

    # 2. Insertar TODO el detalle en una sola llamada (batch)
    detalle_rows = [{
        "venta_id": venta_id,
        "producto_id": item.producto_id,
        "nivel_id": item.nivel_id,
        "cantidad": item.cantidad,
        "precio_unitario": item.precio_unitario,
        "precio_compra": item.precio_compra,
        "subtotal": item.subtotal
    } for item in venta.items]
    supabase.table("detalle_ventas").insert(detalle_rows).execute()

    # 3. Descontar stock del nivel exacto + registrar movimientos, en 1 sola llamada
    items_json = [{
        "nivel_id": item.nivel_id,
        "cantidad": item.cantidad
    } for item in venta.items]
    supabase.rpc("procesar_venta_niveles", {"p_items": items_json}).execute()

    # 4. Si es venta a crédito, cargar el saldo pendiente a la cuenta del cliente
    if venta.es_credito and venta.cliente_id:
        saldo_credito = max(0, total - (venta.monto_recibido or 0))
        if saldo_credito > 0:
            supabase.rpc("registrar_cargo_cliente", {
                "p_cliente_id": venta.cliente_id,
                "p_monto": saldo_credito,
                "p_motivo": f"Venta {numero}",
                "p_venta_id": venta_id
            }).execute()

    return {
        "success": True,
        "numero_venta": numero,
        "total": total,
        "cambio": cambio,
        "venta_id": venta_id
    }


# ── Rutas CON parámetros dinámicos DESPUÉS ──────────────────────────

@router.get("/{venta_id}")
def get_venta(venta_id: int):
    venta = supabase.table("ventas")\
        .select("*, clientes(nombre)")\
        .eq("id", venta_id)\
        .execute()
    if not venta.data:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    detalle = supabase.table("detalle_ventas")\
        .select("*, productos(nombre, codigo), producto_niveles(nivel)")\
        .eq("venta_id", venta_id)\
        .execute()

    return {**venta.data[0], "detalle": detalle.data}


@router.get("/{venta_id}/detalle")
def get_detalle_venta(venta_id: int):
    detalles = supabase.table("detalle_ventas")\
        .select("*, productos(nombre, codigo), producto_niveles(nivel)")\
        .eq("venta_id", venta_id)\
        .execute()

    items = []
    for d in detalles.data:
        prod = d.get("productos") or {}
        nivel = d.get("producto_niveles") or {}
        items.append({
            "nombre": prod.get("nombre", "Desconocido"),
            "nivel": nivel.get("nivel"),
            "cantidad": d["cantidad"],
            "precio": d["precio_unitario"],
            "subtotal": d["subtotal"]
        })
    return items


@router.put("/{venta_id}/anular")
def anular_venta(venta_id: int):
    venta = supabase.table("ventas")\
        .select("*")\
        .eq("id", venta_id)\
        .execute()
    if not venta.data:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    if venta.data[0]["estado"] == "anulada":
        raise HTTPException(status_code=400, detail="La venta ya está anulada")

    venta_data = venta.data[0]

    detalle = supabase.table("detalle_ventas")\
        .select("*")\
        .eq("venta_id", venta_id)\
        .execute()

    if detalle.data:
        items_json = [{
            "nivel_id": item["nivel_id"],
            "cantidad": item["cantidad"]
        } for item in detalle.data]
        motivo = f"Anulación venta #{venta_data['numero_venta']}"
        supabase.rpc("revertir_stock_venta_niveles", {"p_items": items_json, "p_motivo": motivo}).execute()

    if venta_data.get("es_credito") and venta_data.get("cliente_id"):
        saldo_cargado = max(0, venta_data["total"] - (venta_data.get("monto_recibido") or 0))
        if saldo_cargado > 0:
            supabase.rpc("registrar_abono_cliente", {
                "p_cliente_id": venta_data["cliente_id"],
                "p_monto": saldo_cargado,
                "p_motivo": f"Reversión por anulación de venta #{venta_data['numero_venta']}"
            }).execute()

    supabase.table("ventas")\
        .update({"estado": "anulada"})\
        .eq("id", venta_id)\
        .execute()

    return {"success": True, "mensaje": "Venta anulada y stock revertido"}


@router.get("/{venta_id}/pdf")
def descargar_pdf_venta(venta_id: int):
    from fpdf import FPDF

    venta = supabase.table("ventas")\
        .select("*, clientes(nombre)")\
        .eq("id", venta_id)\
        .execute()
    if not venta.data:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    v = venta.data[0]

    detalles = supabase.table("detalle_ventas")\
        .select("*, productos(nombre), producto_niveles(nivel)")\
        .eq("venta_id", venta_id)\
        .execute()

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
    pdf.cell(col, 6, f"Fecha: {v['fecha'][:10]}", ln=True, align="R")
    pdf.cell(col, 6, f"Metodo: {metodo_display}")
    pdf.cell(col, 6, f"Estado: {v['estado'].upper()}", ln=True, align="R")

    cliente_nombre = (v.get("clientes") or {}).get("nombre") or "Consumidor final"
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, f"Cliente: {cliente_nombre}", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.ln(2)

    pdf.set_fill_color(255, 235, 210)
    pdf.set_text_color(150, 60, 0)
    pdf.set_font("Helvetica", "B", 8)
    col_prod   = ancho * 0.42
    col_cant   = ancho * 0.13
    col_precio = ancho * 0.22
    col_sub    = ancho * 0.23
    pdf.cell(col_prod,  7, "PRODUCTO",  fill=True)
    pdf.cell(col_cant,  7, "CANT.",     fill=True, align="C")
    pdf.cell(col_precio,7, "P.UNIT.",   fill=True, align="R")
    pdf.cell(col_sub,   7, "SUBTOTAL",  fill=True, align="R", ln=True)

    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "", 8)
    fill = False
    for d in detalles.data:
        nombre = (d.get("productos") or {}).get("nombre", "-")
        nivel_nombre = (d.get("producto_niveles") or {}).get("nivel")
        if nivel_nombre:
            nombre = f"{nombre} ({nivel_nombre})"
        pdf.set_fill_color(252, 248, 244) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_prod,  6, nombre[:32],                              fill=True)
        pdf.cell(col_cant,  6, str(d["cantidad"]),                       fill=True, align="C")
        pdf.cell(col_precio,6, f"Bs. {float(d['precio_unitario']):.2f}", fill=True, align="R")
        pdf.cell(col_sub,   6, f"Bs. {float(d['subtotal']):.2f}",        fill=True, align="R", ln=True)
        fill = not fill

    pdf.ln(2)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.line(12, pdf.get_y(), pdf.w - 12, pdf.get_y())
    pdf.ln(3)

    if v.get("descuento") and float(v["descuento"]) > 0:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(ancho - col_sub, 6, "Descuento:", align="R")
        pdf.cell(col_sub, 6, f"- Bs. {float(v['descuento']):.2f}", align="R", ln=True)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(255, 107, 43)
    pdf.cell(ancho - col_sub, 8, "TOTAL:", align="R")
    pdf.set_text_color(40, 40, 40)
    pdf.cell(col_sub, 8, f"Bs. {float(v['total']):.2f}", align="R", ln=True)

    if v.get("es_credito"):
        pagado = float(v.get("monto_recibido") or 0)
        pendiente = max(0.0, float(v["total"]) - pagado)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(ancho - col_sub, 6, "Pagado ahora:", align="R")
        pdf.cell(col_sub, 6, f"Bs. {pagado:.2f}", align="R", ln=True)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(ancho - col_sub, 6, "Queda a credito:", align="R")
        pdf.cell(col_sub, 6, f"Bs. {pendiente:.2f}", align="R", ln=True)
    elif v.get("cambio") and float(v["cambio"]) > 0:
        pdf.set_font("Helvetica", "", 9)
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
    pdf.cell(0, 5, "Almacen Cori - su tienda de confianza", ln=True, align="C")

    buffer = io.BytesIO(pdf.output())
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Venta_{v['numero_venta']}.pdf"}
    )