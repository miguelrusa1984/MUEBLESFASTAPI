from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_jwt_extended import ( 
                                create_access_token, 
                                create_refresh_token, 
                                jwt_required, 
                                get_jwt_identity, 
                                get_jwt 
                                )

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os
from conexión.config import app, db
from modelos import model_mueble
from models.UserModels import db, Users
from datetime import timedelta

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = False

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False


app.json.ensure_ascii = False

jwt = JWTManager(app)
revoked_tokens = set()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload["jti"] in revoked_tokens

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "El token ha expirado", "code": "token_expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"error": "Token inválido", "code": "invalid_token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"error": "Token requerido", "code": "authorization_required"}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"error": "Token revocado", "code": "token_revoked"}), 401





@app.route("/api/public", methods=["GET"])
def public():
    """Ruta pública: no requiere autenticación."""
    return jsonify({"message": "Esta ruta es pública"}), 200



@app.route("/auth/register", methods=["POST"])
def registrarUsuario():
    data = request.get_json()
    nom_user = data.get("nom_user", "").strip()
    passw = data.get("password", "")

    if not nom_user or not passw:
        return jsonify({"Error": "El usuario y la contraseña son necesarias.."}), 400
    
    if Users.query.filter_by(nom_user=nom_user).first():
        return jsonify({"Error..": "El usuario ya existe...."}), 409

    usuario_helper = Users()
    usuario_helper.set_password(passw)
    
    nuevo_usuario = Users(
        nom_user=nom_user,
        password=usuario_helper.password,
        rol="user"
    )

    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"Message": f"El usuario {nom_user} ha sido creado con éxito."}), 201



@app.route("/api/login", methods=["POST"])
def loguearUsuario():
    data = request.get_json()
    username = data.get('nom_user')
    password = data.get('password')

    user = Users.query.filter_by(nom_user=username).first()

    if not user or not user.get_password(password):
        return jsonify({"Error..": "Credenciales invalidas..."}), 401
    
    additional_claims = {"role": user.rol}
    
    access_token = create_access_token(
        identity=user.nom_user, 
        additional_claims={"role": user.rol},
    )
    
    refresh_token = create_refresh_token(identity=user.nom_user)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": 900000000,
        "Usuario": user.nom_user
    }), 200


@app.route("/api/usuario", methods=['GET']) # Asegúrate que diga GET
@jwt_required() 
def consultar():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as = current_user), 200


@app.route("/api/profile", methods=["GET"])
@jwt_required()
def profile():
    """Ruta protegida: devuelve detalles del usuario autenticado."""
    current_user = get_jwt_identity() 
    claims = get_jwt()                
    
    return jsonify({
        "username": current_user,
        "role": claims.get("role"),
        "message": f"¡Hola, {current_user}!"
    }), 200


@app.route("/api/admin", methods=["GET"])
@jwt_required()
def admin_only():
    """Ruta protegida: solo usuarios con rol 'admin'."""
    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Acceso denegado: se requiere rol admin"}), 403

    todos_los_usuarios = Users.query.all()
    nombres_usuarios = [u.nom_user for u in todos_los_usuarios]

    return jsonify({
        "message": "Bienvenido al panel de administración",
        "users": nombres_usuarios
    }), 200



@app.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Obtener un nuevo access token usando el refresh token."""
    current_user = get_jwt_identity()
    
    user = Users.query.filter_by(nom_user=current_user).first()
    
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    new_access_token = create_access_token(
        identity=current_user,
        additional_claims={"role": user.rol}
    )
    
    return jsonify({"access_token": new_access_token}), 200

@app.route("/auth/logout", methods=["DELETE"])
@jwt_required()
def logout():
    """Añadir el identificador del token (jti) a la lista negra."""
    jti = get_jwt()["jti"]
    revoked_tokens.add(jti) 
    return jsonify({"message": "Sesión cerrada exitosamente"}), 200



@app.route("/auth/register-admin", methods=["POST"])
def registrarAdmin():
    data = request.get_json()
    nom_user = data.get("nom_user", "").strip()
    passw = data.get("password", "")

    if not nom_user or not passw:
        return jsonify({"Error": "El usuario y la contraseña son necesarios para el Admin"}), 400

    if Users.query.filter_by(nom_user=nom_user).first():
        return jsonify({"Error": "Este nombre de usuario ya está ocupado"}), 409

    usuario_helper = Users()
    usuario_helper.set_password(passw)

    nuevo_admin = Users(
        nom_user=nom_user,
        password=usuario_helper.password,
        rol="admin"  
    )

    try:
        db.session.add(nuevo_admin)
        db.session.commit()
        return jsonify({"Message": f"Administrador {nom_user} creado con éxito"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"Error": "No se pudo guardar en la base de datos"}), 500




# --- RUTAS DE INVENTARIO (Añadidas a app.py) ---

@app.route("/muebles/", methods=["GET"])
def consultar_muebles_root():
    return jsonify({"mensaje": "Conexión exitosa al módulo de inventario"}), 200

@app.route("/muebles/mueble_all", methods=["GET"])
def get_all_muebles():
    muebles = db.session.query(model_mueble.Mueble).all()
    resultado = []
    for m in muebles:
        resultado.append({
            "id": m.id,
            "nombre": m.nombre,
            "tipo": m.tipo,
            "material": m.material,
            "precio": m.precio,
            "stock": m.stock
        })
    return jsonify(resultado), 200

@app.route("/muebles/mueble/<int:muebleId>", methods=["GET"])
def get_mueble_by_id(muebleId):
    mueble = db.session.query(model_mueble.Mueble).filter_by(id=muebleId).first()
    if mueble:
        return jsonify({
            "id": mueble.id,
            "nombre": mueble.nombre,
            "precio": mueble.precio
        }), 200
    return jsonify({"error": "Mueble no encontrado"}), 404

@app.route("/muebles/add", methods=["POST"])
def crear_mueble_flask():
    data = request.get_json()
    nuevo_mueble = model_mueble.Mueble(
        id=data.get("id"), # Si tu modelo requiere ID manual
        nombre=data.get("nombre"),
        tipo=data.get("tipo"),
        material=data.get("material"),
        precio=data.get("precio"),
        stock=data.get("stock")
    )
    db.session.add(nuevo_mueble)
    db.session.commit()
    return jsonify({"message": "Mueble creado con éxito"}), 201

@app.route("/muebles/eliminar/<int:muebleId>", methods=["DELETE"])
def eliminar_mueble_flask(muebleId):
    mueble = db.session.query(model_mueble.Mueble).filter_by(id=muebleId).first()
    if not mueble:
        return jsonify({"error": "Mueble no encontrado"}), 404
    
    db.session.delete(mueble)
    db.session.commit()
    return jsonify({"mensaje": "Mueble eliminado con éxito", "id_eliminado": muebleId}), 200






from conexión.config import app, db

if __name__ == "__main__":
    # Esto permite que Railway asigne el puerto automáticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)