from sqlalchemy import Column, Integer, String, Numeric 
from database import Base

class Mueble(Base):
    __tablename__ = "muebles"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50))
    material = Column(String(50))
    precio = Column(Numeric(10, 2)) 
    stock = Column(Integer)