from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='administrador')

    #Campos para manejo de intentos
    login_attempts = db.Column(db.Integer, default=0, nullable =False)
    locked_until = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    #Campos de Autenticación Multifactor (MFA) 
    mfa_secret = db.Column(db.String(16), nullable=True) 
    mfa_enabled = db.Column(db.Boolean, default=False)

    # MÉTODOS DE CONTRASEÑA

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # MANEJO DE INTENTOS
    def increment_login_attempts(self):
        self.login_attempts += 1
        # Bloquear después de 5 intentos fallidos
        if self.login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)

    def reset_login_attempts(self):
        self.login_attempts = 0
        self.locked_until = None

    def is_account_locked(self):
        return self.locked_until and datetime.utcnow() < self.locked_until

    def to_dict(self, include_mfa_status=False): 
        """Convierte la instancia de Usuario a un diccionario."""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "rol": self.rol
        }
        if include_mfa_status:
            data["mfa_enabled"] = self.mfa_enabled 

        return data