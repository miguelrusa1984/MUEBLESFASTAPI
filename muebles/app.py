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
from models.UserModels import db, Users

jwt = JWTManager(app)
revoked_tokens = set()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    # jti es el identificador único del token
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
    
    additional_claims = {"rol": user.rol}
    
    access_token = create_access_token(
        identity=user.nom_user, 
        additional_claims=additional_claims
    )
    
    refresh_token = create_refresh_token(identity=user.nom_user)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": 900,
        "Usuario": user.nom_user
    }), 200


@app.route("/api/usuario", methods=['GET'])
@jwt_required() 
def consultar():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as = current_user), 200




from conexión.config import app, db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True, port=5000)