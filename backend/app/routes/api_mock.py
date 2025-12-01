import datetime
from flask import jsonify, request, Flask, send_file
from flask_cors import CORS
import io

# Blueprint de autenticación
from .auth_routes import auth_bp

# ---------------------------------------------
# APP MOCK PARA AUTENTICACIÓN Y CONSULTA
# ---------------------------------------------
def create_mock_app():
    app = Flask(__name__)
    CORS(app)
    app.config['DEBUG'] = True
    return app

app = create_mock_app()

MOCK_CERTIFICADOS = [
    # Tus datos mock…
]

app.register_blueprint(auth_bp)

# ---------------------------------------------
# CERTIFICADOS RECIENTES
# ---------------------------------------------
@app.route('/api/v1/certificados/recientes', methods=['GET'])
def get_recent_certificates():
    return jsonify(MOCK_CERTIFICADOS), 200

# ---------------------------------------------
# VERIFICAR CERTIFICADO
# ---------------------------------------------
@app.route('/api/v1/certificados/verificar/<codigo_unico>', methods=['GET'])
def verify_certificate(codigo_unico):
    if codigo_unico == 'CODE1234':
        return jsonify({
            "message": "Certificado Válido y Auténtico.",
            "estudiante_nombre": "María Fernanda Gómez",
            "titulo_obtenido": "Certificado de Estudios de Nivel Secundaria",
            "fecha_emision": "2025-01-15",
            "hash_verificado": "ABCDEF1234567890...",
            "log_creado": True
        }), 200

    return jsonify({"error": f"Certificado con código {codigo_unico} no encontrado o inválido."}), 404
