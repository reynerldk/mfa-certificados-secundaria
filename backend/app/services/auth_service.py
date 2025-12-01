from datetime import datetime, timedelta
import jwt
from flask import current_app, request, jsonify 
from functools import wraps 
from app.models import db
from app.models.usuario import Usuario
import pyotp
import qrcode
import os

class AuthService:
    """Servicio para manejar autenticación y autorización"""
    
    @staticmethod
    def _generar_token(usuario, type='access'):
        """Genera un token JWT para el usuario con expiración dinámica."""
        
        # Determinar la expiración basada en el tipo de token
        if type == 'access':
            expires_delta = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=24))
        elif type == 'temp':
            # Token de corta duración para el proceso MFA (ej: 5 minutos)
            expires_delta = timedelta(minutes=5)
        else:
            expires_delta = timedelta(seconds=0) # Por seguridad

        payload = {
            'user_id': usuario.id,
            'username': usuario.username,
            'email': usuario.email,
            'rol': usuario.rol,
            'type': type, # Indica si es 'access' o 'temp'
            'exp': datetime.utcnow() + expires_delta,
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        return token

    @staticmethod
    def generar_token(usuario):
        """Genera el token de acceso final de larga duración."""
        return AuthService._generar_token(usuario, type='access')

    @staticmethod
    def registrar_usuario(username, email, password, rol='administrador'):
        """
        Registra un nuevo usuario en el sistema.
        Retorna: (success: bool, message: str, user: Usuario)
        """
        # Validar que el username no exista
        if Usuario.query.filter_by(username=username).first():
            return False, "El nombre de usuario ya existe", None
        
        # Validar que el email no exista
        if Usuario.query.filter_by(email=email).first():
            return False, "El correo electrónico ya está registrado", None
        
        # Validar contraseña (mínimo 6 caracteres)
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres", None
        
        # Crear nuevo usuario
        try:
            nuevo_usuario = Usuario(
                username=username,
                email=email,
                rol=rol
            )
            # Asumiendo que set_password hashea la contraseña
            nuevo_usuario.set_password(password)
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            return True, "Usuario registrado exitosamente", nuevo_usuario
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error al registrar usuario: {str(e)}", None
    
    @staticmethod
    def login(username, password):
        """
        Autentica un usuario con username y password, e inicia el flujo MFA si está activo.
        Retorna: (success: bool, message: str, token: str, user: dict)
        """
        usuario = Usuario.query.filter_by(username=username).first()
        
        if not usuario:
            return False, "Usuario o contraseña incorrectos", None, None
        
        if not usuario.is_active:
            return False, "Usuario inactivo. Contacte al administrador", None, None
        
        if usuario.is_account_locked():
            tiempo_restante = (usuario.locked_until - datetime.utcnow()).seconds // 60
            return False, f"Cuenta bloqueada. Intente en {tiempo_restante} minutos", None, None
        
        if not usuario.check_password(password):
            usuario.increment_login_attempts()
            db.session.commit()
            
            intentos_restantes = 5 - usuario.login_attempts
            if intentos_restantes > 0:
                return False, f"Contraseña incorrecta. {intentos_restantes} intentos restantes", None, None
            else:
                return False, "Cuenta bloqueada por múltiples intentos fallidos", None, None
        
        # Login exitoso - resetear intentos
        usuario.reset_login_attempts()
        db.session.commit()
        
        # LÓGICA DE FLUJO MFA
        if usuario.mfa_enabled:
            # Se genera el token TEMPORAL para la verificación en el Paso 2
            temp_token = AuthService._generar_token(usuario, type='temp')
            return True, "Login exitoso. Se requiere código MFA", temp_token, usuario.to_dict(include_mfa_status=True)
        else:
            # Login directo, se genera el token de ACCESO final
            access_token = AuthService.generar_token(usuario)
            return True, "Login exitoso", access_token, usuario.to_dict(include_mfa_status=True)

    
    @staticmethod
    def verificar_token(token):
        """
        Verifica y decodifica un token JWT.
        Retorna: (valid: bool, payload: dict)
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            return True, payload
        
        except jwt.ExpiredSignatureError:
            return False, {'error': 'Token expirado'}
        
        except jwt.InvalidTokenError:
            return False, {'error': 'Token inválido'}
    
    @staticmethod
    def obtener_usuario_por_id(user_id):
        """Obtiene un usuario por su ID"""
        return Usuario.query.get(user_id)
    
    @staticmethod
    def cambiar_password(usuario, password_actual, password_nueva):
        """
        Cambia la contraseña de un usuario.
        Retorna: (success: bool, message: str)
        """
        if not usuario.check_password(password_actual):
            return False, "Contraseña actual incorrecta"
        
        if len(password_nueva) < 6:
            return False, "La nueva contraseña debe tener al menos 6 caracteres"
        
        try:
            usuario.set_password(password_nueva)
            db.session.commit()
            return True, "Contraseña cambiada exitosamente"
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error al cambiar contraseña: {str(e)}"
        
    @staticmethod
    def generar_mfa_setup(usuario):
        """
        Genera el secreto TOTP, lo guarda en el usuario y devuelve el URL 
        para el código QR.
        Retorna: (success: bool, message: str, qrcode_url: str)
        """
        if usuario.mfa_enabled:
            return False, "La autenticación multifactor ya está activada.", None
        
        secreto = pyotp.random_base32()
        
        # Guardar el secreto TEMPORALMENTE en el usuario
        usuario.mfa_secret = secreto
        db.session.commit()
        
        # Generar URL de aprovisionamiento (otpauth://...)
        app_name = "SistemaCertificados" 
        otp_uri = pyotp.totp.TOTP(secreto).provisioning_uri(
            name=usuario.email, 
            issuer_name=app_name
        )
        
        # Generar y guardar el código QR como imagen
        try:
            qr_filename = f"{usuario.username}_mfa_setup.png"
            qr_path = os.path.join(current_app.config['QR_CODES_FOLDER'], qr_filename)
            
            img = qrcode.make(otp_uri)
            img.save(qr_path)
            
            base_url = current_app.config['BASE_URL']
            qrcode_url = f"{base_url}/static/qrcodes/{qr_filename}"
            
            return True, "Secreto MFA generado. Escanee el código QR y verifique.", qrcode_url
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error al generar QR. Revise la configuración de la carpeta: {str(e)}", None

    @staticmethod
    def verificar_y_activar_mfa(usuario, codigo_totp):
        """
        Verifica el código TOTP y, si es válido, activa la MFA para el usuario.
        Retorna: (success: bool, message: str)
        """
        if usuario.mfa_enabled:
            return False, "La autenticación multifactor ya está activada."

        if not usuario.mfa_secret:
            return False, "El secreto MFA no ha sido generado. Ejecute /mfa/setup primero."

        totp = pyotp.TOTP(usuario.mfa_secret)

        if totp.verify(codigo_totp):
            # Código Válido: Activar la MFA permanentemente
            usuario.mfa_enabled = True
            db.session.commit()
            return True, "Autenticación multifactor activada exitosamente."
        else:
            # Código Inválido
            return False, "Código de verificación inválido. Intente de nuevo."
    
    @staticmethod
    def verificar_login_mfa(usuario, codigo_totp):
        """
        Verifica el código TOTP en el login.
        Retorna: (success: bool, message: str, token: str)
        """
        if not usuario.mfa_enabled:
            return False, "MFA no está activada para este usuario.", None

        if not usuario.mfa_secret:
            return False, "Error interno: Secreto MFA no encontrado.", None

        totp = pyotp.TOTP(usuario.mfa_secret)
        
        if totp.verify(codigo_totp):
            # Código válido: generar el token JWT de acceso final
            access_token = AuthService.generar_token(usuario)
            return True, "Verificación MFA exitosa.", access_token
        else:
            # Código inválido
            return False, "Código MFA inválido.", None
# DECORADOR PARA PROTECCIÓN DE RUTAS (token_requerido)
def token_requerido(f):
    """
    Decorador para proteger rutas, asegurando que el request contenga
    un token JWT válido en el header 'Authorization'.
    
    Pasa el objeto `usuario_actual` (instancia de app.models.Usuario) a la ruta.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        #Obtener el token del header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # El formato es "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                # Si no tiene el formato correcto, ignorar
                pass
        
        if not token:
            return jsonify({'success': False, 'message': 'Token de autenticación es requerido.'}), 401

        #Verificar y decodificar el token
        valid, payload = AuthService.verificar_token(token)

        if not valid:
            # El mensaje de error (expirado, inválido) ya viene en el payload
            error_message = payload.get('error', 'Token inválido o expirado')
            return jsonify({'success': False, 'message': error_message}), 401

        #Validar el tipo de token (debe ser 'access' para acceder a rutas protegidas)
        if payload.get('type') != 'access':
             return jsonify({'success': False, 'message': 'Token incorrecto. Se requiere un token de acceso.'}), 401

        #Encontrar el usuario en la base de datos
        user_id = payload.get('user_id')
        usuario_actual = AuthService.obtener_usuario_por_id(user_id)
        
        if not usuario_actual:
            return jsonify({'success': False, 'message': 'Usuario asociado al token no encontrado.'}), 401
        
        if not usuario_actual.is_active:
             return jsonify({'success': False, 'message': 'Usuario inactivo.'}), 403

        #Pasar el objeto usuario a la función decorada
        return f(usuario_actual, *args, **kwargs)

    return decorated