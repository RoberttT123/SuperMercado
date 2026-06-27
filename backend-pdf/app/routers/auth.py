from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import Usuario
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Buscar usuario en la base de datos
    user = db.query(Usuario).filter(Usuario.username == form_data.username).first()
    
    # 2. Validar usuario y contraseña
    # Nota: Aquí deberías usar verify_password(form_data.password, user.hashed_password)
    # Por ahora, simulamos la validación
    if not user or form_data.password != "admin": # Ejemplo simple
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # 3. Crear el token JWT
    token = create_access_token({"sub": user.username, "role": user.role})
    
    return {"access_token": token, "token_type": "bearer"}