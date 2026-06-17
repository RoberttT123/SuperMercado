import streamlit as st
import os
import sys
import base64

st.set_page_config(page_title="Almacen Gloria", page_icon="🛒", layout="wide")

sys.path.append(os.path.abspath("src"))
from services.supabase_client import supabase

try:
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.role = None
except Exception:
    st.rerun()

if st.session_state.logged_in:
    if st.session_state.role == "admin":
        st.switch_page("pages/0_Dashboard_Admin.py")
    elif st.session_state.role == "vendedor":
        st.switch_page("pages/interface.py")
    st.stop()

# ✅ Cargar logo como base64 para poder centrarlo con HTML puro
def get_logo_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_html = ""
if os.path.exists("assets/logo.png"):
    logo_b64 = get_logo_base64("assets/logo.png")
    logo_html = f"""
        <div style="display:flex; justify-content:center; margin-bottom:8px;">
            <img src="data:image/png;base64,{logo_b64}" width="120" style="border-radius:8px;" />
        </div>
    """

st.markdown("""
<style>
    #MainMenu, header, [data-testid="stHeader"] { display: none !important; }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #FFDAB9 0%, #FF8C00 100%);
    }

    .stTextInput > div > div > input {
        border-radius: 15px !important;
        padding: 10px 15px !important;
        border: 1px solid #FFDAB9 !important;
    }

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

def autenticar_usuario(username, password):
    try:
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

col_left, col_center, col_right = st.columns([1, 1.5, 1])

with col_center:
    with st.container(border=True):

        # ✅ Logo centrado via HTML con base64 — no depende de st.image()
        st.markdown(logo_html, unsafe_allow_html=True)

        st.markdown(
            "<h3 style='text-align:center; color:#E85510; margin-top:0;'>Almacen Gloria</h3>",
            unsafe_allow_html=True
        )

        user = st.text_input("", placeholder="👤 Usuario")
        pwd  = st.text_input("", type="password", placeholder="🔒 Contraseña")

        if st.button("Ingresar"):
            if not user or not pwd:
                st.warning("Por favor, ingresa tus credenciales.")
            else:
                usuario_db = autenticar_usuario(user, pwd)
                if usuario_db:
                    st.session_state.logged_in = True
                    st.session_state.role = usuario_db.get("role")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

        st.markdown("""
            <div style="text-align:center; font-size:0.7rem; color:#666; margin-top:10px;">
                ¿Olvidaste tu contraseña? <br>
                ¿No tienes cuenta? <b>Contacta al administrador</b>
            </div>
        """, unsafe_allow_html=True)