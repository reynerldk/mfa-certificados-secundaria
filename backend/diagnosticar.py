# diagnostic.py
import sys
import os

# Agregar la ruta actual al path de Python
sys.path.append(os.path.dirname(__file__))

print("🔍 Iniciando diagnóstico...")

try:
    print("1. Intentando importar create_app...")
    from app import create_app
    print(" create_app importado correctamente")
    
    print("2. Ejecutando create_app()...")
    app = create_app()
    
    if app is None:
        print(" create_app() retornó None")
        print("3. Probable causa: Error en la inicialización de blueprints o base de datos")
    else:
        print(" create_app() retornó una aplicación Flask válida")
        print(f"   Tipo: {type(app)}")
        
except ImportError as e:
    print(f" Error de importación: {e}")
    print("   Posibles causas:")
    print("   - Falta archivo __init__.py en alguna carpeta")
    print("   - Error en imports circulares")
    print("   - Módulo no encontrado")
    
except Exception as e:
    print(f" Error general: {e}")
    print("   Revisa los archivos de inicialización")

print(" Diagnóstico completado")