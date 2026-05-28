import streamlit as st
import os
import sys

# 1. CONFIGURACIÓN (Debe ser el primer comando de Streamlit)
st.set_page_config(page_title="Almacen Gloria", page_icon="🛒", layout="centered")

# 2. CONFIGURACIÓN DE RUTA PARA IMPORTAR SERVICIOS
sys.path.append(os.path.abspath("src"))
from services.supabase_client import supabase

# 3. INICIALIZACIÓN DE ESTADO
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# 4. "GUARDIA" DE NAVEGACIÓN (Redirección automática)
if st.session_state.logged_in:
    if st.session_state.role == "admin":
        st.switch_page("pages/0_Dashboard_Admin.py")
    elif st.session_state.role == "vendedor":
        st.switch_page("pages/interface.py")
    st.stop()

# 5. CSS PARA EL DISEÑO COMPACTO Y ELIMINACIÓN DE UI STREAMLIT
st.markdown("""
<style>
    /* Ocultar elementos de Streamlit */
    #MainMenu, header, [data-testid="stHeader"] { display: none !important; }
    
    /* Fondo */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #FFDAB9 0%, #FF8C00 100%);
    }

    /* Estilo de inputs */
    .stTextInput > div > div > input {
        border-radius: 15px !important;
        padding: 10px 15px !important;
        border: 1px solid #FFDAB9 !important;
    }

    /* Estilo del botón */
    div.stButton > button {
        background-color: #FF6B2B !important;
        color: white !important;
        border-radius: 15px !important;
        width: 100% !important;
        font-weight: bold;
        border: none !important;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 6. FUNCIÓN DE AUTENTICACIÓN
def autenticar_usuario(username, password):
    try:
        # Nota: Cambia "usuarios" y los nombres de columnas si tu tabla es diferente
        response = supabase.table("usuarios") \
            .select("username, role") \
            .eq("username", username) \
            .eq("password", password) \
            .maybe_single() \
            .execute()
        
        return response.data if response.data else None
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

# 7. ESTRUCTURA VISUAL
col_left, col_center, col_right = st.columns([1, 1.5, 1]) 

with col_center:
    with st.container(border=True):
        
        # Logo centrado
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if os.path.exists("assets/logo.png"):
                st.image("assets/logo.png", width=120)

        st.markdown("<h3 style='text-align: center; color: #E85510;'>Almacen Gloria</h3>", unsafe_allow_html=True)

        # Formulario
        user = st.text_input("", placeholder="👤 Usuario")
        pwd = st.text_input("", type="password", placeholder="🔒 Contraseña")

        if st.button("Ingresar"):
            if not user or not pwd:
                st.warning("Por favor, ingresa tus credenciales.")
            else:
                usuario_db = autenticar_usuario(user, pwd)
                
                if usuario_db:
                    st.session_state.logged_in = True
                    st.session_state.role = usuario_db.get("role")
                    st.rerun() # Recarga para activar el guardia de arriba y redirigir
                else:
                    st.error("Usuario o contraseña incorrectos.")

        # Footer
        st.markdown("""
            <div style="text-align: center; font-size: 0.7rem; color: #666; margin-top: 10px;">
                ¿Olvidaste tu contraseña? <br>
                ¿No tienes cuenta? <b>Contacta al administrador</b>
            </div>
        """, unsafe_allow_html=True)