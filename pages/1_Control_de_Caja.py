"""
pages/1_Control_de_Caja.py
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="Caja · Almacén Gloria", page_icon="💵", layout="wide")

from src.utils.sidebar import render_sidebar
from src.services.caja_service import (
    get_caja_abierta, abrir_caja, cerrar_caja, get_resumen_caja, get_historial_cajas
)
from src.utils.helpers import fmt_bs, fmt_fecha

# Renderizar sidebar personalizado
render_sidebar("caja")

# ── ESTILOS INYECTADOS CORREGIDOS ─────────────────────────────────────────────
st.markdown("""
<style>
    /* 🎨 NUEVO: Fuerza a que TODA la base de la app sea crema y elimina la franja blanca */
    [data-testid="stAppViewContainer"] {
        background-color: #FDF6F0 !important;
    }

    /* 🚫 1. OCULTAR POR COMPLETO LA BARRA SUPERIOR DE STREAMLIT */
    [data-testid="stHeader"], 
    .stHeader {
        display: none !important;
    }

    /* 🚀 2. SUBIR EL CONTENIDO AL RAS DE LA PANTALLA */
    .main .block-container, 
    [data-testid="stMainBlockContainer"], 
    [data-testid="stBlockContainer"], 
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        margin-top: 0rem !important;
    }

    /* Evita márgenes heredados en el título principal */
    h1 {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
        color: #FF6B2B;
    }

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
</style>
""", unsafe_allow_html=True)

# ── LOGICA DE NEGOCIO Y RENDERIZADO ───────────────────────────────────────────

st.title("💵 Control de Caja")
st.markdown("---")

caja_activa = get_caja_abierta()

if caja_activa:
    st.markdown(f"""
    <div style="background:#0a1f0a;border:1px solid #4CAF50;border-left:4px solid #4CAF50;
                border-radius:10px;padding:0.8rem 1.2rem;margin-bottom:1rem;">
        ✅ <strong>Caja abierta</strong> desde {fmt_fecha(caja_activa['fecha_apertura'])}
        &nbsp;|&nbsp; Monto inicial: <strong>{fmt_bs(caja_activa['monto_inicial'])}</strong>
        &nbsp;|&nbsp; Cajero: <strong>{caja_activa.get('usuario','—')}</strong>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background:#1f0a0a;border:1px solid #FF6B2B;border-left:4px solid #FF6B2B;
                border-radius:10px;padding:0.8rem 1.2rem;margin-bottom:1rem;">
        🔒 <strong>No hay caja abierta.</strong> Abre la caja para comenzar a vender.
    </div>
    """, unsafe_allow_html=True)

tab_abrir, tab_cerrar, tab_historial = st.tabs(["🟢 Abrir Caja", "🔴 Cerrar Caja", "📋 Historial"])

with tab_abrir:
    if caja_activa:
        st.info("Ya hay una caja abierta. Ciérrala primero para abrir una nueva.")
    else:
        st.subheader("Apertura de Caja")
        col1, col2 = st.columns(2)
        with col1:
            monto_inicial = st.number_input("💰 Monto inicial (Bs.)", min_value=0.0, value=100.0, step=10.0, format="%.2f")
        with col2:
            usuario = st.text_input("👤 Nombre del cajero", value="Admin")
        if st.button("🟢 Abrir Caja Ahora", use_container_width=True):
            try:
                abrir_caja(monto_inicial, usuario)
                st.success(f"✅ Caja abierta con {fmt_bs(monto_inicial)}.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

with tab_cerrar:
    if not caja_activa:
        st.info("No hay caja abierta para cerrar.")
    else:
        st.subheader("Cierre y Arqueo de Caja")
        resumen = get_resumen_caja(caja_activa["id"])
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🧾 Transacciones",  resumen["total_transacciones"])
        c2.metric("💵 Total ventas",    fmt_bs(resumen["total_ingresos"]))
        c3.metric("💸 Efectivo",        fmt_bs(resumen["efectivo"]))
        c4.metric("📱 QR / Tarjeta",    fmt_bs(resumen["qr"] + resumen["tarjeta"]))
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            monto_final = st.number_input(
                "💰 Dinero contado (Bs.)",
                min_value=0.0,
                value=float(caja_activa["monto_inicial"]) + resumen["efectivo"],
                step=1.0, format="%.2f"
            )
        with col2:
            notas_cierre = st.text_area("📝 Notas (opcional)", height=80)
        monto_esperado = caja_activa["monto_inicial"] + resumen["efectivo"]
        diferencia     = monto_final - monto_esperado
        color_dif      = "#4CAF50" if diferencia >= 0 else "#F44336"
        st.markdown(f"""
        | | Monto |
        |---|---|
        | Monto inicial | **{fmt_bs(caja_activa['monto_inicial'])}** |
        | Ventas en efectivo | **{fmt_bs(resumen['efectivo'])}** |
        | **Total esperado** | **{fmt_bs(monto_esperado)}** |
        | Monto contado | **{fmt_bs(monto_final)}** |
        """)
        st.markdown(f"**Diferencia:** <span style='color:{color_dif};font-size:1.3rem;font-weight:700;'>{fmt_bs(diferencia)}</span>", unsafe_allow_html=True)
        if st.button("🔴 Cerrar Caja", use_container_width=True):
            cerrar_caja(caja_activa["id"], monto_final, notas_cierre)
            st.success("✅ Caja cerrada correctamente.")
            st.balloons()
            st.rerun()

with tab_historial:
    st.subheader("Historial de Cajas")
    historial = get_historial_cajas(20)
    if not historial:
        st.info("Aún no hay cajas cerradas.")
    else:
        for c in historial:
            dif   = c.get("diferencia") or 0
            emoji = "✅" if dif >= 0 else "⚠️"
            with st.expander(f"{emoji} {fmt_fecha(c['fecha_apertura'])} — {fmt_bs(c.get('monto_final') or 0)}"):
                cc1, cc2, cc3 = st.columns(3)
                cc1.metric("Monto inicial",  fmt_bs(c["monto_inicial"]))
                cc2.metric("Monto esperado", fmt_bs(c.get("monto_esperado") or 0))
                cc3.metric("Diferencia",     fmt_bs(dif))
                if c.get("notas"):
                    st.caption(f"📝 {c['notas']}")