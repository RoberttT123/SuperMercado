import os
import re
import pandas as pd
from supabase import create_client, Client

# ============================================================
# CONFIGURACIÓN DE CONEXIÓN A TU SUPABASE
# ============================================================
SUPABASE_URL = "https://vpdbqgrjzhwrqmvmjrlh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwZGJxZ3Jqemh3cnFtdm1qcmxoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMDA4MDIsImV4cCI6MjA5NDg3NjgwMn0.YXh9z_RDR0JKu0KCVKiv56tR2PFfFv6SjN9dbVya3xw"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def limpiar_precio(val):
    """Extrae y normaliza un valor numérico decimal para los precios."""
    if pd.isna(val) or str(val).strip() in ["", "-", "0"]:
        return 0.0
    
    val_str = str(val).replace("Bs", "").replace(",", ".").strip()
    
    # Manejar formato de precios con barra (Ej: 120/119 o 265/260)
    if '/' in val_str:
        val_str = val_str.split('/')[0]
        
    # Extraer solo secuencias numéricas con o sin decimales
    numeros = re.findall(r"\d+\.\d+|\d+", val_str)
    if numeros:
        try:
            precio = round(float(numeros[0]), 2)
            if precio > 9999: 
                return 0.0
            return precio
        except ValueError:
            return 0.0
    return 0.0

def limpiar_cantidad(val):
    """Extrae de forma limpia la cantidad por empaque/bulto."""
    if pd.isna(val) or str(val).strip() == "":
        return 1
    numeros = re.findall(r"\d+", str(val))
    if numeros:
        return int(numeros[0])
    return 1

def migrar_almacen_a_supabase(file_path):
    excel_file = pd.ExcelFile(file_path)
    
    # ── 1. MIGRACIÓN DE PROVEEDORES (Pestaña NUMEROS) ──
    print("🚀 Procesando e insertando Proveedores desde la pestaña NUMEROS...")
    if "NUMEROS" in excel_file.sheet_names:
        df_prov = pd.read_excel(file_path, sheet_name="NUMEROS", header=None)
        df_prov.columns = ['telefono', 'nombre']
        df_prov = df_prov.dropna(subset=['telefono', 'nombre'], how='all')
        
        batch_proveedores = []
        for _, row in df_prov.iterrows():
            tel = str(row['telefono']).replace(".0", "").strip()
            nom = str(row['nombre']).strip()
            if nom and nom != "nan":
                batch_proveedores.append({
                    "nombre": nom,
                    "telefono": tel[:20],
                    "contacto": "Preventista",
                    "activo": True
                })
        
        if batch_proveedores:
            try:
                supabase.table("proveedores").insert(batch_proveedores).execute()
                print(f"   ✅ Se cargaron {len(batch_proveedores)} proveedores exitosamente.")
            except Exception as e:
                print(f"   ⚠️ Nota sobre proveedores (posible duplicado): {e}")

    # Homologación corregida según las categorías reales de tu Supabase
    map_categorias = {
        "COCINA": "Abarrotes",
        "CONSERVAS": "Abarrotes",
        "BEBIDAS SA": "Bebidas",
        "BEBIDAS CA": "Bebidas",
        "LÁCTEOS": "Lácteos",
        "LIMPIEZA": "Limpieza",
        "GALLETAS": "Panadería",
        "DULCES": "Confitería",
        "PLASTICOS": "Bazar / Otros",    # Corregido
        "CIGARROS": "Bazar / Otros",     # Corregido
        "MEDICAMENTOS": "Bazar / Otros", # Corregido
        "MAT.HOGAR": "Bazar / Otros"     # Corregido
    }

    # Descargar los IDs reales de las categorías desde tu Supabase
    print("\n🔍 Sincronizando identificadores de categorías desde Supabase...")
    res_cats = supabase.table("categorias").select("id, nombre").execute()
    db_categorias = {cat['nombre'].lower().strip(): cat['id'] for cat in res_cats.data}

    # ── 2. MIGRACIÓN DE PRODUCTOS ──
    print("\n📦 Iniciando lectura y transformación de productos...")
    contador_codigo_manual = 1000

    for sheet_name in excel_file.sheet_names:
        if sheet_name.upper() == "NUMEROS":
            continue
            
        print(f" -> Procesando hoja: {sheet_name}")
        df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        # Detectar la fila de cabecera
        header_row_idx = None
        for idx, row in df_raw.iterrows():
            row_str = row.astype(str).tolist()
            if any("PRODUCTO" in str(cell).upper() or "DESCRIPCIÓN" in str(cell).upper() for cell in row_str):
                header_row_idx = idx
                break
                
        if header_row_idx is None:
            print(f"   ⚠️ No se encontró la fila de cabecera en '{sheet_name}'. Saltando hoja.")
            continue
            
        df_sheet = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=header_row_idx)
        df_sheet.columns = [str(c).strip().upper() for c in df_sheet.columns]
        
        col_producto = [c for c in df_sheet.columns if "PRODUCTO" in c]
        col_descripcion = [c for c in df_sheet.columns if "DESCRIP" in c]
        col_cantidad = [c for c in df_sheet.columns if "CANTIDAD" in c or "CATIDAD" in c]
        col_p_unitario = [c for c in df_sheet.columns if "UNITARIO" in c]
        col_p_mayor = [c for c in df_sheet.columns if "MAYOR" in c]
        col_codigo_orig = [c for c in df_sheet.columns if "CODIGO" in c or "CÓDIGO" in c]

        # Resolver el ID de categoría con el nuevo mapeo corregido
        nombre_cat_destino = map_categorias.get(sheet_name.upper().strip(), "Bazar / Otros")
        categoria_id = db_categorias.get(nombre_cat_destino.lower().strip(), None)

        if categoria_id is None:
            print(f"   ⚠️ No se pudo encontrar el ID para la categoría '{nombre_cat_destino}'.")

        batch_productos = []

        for _, row in df_sheet.iterrows():
            prod_val = row[col_producto[0]] if col_producto else None
            desc_val = row[col_descripcion[0]] if col_descripcion else None
            cant_val = row[col_cantidad[0]] if col_cantidad else None
            p_uni_raw = row[col_p_unitario[0]] if col_p_unitario else None
            p_may_raw = row[col_p_mayor[0]] if col_p_mayor else None
            cod_raw = row[col_codigo_orig[0]] if col_codigo_orig else None
            
            if pd.isna(prod_val) and pd.isna(desc_val) and pd.isna(p_uni_raw) and pd.isna(p_may_raw):
                continue
                
            marca = str(prod_val).strip() if not pd.isna(prod_val) else ""
            desc = str(desc_val).strip() if not pd.isna(desc_val) else ""
            
            if "LISTA DE PRECIOS" in marca.upper() or "BUSCADOR" in marca.upper() or "TIPO DE" in marca.upper() or "N°" == marca:
                continue

            nombre_completo = f"{marca} {desc}".strip()
            if not nombre_completo or nombre_completo.lower() == "nan" or nombre_completo.isdigit():
                continue

            if cod_raw and not pd.isna(cod_raw) and str(cod_raw).strip() != "":
                codigo_final = str(cod_raw).strip()
            else:
                codigo_final = f"ALX-{sheet_name.replace(' ', '')[:3].upper()}-{contador_codigo_manual}"
                contador_codigo_manual += 1

            precio_venta_u = limpiar_precio(p_uni_raw)
            precio_mayor_bulto = limpiar_precio(p_may_raw)
            unidades_por_bulto = limpiar_cantidad(cant_val)

            if precio_venta_u == 0.0 and precio_mayor_bulto > 0:
                precio_venta_u = round((precio_mayor_bulto / unidades_por_bulto) * 1.15, 2)

            if precio_mayor_bulto > 0 and unidades_por_bulto > 0:
                precio_compra_u = round(precio_mayor_bulto / unidades_por_bulto, 2)
            else:
                precio_compra_u = round(precio_venta_u * 0.82, 2)

            if precio_venta_u == 0.0:
                precio_venta_u = round(precio_compra_u * 1.18, 2)

            batch_productos.append({
                "codigo": codigo_final[:50],
                "nombre": nombre_completo[:200],
                "descripcion": f"Empaque original: {cant_val if not pd.isna(cant_val) else '1 u'}",
                "categoria_id": categoria_id,  # Ahora sí tendrá el ID correcto (ej: 10)
                "precio_compra": precio_compra_u,
                "precio_venta": precio_venta_u,
                "stock": 0,
                "stock_minimo": 5,
                "unidad": "caja" if unidades_por_bulto > 1 and "1" not in str(cant_val) else "unidad",
                "activo": True
            })

        if batch_productos:
            try:
                supabase.table("productos").insert(batch_productos).execute()
                print(f"   ✅ Insertados {len(batch_productos)} productos correctamente en '{sheet_name}'.")
            except Exception as e:
                print(f"   ❌ Error al subir lote de '{sheet_name}': {e}")

if __name__ == "__main__":
    archivo_excel = "PRECIOS DE AA.xlsx"
    
    if os.path.exists(archivo_excel):
        print("⚡ Conectando a Supabase con mapeo corregido...")
        migrar_almacen_a_supabase(archivo_excel)
        print("\n🎉 ¡Proceso completado! Verifica de nuevo tu tabla 'productos' en Supabase.")
    else:
        print(f"❌ Error: El archivo '{archivo_excel}' no se encuentra en el directorio.")