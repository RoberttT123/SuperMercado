import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import sys, os
from typing import Optional

sys.path.append(os.path.abspath("src"))
from logic.pos_logica import obtener_productos, registrar_venta, obtener_ultimas_ventas, obtener_detalle_venta
from services.pedidos_service import (
    guardar_pedido,
    obtener_pedidos_pendientes,
    obtener_detalle_pedido,
    marcar_pedido_entregado,
    cancelar_pedido,
)

# ─── GUARDIA ────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("main.py")

# ─── ESTADO ─────────────────────────────────────────────────────────────
for key, default in [
    ("carrito", {}),
    ("pedido_items", {}),
    ("ultima_venta", None),
    ("pedido_cargado_id", None),
    ("ultimo_pedido_guardado", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

vendedor = st.session_state.get("username", "vendedor")

# ─── CSS ────────────────────────────────────────────────────────────────
with open("logic/css/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# FUNCIONES PDF
# ═══════════════════════════════════════════════════════════════════════

def _encabezado_pdf(pdf: FPDF, titulo: str, numero: str) -> None:
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "ALMACEN GLORIA", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, titulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 6, f"N° {numero}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 6, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(4)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)

def generar_pdf_nota_venta(carrito: dict, total: float, numero: str, nombre_cliente: str) -> bytes:
    pdf = FPDF(format="A5")
    pdf.add_page()
    pdf.set_margins(12, 12, 12)
    ancho = pdf.w - 24

    pdf.set_fill_color(255, 107, 43)
    pdf.rect(0, 0, pdf.w, 28, style="F")

    pdf.set_y(6)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, "ALMACEN GLORIA", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Nota de Entrega", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    pdf.set_y(32)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("Helvetica", "", 8)

    pdf.cell(ancho / 2, 6, f"N° Nota: {numero}", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(ancho / 2, 6, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(40, 40, 40)
    cliente_label = nombre_cliente if nombre_cliente else "Consumidor final"
    pdf.cell(0, 6, f"Cliente: {cliente_label}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(3)

    pdf.set_draw_color(255, 107, 43)
    pdf.set_line_width(0.5)
    pdf.line(12, pdf.get_y(), pdf.w - 12, pdf.get_y())
    pdf.ln(3)

    pdf.set_fill_color(255, 235, 210)
    pdf.set_text_color(150, 60, 0)
    pdf.set_font("Helvetica", "B", 8)

    col_prod  = ancho * 0.45
    col_cant  = ancho * 0.15
    col_precio = ancho * 0.20
    col_sub   = ancho * 0.20

    pdf.cell(col_prod,  7, "PRODUCTO",   border=0, fill=True)
    pdf.cell(col_cant,  7, "CANT.",      border=0, fill=True, align="C")
    pdf.cell(col_precio,7, "P.UNIT",     border=0, fill=True, align="R")
    pdf.cell(col_sub,   7, "SUBTOTAL",   border=0, fill=True, align="R",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "", 8)
    fill = False

    for item in carrito.values():
        sub = float(item["cantidad"]) * float(item["precio_venta"])
        if fill:
            pdf.set_fill_color(252, 248, 244)
        else:
            pdf.set_fill_color(255, 255, 255)

        pdf.cell(col_prod,  6, item["nombre"][:30],                   border=0, fill=True)
        pdf.cell(col_cant,  6, str(item["cantidad"]),                  border=0, fill=True, align="C")
        pdf.cell(col_precio,6, f"Bs. {float(item['precio_venta']):.2f}", border=0, fill=True, align="R")
        pdf.cell(col_sub,   6, f"Bs. {sub:.2f}",                      border=0, fill=True, align="R",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        fill = not fill

    pdf.ln(2)

    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.line(12, pdf.get_y(), pdf.w - 12, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(255, 107, 43)
    pdf.cell(ancho - col_sub, 8, "TOTAL A PAGAR:", align="R")
    pdf.set_text_color(40, 40, 40)
    pdf.cell(col_sub, 8, f"Bs. {total:.2f}", align="R",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(6)

    pdf.set_draw_color(255, 107, 43)
    pdf.set_line_width(0.5)
    pdf.line(12, pdf.get_y(), pdf.w - 12, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "¡Gracias por su compra!", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 5, "Almacen Gloria - su tienda de confianza",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    return bytes(pdf.output())

def generar_pdf_pedido(pedido_items: dict, nombre_cliente: str, numero: str) -> bytes:
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    _encabezado_pdf(pdf, "Hoja de Pedido", numero)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, f"Cliente: {nombre_cliente}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(110, 8, "Producto")
    pdf.cell(35,  8, "Cantidad", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    for item in pedido_items.values():
        pdf.cell(110, 7, item["nombre"][:45])
        pdf.cell(35,  7, str(item["cantidad"]), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(6)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, "Pedido tomado en visita - pendiente de entrega",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    return bytes(pdf.output())


# ═══════════════════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════════════════

st.markdown("## 🛒 Almacen Gloria")
st.caption(f"Vendedor: **{vendedor}**")

tab1, tab2, tab3 = st.tabs(["📋 Tomar Pedido", "📦 Mis Pedidos", "💰 Registrar Venta"])


# ═══════════════════════════════════════════════════════════════════════
# TAB 1 — TOMAR PEDIDO (MEJORADO)
# ═══════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("📝 Tomar pedido en visita")
    st.caption("Anota qué necesita el cliente para traerlo en la próxima visita.")

    # Información del cliente
    col1, col2 = st.columns(2)
    with col1:
        nombre_cliente = st.text_input(
            "Nombre del cliente *",
            placeholder="Ej: Doña Rosa",
            key="cliente_nombre"
        )
    with col2:
        notas_pedido = st.text_input(
            "Notas (opcional)",
            placeholder="Ej: entregar el martes",
            key="cliente_notas"
        )

    st.divider()

    # Búsqueda mejorada
    st.markdown("### 🔍 Buscar producto")
    productos = obtener_productos()
    busqueda = st.text_input(
        "",
        placeholder="Escribe el nombre del producto...",
        key="busq_pedido",
        label_visibility="collapsed"
    )

    if busqueda:
        productos_filtrados = [
            p for p in productos if busqueda.lower() in p["nombre"].lower()
        ][:5]

        if not productos_filtrados:
            st.info("📭 No se encontraron productos con ese nombre.")
        else:
            st.markdown(f"**Resultados: {len(productos_filtrados)} producto(s)**")
            
            for prod in productos_filtrados:
                pid = str(prod["id"])
                col_prod, col_stock, col_cant = st.columns([2, 1.5, 0.8])

                with col_prod:
                    st.markdown(f"**{prod['nombre']}**")
                    st.caption(f"Bs. {prod['precio_venta']:.2f}")

                with col_stock:
                    stock_color = "🟢" if prod['stock'] > 5 else "🟡" if prod['stock'] > 0 else "🔴"
                    st.metric("Stock", f"{stock_color} {prod['stock'] or 0}")

                with col_cant:
                    cant = st.number_input(
                        "Cant.",
                        min_value=0,
                        max_value=int(prod['stock'] or 999),
                        value=st.session_state.pedido_items.get(pid, {}).get("cantidad", 0),
                        step=1,
                        key=f"ped_{pid}",
                    )or 0
                    if cant > 0:
                        st.session_state.pedido_items[pid] = {**prod, "cantidad": cant}
                    elif pid in st.session_state.pedido_items:
                        del st.session_state.pedido_items[pid]

                st.divider()
    else:
        st.info("💡 Escribe el nombre de un producto para buscarlo.")

    # Resumen del pedido
    if st.session_state.pedido_items:
        st.markdown("### 📋 Resumen del pedido")
        
        resumen_df = pd.DataFrame([
            {
                "Producto": v["nombre"],
                "Cantidad": int(v["cantidad"]),
                "Precio": f"Bs. {v['precio_venta']:.2f}",
                "Subtotal": f"Bs. {float(v['precio_venta']) * int(v['cantidad']):.2f}"
            }
            for v in st.session_state.pedido_items.values()
        ])
        
        st.dataframe(resumen_df, use_container_width=True, hide_index=True)

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("🗑️ Limpiar pedido", use_container_width=True):
                st.session_state.pedido_items = {}
                st.rerun()

        with col_b:
            if st.button("💾 Guardar pedido", use_container_width=True, type="primary"):
                if not nombre_cliente:
                    st.warning("⚠️ Ingresa el nombre del cliente.")
                else:
                    pedido = guardar_pedido(
                        nombre_cliente=nombre_cliente,
                        vendedor=vendedor,
                        items=st.session_state.pedido_items,
                        notas=notas_pedido,
                    )
                    if pedido:
                        st.success(f"✅ Pedido {pedido['numero']} guardado correctamente.")
                        st.session_state.ultimo_pedido_guardado = {
                            "numero": pedido["numero"],
                            "cliente": nombre_cliente,
                            "items": dict(st.session_state.pedido_items),
                        }
                        st.session_state.pedido_items = {}
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar el pedido.")

        with col_c:
            if st.session_state.ultimo_pedido_guardado:
                upg = st.session_state.ultimo_pedido_guardado
                pdf_bytes = generar_pdf_pedido(upg["items"], upg["cliente"], upg["numero"])
                st.download_button(
                    "📄 Descargar PDF",
                    data=pdf_bytes,
                    file_name=f"pedido_{upg['numero']}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
    else:
        st.info("💡 Selecciona productos arriba para crear el pedido.")


# ═══════════════════════════════════════════════════════════════════════
# TAB 2 — MIS PEDIDOS PENDIENTES
# ═══════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Pedidos pendientes de entrega")
    
    if st.button("🔄 Actualizar lista"):
        st.rerun()

    pedidos = obtener_pedidos_pendientes(vendedor=vendedor)

    if not pedidos:
        st.info("No hay pedidos pendientes.")
    else:
        for pedido in pedidos:
            notas_label = f" | 📝 {pedido['notas']}" if pedido.get("notas") else ""
            with st.expander(
                f"📋 {pedido['numero']} — {pedido['cliente']} | {pedido['fecha'][:10]}{notas_label}"
            ):
                detalle = obtener_detalle_pedido(pedido["id"])

                items_para_pos: dict = {}

                if detalle:
                    rows = []
                    for d in detalle:
                        prod_info = d.get("productos") or {}
                        nombre = prod_info.get("nombre", f"Producto {d['producto_id']}")
                        rows.append({
                            "Producto": nombre,
                            "Cantidad": d["cantidad"],
                            "P. Venta": f"Bs. {d['precio_venta']:.2f}",
                        })
                        items_para_pos[str(d["producto_id"])] = {
                            "id":           d["producto_id"],
                            "nombre":       nombre,
                            "cantidad":     d["cantidad"],
                            "precio_venta": d["precio_venta"],
                        }
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("🛒 Convertir en venta", key=f"conv_{pedido['id']}", use_container_width=True):
                        st.session_state.carrito = items_para_pos
                        st.session_state.pedido_cargado_id = pedido["id"]
                        st.success("Pedido cargado en el POS. Ve a 💰 Registrar Venta.")

                with col2:
                    if st.button("❌ Cancelar pedido", key=f"cancel_{pedido['id']}", use_container_width=True):
                        if cancelar_pedido(pedido["id"]):
                            st.success("Pedido cancelado.")
                            st.rerun()

                with col3:
                    if detalle:
                        pdf_items = {
                            str(d["producto_id"]): {
                                "nombre":   (d.get("productos") or {}).get("nombre", f"Prod {d['producto_id']}"),
                                "cantidad": d["cantidad"],
                            }
                            for d in detalle
                        }
                        pdf_p = generar_pdf_pedido(pdf_items, pedido["cliente"], pedido["numero"])
                        st.download_button(
                            "📄 PDF pedido",
                            data=pdf_p,
                            file_name=f"pedido_{pedido['numero']}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"pdf_{pedido['id']}",
                        )


# ═══════════════════════════════════════════════════════════════════════
# TAB 3 — REGISTRAR VENTA (POS) - MEJORADO
# ═══════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("💰 Registrar Venta")

    # Banner de pedido cargado
    if st.session_state.pedido_cargado_id:
        col_info, col_cancel = st.columns([5, 1])
        with col_info:
            st.success(f"📋 Pedido N° {st.session_state.pedido_cargado_id} cargado. Puedes editar.")
        with col_cancel:
            if st.button("✖", use_container_width=True):
                st.session_state.pedido_cargado_id = None
                st.session_state.carrito = {}
                st.rerun()

    # Añadir producto extra
    with st.expander("➕ Añadir producto al carrito"):
        busqueda_extra = st.text_input("🔍 Buscar", key="busq_extra", placeholder="Nombre del producto...")
        if busqueda_extra:
            todos_prods = obtener_productos()
            encontrados = [
                p for p in todos_prods
                if busqueda_extra.lower() in p["nombre"].lower()
            ][:5]
            if not encontrados:
                st.caption("Sin resultados.")
            for prod in encontrados:
                pid_e = str(prod["id"])
                col_n, col_b = st.columns([3, 1])
                col_n.write(f"**{prod['nombre']}** — Bs. {prod['precio_venta']:.2f} | Stock: {prod.get('stock') or 0}")
                if col_b.button("Añadir", key=f"add_extra_{pid_e}", use_container_width=True):
                    if pid_e in st.session_state.carrito:
                        st.session_state.carrito[pid_e]["cantidad"] += 1
                    else:
                        st.session_state.carrito[pid_e] = {**prod, "cantidad": 1}
                    st.rerun()

    st.divider()

    # Carrito
    if not st.session_state.carrito:
        st.warning("🛒 Carrito vacío. Carga un pedido o añade productos.")
    else:
        st.markdown("### 🛒 Tu carrito")

        # Tabla del carrito
        datos_carrito = []
        for pid, item in list(st.session_state.carrito.items()):
            cantidad_actual = int(item.get("cantidad") or 1)
            precio_unit = float(item["precio_venta"])
            subtotal = precio_unit * cantidad_actual

            datos_carrito.append({
                "Producto": item["nombre"],
                "Cantidad": cantidad_actual,
                "P. Unitario": f"Bs. {precio_unit:.2f}",
                "Subtotal": f"Bs. {subtotal:.2f}"
            })

        st.dataframe(
            pd.DataFrame(datos_carrito),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # Editar cantidades
        st.markdown("### ✏️ Editar cantidades")
        
        items_a_eliminar = []
        for pid, item in list(st.session_state.carrito.items()):
            col_edit1, col_edit2, col_edit3 = st.columns([2, 1.5, 1])

            with col_edit1:
                st.caption(f"**{item['nombre'][:40]}**")

            with col_edit2:
                nueva_cant = st.number_input(
                    "Cantidad",
                    min_value=1,
                    max_value=int(item.get("stock") or 999),
                    value=int(item.get("cantidad") or 1),
                    step=1,
                    key=f"edit_{pid}",
                )
                st.session_state.carrito[pid]["cantidad"] = nueva_cant

            with col_edit3:
                if st.button("🗑 Eliminar", key=f"del_{pid}", use_container_width=True):
                    items_a_eliminar.append(pid)

        # Eliminar items
        for pid in items_a_eliminar:
            del st.session_state.carrito[pid]
        if items_a_eliminar:
            st.rerun()

        st.divider()

        # Total y cliente
        total = sum(
            float(i["precio_venta"]) * int(i.get("cantidad") or 1)
            for i in st.session_state.carrito.values()
        )

        col_total, col_cliente = st.columns([1, 2])
        
        with col_total:
            st.metric("💰 Total", f"Bs. {total:.2f}")

        with col_cliente:
            nombre_cliente_venta = st.text_input(
                "Cliente (opcional)",
                placeholder="Ej: Doña Rosa",
                key="nombre_cliente_venta",
            )

        # Botón confirmar
        if st.button("✅ Confirmar y registrar venta", type="primary", use_container_width=True):
            items_lista = list(st.session_state.carrito.values())
            resultado = registrar_venta(items_lista, total, cliente=nombre_cliente_venta)

            if resultado:
                if st.session_state.pedido_cargado_id:
                    marcar_pedido_entregado(
                        st.session_state.pedido_cargado_id,
                        venta_id=resultado,
                    )
                    st.session_state.pedido_cargado_id = None

                st.session_state.ultima_venta = {
                    "carrito": dict(st.session_state.carrito),
                    "total": total,
                    "numero": datetime.now().strftime("V%Y%m%d%H%M%S"),
                    "cliente": nombre_cliente_venta,
                }
                st.session_state.carrito = {}
                st.success("✅ Venta registrada exitosamente.")
                st.rerun()
            else:
                st.error("❌ Error al registrar la venta.")

    # Descarga PDF última venta
    if st.session_state.ultima_venta:
        st.divider()
        uv = st.session_state.ultima_venta
        col_msg, col_pdf = st.columns([4, 1])
        
        with col_msg:
            st.success(f"🧾 Última venta: **{uv['numero']}** — Bs. {uv['total']:.2f}")
        
        with col_pdf:
            pdf_v = generar_pdf_nota_venta(
                uv["carrito"],
                uv["total"],
                uv["numero"],
                uv.get("cliente", ""),
            )
            st.download_button(
                "Descargar",
                data=pdf_v,
                file_name=f"nota_{uv['numero']}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    # Historial de ventas
    st.divider()
    st.markdown("### 📊 Historial de ventas")

    col_lim, col_ref = st.columns([4, 1])
    limite = int(col_lim.selectbox("Mostrar últimas", [5, 10, 20, 50], index=1) or 10)
    if col_ref.button("🔄 Actualizar"):
        st.rerun()

    ventas = obtener_ultimas_ventas(limite=limite)

    if not ventas:
        st.info("📭 No hay ventas registradas.")
    else:
        for v in ventas:
            items_hist, nombre_hist = obtener_detalle_venta(v["id"])
            cliente_str = v.get("cliente") or nombre_hist or "Consumidor final"

            with st.expander(f"🧾 {v['numero_venta']} • {cliente_str} • Bs. {v['total']:.2f}"):
                if items_hist:
                    st.dataframe(
                        pd.DataFrame([
                            {
                                "Producto": i["nombre"],
                                "Cantidad": i["cantidad"],
                                "P. Unitario": f"Bs. {i['precio_venta']:.2f}",
                                "Subtotal": f"Bs. {i['precio_venta'] * i['cantidad']:.2f}",
                            }
                            for i in items_hist.values()
                        ]),
                        use_container_width=True,
                        hide_index=True,
                    )

                    pdf_h = generar_pdf_nota_venta(
                        items_hist,
                        float(v["total"]),
                        v["numero_venta"],
                        cliente_str,
                    )
                    st.download_button(
                        "📥 Descargar PDF",
                        data=pdf_h,
                        file_name=f"nota_{v['numero_venta']}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"pdf_hist_{v['id']}",
                    )
                else:
                    st.caption("Sin detalle disponible.")