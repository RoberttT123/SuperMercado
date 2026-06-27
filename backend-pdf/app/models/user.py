# app/models/user.py
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    # Supabase utiliza UUIDs para la autenticación
    # 'as_uuid=True' permite trabajar con el ID como un objeto UUID de Python
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    
    # Username único y requerido
    username = Column(String, unique=True, nullable=False, index=True)
    
    # Rol del usuario (ej: 'admin' o 'vendedor')
    role = Column(String, nullable=False)

    def __repr__(self):
        return f"<Usuario(username='{self.username}', role='{self.role}')>"