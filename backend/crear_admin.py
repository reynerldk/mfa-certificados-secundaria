from app import create_app
from app.services.auth_service import AuthService

app = create_app()

with app.app_context():
    print("🔧 Creando usuario administrador...\n")
    
    # Datos del admin
    username = "admin"
    email = "admin@certificados.edu"
    password = "Admin123!"  # CAMBIAR en producción
    rol = "admin"
    
    # Intentar crear
    success, message, usuario = AuthService.registrar_usuario(username, email, password, rol)
    
    if success:
        print(" Usuario administrador creado exitosamente!")
        print(f"\n CREDENCIALES:")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Rol: {rol}")
        print(f"\n  IMPORTANTE: Cambia la contraseña después del primer login")
    else:
        print(f" Error: {message}")
        
        if "ya existe" in message.lower():
            print("\n El usuario admin ya existe. Intenta hacer login con las credenciales anteriores.")
    
    print("\n Proceso completado")