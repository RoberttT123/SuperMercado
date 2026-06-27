from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Reemplaza con tus datos reales de Supabase
# El formato es: postgresql://usuario:password@host:puerto/base_de_datos
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:[TU_PASSWORD]@db.xxxxxxx.supabase.co:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para usar en las rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()