from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from app.routers import auth, inventario, ventas,categoria, reportes,producto,caja,dashboard,proveedores,pedidos
app = FastAPI()



origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5176").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    )

app.include_router(auth.router)
app.include_router(inventario.router)
app.include_router(producto.router)
app.include_router(categoria.router)
app.include_router(proveedores.router)
app.include_router(ventas.router)
app.include_router(reportes.router)
app.include_router(caja.router)  
app.include_router(dashboard.router)
app.include_router(pedidos.router)

