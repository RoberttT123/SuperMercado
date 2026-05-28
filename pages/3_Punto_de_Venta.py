"""
pages/3_🛒_Punto_de_Venta.py
LA PANTALLA CRÍTICA — Escaneo, carrito y cobro rápido.
"""
# 🔒 BARRERA DE SEGURIDAD

import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from src.utils.sidebar import render_sidebar
from src.services.caja_service     import get_caja_abierta
from src.services.inventario_service import buscar_producto_por_codigo, buscar_productos
from src.services.ventas_service   import procesar_venta, get_ventas_del_dia
from src.utils.helpers             import fmt_bs, calcular_cambio, fmt_fecha

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "POS · Almacén Gloria",
    page_icon  = "🛒",
    layout     = "wide",
)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("main.py")

if st.session_state.get("role") != "admin":
    st.error("Acceso denegado. Esta sección es solo para administradores.")
    st.stop()
render_sidebar()
st.markdown("""
<style>
            
    [data-testid="stAppViewContainer"] {
        background-color: #FDF6F0 !important;
    }
    /* 🚫 1. OCULTAR POR COMPLETO LA BARRA SUPERIOR DE STREAMLIT */
    [data-testid="stHeader"], 
    .stHeader {
        display: none !important;
    }

    /* 🚀 2. SUBIR EL CONTENIDO AL RAS DE LA PANTALLA (Ya no se cortará) */
    .main .block-container, 
    [data-testid="stMainBlockContainer"], 
    [data-testid="stBlockContainer"], 
    .block-container {
        padding-top: 1rem !important; /* Ajustado a 1rem para aprovechar todo el alto */
        padding-bottom: 1rem !important;
        margin-top: 0rem !important;
    }

    /* Evita márgenes heredados en el título principal */
    h1 {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
        color: #FF6B2B;
    }

    /* Tus estilos de personalización se quedan igual abajo: */
    h2, h3 { color: #FF6B2B; }
    [data-testid="stMetricValue"] { color: #FF6B2B !important; }
    
    .stButton > button { 
        background: #FF6B2B; 
        color: #fff; 
        border: none; 
        border-radius: 8px; 
        font-weight: 700; 
    }
    .stButton > button:hover { background: #E85D04; }
    
    .stock-bajo { 
        background: #3a1e1e; 
        border-left: 4px solid #F44336; 
        padding: 0.5rem 1rem; 
        border-radius: 4px; 
    }
</style>
""", unsafe_allow_html=True)

# ── Verificar caja abierta ────────────────────────────────────────────────────
caja_activa = get_caja_abierta()
if not caja_activa:
    st.error("🔒 No hay caja abierta. Ve a **Control de Caja** y abre la caja para comenzar a vender.")
    st.stop()

st.title("🛒 Punto de Venta")
st.caption(f"Caja #{caja_activa['id']} · Cajero: {caja_activa.get('usuario','—')}")
st.markdown("---")

# ── Estado del carrito ────────────────────────────────────────────────────────
if "carrito"     not in st.session_state: st.session_state.carrito     = []
if "venta_ok"    not in st.session_state: st.session_state.venta_ok    = None
if "scan_codigo" not in st.session_state: st.session_state.scan_codigo = ""

# ── Layout principal: izquierda = escaneo+carrito | derecha = cobro ───────────
col_left, col_right = st.columns([3, 2], gap="large")

# ══════════════════════ COLUMNA IZQUIERDA ════════════════════════════════════
with col_left:
    # ── Búsqueda / Escaneo ────────────────────────────────────────────────────
    st.subheader("📊 Escanear o Buscar Producto")

    metodo = st.radio("Método de búsqueda:", ["Código de barras (escaneo)", "Búsqueda por nombre"], horizontal=True)

    if metodo == "Código de barras (escaneo)":
        codigo_input = st.text_input(
            "Escanea aquí 👇",
            placeholder="Escanea o escribe el código...",
            key="scan_input",
            label_visibility="collapsed"
        )
        cantidad_scan = st.number_input("Cantidad", min_value=1, value=1, step=1, key="scan_cant")

        if st.button("➕ Agregar al carrito", key="btn_scan") and codigo_input:
            prod = buscar_producto_por_codigo(codigo_input)
            if not prod:
                st.error(f"❌ Código '{codigo_input}' no encontrado en el inventario.")
            elif prod["stock"] < cantidad_scan:
                st.warning(f"⚠️ Solo hay {prod['stock']} unidades de '{prod['nombre']}'.")
            else:
                # Revisar si ya está en el carrito
                existe = next((i for i in st.session_state.carrito if i["producto_id"] == prod["id"]), None)
                if existe:
                    existe["cantidad"] += cantidad_scan
                    existe["subtotal"]  = existe["cantidad"] * existe["precio_unitario"]
                else:
                    st.session_state.carrito.append({
                        "producto_id":    prod["id"],
                        "nombre":         prod["nombre"],
                        "codigo":         prod["codigo"],
                        "precio_unitario":prod["precio_venta"],
                        "precio_compra":  prod["precio_compra"],
                        "cantidad":       cantidad_scan,
                        "subtotal":       cantidad_scan * prod["precio_venta"],
                    })
                st.rerun()

    else:  # Búsqueda por nombre
        nombre_busq  = st.text_input("Nombre del producto", placeholder="Ej: leche...", key="nombre_busq")
        cantidad_nom = st.number_input("Cantidad", min_value=1, value=1, step=1, key="nom_cant")

        if nombre_busq:
            resultados = buscar_productos(nombre_busq)
            if resultados:
                opciones  = {f"{p['codigo']} — {p['nombre']} ({fmt_bs(p['precio_venta'])})": p for p in resultados}
                sel_prod  = st.selectbox("Selecciona:", list(opciones.keys()))
                prod_obj  = opciones[sel_prod]

                if st.button("➕ Agregar", key="btn_nombre"):
                    existe = next((i for i in st.session_state.carrito if i["producto_id"] == prod_obj["id"]), None)
                    if existe:
                        existe["cantidad"] += cantidad_nom
                        existe["subtotal"]  = existe["cantidad"] * existe["precio_unitario"]
                    else:
                        st.session_state.carrito.append({
                            "producto_id":    prod_obj["id"],
                            "nombre":         prod_obj["nombre"],
                            "codigo":         prod_obj["codigo"],
                            "precio_unitario":prod_obj["precio_venta"],
                            "precio_compra":  prod_obj["precio_compra"],
                            "cantidad":       cantidad_nom,
                            "subtotal":       cantidad_nom * prod_obj["precio_venta"],
                        })
                    st.rerun()
            elif nombre_busq:
                st.warning("No se encontraron productos.")

    st.markdown("---")

    # ── Carrito ───────────────────────────────────────────────────────────────
    st.subheader(f"🛒 Carrito ({len(st.session_state.carrito)} items)")

    if not st.session_state.carrito:
        st.info("El carrito está vacío. Escanea un producto para comenzar.")
    else:
        # Cabecera
        hc1, hc2, hc3, hc4, hc5 = st.columns([4, 1, 1, 2, 1])
        hc1.markdown("**Producto**")
        hc2.markdown("**Cant.**")
        hc3.markdown("**Precio**")
        hc4.markdown("**Subtotal**")
        hc5.markdown("**—**")

        for i, item in enumerate(st.session_state.carrito):
            c1, c2, c3, c4, c5 = st.columns([4, 1, 1, 2, 1])
            c1.write(item["nombre"])
            # Editar cantidad inline
            nueva_cant = c2.number_input(
                "Cant", min_value=1, value=item["cantidad"], step=1,
                key=f"cant_{i}", label_visibility="collapsed"
            )
            if nueva_cant != item["cantidad"]:
                item["cantidad"] = nueva_cant
                item["subtotal"] = nueva_cant * item["precio_unitario"]
                st.rerun()
            c3.write(fmt_bs(item["precio_unitario"]))
            c4.write(fmt_bs(item["subtotal"]))
            if c5.button("🗑️", key=f"del_{i}"):
                st.session_state.carrito.pop(i)
                st.rerun()

# ══════════════════════ COLUMNA DERECHA ══════════════════════════════════════
with col_right:
    subtotal = sum(i["subtotal"] for i in st.session_state.carrito)

    # Descuento
    # ── Cambio sugerido ──
# Convertimos subtotal a float explícitamente para asegurar consistencia
    descuento = st.number_input(
        "🏷️ Descuento (Bs.)", 
        min_value=0.0, 
        max_value=float(subtotal), 
        value=0.0, 
        step=1.0, 
        format="%.2f"
    )
    total     = max(0.0, subtotal - descuento)

    # Total grande
    st.markdown(f"""
    <div class="total-box">
        <div class="total-label">TOTAL A PAGAR</div>
        <div class="total-monto">{fmt_bs(total)}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Método de pago
    metodo_pago = st.radio(
        "💳 Método de pago:",
        ["efectivo", "qr", "tarjeta"],
        format_func=lambda x: {"efectivo":"💵 Efectivo","qr":"📱 QR / Transferencia","tarjeta":"💳 Tarjeta"}.get(x, x),
        horizontal=True,
    )

    cambio = 0.0
    if metodo_pago == "efectivo":
        monto_recibido = st.number_input(
            "💵 Monto recibido (Bs.)",
            min_value=0.0, value=total, step=1.0, format="%.2f"
        )
        cambio = calcular_cambio(total, monto_recibido)
        if monto_recibido > 0:
            color_cambio = "#4CAF50" if cambio >= 0 else "#F44336"
            st.markdown(f"**Cambio:** <span style='color:{color_cambio};font-size:1.4rem;font-weight:700;'>{fmt_bs(cambio)}</span>", unsafe_allow_html=True)
    else:
        monto_recibido = total

    notas_venta = st.text_input("📝 Notas (opcional)", key="notas_venta")

    st.markdown("---")

    # Botón COBRAR
    disabled_cobrar = (not st.session_state.carrito) or (metodo_pago == "efectivo" and monto_recibido < total)

    col_cobrar, col_cancel = st.columns(2)
    with col_cobrar:
        st.markdown('<div class="btn-cobrar">', unsafe_allow_html=True)
        cobrar = st.button("✅ COBRAR", use_container_width=True, disabled=disabled_cobrar)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_cancel:
        st.markdown('<div class="btn-cancel">', unsafe_allow_html=True)
        cancelar = st.button("🗑️ Cancelar", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if cancelar:
        st.session_state.carrito  = []
        st.session_state.venta_ok = None
        st.rerun()

    if cobrar:
        try:
            venta = procesar_venta(
                carrito        = st.session_state.carrito,
                caja_id        = caja_activa["id"],
                metodo_pago    = metodo_pago,
                descuento      = descuento,
                monto_recibido = monto_recibido,
                notas          = notas_venta,
            )
            st.session_state.venta_ok = {
                "numero": venta["numero_venta"],
                "total":  venta["total"],
                "cambio": cambio,
            }
            st.session_state.carrito = []
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al procesar la venta: {e}")

    # ── Confirmación de venta ─────────────────────────────────────────────────
    if st.session_state.venta_ok:
        v = st.session_state.venta_ok
        st.success(f"""
        ✅ **¡Venta completada!**
        Nº {v['numero']} · Total: **{fmt_bs(v['total'])}**
        {f"Cambio: **{fmt_bs(v['cambio'])}**" if v['cambio'] > 0 else ""}
        """)
        if st.button("🔄 Nueva venta"):
            st.session_state.venta_ok = None
            st.rerun()

    st.markdown("---")
    # ── Resumen rápido del día ─────────────────────────────────────────────────
    ventas_hoy = get_ventas_del_dia()
    completadas = [v for v in ventas_hoy if v["estado"] == "completada"]
    c1, c2 = st.columns(2)
    c1.metric("Ventas hoy", len(completadas))
    c2.metric("Total hoy",  fmt_bs(sum(v["total"] for v in completadas)))