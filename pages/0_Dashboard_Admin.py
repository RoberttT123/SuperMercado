"""
0_Dashboard_Admin.py - Dashboard principal de Almacen Gloria
"""
import streamlit as st
import os, sys

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser el primer comando de Streamlit)
st.set_page_config(
    page_title            = "Almacen Gloria",
    page_icon             = "🛒",
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

# 2. 🔒 BARRERA DE SEGURIDAD
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("main.py")

if st.session_state.get("role") != "admin":
    st.error("Acceso denegado. Esta sección es solo para administradores.")
    st.stop()

# 3. AJUSTE DE RUTA (Sube un nivel desde 'pages/' a la raíz para encontrar 'src')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.sidebar import render_sidebar
render_sidebar()

# 4. TU CÓDIGO CSS ORIGINAL
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

    /* 🚀 2. SUBIR EL CONTENIDO AL RAS DE LA PANTALLA */
    .main .block-container, 
    [data-testid="stMainBlockContainer"], 
    [data-testid="stBlockContainer"], 
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 1rem !important;
        margin-top: 0rem !important;
    }

    /* HERO BANNER */
    .welcome-container {
        background: linear-gradient(135deg, #FFFFFF 0%, #FFF4EE 100%);
        border-left: 6px solid #FF6B2B;
        border-radius: 16px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(255,107,43,0.08);
    }
    .welcome-badge {
        background: rgba(255,107,43,0.1);
        color: #E85510;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        display: inline-block;
        margin-bottom: 0.7rem;
        text-transform: uppercase;
        border: 1px solid rgba(255,107,43,0.15);
    }
    .welcome-title {
        font-size: 2.8rem;
        font-weight: 900;
        color: #2A1A0A;
        margin: 0;
        line-height: 1.2;
    }
    .welcome-title span { color: #FF6B2B; }
    .welcome-subtitle {
        font-size: 1.1rem;
        color: #888888;
        margin-top: 0.5rem;
        font-style: italic;
    }

    /* 🎯 TARJETAS DE MÓDULOS AISLADAS (Solo aplica si tienen la clase .card-marker) */
    [data-testid="column"]:has(.card-marker) {
        background-color: #FFFFFF !important;
        border: 2px solid #FFE0CC !important; /* Un tono más suave que combina con el pastel */
        border-radius: 16px !important;
        padding: 24px 20px !important;
        box-shadow: 0 4px 16px rgba(255,107,43,0.05) !important;
        transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
    }
    
    [data-testid="column"]:has(.card-marker):hover {
        transform: translateY(-5px) !important;
        border-color: #FF6B2B !important;
        box-shadow: 0 12px 28px rgba(255,107,43,0.15) !important;
    }
    
    [data-testid="column"]:has(.card-marker) p {
        color: #666666 !important;
        font-size: 0.92rem !important;
        line-height: 1.55 !important;
    }
    
    [data-testid="column"]:has(.card-marker) h3 {
        color: #2A1A0A !important;
        font-weight: 700 !important;
        margin-top: 0 !important;
    }

    /* BOTONES page_link EXCLUSIVOS DE LAS TARJETAS */
    [data-testid="column"]:has(.card-marker) [data-testid="stPageLink"] a {
        background: #FFF3EE !important;
        border: 1.5px solid #FFB38A !important;
        color: #E85510 !important;
        border-radius: 9px !important;
        padding: 10px 16px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        font-weight: 700 !important;
        font-size: 0.875rem !important;
        transition: all 0.2s ease !important;
        text-decoration: none !important;
        margin-top: 14px !important;
    }
    
    [data-testid="column"]:has(.card-marker) [data-testid="stPageLink"] a:hover {
        background: #FF6B2B !important;
        color: #FFFFFF !important;
        border-color: #FF6B2B !important;
        box-shadow: 0 4px 14px rgba(255,107,43,0.25) !important;
        transform: translateY(-1px) !important;
    }
    
    [data-testid="column"]:has(.card-marker) [data-testid="stPageLink"] a:hover span {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# 5. TU LÓGICA DE INTERFAZ ORIGINAL (HERO BANNER)
if os.path.exists("almacen_logo.png") or os.path.exists("almacen_logo.jpg"):
    logo = "almacen_logo.png" if os.path.exists("almacen_logo.png") else "almacen_logo.jpg"
    # Ahora estas columnas están 100% a salvo de convertirse en tarjetas cuadradas involuntarias:
    c_img, c_txt = st.columns([1, 4])
    with c_img:
        st.image(logo, use_container_width=True)
    with c_txt:
        st.markdown("""
        <div style="padding-top:12px;">
            <div class="welcome-badge">Sistema de Gestión Comercial</div>
            <div class="welcome-title">Almacen <span>Gloria</span></div>
            <div class="welcome-subtitle">Precio, calidad y confianza.</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-badge">Sistema de Gestión Comercial</div>
        <div class="welcome-title">🛒 Almacen <span>Gloria</span></div>
        <div class="welcome-subtitle">Precio, calidad y confianza.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. GRID DE MÓDULOS
col1, col2, col3, col4 = st.columns(4)

with col1:
    # 💡 Inyectamos la marca invisible para activar el diseño de tarjeta en esta columna
    st.markdown('<div class="card-marker"></div>', unsafe_allow_html=True)
    st.markdown("### 💵 Control de Caja")
    st.write("Abre y cierra la caja del día. Realiza el arqueo y consulta el historial histórico.")
    st.page_link("pages/1_Control_de_Caja.py", label="Ir a Caja", icon="💵", use_container_width=True)

with col2:
    st.markdown('<div class="card-marker"></div>', unsafe_allow_html=True)
    st.markdown("### 📦 Inventario")
    st.write("Registra productos, actualiza precios y gestiona el stock disponible con el lector.")
    st.page_link("pages/2_Inventario.py", label="Ir a Inventario", icon="📦", use_container_width=True)

with col3:
    st.markdown('<div class="card-marker"></div>', unsafe_allow_html=True)
    st.markdown("### 🛒 Punto de Venta")
    st.write("Escanea códigos de barra, procesa ventas y cobra de forma rápida y sencilla.")
    st.page_link("pages/3_Punto_de_Venta.py", label="Ir a POS", icon="🛒", use_container_width=True)

with col4:
    st.markdown('<div class="card-marker"></div>', unsafe_allow_html=True)
    st.markdown("### 📊 Reportes")
    st.write("Consulta gráficos de ventas, utilidades netas y los artículos más vendidos del mes.")
    st.page_link("pages/4_Reportes.py", label="Ir a Reportes", icon="📊", use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("Panel Central de Administración - Almacen Gloria · Beni, Bolivia")