from fastapi import FastAPI
from app.routers import auth, ventas, reportes # Asegúrate de que estos archivos existan

app = FastAPI(title="API Almacen Gloria")

# Incluir los routers
app.include_router(auth.router)
app.include_router(ventas.router)
app.include_router(reportes.router) # (si usas router en reportes.py)