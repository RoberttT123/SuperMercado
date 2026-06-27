from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.supabase_client import supabase
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"👤 Intentando login con: {form_data.username}")
    
    try:
        result = supabase.table("usuarios")\
            .select("*")\
            .eq("username", form_data.username)\
            .execute()
        print(f"📦 Resultado BD: {result.data}")
    except Exception as e:
        print(f"❌ Error BD: {e}")
        raise HTTPException(status_code=500, detail=f"Error BD: {str(e)}")

    if not result.data:
        print("⚠️ Usuario no encontrado")
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    user = result.data[0]
    print(f"✅ Usuario encontrado: {user['username']} / role: {user['role']}")
    print(f"🔑 Hash en BD: {user.get('hashed_password', 'VACIO')[:20]}...")

    if not user.get("hashed_password"):
        raise HTTPException(status_code=500, detail="Usuario sin contraseña configurada")

    if not verify_password(form_data.password, user["hashed_password"]):
        print("❌ Contraseña incorrecta")
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = create_access_token({"sub": user["username"], "role": user["role"]})
    print("🎉 Login exitoso")

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"]
    }