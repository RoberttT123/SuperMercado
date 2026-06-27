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
    
    # ¡Columna agregada según tu esquema de base de datos original!
    unidad = Column(String, default="unidad") 
    
    activo = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relación: El producto pertenece a una categoría
    categoria = relationship("Categoria", back_populates="productos")
    
    # -------------------------------------------------------------------------
    # FUTURAS RELACIONES (Descomenta estas líneas a medida que crees los 
    # modelos de ventas, compras e inventario para mantener todo conectado)
    # -------------------------------------------------------------------------
    # detalles_ventas = relationship("DetalleVenta", back_populates="producto")
    # detalles_compras = relationship("DetalleCompra", back_populates="producto")
    # detalles_pedidos = relationship("DetallePedido", back_populates="producto")
    # movimientos = relationship("InventarioMovimiento", back_populates="producto")