from pydantic import BaseModel
from typing import Optional

class MuebleBase(BaseModel):
    nombre: str
    tipo: str
    material: str
    precio: float
    stock: int

    class Config:
        orm_mode = True