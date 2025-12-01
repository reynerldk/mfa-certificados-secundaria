from app.models import db
from app.models.estudiante import Estudiante
from app.models.certificado import Certificado
from datetime import datetime

def seed_initial_data():
    """Crear datos iniciales de estudiantes"""
    
    # Verificar si ya existen estudiantes
    if Estudiante.query.count() == 0:
        estudiantes = [
            {
                'nombre_completo': 'Ana Sofía Gómez López',
                'email': 'student1@cebrena.edu.pe',
                'password': 'studentpassword1'
            },
            {
                'nombre_completo': 'Juan Pablo Rodríguez López', 
                'email': 'student2@cebrena.edu.pe',
                'password': 'studentpassword2'
            },
            {
                'nombre_completo': 'María Fernanda Cruz Salazar',
                'email': 'student3@cebrena.edu.pe', 
                'password': 'studentpassword3'
            },
            {
                'nombre_completo': 'Luis Alberto Medina Torres',
                'email': 'student4@cebrena.edu.pe',
                'password': 'studentpassword4'
            },
            {
                'nombre_completo': 'Mónica Villavicienzo Hurtado',
                'email': 'student5@cebrena.edu.pe',
                'password': 'studentpassword5'
            }
        ]
        
        for est_data in estudiantes:
            estudiante = Estudiante(
                nombre_completo=est_data['nombre_completo'],
                email=est_data['email'],
                password=est_data['password'] 
            )
            db.session.add(estudiante)
        
        db.session.commit()
        print(" 5 estudiantes creados exitosamente")


        