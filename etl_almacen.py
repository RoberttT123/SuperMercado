import os
import re
import pandas as pd
import numpy as np
import sqlite3  # O puedes usar el engine de Supabase / SQL Server con sqlalchemy

def limpiar_precio_compuesto(val):
    """
    Divide precios con formato '265/260' en dos valores numéricos.
    Si no tiene barra, asigna el mismo valor a ambos o deja el segundo como None.
    """
    if pd.isna(val) or str(val).strip() == "" or str(val).strip() == "-":
        return None, None
    
    val_str = str(val).replace("Bs", "").replace(",", ".").strip()
    
    # Manejar formato con barra (Ej: 265/260)
    if '/' in val_str:
        partes = val_str.split('/')
        try:
            p1 = round(float(partes[0].strip()), 2)
            p2 = round(float(partes[1].strip()), 2)
            return p1, p2
        except ValueError:
            return None, None
    else:
        # Intentar extraer solo números si hay texto basura (como el caso de la sardina '¿´'p0677...')
        numeros = re.findall(r"\d+\.\d+|\d+", val_str)
        if numeros:
            try:
                p = round(float(numeros[0]), 2)
                return p, p
            except ValueError:
                return None, None
    return None, None

def procesar_almacen(file_path):
    excel_file = pd.ExcelFile(file_path)
    lista_productos = []
    df_proveedores = pd.DataFrame()

    for sheet_name in excel_file.sheet_names:
        # 1. Caso especial: Pestaña de contactos/proveedores
        if sheet_name.upper() == "NUMEROS":
            print("Processing sheet: NUMEROS (Proveedores)...")
            df_prov = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            df_prov.columns = ['telefono', 'nombre_preventista']
            df_prov = df_prov.dropna(subset=['telefono', 'nombre_preventista'], how='all')
            df_prov['telefono'] = df_prov['telefono'].astype(str).str.replace(".0", "", regex=False).str.strip()
            df_prov['nombre_preventista'] = df_prov['nombre_preventista'].str.strip()
            df_proveedores = df_prov
            continue
            
        print(f"Processing sheet: {sheet_name}...")
        
        # Leer la hoja completa sin procesar primero
        df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        # 2. Encontrar dinámicamente la fila de cabecera
        header_row_idx = None
        codigo_item_cat = "A-UNKNOWN"
        
        for idx, row in df_raw.iterrows():
            row_str = row.astype(str).tolist()
            # Capturar el código de categoría si aparece en las filas superiores (Ej: A-AP02)
            for cell in row_str:
                match = re.search(r"A-AP\d+", cell)
                if match:
                    codigo_item_cat = match.group(0)
            
            # Identificar cabecera por palabras clave
            if any("PRODUCTO" in str(cell).upper() or "DESCRIPCIÓN" in str(cell).upper() for cell in row_str):
                header_row_idx = idx
                break
                
        if header_row_idx is None:
            print(f"⚠️ No se detectó cabecera estándar en la hoja {sheet_name}. Saltando...")
            continue
            
        # Re-leer la hoja saltando las filas basura superiores
        df_sheet = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=header_row_idx)
        
        # Limpiar nombres de columnas (quitar espacios, acentos y pasar a minúsculas)
        df_sheet.columns = [str(c).strip().upper() for c in df_sheet.columns]
        
        # Mapeo dinámico de columnas para evitar fallos de ortografía en el Excel
        col_producto = [c for c in df_sheet.columns if "PRODUCTO" in c]
        col_descripcion = [c for c in df_sheet.columns if "DESCRIP" in c]
        col_cantidad = [c for c in df_sheet.columns if "CANTIDAD" in c or "CATIDAD" in c]
        col_p_unitario = [c for c in df_sheet.columns if "UNITARIO" in c]
        col_p_mayor = [c for c in df_sheet.columns if "MAYOR" in c]
        
        # Procesar fila por fila de la hoja actual
        for _, row in df_sheet.iterrows():
            prod_val = row[col_producto[0]] if col_producto else None
            desc_val = row[col_descripcion[0]] if col_descripcion else None
            cant_val = row[col_cantidad[0]] if col_cantidad else None
            p_uni_raw = row[col_p_unitario[0]] if col_p_unitario else None
            p_may_raw = row[col_p_vector[0]] if col_p_mayor else (row[col_p_mayor[0]] if col_p_mayor else None)
            
            # Si toda la fila está vacía en datos clave, ignorar
            if pd.isna(prod_val) and pd.isna(desc_val) and pd.isna(p_uni_raw) and pd.isna(p_may_raw):
                continue
                
            # Normalizar Marca y Descripción (si el producto está en la columna PRODUCTO, suele ser la marca)
            marca = str(prod_val).strip() if not pd.isna(prod_val) else "Genérico"
            descripcion = str(desc_val).strip() if not pd.isna(desc_val) else ""
            
            if descripcion == "" and marca != "Genérico":
                descripcion = marca
                marca = "Genérico"
                
            # Evitar jalar filas de separación que dicen "BUSCADOR" o títulos repetidos
            if "LISTA DE PRECIOS" in marca.upper() or "TIPO DE" in marca.upper() or "BUSCADOR" in marca.upper():
                continue

            # Procesar la conversión de precios complejos
            p_uni_abierto, p_uni_cerrado = limpiar_precio_compuesto(p_uni_raw)
            p_may_abierto, p_may_cerrado = limpiar_precio_compuesto(p_may_raw)
            
            # Si el unitario cerrado es None pero el abierto existe, homologar
            if p_uni_abierto and not p_uni_cerrado: p_uni_cerrado = p_uni_abierto
            if p_may_abierto and not p_may_cerrado: p_may_cerrado = p_may_abierto

            # Estructurar el registro limpio
            lista_productos.append({
                "categoria": sheet_name.upper().strip(),
                "codigo_categoria": codigo_item_cat,
                "marca": marca if marca != "nan" else "Genérico",
                "descripcion": descripcion if descripcion != "nan" else "",
                "empaque_cantidad": str(cant_val).strip() if not pd.isna(cant_val) else "1 u",
                "precio_unitario_min": p_uni_abierto,
                "precio_unitario_max": p_uni_cerrado,
                "precio_mayorista_abierto": p_may_abierto,
                "precio_mayorista_cerrado": p_may_cerrado
            })
            
    df_productos_final = pd.DataFrame(lista_productos)
    return df_productos_final, df_proveedores

# --- EJECUCIÓN DEL SCRIPT ---
if __name__ == "__main__":
    # Cambia esto por la ruta de tu archivo (.xlsx o .xlsm)
    archivo_excel = "PRECIOS DE AA.xlsx" 
    
    if os.path.exists(archivo_excel):
        df_prod, df_prov = procesar_almacen(archivo_excel)
        
        print("\n Dataframe de Productos Limpio (Primeras 5 filas):")
        print(df_prod.head())
        
        print("\n Dataframe de Proveedores Limpio:")
        print(df_prov.head())
        
        # Guardar a Base de Datos Local SQLite de prueba para tu app
        conn = sqlite3.connect("almacen_alexandra.db")
        df_prod.to_sql("productos", conn, if_exists="replace", index=False)
        df_prov.to_sql("proveedores", conn, if_exists="replace", index=False)
        conn.close()
        
        print("\n¡Proceso de carga completado con éxito! Creada base de datos 'almacen_alexandra.db'")
    else:
        print(f"❌ No se encontró el archivo {archivo_excel} en el directorio actual.")