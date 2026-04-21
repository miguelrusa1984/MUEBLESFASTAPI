from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import os

app = Flask(__name__)

# Configuración de Base de Datos para Railway
# Intentamos leer de la variable de entorno de Railway primero
DB_URL = os.environ.get("DATABASE_URL", "mysql+pymysql://root:wbhfwXfyyIcHMVmuCOYIRkKaLAjnJxKo@shinkansen.proxy.rlwy.net:34734/railway")

if DB_URL.startswith("mysql://"):
    DB_URL = DB_URL.replace("mysql://", "mysql+pymysql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de Seguridad
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "super-secret-dev-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

db = SQLAlchemy(app)