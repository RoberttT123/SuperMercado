"""
Control de acceso de la API.

- usuario_actual: exige un token válido y vigente (401 si no hay o expiró).
- solo(...roles): además exige uno de esos roles (403 si no).
- Renovación: cuando al token le queda menos de lo que dura una sesión menos
  una hora (o sea, se emitió hace más de una hora), se vuelve a leer el usuario
  de la base de datos y se emite un token nuevo, que el middleware de main.py
  devuelve en la cabecera X-Nuevo-Token. Así la sesión no vence mientras se usa,
  y si el admin cambia el rol de alguien, el cambio se aplica en máximo una hora.
"""
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError, ExpiredSignatureError

from app.supabase_client import supabase
from app.core.security import SECRET_KEY, ALGORITHM, DURACION_SESION, create_access_token

CABECERA_TOKEN_NUEVO = "X-Nuevo-Token"
RENOVAR_DESPUES_DE = timedelta(hours=1)

ADMIN = "admin"
CAJERO = "cajero"
VENDEDOR = "vendedor"
TODOS = (ADMIN, CAJERO, VENDEDOR)
GESTION = (ADMIN, CAJERO)


def _token(request: Request):
    auth = request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip() or None
    return None


def usuario_actual(request: Request) -> dict:
    token = _token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Inicia sesión para continuar")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Tu sesión expiró, vuelve a iniciar sesión")
    except JWTError:
        raise HTTPException(status_code=401, detail="Sesión no válida, vuelve a iniciar sesión")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Sesión no válida, vuelve a iniciar sesión")
    usuario = {"username": username, "role": payload.get("role")}

    restante = datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc) - datetime.now(timezone.utc)
    if restante < DURACION_SESION - RENOVAR_DESPUES_DE:
        filas = supabase.table("usuarios").select("username, role").eq("username", username).execute().data
        if not filas:
            raise HTTPException(status_code=401, detail="Tu usuario ya no existe, consulta con el administrador")
        usuario = {"username": filas[0]["username"], "role": filas[0]["role"]}
        request.state.token_renovado = create_access_token({"sub": usuario["username"], "role": usuario["role"]})

    request.state.usuario = usuario
    return usuario


def solo(*roles: str):
    """Dependencia que deja pasar solo a los roles indicados."""
    def verificar_rol(usuario: dict = Depends(usuario_actual)) -> dict:
        if usuario.get("role") not in roles:
            raise HTTPException(status_code=403, detail="No tienes permiso para esta acción")
        return usuario
    return verificar_rol


SOLO_GESTION = [Depends(solo(*GESTION))]
