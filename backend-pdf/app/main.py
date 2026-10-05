from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from app.routers import auth, inventario, ventas, categoria, reportes, caja, dashboard, proveedores, pedidos, clientes, historial
from app.core.auth import solo, ADMIN, VENDEDOR, TODOS, GESTION, CABECERA_TOKEN_NUEVO
app = FastAPI()

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")


# Si la sesión se renovó durante esta petición (ver app/core/auth.py),
# se manda el token nuevo al navegador en una cabecera.
@app.middleware("http")
async def entregar_token_renovado(request: Request, call_next):
    response = await call_next(request)
    token_nuevo = getattr(request.state, "token_renovado", None)
    if token_nuevo:
        response.headers[CABECERA_TOKEN_NUEVO] = token_nuevo
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[CABECERA_TOKEN_NUEVO],  # sin esto el navegador no deja leer el token renovado
)


# Endpoint liviano para el ping de mantenimiento (UptimeRobot / cron-job.org),
# NO toca Supabase para nada — solo mantiene despierto el contenedor de Render.
# Acepta HEAD porque UptimeRobot revisa así; sin esto respondía 405.
@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin")
    headers = {}
    if origin and origin in origins:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers=headers
    )


# ── Quién puede usar cada módulo ──────────────────────────────────────
# Todo exige sesión iniciada, salvo /auth/login y /health.
# Dentro de algunos módulos hay acciones con una regla más estricta
# (ej. en Inventario el vendedor solo puede ver productos, no modificarlos).
def acceso(*roles):
    return [Depends(solo(*roles))]


app.include_router(auth.router)                                         # público: login
app.include_router(dashboard.router, dependencies=acceso(*GESTION))
app.include_router(caja.router, dependencies=acceso(*GESTION))
app.include_router(ventas.router, dependencies=acceso(*GESTION))
app.include_router(reportes.router, dependencies=acceso(*GESTION))
app.include_router(proveedores.router, dependencies=acceso(*GESTION))
app.include_router(categoria.router, dependencies=acceso(*GESTION))
app.include_router(inventario.router, dependencies=acceso(*TODOS))      # escrituras: solo admin/cajero
app.include_router(clientes.router, dependencies=acceso(*TODOS))        # borrar: solo admin/cajero
app.include_router(pedidos.router, dependencies=acceso(ADMIN, VENDEDOR))
app.include_router(historial.router, dependencies=acceso(ADMIN))
