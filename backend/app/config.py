import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

class Config:
    """Configuración base del proyecto"""
    
    # Configuración general
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///certificados.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Seguridad MFA
    MFA_SECRET_KEY = os.getenv('MFA_SECRET_KEY', 'mfa-secret')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # Rutas de archivos
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_FOLDER = os.path.join(BASE_DIR, '..', 'static')
    QR_CODES_FOLDER = os.path.join(STATIC_FOLDER, 'qrcodes')
    CERTIFICADOS_FOLDER = os.path.join(BASE_DIR, "certificados_pdf")
    
    # URL base
    BASE_URL = "http://localhost:5000"
    
    @staticmethod
    def init_app(app):
        """Crear carpetas necesarias"""
        os.makedirs(Config.QR_CODES_FOLDER, exist_ok=True)
        os.makedirs(Config.CERTIFICADOS_FOLDER, exist_ok=True)
        print("Carpetas de archivos creadas")