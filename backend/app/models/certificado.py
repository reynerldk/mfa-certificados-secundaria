from app.models import db 
from datetime import datetime

class Certificado(db.Model):
    __tablename__ = 'certificados'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id'))
    
    # Relación
    estudiante = db.relationship('Estudiante', backref='certificados')
    
    def __repr__(self):
        return f'<Certificado {self.codigo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'titulo': self.titulo,
            'fecha_emision': self.fecha_emision.strftime('%d/%m/%Y'),
            'estudiante_id': self.estudiante_id
        }