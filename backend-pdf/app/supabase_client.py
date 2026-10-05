from supabase import create_client
from supabase.lib.client_options import SyncClientOptions
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Por defecto, el cliente de Supabase usa UNA sola conexión HTTP/2 compartida.
# FastAPI atiende varias peticiones a la vez en hilos distintos (el Dashboard
# pide 5 cosas en paralelo), y cuando varios hilos usan esa misma conexión se
# pisan: falla una lectura ("[Errno 11] Resource temporarily unavailable") y
# arrastra a todas las consultas en curso, que terminan en error 500.
# Con HTTP/1.1, httpx usa un pool: cada consulta simultánea va por su propia
# conexión y no se pisan.
_http = httpx.Client(
    http2=False,
    timeout=httpx.Timeout(120.0, connect=15.0),  # 120 s, igual que el valor por defecto de Supabase
    limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
    follow_redirects=True,
)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY, options=SyncClientOptions(httpx_client=_http))
