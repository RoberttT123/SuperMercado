"""
pages/2_📦_Inventario.py
Gestión de productos, stock y registro de compras.
"""

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from src.utils.sidebar import render_sidebar
from src.services.inventario_service import (
    get_todos_productos, get_categorias, buscar_productos,
    crear_producto, actualizar_producto, get_stock_critico,
    registrar_compra, get_producto_por_id
)
from src.utils.helpers import fmt_bs, calcular_margen

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Inventario · Almacén Gloria", page_icon="📦", layout="wide")


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

st.title("📦 Inventario")
st.markdown("---")

# ── Alertas de stock crítico ──────────────────────────────────────────────────
criticos = get_stock_critico()
if criticos:
    with st.expander(f"⚠️ {len(criticos)} producto(s) con stock crítico — clic para ver", expanded=False):
        for p in criticos:
            st.markdown(
                f"<div class='stock-bajo'>🔴 <strong>{p['nombre']}</strong> "
                f"— Stock: {p['stock']} / Mínimo: {p['stock_minimo']}</div>",
                unsafe_allow_html=True
            )

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_lista, tab_nuevo, tab_editar, tab_compra = st.tabs([
    "📋 Lista de Productos", "➕ Nuevo Producto", "✏️ Editar Producto", "📥 Registrar Compra"
])

categorias   = get_categorias()
cat_dict     = {c["nombre"]: c["id"] for c in categorias}
cat_nombres  = ["— Sin categoría —"] + list(cat_dict.keys())

# ── Tab 1: Lista ──────────────────────────────────────────────────────────────
with tab_lista:
    st.subheader("Todos los Productos")

    col_b, col_c = st.columns([3, 1])
    with col_b:
        termino = st.text_input("🔍 Buscar por nombre o código", placeholder="Ej: arroz o 7500123...")
    with col_c:
        cat_filtro = st.selectbox("Categoría", cat_nombres, key="filtro_cat")

    cat_id_filtro = cat_dict.get(cat_filtro) if cat_filtro != "— Sin categoría —" else None
    productos     = buscar_productos(termino, cat_id_filtro)

    if not productos:
        st.info("No se encontraron productos.")
    else:
        filas = []
        for p in productos:
            margen = calcular_margen(p["precio_compra"], p["precio_venta"])
            cat_n  = (p.get("categorias") or {}).get("nombre", "—")
            filas.append({
                "Código":       p["codigo"],
                "Nombre":       p["nombre"],
                "Categoría":    cat_n,
                "Compra":       fmt_bs(p["precio_compra"]),
                "Venta":        fmt_bs(p["precio_venta"]),
                "Margen":       f"{margen:.1f}%",
                "Stock":        p["stock"],
                "Mín.":         p["stock_minimo"],
                "Estado":       "✅" if p["stock"] > p["stock_minimo"] else "⚠️",
            })
        df = pd.DataFrame(filas)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Total: {len(productos)} productos")

# ── Tab 2: Nuevo Producto ─────────────────────────────────────────────────────
with tab_nuevo:
    st.subheader("Registrar Nuevo Producto")

    with st.form("form_nuevo_producto"):
        c1, c2 = st.columns(2)
        with c1:
            codigo   = st.text_input("📊 Código de barras *", placeholder="Ej: 7500123456789")
            nombre   = st.text_input("📝 Nombre del producto *", placeholder="Ej: Arroz Superior 1kg")
            cat_sel  = st.selectbox("🏷️ Categoría", cat_nombres, key="nuevo_cat")
            unidad   = st.selectbox("📐 Unidad de medida", ["unidad", "kg", "litro", "caja", "bolsa", "paquete"])
        with c2:
            precio_compra = st.number_input("💸 Precio de compra (Bs.)", min_value=0.0, value=0.0, step=0.5, format="%.2f")
            precio_venta  = st.number_input("💰 Precio de venta (Bs.) *", min_value=0.0, value=0.0, step=0.5, format="%.2f")
            stock_inicial = st.number_input("📦 Stock inicial", min_value=0, value=0, step=1)
            stock_min     = st.number_input("⚠️ Stock mínimo (alerta)", min_value=0, value=5, step=1)

        descripcion = st.text_area("📄 Descripción (opcional)", height=60)

        if precio_compra > 0 and precio_venta > 0:
            margen = calcular_margen(precio_compra, precio_venta)
            st.info(f"💡 Margen de ganancia: **{margen:.1f}%** — Ganancia por unidad: **{fmt_bs(precio_venta - precio_compra)}**")

        submitted = st.form_submit_button("✅ Guardar Producto", use_container_width=True)
        if submitted:
            if not codigo or not nombre or precio_venta <= 0:
                st.error("⚠️ Código, nombre y precio de venta son obligatorios.")
            else:
                cat_id = cat_dict.get(cat_sel) if cat_sel != "— Sin categoría —" else None
                try:
                    crear_producto({
                        "codigo":        codigo.strip(),
                        "nombre":        nombre.strip(),
                        "descripcion":   descripcion,
                        "categoria_id":  cat_id,
                        "precio_compra": precio_compra,
                        "precio_venta":  precio_venta,
                        "stock":         stock_inicial,
                        "stock_minimo":  stock_min,
                        "unidad":        unidad,
                    })
                    st.success(f"✅ Producto '{nombre}' registrado correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# ── Tab 3: Editar Producto ────────────────────────────────────────────────────
with tab_editar:
    st.subheader("Editar Producto Existente")
    busq_edit = st.text_input("🔍 Buscar producto a editar", placeholder="Nombre o código...", key="busq_edit")

    if busq_edit:
        resultados = buscar_productos(busq_edit)
        if not resultados:
            st.warning("No se encontraron productos.")
        else:
            opciones = {f"{p['codigo']} — {p['nombre']}": p for p in resultados}
            seleccion = st.selectbox("Selecciona el producto:", list(opciones.keys()))
            prod_sel  = opciones[seleccion]

            with st.form("form_editar_producto"):
                c1, c2 = st.columns(2)
                with c1:
                    e_nombre  = st.text_input("Nombre", value=prod_sel["nombre"])
                    e_cat     = st.selectbox(
                        "Categoría",
                        cat_nombres,
                        index=cat_nombres.index(
                            next((c["nombre"] for c in categorias if c["id"] == prod_sel.get("categoria_id")), "— Sin categoría —")
                        ) if prod_sel.get("categoria_id") else 0,
                        key="edit_cat"
                    )
                with c2:
                    e_compra  = st.number_input("Precio compra (Bs.)", value=float(prod_sel["precio_compra"]), step=0.5, format="%.2f")
                    e_venta   = st.number_input("Precio venta (Bs.)",  value=float(prod_sel["precio_venta"]),  step=0.5, format="%.2f")
                    e_stock   = st.number_input("Stock actual",         value=int(prod_sel["stock"]),   step=1)
                    e_stock_m = st.number_input("Stock mínimo",         value=int(prod_sel["stock_minimo"]), step=1)

                if st.form_submit_button("💾 Actualizar", use_container_width=True):
                    cat_id = cat_dict.get(e_cat) if e_cat != "— Sin categoría —" else None
                    actualizar_producto(prod_sel["id"], {
                        "nombre":        e_nombre,
                        "categoria_id":  cat_id,
                        "precio_compra": e_compra,
                        "precio_venta":  e_venta,
                        "stock":         e_stock,
                        "stock_minimo":  e_stock_m,
                    })
                    st.success("✅ Producto actualizado.")
                    st.rerun()

# ── Tab 4: Registrar Compra ───────────────────────────────────────────────────
with tab_compra:
    st.subheader("📥 Registrar Compra / Ingreso de Mercadería")
    st.caption("Agrega productos al carrito de compra para actualizar el stock.")

    if "carrito_compra" not in st.session_state:
        st.session_state.carrito_compra = []

    col_busq, col_cant, col_precio = st.columns([3, 1, 1])
    with col_busq:
        codigo_compra = st.text_input("📊 Código o nombre del producto", key="compra_codigo")
    with col_cant:
        cant_compra   = st.number_input("Cantidad", min_value=1, value=1, step=1, key="compra_cant")
    with col_precio:
        precio_compra_nuevo = st.number_input("Precio unit. (Bs.)", min_value=0.0, value=0.0, step=0.5, format="%.2f", key="compra_precio")

    if st.button("➕ Agregar al carrito"):
        prods = buscar_productos(codigo_compra)
        if not prods:
            st.error("Producto no encontrado.")
        else:
            p = prods[0]
            st.session_state.carrito_compra.append({
                "producto_id":    p["id"],
                "nombre":         p["nombre"],
                "cantidad":       cant_compra,
                "precio_unitario":precio_compra_nuevo or p["precio_compra"],
                "subtotal":       cant_compra * (precio_compra_nuevo or p["precio_compra"]),
            })

    if st.session_state.carrito_compra:
        st.markdown("#### Carrito de Compra")
        total_compra = 0
        for i, item in enumerate(st.session_state.carrito_compra):
            cc1, cc2, cc3, cc4 = st.columns([4, 1, 2, 1])
            cc1.write(item["nombre"])
            cc2.write(f"x{item['cantidad']}")
            cc3.write(fmt_bs(item["subtotal"]))
            if cc4.button("🗑️", key=f"del_compra_{i}"):
                st.session_state.carrito_compra.pop(i)
                st.rerun()
            total_compra += item["subtotal"]

        st.markdown(f"**Total compra: {fmt_bs(total_compra)}**")
        notas_compra = st.text_input("Notas (factura, proveedor, etc.)")

        c_reg, c_limpiar = st.columns(2)
        if c_reg.button("✅ Registrar Compra", use_container_width=True):
            try:
                registrar_compra(st.session_state.carrito_compra, notas=notas_compra)
                st.success("✅ Compra registrada y stock actualizado.")
                st.session_state.carrito_compra = []
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        if c_limpiar.button("🗑️ Limpiar carrito", use_container_width=True):
            st.session_state.carrito_compra = []
            st.rerun()