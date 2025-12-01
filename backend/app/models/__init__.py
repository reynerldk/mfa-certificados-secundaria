from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from .usuario import Usuario
from .estudiante import Estudiante 
from .certificado import Certificado
from .log_verificacion import LogVerificacion

def init_db(app):
    """Inicializar la base de datos"""
    db.init_app(app)
    
    with app.app_context():


        # Crear todas las tablas
        db.create_all()
        print("Base de datos inicializada")
        
        # Mostrar estadísticas
        num_usuarios = Usuario.query.count()
        num_estudiantes = Estudiante.query.count()
        num_certificados = Certificado.query.count()
        
        print(f" Usuarios: {num_usuarios} | Estudiantes: {num_estudiantes} | Certificados: {num_certificados}")