from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from app.routers import auth, inventario, ventas,categoria, reportes,producto,caja,dashboard,proveedores,pedidos
app = FastAPI()



origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={"Access-Control-Allow-Origin": "http://localhost:5176"}
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

