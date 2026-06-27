from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class Categoria(Base):
    __tablename__ = "categorias"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relación bidireccional: Una categoría tiene muchos productos
    productos = relationship("Producto", back_populates="categoria")