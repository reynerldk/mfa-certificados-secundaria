from app.models import db
from datetime import datetime
from flask import request, current_app

class LogVerificacion(db.Model):
    """Modelo para registrar intentos de verificación de certificados"""
    __tablename__ = 'log_verificaciones'

    id = db.Column(db.Integer, primary_key=True)
    
    certificado_id = db.Column(db.Integer, db.ForeignKey('certificados.id'), nullable=True, index=True) 
    
    codigo_unico = db.Column(db.String(36), nullable=False, index=True)
    fecha_verificacion = db.Column(db.DateTime, default=datetime.utcnow)
    es_valido = db.Column(db.Boolean, nullable=False)
    ip_verificacion = db.Column(db.String(45), nullable=True)
    notas = db.Column(db.String(500), nullable=True)


    
    @staticmethod
    def registrar(codigo_unico: str, es_valido: bool, notas: str, certificado_id: int = None):
        """
        Registra un evento de verificación.
        Si el certificado_id es conocido (verificación exitosa), se guarda.
        """
        try:
            ip_address = request.remote_addr if request and request.remote_addr else 'CLI/SYSTEM'
        except RuntimeError:
            ip_address = 'CLI/SYSTEM'

        nuevo_log = LogVerificacion(
            certificado_id=certificado_id,
            codigo_unico=codigo_unico,
            es_valido=es_valido,
            ip_verificacion=ip_address,
            notas=notas
        )
        db.session.add(nuevo_log)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al registrar log de verificación: {str(e)}")
            
    def to_dict(self):
        return {
            'id': self.id,
            'codigo_unico': self.codigo_unico,
            'fecha_verificacion': self.fecha_verificacion.isoformat(),
            'es_valido': self.es_valido,
            'ip_verificacion': self.ip_verificacion,
            'notas': self.notas,
        }