from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

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

@router.get("/")
def get_ventas():
    result = supabase.table("ventas")\
        .select("*")\
        .order("fecha", desc=True)\
        .limit(100)\
        .execute()
    return result.data

@router.get("/{venta_id}")
def get_venta(venta_id: int):
    venta = supabase.table("ventas").select("*").eq("id", venta_id).execute()
    if not venta.data:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    detalle = supabase.table("detalle_ventas")\
        .select("*, productos(nombre, codigo)")\
        .eq("venta_id", venta_id)\
        .execute()
    return {**venta.data[0], "detalle": detalle.data}

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
        prod = supabase.table("productos").select("stock").eq("id", item.producto_id).execute()
        nuevo_stock = prod.data[0]["stock"] - item.cantidad
        supabase.table("productos").update({"stock": nuevo_stock}).eq("id", item.producto_id).execute()

        # 4. Registrar movimiento
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

@router.put("/{venta_id}/anular")
def anular_venta(venta_id: int):
    venta = supabase.table("ventas").select("*").eq("id", venta_id).execute()
    if not venta.data:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    if venta.data[0]["estado"] == "anulada":
        raise HTTPException(status_code=400, detail="La venta ya está anulada")

    # Revertir stock
    detalle = supabase.table("detalle_ventas").select("*").eq("venta_id", venta_id).execute()
    for item in detalle.data:
        prod = supabase.table("productos").select("stock").eq("id", item["producto_id"]).execute()
        nuevo_stock = prod.data[0]["stock"] + item["cantidad"]
        supabase.table("productos").update({"stock": nuevo_stock}).eq("id", item["producto_id"]).execute()

    supabase.table("ventas").update({"estado": "anulada"}).eq("id", venta_id).execute()
    return {"success": True, "mensaje": "Venta anulada y stock revertido"}

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


@router.get("/{venta_id}/pdf")
def descargar_pdf(venta_id: int):
    from fastapi.responses import StreamingResponse
    from fpdf import FPDF
    import io

    # Datos de la venta
    venta = supabase.table("ventas").select("*").eq("id", venta_id).execute()
    if not venta.data:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    v = venta.data[0]

    detalles = supabase.table("detalle_ventas")\
        .select("*, productos(nombre)")\
        .eq("venta_id", venta_id).execute()

    # Generar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "FACTURA DE VENTA", ln=True, align="C")
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 8, f"Nro: {v['numero_venta']}", ln=True)
    pdf.cell(0, 8, f"Fecha: {v['fecha']}", ln=True)
    pdf.cell(0, 8, f"Metodo de pago: {v['metodo_pago']}", ln=True)
    pdf.ln(5)

    # Tabla de productos
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(90, 8, "Producto", border=1)
    pdf.cell(25, 8, "Cant.", border=1, align="C")
    pdf.cell(35, 8, "P. Unit.", border=1, align="R")
    pdf.cell(35, 8, "Subtotal", border=1, align="R")
    pdf.ln()

    pdf.set_font("Helvetica", size=10)
    for d in detalles.data:
        nombre = (d.get("productos") or {}).get("nombre", "—")
        pdf.cell(90, 8, nombre[:40], border=1)
        pdf.cell(25, 8, str(d["cantidad"]), border=1, align="C")
        pdf.cell(35, 8, f"Bs. {d['precio_unitario']:.2f}", border=1, align="R")
        pdf.cell(35, 8, f"Bs. {d['subtotal']:.2f}", border=1, align="R")
        pdf.ln()

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"TOTAL: Bs. {v['total']:.2f}", align="R")

    # Devolver como stream
    buffer = io.BytesIO(pdf.output())
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Venta_{v['numero_venta']}.pdf"}
    )