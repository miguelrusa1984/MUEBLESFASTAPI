from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Corregido: sin el prefijo "DATABASE_URL=" y con +pymysql
DB_URL = "mysql+pymysql://root:wbhfwXfyyIcHMVmuCOYIRkKaLAjnJxKo@shinkansen.proxy.rlwy.net:34734/railway"

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()