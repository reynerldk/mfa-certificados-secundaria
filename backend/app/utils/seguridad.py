import bcrypt
import jwt
import datetime
import pyotp 
import hashlib
import hmac

SECRET_KEY = "TU_SUPER_SECRETO_PARA_JWT" 
ALGORITHM = "HS256"

#1)Hashing de Contraseñas (Bcrypt)
def hash_password(password: str) -> str:
    """Hashea una contraseña para almacenamiento seguro."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return bcrypt.checkpw(
        password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

#2)JSON Web Tokens (JWT)
def generate_auth_token(user_id: int, rol: str, token_type='access') -> str:
    """Genera un token JWT de acceso o temporal."""
    try:
        if token_type == 'access':
            # Token de larga duración 
            exp = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        elif token_type == 'temp':
            # Token temporal para el proceso MFA (ej. 5 minutos)
            exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        
        payload = {
            'exp': exp,
            'iat': datetime.datetime.utcnow(),
            'sub': user_id,       # Subject: ID del usuario
            'rol': rol,           # Rol del usuario
            'type': token_type
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        return str(e)

#3)Autenticación Multifactor (TOTP / PyOTP)
def generate_mfa_secret() -> str:
    """Genera un secreto TOTP base32 seguro."""
    return pyotp.random_base32()

def verify_mfa_token(secret: str, token: str) -> bool:
    """Verifica el código TOTP de 6 dígitos."""
    totp = pyotp.TOTP(secret)
    # Permite un pequeño desfase para tolerar errores de sincronización
    return totp.verify(token, valid_window=1) 

#4)Firma Digital de Certificados (HMAC)
def calculate_certificate_hash(data_string: str) -> str:
    """
    Calcula la firma digital (HMAC-SHA256) de una cadena de datos del certificado.
    Se utiliza una clave secreta (SECRET_KEY) compartida entre el generador y el verificador.
    """
    # Usamos la misma clave secreta de JWT, pero idealmente debería ser otra específica de certificados.
    # El hmac garantiza que solo alguien con la clave secreta pudo haber generado la firma.
    return hmac.new(
        SECRET_KEY.encode('utf-8'), 
        data_string.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()



