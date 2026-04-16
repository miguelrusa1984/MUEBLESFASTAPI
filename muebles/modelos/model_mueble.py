from sqlalchemy import Column, Integer, String, Float
from app_database.database import Base

class Mueble(Base):
    __tablename__ = "muebles"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    tipo = Column(String(50))
    material = Column(String(50))
    precio = Column(Float)
    stock = Column(Integer)