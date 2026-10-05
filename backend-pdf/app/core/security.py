import os
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Carga las variables del .env
load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Clave con la que se firman las sesiones. Si alguien la conoce puede fabricar
# un token de admin, así que en Render es OBLIGATORIA: sin ella el backend no
# arranca (Render sigue sirviendo la versión anterior hasta que se configure).
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if os.getenv("RENDER"):
        raise RuntimeError(
            "Falta la variable de entorno SECRET_KEY en Render. "
            "Agrégala en el servicio del backend (Environment) con un valor largo y aleatorio."
        )
    SECRET_KEY = "solo-para-desarrollo-local"

ALGORITHM = "HS256"

# Una sesión dura 12 horas sin uso. Mientras la persona sigue usando el sistema
# se renueva sola (ver app/core/auth.py), así nadie es expulsado a mitad de turno.
DURACION_SESION = timedelta(hours=12)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now(timezone.utc) + DURACION_SESION})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
