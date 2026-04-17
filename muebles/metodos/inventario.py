from fastapi import APIRouter, Depends, HTTPException, status 
from sqlalchemy.orm import Session
from database import get_db
from modelos import model_mueble
from esquemas import schemas
from fastapi import HTTPException

router = APIRouter()

@router.get("/")
async def consultar():
    return "Conexión exitosa al módulo de inventario"

@router.get("/mueble_all")
def get_all_muebles(db: Session = Depends(get_db)):
    muebles = db.query(model_mueble.Mueble).all()
    return muebles

@router.get("/mueble/{muebleId}") 
def get_id_filter(muebleId: int, db: Session = Depends(get_db)):
    mueble = db.query(model_mueble.Mueble).filter(model_mueble.Mueble.id == muebleId).first()
    
    if mueble:
        return mueble
    
    return {"error": "Mueble no encontrado"}

@router.get("/mueble/{muebleId}")
def get_id_direct(muebleId : int, db: Session = Depends(get_db)):
    mueble = db.query(model_mueble.Mueble).get(muebleId)
    if (mueble):
        return mueble
    else:
        raise HTTPException(status_code=404, detail=f"Mueble con id {muebleId} no encontrado")
    
@router.post("/add", response_model=schemas.Mueble, status_code=status.HTTP_201_CREATED)
def crear_mueble(mueble: schemas.Mueble, sesion: Session = Depends(get_db)):
    muebleAdd = model_mueble.Mueble(
        id=mueble.id,
        nombre=mueble.nombre,
        tipo=mueble.tipo,
        material=mueble.material,
        precio=mueble.precio,
        stock=mueble.stock
    )
    
    sesion.add(muebleAdd)
    sesion.commit()
    sesion.refresh(muebleAdd)
    
    return muebleAdd


@router.delete("/eliminar/{muebleId}")
def eliminar_mueble(muebleId: int, db: Session = Depends(get_db)):
    mueble = db.query(model_mueble.Mueble).filter(model_mueble.Mueble.id == muebleId).first()
    
    if not mueble:
        raise HTTPException(status_code=404, detail=f"Mueble con id {muebleId} no encontrado")
    
    db.delete(mueble)
    db.commit()
    
    return {"mensaje": "Mueble eliminado con éxito", "id_eliminado": muebleId}