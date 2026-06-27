from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class Producto(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, nullable=False, index=True) # Indexado para búsquedas rápidas
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    
    # Llave foránea que conecta con la tabla de categorías
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    
    precio_compra = Column(Numeric, default=0)
    precio_venta = Column(Numeric, default=0)
    stock = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=5)
    activo = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relación: El producto pertenece a una categoría
    categoria = relationship("Categoria", back_populates="productos")