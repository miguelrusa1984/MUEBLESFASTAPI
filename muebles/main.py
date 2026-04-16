from fastapi import FastAPI
from app_database.metodos import inventario

app = FastAPI()

# Incluimos el router siguiendo la guía [cite: 204, 221]
app.include_router(inventario.router, prefix="/inventario", tags=["Muebles"])
