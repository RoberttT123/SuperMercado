"""
src/database/connection.py
Conexión única (singleton) al cliente de Supabase.
"""

import os
from functools import lru_cache
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """
    Retorna un cliente Supabase reutilizable.
    lru_cache garantiza que solo se crea UNA instancia en toda la app.
    """
    url  = os.getenv("SUPABASE_URL")
    key  = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise EnvironmentError(
            "❌ Variables SUPABASE_URL y SUPABASE_KEY no encontradas.\n"
            "   Verifica que el archivo .env exista en la raíz del proyecto."
        )

    return create_client(url, key)