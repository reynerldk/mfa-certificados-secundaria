from flask import Blueprint, jsonify
from app.models import Estudiante

estudiantes_bp = Blueprint('estudiantes_bp', __name__, url_prefix='/api/v1/estudiantes')

@estudiantes_bp.route('/', methods=['GET'])
def listar_estudiantes():
    estudiantes = Estudiante.query.all()

    lista = [
        {
            "id": e.id,
            "nombres": e.nombres,
            "apellido_paterno": e.apellido_paterno,
            "apellido_materno": e.apellido_materno,
            "dni": e.dni,
            "matricula": e.matricula
        }
        for e in estudiantes
    ]

    return jsonify({
        "success": True,
        "estudiantes": lista
    }), 200

