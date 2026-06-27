from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Copia la URI exacta desde Supabase Dashboard → Settings → Database
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.vpdbqgrjzhwrqmvmjrlh:MiPassword123456Rober@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"connect_timeout": 10}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()