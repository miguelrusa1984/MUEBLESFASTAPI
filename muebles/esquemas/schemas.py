from pydantic import BaseModel
from typing import Optional

class Mueble(BaseModel):
    id: Optional[int] = None
    nombre: str
    tipo: str
    material: str
    precio: float
    stock: int

    class Config:
        from_attributes = True