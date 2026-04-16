from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app_database.database import get_db
from app_database.modelos import model_mueble
from app_database.esquemas import schemas

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- SEGURIDAD ---
SECRET_KEY = "SUPER_SECRET_KEY"
users_db = {
    "admin": {"user": "admin", "pass": pwd_context.hash("admin123"), "role": "superuser"},
    "tecnico": {"user": "tecnico", "pass": pwd_context.hash("tec123"), "role": "tecnico"},
    "invitado": {"user": "invitado", "pass": "", "role": "usuario"}
}

def create_token(data: dict):
    return jwt.encode({**data, "exp": datetime.utcnow() + timedelta(minutes=30)}, SECRET_KEY, algorithm="HS256")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return users_db.get(payload.get("sub"))

# --- MÉTODOS ---

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user: raise HTTPException(status_code=400, detail="Error")
    if user["role"] != "usuario" and not pwd_context.verify(form_data.password, user["pass"]):
        raise HTTPException(status_code=400, detail="Clave incorrecta")
    return {"access_token": create_token({"sub": user["user"], "role": user["role"]}), "token_type": "bearer"}

# GET - Todos los niveles
@router.get("/") 
def read_all(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return db.query(model_mueble.Mueble).all()

# POST - Solo Superusuario y Tecnico
@router.post("/add") 
def create(mueble: schemas.MuebleBase, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if user["role"] not in ["superuser", "tecnico"]: raise HTTPException(status_code=403)
    nuevo = model_mueble.Mueble(**mueble.dict())
    db.add(nuevo)
    db.commit()
    return nuevo

# PUT - Solo Superusuario y Tecnico
@router.put("/update/{id}") 
def update(id: int, datos: schemas.MuebleBase, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if user["role"] not in ["superuser", "tecnico"]: raise HTTPException(status_code=403)
    m = db.query(model_mueble.Mueble).filter(model_mueble.Mueble.id == id).first()
    for k, v in datos.dict().items(): setattr(m, k, v)
    db.commit()
    return m

#DELETE - Solo Superusuario
@router.delete("/delete/{id}")
def delete(id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if user["role"] != "superuser": raise HTTPException(status_code=403)
    m = db.query(model_mueble.Mueble).filter(model_mueble.Mueble.id == id).first()
    db.delete(m)
    db.commit()
    return {"status": "eliminado"}