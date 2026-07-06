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
    subtotal = sum(item.subtotal for item in venta.items)
    total = subtotal - venta.descuento
    cambio = (venta.monto_recibido - total) if venta.monto_recibido else 0
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
        "estado": "completada"
    }).execute()

    if not nueva_venta.data:
        raise HTTPException(status_code=500, detail="Error al crear la venta")

    venta_id = nueva_venta.data[0]["id"]

    for item in venta.items:
        # 2. Insertar detalle
        supabase.table("detalle_ventas").insert({
            "venta_id": venta_id,
            "producto_id": item.producto_id,
            "cantidad": item.cantidad,
            "precio_unitario": item.precio_unitario,
            "precio_compra": item.precio_compra,
            "subtotal": item.subtotal
        }).execute()

        # 3. Descontar stock
        prod = supabase.table("productos")\
            .select("stock")\
            .eq("id", item.producto_id)\
            .execute()
        if prod.data:
            nuevo_stock = prod.data[0]["stock"] - item.cantidad
            supabase.table("productos")\
                .update({"stock": nuevo_stock})\
                .eq("id", item.producto_id)\
                .execute()

        # 4. Registrar movimiento de inventario
        supabase.table("inventario_movimientos").insert({
            "producto_id": item.producto_id,
            "tipo_movimiento": "egreso",
            "cantidad": item.cantidad,
            "motivo": f"Venta #{numero}"
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
        .select("*")\
        .eq("id", venta_id)\
        .execute()
    if not venta.data:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    detalle = supabase.table("detalle_ventas")\
        .select("*, productos(nombre, codigo)")\
        .eq("venta_id", venta_id)\
        .execute()

    return {**venta.data[0], "detalle": detalle.data}


@router.get("/{venta_id}/detalle")
def get_detalle_venta(venta_id: int):
    detalles = supabase.table("detalle_ventas")\
        .select("*, productos(nombre, codigo)")\
        .eq("venta_id", venta_id)\
        .execute()

    items = []
    for d in detalles.data:
        prod = d.get("productos") or {}
        items.append({
            "nombre": prod.get("nombre", "Desconocido"),
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

    # Revertir stock
    detalle = supabase.table("detalle_ventas")\
        .select("*")\
        .eq("venta_id", venta_id)\
        .execute()

    for item in detalle.data:
        prod = supabase.table("productos")\
            .select("stock")\
            .eq("id", item["producto_id"])\
            .execute()
        if prod.data:
            nuevo_stock = prod.data[0]["stock"] + item["cantidad"]
            supabase.table("productos")\
                .update({"stock": nuevo_stock})\
                .eq("id", item["producto_id"])\
                .execute()

            # Registrar movimiento de reversión
            supabase.table("inventario_movimientos").insert({
                "producto_id": item["producto_id"],
                "tipo_movimiento": "ingreso",
                "cantidad": item["cantidad"],
                "motivo": f"Anulación venta #{venta.data[0]['numero_venta']}"
            }).execute()

    supabase.table("ventas")\
        .update({"estado": "anulada"})\
        .eq("id", venta_id)\
        .execute()

    return {"success": True, "mensaje": "Venta anulada y stock revertido"}


@router.get("/{venta_id}/pdf")
def descargar_pdf_venta(venta_id: int):
    from fpdf import FPDF

    # Datos de la venta
    venta = supabase.table("ventas")\
        .select("*")\
        .eq("id", venta_id)\
        .execute()
    if not venta.data:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    v = venta.data[0]

    detalles = supabase.table("detalle_ventas")\
        .select("*, productos(nombre)")\
        .eq("venta_id", venta_id)\
        .execute()

    # Generar PDF A5
    pdf = FPDF(format="A5")
    pdf.add_page()
    pdf.set_margins(12, 12, 12)
    ancho = pdf.w - 24

    # Header naranja
    pdf.set_fill_color(255, 107, 43)
    pdf.rect(0, 0, pdf.w, 30, style="F")
    pdf.set_y(6)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, "ALMACEN GLORIA", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Nota de Venta", ln=True, align="C")

    # Info venta
    pdf.set_y(34)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("Helvetica", "", 8)
    col = ancho / 2
    pdf.cell(col, 6, f"N° Venta: {v['numero_venta']}")
    pdf.cell(col, 6, f"Fecha: {v['fecha'][:10]}", ln=True, align="R")
    pdf.cell(col, 6, f"Método: {v['metodo_pago'].upper()}")
    pdf.cell(col, 6, f"Estado: {v['estado'].upper()}", ln=True, align="R")
    pdf.ln(2)

    # Tabla de productos
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
        nombre = (d.get("productos") or {}).get("nombre", "—")
        pdf.set_fill_color(252, 248, 244) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_prod,  6, nombre[:28],                              fill=True)
        pdf.cell(col_cant,  6, str(d["cantidad"]),                       fill=True, align="C")
        pdf.cell(col_precio,6, f"Bs. {float(d['precio_unitario']):.2f}", fill=True, align="R")
        pdf.cell(col_sub,   6, f"Bs. {float(d['subtotal']):.2f}",        fill=True, align="R", ln=True)
        fill = not fill

    pdf.ln(2)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.line(12, pdf.get_y(), pdf.w - 12, pdf.get_y())
    pdf.ln(3)

    # Descuento si hubo
    if v.get("descuento") and float(v["descuento"]) > 0:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(ancho - col_sub, 6, "Descuento:", align="R")
        pdf.cell(col_sub, 6, f"- Bs. {float(v['descuento']):.2f}", align="R", ln=True)

    # Total
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(255, 107, 43)
    pdf.cell(ancho - col_sub, 8, "TOTAL:", align="R")
    pdf.set_text_color(40, 40, 40)
    pdf.cell(col_sub, 8, f"Bs. {float(v['total']):.2f}", align="R", ln=True)

    # Cambio si hubo
    if v.get("cambio") and float(v["cambio"]) > 0:
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
    pdf.cell(0, 5, "¡Gracias por su compra!", ln=True, align="C")
    pdf.cell(0, 5, "Almacen Gloria — su tienda de confianza", ln=True, align="C")

    buffer = io.BytesIO(pdf.output())
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Venta_{v['numero_venta']}.pdf"}
    )