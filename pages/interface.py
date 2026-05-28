import streamlit as st
import pandas as pd
from logic.pos_logica import obtener_productos, registrar_venta

# Guardia de seguridad
if not st.session_state.get("logged_in"):
    st.switch_page("main.py")

# Inicialización de estado
if "carrito" not in st.session_state:
    st.session_state.carrito = []

st.title("🛒 Gestión Almacén Alexandra")

# Definición de pestañas
tab1, tab2 = st.tabs(["📦 Inventario", "💰 Punto de Venta (POS)"])

# --- PESTAÑA 1: INVENTARIO ---
with tab1:
    st.subheader("Stock Actual")
    productos = obtener_productos()
    if productos:
        df = pd.DataFrame(productos)
        # Seleccionamos solo las columnas relevantes para mostrar
        st.dataframe(df[['codigo', 'nombre', 'stock', 'precio_venta', 'categoria_id']], use_container_width=True)
    else:
        st.warning("No hay productos cargados.")

# --- PESTAÑA 2: POS ---
with tab2:
    col_prod, col_cart = st.columns([1.5, 1])
    
    with col_prod:
        st.subheader("Seleccionar Productos")
        productos = obtener_productos()
        for prod in productos:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{prod['nombre']}** | Stock: {prod['stock']} | Bs. {prod['precio_venta']}")
                if c2.button("➕", key=f"add_{prod['id']}"):
                    st.session_state.carrito.append(prod)
                    st.rerun()

    with col_cart:
        st.subheader("Carrito")
        total = 0
        if not st.session_state.carrito:
            st.info("El carrito está vacío")
        else:
            for i, item in enumerate(st.session_state.carrito):
                st.write(f"{item['nombre']} - Bs. {item['precio_venta']}")
                total += item['precio_venta']
            
            st.divider()
            st.metric("Total a pagar", f"Bs. {total:.2f}")
            
            if st.button("✅ Finalizar Venta"):
                # Se llama a la lógica de guardado
                if registrar_venta(st.session_state.carrito, total):
                    st.success("Venta registrada con éxito")
                    st.session_state.carrito = [] # Limpiar carrito
                    st.rerun()