from fastapi import FastAPI, Depends

from metodos import inventario

app = FastAPI()
app.include_router(inventario.router, prefix="/muebles")