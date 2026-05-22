"""
pages/4_📊_Reportes.py
Analítica de ventas, ganancias y productos más vendidos.
"""

import streamlit as st
import pandas as pd
import sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from src.utils.sidebar import render_sidebar
from src.services.ventas_service    import get_ventas_por_rango, get_resumen_ventas, get_productos_mas_vendidos
from src.services.inventario_service import get_stock_critico, get_todos_productos
from src.utils.helpers              import fmt_bs, fmt_fecha_corta, now_bolivia

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Reportes · Almacén Gloria", page_icon="📊", layout="wide")


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
    
</style>
""", unsafe_allow_html=True)

st.title("📊 Reportes y Analítica")
st.markdown("---")

# ── Selector de período ───────────────────────────────────────────────────────
hoy      = now_bolivia().date()
col_p, col_desde, col_hasta = st.columns([2, 1, 1])

with col_p:
    periodo = st.selectbox(
        "📅 Período",
        ["Hoy", "Ayer", "Últimos 7 días", "Últimos 30 días", "Este mes", "Rango personalizado"],
    )

if periodo == "Hoy":
    desde, hasta = hoy, hoy
elif periodo == "Ayer":
    desde = hasta = hoy - timedelta(days=1)
elif periodo == "Últimos 7 días":
    desde, hasta = hoy - timedelta(days=6), hoy
elif periodo == "Últimos 30 días":
    desde, hasta = hoy - timedelta(days=29), hoy
elif periodo == "Este mes":
    desde = hoy.replace(day=1)
    hasta = hoy
else:
    with col_desde:
        desde = st.date_input("Desde", value=hoy - timedelta(days=6))
    with col_hasta:
        hasta = st.date_input("Hasta", value=hoy)

fi = f"{desde}T00:00:00-04:00"
ff = f"{hasta}T23:59:59-04:00"

resumen = get_resumen_ventas(fi, ff)

# ── KPIs principales ──────────────────────────────────────────────────────────
st.subheader("📈 Resumen del período")
k1, k2, k3, k4 = st.columns(4)
k1.metric("🧾 Transacciones",   resumen["total_transacciones"])
k2.metric("💰 Ingresos",         fmt_bs(resumen["ingresos_totales"]))
k3.metric("🏷️ Descuentos",       fmt_bs(resumen["descuentos"]))
k4.metric("🎫 Ticket promedio",  fmt_bs(resumen["ticket_promedio"]))

st.markdown("---")

# ── Ganancia neta y desglose por método de pago ───────────────────────────────
col_gan, col_pago = st.columns([1, 2])

with col_gan:
    # Calcular ganancia neta desde el detalle de ventas
    ventas = get_ventas_por_rango(fi, ff)
    venta_ids = [v["id"] for v in ventas]
    ganancia = 0.0
    if venta_ids:
        from src.database.connection import get_supabase
        db  = get_supabase()
        det = (
            db.table("detalle_ventas")
            .select("subtotal, precio_compra, cantidad")
            .in_("venta_id", venta_ids)
            .execute()
        ).data or []
        ganancia = sum(d["subtotal"] - d["cantidad"] * d["precio_compra"] for d in det)

    st.markdown(f"""
    <div class="ganancia-box">
        <div class="ganancia-label">GANANCIA NETA DEL PERÍODO</div>
        <div class="ganancia-monto">{fmt_bs(ganancia)}</div>
    </div>
    """, unsafe_allow_html=True)

with col_pago:
    st.subheader("💳 Ingresos por método de pago")
    metodos_df = pd.DataFrame({
        "Método":  ["💵 Efectivo", "📱 QR / Transferencia", "💳 Tarjeta"],
        "Monto":   [resumen["efectivo"], resumen["qr"], resumen["tarjeta"]],
    })
    st.dataframe(
        metodos_df.style.format({"Monto": lambda x: fmt_bs(x)}),
        use_container_width=True, hide_index=True
    )

st.markdown("---")

# ── Tabs: ventas, top productos, stock ───────────────────────────────────────
tab_ventas, tab_top, tab_stock = st.tabs(["📋 Historial de Ventas", "🏆 Top Productos", "⚠️ Stock Crítico"])

with tab_ventas:
    ventas_lista = get_ventas_por_rango(fi, ff)
    if not ventas_lista:
        st.info("No hay ventas en el período seleccionado.")
    else:
        filas = []
        for v in ventas_lista:
            filas.append({
                "Nº Venta":    v["numero_venta"],
                "Fecha":       fmt_fecha_corta(v["fecha"]),
                "Total":       fmt_bs(v["total"]),
                "Descuento":   fmt_bs(v["descuento"]),
                "Método":      v["metodo_pago"].title(),
                "Estado":      "✅ Completada" if v["estado"] == "completada" else "❌ Anulada",
            })
        st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)
        st.caption(f"{len(ventas_lista)} venta(s) en el período.")

with tab_top:
    st.subheader("🏆 Productos más vendidos")
    top_prods = get_productos_mas_vendidos(fi, ff, limite=15)
    if not top_prods:
        st.info("No hay datos de ventas para el período.")
    else:
        df_top = pd.DataFrame(top_prods)
        df_top["ingresos"]  = df_top["ingresos"].apply(fmt_bs)
        df_top["ganancia"]  = df_top["ganancia"].apply(fmt_bs)
        df_top = df_top.rename(columns={
            "nombre":   "Producto",
            "codigo":   "Código",
            "unidades": "Unidades",
            "ingresos": "Ingresos",
            "ganancia": "Ganancia",
        })
        st.dataframe(
            df_top[["Producto", "Código", "Unidades", "Ingresos", "Ganancia"]],
            use_container_width=True, hide_index=True
        )

        # Gráfico simple de barras con Streamlit
        st.subheader("📊 Unidades vendidas")
        chart_data = pd.DataFrame({
            "Producto": [p["nombre"][:20] for p in top_prods[:10]],
            "Unidades": [p["unidades"]    for p in top_prods[:10]],
        }).set_index("Producto")
        st.bar_chart(chart_data)

with tab_stock:
    st.subheader("⚠️ Productos con Stock Crítico")
    criticos = get_stock_critico()
    if not criticos:
        st.success("✅ Todos los productos tienen stock suficiente.")
    else:
        filas_s = []
        for p in criticos:
            filas_s.append({
                "Código":    p["codigo"],
                "Nombre":    p["nombre"],
                "Stock":     p["stock"],
                "Mínimo":    p["stock_minimo"],
                "Faltante":  p["stock_minimo"] - p["stock"],
                "Categoría": (p.get("categorias") or {}).get("nombre", "—"),
            })
        df_s = pd.DataFrame(filas_s)
        st.dataframe(df_s, use_container_width=True, hide_index=True)
        st.warning(f"{len(criticos)} producto(s) necesitan reposición urgente.")

st.markdown("---")
st.caption(f"Almacén Gloria · Generado el {fmt_fecha_corta(now_bolivia())}")