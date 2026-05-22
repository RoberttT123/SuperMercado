"""
src/utils/sidebar.py
Sidebar premium — Almacen Gloria
Diseño compacto optimizado para subir la navegación y colapsar correctamente sin FOUC ni saltos de imagen.
"""

import streamlit as st
import os
import base64

SIDEBAR_CSS = """
<style>

/* ❌ REEMPLAZAR LA 'X' NATIVA Y FORZAR VISIBILIDAD CONSTANTE */
section[data-testid="stSidebar"] button svg {
    display: none !important; /* Oculta la X original */
}

section[data-testid="stSidebar"] button {
    background-color: #FFFFFF !important; /* Fondo blanco para que contraste con el pastel */
    border: 1px solid #FFCCB3 !important; 
    border-radius: 8px !important;
    width: 32px !important;
    height: 32px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease-in-out !important;
    opacity: 1 !important; 
    visibility: visible !important;
    z-index: 99999 !important; 
    position: absolute !important; 
    top: 12px !important;
    right: 30px !important; /* Controla qué tan a la izquierda se posiciona */
}

section[data-testid="stSidebar"] button::before {
    content: "❯" !important; 
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    color: #FF6B2B !important; 
    display: block !important;
    opacity: 1 !important;
    visibility: visible !important;
}

section[data-testid="stSidebar"] button:hover {
    background-color: #FFF3EE !important;
    border-color: #FF6B2B !important;
    box-shadow: 0 2px 8px rgba(255,107,43,0.15) !important;
}


/* 🚀 ELIMINAR EL TECHO NATIVO DE STREAMLIT */
[data-testid="stSidebarContent"], 
[data-testid="stSidebarUserContent"],
[data-testid="stSidebarHeader"] {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}

[data-testid="stHeader"], .stHeader {
    display: none !important;
}

/* 🎨 FONDO GLOBAL DE LA APP */
[data-testid="stAppViewContainer"] {
    background-color: #FDF6F0 !important;
}
[data-testid="stAppViewContainer"] > .main {
    background-color: #FDF6F0 !important;
}

/* 🚪 🟠 BARRA LATERAL CON DEGRADADO NARANJA PASTEL */
[data-testid="stSidebar"][data-collapsed="false"] {
    /* Va de un tono crema casi blanco arriba a un naranja pastel suave abajo */
    background: linear-gradient(180deg, #FFF9F6 0%, #FFE4D6 100%) !important;
    border-right: 2px solid #FFD0B8 !important;
    min-width: 260px !important;
    max-width: 260px !important;
    box-shadow: 3px 0 20px rgba(255,107,43,0.05) !important;
    transition: all 0.2s ease-in-out !important;
}

[data-testid="stSidebar"][data-collapsed="true"] {
    min-width: 0px !important;
    max-width: 0px !important;
    width: 0px !important;
    border-right: none !important;
    margin-left: -260px !important;
    transition: all 0.2s ease-in-out !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    overflow-x: hidden;
}

[data-testid="stSidebarNav"] { 
    display: none !important; 
    visibility: hidden !important;
}

/* 🎛️ HEADER BANNER */
.sb-header {
    background: linear-gradient(150deg, #FF6B2B 0%, #E85510 100%);
    padding: 1.4rem 1rem 0.8rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-top: -3.5rem !important; 
}

/* ✨ QUITAR EL RECUADRO CUADRADO DEL LOGO (VOLVERLO CIRCULAR Y SIN SOMBRA) */
.sb-logo-img {
    width: 125px !important;
    max-width: 125px !important;
    height: 125px !important;
    margin: 0 auto 0.3rem auto;
    display: block;
    border-radius: 50% !important; /* Hace que el logo sea perfectamente redondo */
    object-fit: cover !important;   /* Evita distorsiones en imágenes no perfectamente cuadradas */
    box-shadow: none !important;    /* Elimina el marco/sombra cuadrada */
    border: none !important;        /* Quita bordes fantasma */
}

.sb-logo-name  {
    font-size: 0.9rem;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: 0.1em;
    margin-top: 0.4rem;
    text-shadow: 0 1px 4px rgba(0,0,0,0.15);
}
.sb-logo-slogan {
    font-size: 0.64rem;
    color: #FFE4D4;
    font-style: italic;
    margin-top: 0.1rem;
}

/* WIDGET CAJA COMPACTO */
.sb-caja-open {
    background: rgba(240, 250, 240, 0.8);
    border: 1px solid #A5D6A7;
    border-left: 3px solid #4CAF50;
    border-radius: 10px;
    padding: 0.45rem 0.75rem;
    margin: 0.6rem 0.7rem 0 0.7rem;
    backdrop-filter: blur(5px);
}
.sb-caja-closed {
    background: rgba(255, 243, 238, 0.8);
    border: 1px solid #FFCCB3;
    border-left: 3px solid #FF6B2B;
    border-radius: 10px;
    padding: 0.45rem 0.75rem;
    margin: 0.6rem 0.7rem 0 0.7rem;
    backdrop-filter: blur(5px);
}
.sb-caja-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    margin-right: 5px;
    vertical-align: middle;
}
.sb-caja-dot.green  { background: #4CAF50; animation: pulse-g 2s infinite; }
.sb-caja-dot.orange { background: #FF6B2B; }
@keyframes pulse-g {
    0%,100% { box-shadow: 0 0 0 0 rgba(76,175,80,0.4); }
    50%      { box-shadow: 0 0 0 5px rgba(76,175,80,0); }
}
.sb-caja-label { font-size: 0.58rem; text-transform: uppercase; letter-spacing: 0.09em; color: #777; margin-bottom: 0.1rem; }
.sb-caja-value { font-size: 0.82rem; font-weight: 700; color: #333; }
.sb-caja-sub   { font-size: 0.65rem; color: #666; margin-top: 1px; }

/* ETIQUETA SECCION */
.sb-nav-label {
    font-size: 0.58rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #A09088;
    padding: 0.8rem 1rem 0.3rem 1rem;
}

/* LINKS DE NAVEGACION (Ajustados para el fondo degradado) */
section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    display: flex !important;
    align-items: center !important;
    border-radius: 10px !important;
    margin: 2px 8px !important;
    padding: 0.55rem 0.85rem !important;
    color: #5C4A40 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    border: 1px solid transparent !important;
    transition: all 0.15s ease !important;
    background: transparent !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background: rgba(255, 255, 255, 0.5) !important;
    color: #FF6B2B !important;
    border-color: #FFCCB3 !important;
    transform: translateX(3px) !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
    background: #FFFFFF !important; /* Blanco sólido para resaltar sobre el fondo pastel */
    color: #E85510 !important;
    border-color: #FFCCB3 !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 10px rgba(232,85,16,0.08) !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] {
    margin: 0 !important;
    padding: 0 !important;
}

/* DIVIDER */
.sb-divider {
    border: none;
    border-top: 1px solid #EAD5C9;
    margin: 0.6rem 0.8rem 0.6rem 0.8rem;
}

/* WIDGET VENTAS */
.sb-stats-box {
    background: rgba(255, 255, 255, 0.6);
    border: 1px solid #FFD0B8;
    border-radius: 10px;
    padding: 0.7rem 0.85rem;
    margin: 0 0.7rem;
}
.sb-stats-label { font-size: 0.58rem; text-transform: uppercase; letter-spacing: 0.09em; color: #9A857A; margin-bottom: 0.25rem; }
.sb-stats-value { font-size: 1rem; font-weight: 800; color: #E85510; }
.sb-stats-sub   { font-size: 0.68rem; color: #8A756A; margin-top: 1px; }

/* FOOTER */
.sb-footer {
    text-align: center;
    font-size: 0.58rem;
    color: #9A857A;
    padding: 0.8rem 1rem;
    margin-top: 0.5rem;
    border-top: 1px solid #EAD5C9;
}

/* ESTILOS GLOBALES REUTILIZADOS */
h1 { color: #CC4A0A !important; }
h2, h3 { color: #E85510 !important; }

.stButton > button {
    background: linear-gradient(135deg, #FF6B2B, #E85510) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(255,107,43,0.25) !important;
    transition: all 0.18s ease !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

[data-testid="stMetricValue"] { color: #E85510 !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: #888888 !important; }

button[data-baseweb="tab"][aria-selected="true"] {
    color: #FF6B2B !important;
    border-bottom-color: #FF6B2B !important;
    font-weight: 700 !important;
}
button[data-baseweb="tab"] { color: #999999 !important; }

[data-testid="stExpander"] {
    border: 1px solid #FFE0CC !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
}

[data-testid="stDataFrame"] th {
    background: #FFF3EE !important;
    color: #E85510 !important;
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #FDF6F0; }
::-webkit-scrollbar-thumb { background: #FFCCB3; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #FF6B2B; }

</style>
"""

@st.cache_data
def obtener_base64_de_imagen(ruta_imagen: str) -> str:
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

def render_sidebar(current_page: str = "") -> None:
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:
        ruta_logo = "assets/logo.png" 
        logo_b64 = obtener_base64_de_imagen(ruta_logo)
        
        if logo_b64:
            extension = ruta_logo.split(".")[-1]
            img_src = f"data:image/{extension};base64,{logo_b64}"
            # 🔥 CORRECCIÓN AQUÍ: Se añade inline border-radius y object-fit para evitar esquinas cuadradas residuales
            logo_html = f'<img src="{img_src}" class="sb-logo-img" width="125" height="125" style="width: 125px !important; max-width: 125px !important; height: 125px !important; display: block !important; margin: 0 auto !important; border-radius: 50% !important; object-fit: cover !important; border: none !important;">'
        else:
            logo_html = '<div class="sb-logo-icon">🛒</div>'

        AJUSTE_EXTRA_CSS = "<style>[data-testid='stSidebarContent'] { padding-top: 0rem !important; } [data-testid='stSidebarUserContent'] { padding-top: 0rem !important; }</style>"

        st.markdown(f"""
{SIDEBAR_CSS}
{AJUSTE_EXTRA_CSS}
<div class="sb-header">
{logo_html}
<div class="sb-logo-name">ALMACEN GLORIA</div>
<div class="sb-logo-slogan">Precio, calidad y confianza.</div>
</div>
""", unsafe_allow_html=True)

        # ── Widget estado de caja compacto ──────────────────────────────────
        try:
            from src.services.caja_service import get_caja_abierta
            from src.utils.helpers import fmt_bs
            caja = get_caja_abierta()
            if caja:
                st.markdown(f"""
                <div class="sb-caja-open">
                    <div class="sb-caja-label"><span class="sb-caja-dot green"></span>Caja abierta</div>
                    <div class="sb-caja-value">{fmt_bs(caja['monto_inicial'])} inicial</div>
                    <div class="sb-caja-sub">Cajero: {caja.get('usuario','---')}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="sb-caja-closed">
                    <div class="sb-caja-label"><span class="sb-caja-dot orange"></span>Caja cerrada</div>
                    <div class="sb-caja-value">Abre la caja para vender</div>
                </div>
                """, unsafe_allow_html=True)
        except Exception:
            pass

        # ── Navegacion compacta ─────────────────────────────────────────────
        st.markdown('<div class="sb-nav-label">Menu principal</div>', unsafe_allow_html=True)

        st.page_link("main.py",                      label="🏠  Dashboard",       use_container_width=True)
        st.page_link("pages/1_Control_de_Caja.py",    label="💵  Control de Caja", use_container_width=True)
        st.page_link("pages/2_Inventario.py",          label="📦  Inventario",      use_container_width=True)
        st.page_link("pages/3_Punto_de_Venta.py",      label="🛒  Punto de Venta",  use_container_width=True)
        st.page_link("pages/4_Reportes.py",            label="📊  Reportes",        use_container_width=True)

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        # ── Widget ventas del dia compacto ──────────────────────────────────
        try:
            from src.services.ventas_service import get_ventas_del_dia
            from src.utils.helpers import fmt_bs
            ventas_hoy = [v for v in get_ventas_del_dia() if v["estado"] == "completada"]
            total_hoy  = sum(v["total"] for v in ventas_hoy)
            st.markdown(f"""
            <div class="sb-stats-box">
                <div class="sb-stats-label">Ventas de hoy</div>
                <div class="sb-stats-value">{fmt_bs(total_hoy)}</div>
                <div class="sb-stats-sub">{len(ventas_hoy)} transacciones</div>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass

        # ── Footer ──────────────────────────────────────────────────────────
        st.markdown("""
        <div class="sb-footer">
            Almacen Gloria &bull; Beni, Bolivia
        </div>
        """, unsafe_allow_html=True)