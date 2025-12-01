from functools import wraps
from flask import request, jsonify
from app.services.auth_service import AuthService

def token_requerido(f):
    """
    Decorador para proteger rutas, asegurando que un token JWT válido esté presente
    y que el usuario asociado exista.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        #Obtener el token del encabezado Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                #Esperamos 'Bearer <token>'
                token = auth_header.split(" ")[1]
            except IndexError:
                pass #Si no hay 'Bearer ' o el formato es incorrecto, token sigue siendo None
        
        if not token:
            return jsonify({
                'success': False, 
                'message': 'Token JWT no encontrado o formato incorrecto.'
            }), 401 
        
        #Verificar y decodificar el token
        valid, payload = AuthService.verificar_token(token)
        
        if not valid:
            error_message = payload.get('error', 'Token inválido')
            return jsonify({
                'success': False, 
                'message': error_message
            }), 401
            
        #Obtener el usuario
        user_id = payload.get('user_id')
        usuario_actual = AuthService.obtener_usuario_por_id(user_id)
        
        if not usuario_actual:
            return jsonify({
                'success': False, 
                'message': 'Usuario asociado al token no encontrado.'
            }), 401 
        
        #Pasar el objeto Usuario al endpoint
        return f(usuario_actual, *args, **kwargs)

    return decorated


def mfa_requerido(f):
    """
    Decorador para proteger rutas sensibles. 
    Asegura que el token JWT sea válido Y que la MFA haya sido verificada en el login, 
    usando el claim 'mfa_verified' en el token.
    """
    @wraps(f)
    @token_requerido  # Asegura que el token sea válido primero
    def decorated(usuario_actual, *args, **kwargs):
        # Obtener el token del encabezado (ya validado por @token_requerido)
        token = request.headers['Authorization'].split(" ")[1]
        
        # Decodificar el token (si pasó @token_requerido, es válido)
        _, payload = AuthService.verificar_token(token)
        
        # Verificar si el usuario tiene MFA activada
        if usuario_actual.mfa_enabled:
            # Verificar si el claim 'mfa_verified' está presente y es True
            if not payload.get('mfa_verified', False):
                return jsonify({
                    'success': False, 
                    'message': 'Acceso denegado. Se requiere verificación MFA reciente (re-login).'
                }), 403 
        
        # Si el usuario NO tiene MFA activa O tiene MFA activa y el claim es True, 
        # se permite el acceso.
        return f(usuario_actual, *args, **kwargs)

    return decorated


def rol_requerido(rol_necesario):
    """
    Decorador que verifica el rol del usuario autenticado.
    """
    def decorator(f):
        @wraps(f)
        @token_requerido
        def decorated_function(usuario_actual, *args, **kwargs):
            if usuario_actual.rol != rol_necesario:
                return jsonify({
                    'success': False, 
                    'message': f'Acceso denegado. Se requiere el rol: {rol_necesario}'
                }), 403 
            return f(usuario_actual, *args, **kwargs)
        return decorated_function
    return decorator