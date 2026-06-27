from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship
from app.database import Base

class InventarioMovimiento(Base):
    __tablename__ = "inventario_movimientos"

    movimiento_id = Column(Integer, primary_key=True, index=True)
    
    # Llave foránea que conecta con la tabla de productos
    producto_id = Column(Integer, ForeignKey("productos.id"))
    
    tipo_movimiento = Column(String, nullable=False) # Ej: 'ingreso', 'egreso', 'ajuste'
    cantidad = Column(Numeric, nullable=False)
    fecha = Column(DateTime, default=func.now())
    motivo = Column(Text, nullable=True)

    # Relación: Acceder a producto.movimientos para ver el historial
    producto = relationship("Producto", backref="movimientos")