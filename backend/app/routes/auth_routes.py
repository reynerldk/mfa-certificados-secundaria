from flask import Blueprint, request, jsonify, current_app
from app.services.auth_service import AuthService
from app.utils.auth_middleware import token_requerido

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({
            'success': False,
            'message': 'Faltan datos requeridos: username, email, password'
        }), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    rol = data.get('rol', 'administrador') 
    
    # Registrar usuario
    success, message, usuario = AuthService.registrar_usuario(
        username=username,
        email=email,
        password=password,
        rol=rol
    )
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'usuario': usuario.to_dict()
        }), 201
    else:
        return jsonify({
            'success': False,
            'message': message
        }), 400



# LOGIN 
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({
            "success": False,
            "message": "Faltan datos requeridos: username, password"
        }), 400

    username = data["username"]
    password = data["password"]
    success, message, token, usuario = AuthService.login(username, password)

    if not success:
        # Fallo de credenciales o bloqueo
        return jsonify({"success": False, "message": message}), 401

    if usuario and usuario.get('mfa_enabled'):
        return jsonify({
            "success": True,
            "message": message, # "Login exitoso. Se requiere código MFA"
            "token": None,
            "usuario": usuario
        }), 200 # 200 OK para iniciar el segundo paso
        
    return jsonify({
        "success": True,
        "message": message,
        "token": token,
        "usuario": usuario
    }), 200



# PERFIL DEL USUARIO

@auth_bp.route('/me', methods=['GET'])
@token_requerido
def get_current_user(usuario_actual):
    return jsonify({
        "success": True,
        "usuario": usuario_actual.to_dict()
    }), 200


# CAMBIAR CONTRASEÑA

@auth_bp.route('/cambiar-password', methods=['POST'])
@token_requerido
def cambiar_password(usuario_actual):
    data = request.get_json()

    if not data or not data.get("password_actual") or not data.get("password_nueva"):
        return jsonify({
            "success": False,
            "message": "Faltan datos requeridos: password_actual, password_nueva"
        }), 400

    success, message = AuthService.cambiar_password(
        usuario_actual,
        data["password_actual"],
        data["password_nueva"]
    )

    status = 200 if success else 400

    return jsonify({
        "success": success,
        "message": message
    }), status

# MFA SETUP (PASO 1: GENERAR QR)

@auth_bp.route('/mfa/setup', methods=['POST'])
@token_requerido
def mfa_setup(usuario_actual):
    """
    Genera el secreto MFA para el usuario autenticado, lo guarda 
    y devuelve el URL del Código QR.
    """
    # Llama al método del servicio que genera el secreto y el QR
    success, message, qrcode_url = AuthService.generar_mfa_setup(usuario_actual)
    
    if success:
        return jsonify({
            "success": True,
            "message": message,
            "qr_code_url": qrcode_url
        }), 200
    else:
        # 400 Bad Request si ya está activado o hubo un error de QR
        return jsonify({
            "success": False,
            "message": message
        }), 400


# MFA ACTIVACIÓN (PASO 2: VERIFICAR CÓDIGO)

@auth_bp.route('/mfa/activate', methods=['POST'])
@token_requerido
def mfa_activate(usuario_actual):
    """
    Verifica el código TOTP y activa permanentemente la MFA.
    Requiere el código TOTP de 6 dígitos en el cuerpo de la petición.
    """
    data = request.get_json()
    codigo_totp = data.get('codigo')

    if not codigo_totp or len(codigo_totp) != 6 or not codigo_totp.isdigit():
        return jsonify({
            "success": False,
            "message": "Se requiere un código TOTP de 6 dígitos válido."
        }), 400

    success, message = AuthService.verificar_y_activar_mfa(usuario_actual, codigo_totp)

    status = 200 if success else 400
    
    return jsonify({
        "success": success,
        "message": message
    }), status


# MFA VERIFICACIÓN EN LOGIN 

@auth_bp.route('/mfa/verify', methods=['POST'])
@token_requerido 
def mfa_verify(usuario_actual):
    """
    Verifica el código TOTP después de un login exitoso que requiere MFA.
    El cliente debe usar un token JWT válido (puede ser el token antiguo o uno temporal).
    """
    data = request.get_json()
    codigo_totp = data.get('codigo')

    if not codigo_totp or len(codigo_totp) != 6 or not codigo_totp.isdigit():
        return jsonify({
            "success": False,
            "message": "Se requiere un código TOTP de 6 dígitos válido."
        }), 400

    success, message, token = AuthService.verificar_login_mfa(usuario_actual, codigo_totp)

    if not success:
        return jsonify({"success": False, "message": message}), 401

    # Éxito: se devuelve el token JWT final 
    return jsonify({
        "success": True,
        "message": message,
        "token": token
    }), 200