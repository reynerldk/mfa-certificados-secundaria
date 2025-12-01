from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config

def create_app():
    """Crea y configura la aplicación Flask"""
    try:
        app = Flask(__name__, static_folder=Config.STATIC_FOLDER)
        print(" Aplicación Flask creada")

        # Cargar configuración
        app.config.from_object(Config)
        Config.init_app(app)

        # Habilitar CORS
        CORS(app)

        # Inicializar base de datos
        from app.models import init_db
        init_db(app)

        # Seed inicial
        with app.app_context():
            from app.seed_data import seed_initial_data
            seed_initial_data()

        # Registrar Blueprints - CON MANEJO DE ERRORES
        try:
            from app.routes.certificado_routes import certificado_bp
            app.register_blueprint(certificado_bp)
            print(" Blueprint de certificados registrado")
        except Exception as e:
            print(f" Error registrando certificado_bp: {e}")

        # ... otros blueprints

        # Rutas básicas
        @app.route('/')
        def index():
            return jsonify({
                'mensaje': '¡Bienvenido al Sistema de Certificados!',
                'version': '1.0',
                'status': 'funcionando',
                'endpoints': {
                    'download_certificate': '/download-certificate?code=CEB-001'
                }
            })

        @app.route('/health')
        def health():
            return jsonify({'status': 'ok'})

        print(" Aplicación configurada completamente")
        return app

    except Exception as e:
        print(f" ERROR CRÍTICO en create_app: {e}")
        import traceback
        traceback.print_exc()
        return None