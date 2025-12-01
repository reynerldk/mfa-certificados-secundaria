from app.models import db  

class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Estudiante {self.nombre_completo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre_completo': self.nombre_completo,
            'email': self.email
        }