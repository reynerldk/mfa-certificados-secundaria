from app import create_app

app = create_app()

if __name__ == '__main__':
    if app is not None:
        print(f"Iniciando Flask en modo DEBUG: {app.config.get('DEBUG')}")
        print("Servidor corriendo en: http://127.0.0.1:5000")
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        print("ERROR: No se pudo crear la aplicación Flask")
        exit(1)