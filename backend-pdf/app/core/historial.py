"""
Historial de movimientos (bitácora de auditoría).

Registra quién hizo qué y cuándo en las operaciones que tocan el catálogo,
los precios y el stock. Solo el admin puede consultarlo (ver routers/historial.py).

Sobre el token: el resto de la API todavía no exige el JWT, así que aquí solo
se LEE para saber quién hace cada operación. Se verifica la firma (nadie puede
hacerse pasar por otro usuario) pero no la expiración, para no cortar las
sesiones largas que el resto del sistema hoy sí acepta.
"""
from datetime import timezone, timedelta
from typing import Optional

from fastapi import Request, HTTPException
from jose import jwt, JWTError

from app.supabase_client import supabase
from app.core.security import SECRET_KEY, ALGORITHM

TABLA = "historial_movimientos"
ZONA_BOLIVIA = timezone(timedelta(hours=-4))  # Bolivia no tiene horario de verano

ETIQUETAS = {
    "producto_creado": "Producto creado",
    "producto_editado": "Producto editado",
    "nivel_agregado": "Nivel agregado",
    "nivel_editado": "Nivel editado",
    "nivel_eliminado": "Nivel eliminado",
    "precio_editado": "Cambio de precio",
    "stock_editado": "Cambio de stock",
    "stock_ajustado": "Ajuste de stock",
    "compra_registrada": "Compra registrada",
    "venta_anulada": "Venta anulada",
}


# ── Identidad del usuario ────────────────────────────────────────────

def usuario_desde_request(request: Request) -> Optional[dict]:
    auth = request.headers.get("authorization") or ""
    if not auth.lower().startswith("bearer "):
        return None
    token = auth.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
    except JWTError:
        return None
    if not payload.get("sub"):
        return None
    return {"username": payload["sub"], "role": payload.get("role")}


def requiere_admin(request: Request) -> dict:
    """Dependencia de FastAPI: deja pasar solo al admin."""
    usuario = usuario_desde_request(request)
    if not usuario:
        raise HTTPException(status_code=401, detail="Sesión no válida, vuelve a iniciar sesión")
    if usuario.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Solo el administrador puede ver el historial")
    return usuario


# ── Registro ─────────────────────────────────────────────────────────

def registrar_varios(request: Request, movimientos: list) -> None:
    """Guarda uno o más movimientos en una sola llamada.

    Nunca lanza excepción: si el registro falla, la operación principal
    (crear producto, registrar compra...) ya se hizo y no debe deshacerse
    ni mostrarle un error al usuario por esto.
    """
    if not movimientos:
        return
    try:
        usuario = usuario_desde_request(request) or {}
        filas = [{
            "usuario": usuario.get("username") or "desconocido",
            "rol": usuario.get("role"),
            "accion": m["accion"],
            "modulo": m.get("modulo", "inventario"),
            "producto_id": m.get("producto_id"),
            "producto_nombre": m.get("producto_nombre"),
            "nivel": m.get("nivel"),
            "detalle": m.get("detalle"),
            "datos": m.get("datos"),
        } for m in movimientos]
        supabase.table(TABLA).insert(filas).execute()
    except Exception as e:
        print(f"⚠️ No se pudo guardar en el historial: {e}")


def registrar(request: Request, accion: str, detalle: str, **campos) -> None:
    registrar_varios(request, [{"accion": accion, "detalle": detalle, **campos}])


# ── Nombres para mostrar (nunca fallan) ──────────────────────────────
# Se consultan DESPUÉS de que la operación principal ya se guardó, así que un
# error aquí no puede convertirse en un error para el usuario (que podría
# reintentar y, por ejemplo, registrar la misma compra dos veces).

def _nombre(tabla: str, id_) -> Optional[str]:
    if not id_:
        return None
    try:
        filas = supabase.table(tabla).select("nombre").eq("id", id_).execute().data
        return filas[0]["nombre"] if filas else None
    except Exception:
        return None


def nombre_producto(producto_id) -> Optional[str]:
    return _nombre("productos", producto_id)


def nombre_proveedor(proveedor_id) -> Optional[str]:
    return _nombre("proveedores", proveedor_id)


# ── Formato y comparación ────────────────────────────────────────────

def bs(valor) -> str:
    try:
        return f"Bs {float(valor):.2f}"
    except (TypeError, ValueError):
        return "—"


def _normalizar(valor):
    return None if valor == "" else valor


def _iguales(a, b) -> bool:
    a, b = _normalizar(a), _normalizar(b)
    if a is None or b is None:
        return a is None and b is None
    try:
        return abs(float(a) - float(b)) < 0.005
    except (TypeError, ValueError):
        return str(a) == str(b)


def _texto(valor, es_dinero=False) -> str:
    valor = _normalizar(valor)
    if valor is None:
        return "—"
    if es_dinero:
        return bs(valor)
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor)


def _diferencias(antes: dict, cambios: dict, campos: dict) -> list:
    """Devuelve [(campo, etiqueta, valor_antes, valor_despues)] solo de lo que cambió de verdad."""
    salida = []
    for campo, etiqueta in campos.items():
        if campo in cambios and not _iguales(antes.get(campo), cambios[campo]):
            salida.append((campo, etiqueta, antes.get(campo), cambios[campo]))
    return salida


def _describir(difs: list, dinero=()) -> str:
    return " · ".join(
        f"{etiqueta}: {_texto(a, campo in dinero)} → {_texto(d, campo in dinero)}"
        for campo, etiqueta, a, d in difs
    )


def _datos(difs: list) -> dict:
    return {campo: {"antes": a, "despues": d} for campo, _, a, d in difs}


# ── Cambios de un nivel (precio / stock / otros) ─────────────────────

CAMPOS_PRECIO = {"precio_compra": "Precio compra", "precio_venta": "Precio venta"}
CAMPOS_STOCK = {"stock": "Stock"}
CAMPOS_OTROS = {"stock_minimo": "Stock mínimo", "contiene": "Contiene", "cantidad_contenida": "Cantidad contenida"}


def registrar_cambios_nivel(request: Request, antes: dict, cambios: dict) -> None:
    """La pantalla de edición reenvía TODOS los campos de cada nivel aunque no se
    hayan tocado, así que aquí se compara contra lo que había y solo se registra
    lo que cambió. Precio, stock y lo demás van en filas separadas para poder
    filtrarlos por tipo."""
    producto_nombre = (antes.get("productos") or {}).get("nombre")
    base = {"producto_id": antes.get("producto_id"), "producto_nombre": producto_nombre, "nivel": antes.get("nivel")}
    movimientos = []

    difs = _diferencias(antes, cambios, CAMPOS_PRECIO)
    if difs:
        movimientos.append({**base, "accion": "precio_editado",
                            "detalle": _describir(difs, dinero=CAMPOS_PRECIO), "datos": _datos(difs)})

    difs = _diferencias(antes, cambios, CAMPOS_STOCK)
    if difs:
        _, _, a, d = difs[0]
        try:
            delta = int(float(d)) - int(float(a or 0))
            signo = f" ({'+' if delta > 0 else ''}{delta})"
        except (TypeError, ValueError):
            signo = ""
        movimientos.append({**base, "accion": "stock_editado",
                            "detalle": _describir(difs) + signo, "datos": _datos(difs)})

    difs = _diferencias(antes, cambios, CAMPOS_OTROS)
    if difs:
        movimientos.append({**base, "accion": "nivel_editado",
                            "detalle": _describir(difs), "datos": _datos(difs)})

    registrar_varios(request, movimientos)


# ── Cambios de un producto (nombre / categoría / descripción) ───────

def registrar_cambios_producto(request: Request, producto_id: int, antes: dict, cambios: dict) -> None:
    campos = {"nombre": "Nombre", "categoria_id": "Categoría", "descripcion": "Descripción"}
    difs = _diferencias(antes, cambios, campos)
    if not difs:
        return

    # Mostrar nombres de categoría en lugar de números
    ids = {v for c, _, a, d in difs if c == "categoria_id" for v in (a, d) if v}
    nombres = {}
    if ids:
        try:
            filas = supabase.table("categorias").select("id, nombre").in_("id", list(ids)).execute().data
            nombres = {f["id"]: f["nombre"] for f in filas}
        except Exception:
            pass
    def categoria(valor):
        return nombres.get(valor, f"#{valor}") if valor else "Sin categoría"

    legibles = [
        (c, e, categoria(a), categoria(d)) if c == "categoria_id" else (c, e, a, d)
        for c, e, a, d in difs
    ]

    registrar(request, "producto_editado", _describir(legibles),
              producto_id=producto_id, producto_nombre=cambios.get("nombre") or antes.get("nombre"),
              datos=_datos(difs))
