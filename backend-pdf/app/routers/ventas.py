from fastapi import APIRouter

# ESTA ES LA LÍNEA QUE FALTA O ESTÁ MAL
router = APIRouter() 

# Aquí irán tus funciones, por ejemplo:
@router.get("/ventas")
def listar_ventas():
    return {"mensaje": "Lista de ventas"}