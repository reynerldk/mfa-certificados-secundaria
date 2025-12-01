from flask import Blueprint, request, send_file, jsonify
import io
from app.pdf_generator import generate_simple_certificate
from datetime import datetime

certificado_bp = Blueprint('certificado', __name__)

# Base de datos simulada con los 5 estudiantes
ESTUDIANTES_DB = {
    "CEB-001": "Ana Sofía Gómez López",
    "CEB-002": "Juan Pablo Rodríguez López", 
    "CEB-003": "María Fernanda Cruz Salazar",
    "CEB-004": "Luis Alberto Medina Torres",
    "CEB-005": "Mónica Villavicienzo Hurtado",
    # También mapear códigos generados automáticamente
    "ANA": "Ana Sofía Gómez López",
    "JUAN": "Juan Pablo Rodríguez López",
    "MARIA": "María Fernanda Cruz Salazar", 
    "LUIS": "Luis Alberto Medina Torres",
    "MONICA": "Mónica Villavicienzo Hurtado"
}

@certificado_bp.route('/download-certificate', methods=['GET'])
def download_certificate():
    try:
        code = request.args.get('code')
        
        if not code:
            return jsonify({'error': 'Código de certificado requerido'}), 400
        
        # Buscar el nombre del estudiante basado en el código
        nombre_estudiante = "Estudiante Demo"
        
        # Método 1: Buscar por código exacto en nuestra base de datos 
        if code in ESTUDIANTES_DB:
            nombre_estudiante = ESTUDIANTES_DB[code]
        else:
            # Método 2: Buscar por partes del código
            code_upper = code.upper()
            if '001' in code or 'ANA' in code_upper:
                nombre_estudiante = "Ana Sofía Gómez López"
            elif '002' in code or 'JUAN' in code_upper:
                nombre_estudiante = "Juan Pablo Rodríguez López"
            elif '003' in code or 'MARIA' in code_upper or 'FERNANDA' in code_upper:
                nombre_estudiante = "María Fernanda Cruz Salazar"
            elif '004' in code or 'LUIS' in code_upper:
                nombre_estudiante = "Luis Alberto Medina Torres" 
            elif '005' in code or 'MONICA' in code_upper:
                nombre_estudiante = "Mónica Villavicienzo Hurtado"
            else:
                # Método 3: Intentar extraer del código generado
                nombre_estudiante = mapear_codigo_a_estudiante(code)
        
        # Datos para el certificado
        cert_data = {
            'nombre_completo': nombre_estudiante,
            'codigo': code,
            'fecha_emision': datetime.now().strftime('%d/%m/%Y'),
            'titulo': 'Certificado de Estudios - Culminación Satisfactoria'
        }
        
        print(f" Generando certificado para: {nombre_estudiante} con código: {code}")
        
        # Generar PDF
        pdf_buffer = generate_simple_certificate(cert_data)
        
        # Devolver el PDF
        filename = f"Certificado_{nombre_estudiante.replace(' ', '_')}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f" Error generando certificado: {str(e)}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

def mapear_codigo_a_estudiante(codigo):
    """
    Función para mapear códigos a estudiantes específicos
    """
    # Mapeo exacto basado en los códigos que genera el frontend
    mapeo_exacto = {
        "CEB-ANA-001": "Ana Sofía Gómez López",
        "CEB-JUAN-002": "Juan Pablo Rodríguez López",
        "CEB-MARIA-003": "María Fernanda Cruz Salazar",
        "CEB-LUIS-004": "Luis Alberto Medina Torres",
        "CEB-MONICA-005": "Mónica Villavicienzo Hurtado"
    }
    
    # Primero buscar coincidencia exacta
    if codigo in mapeo_exacto:
        return mapeo_exacto[codigo]
    
    # Luego buscar por partes del código
    codigo_upper = codigo.upper()
    
    if 'ANA' in codigo_upper or '001' in codigo:
        return "Ana Sofía Gómez López"
    elif 'JUAN' in codigo_upper or '002' in codigo:
        return "Juan Pablo Rodríguez López"
    elif 'MARIA' in codigo_upper or '003' in codigo or 'FERNANDA' in codigo_upper:
        return "María Fernanda Cruz Salazar"
    elif 'LUIS' in codigo_upper or '004' in codigo:
        return "Luis Alberto Medina Torres"
    elif 'MONICA' in codigo_upper or '005' in codigo:
        return "Mónica Villavicienzo Hurtado"
    
    # Si no se encuentra, usar lógica de fallback
    estudiantes = [
        "Ana Sofía Gómez López",
        "Juan Pablo Rodríguez López", 
        "María Fernanda Cruz Salazar",
        "Luis Alberto Medina Torres",
        "Mónica Villavicienzo Hurtado"
    ]
    
    # Intentar extraer número del código
    try:
        numeros = ''.join(filter(str.isdigit, codigo))
        if numeros:
            indice = (int(numeros) % len(estudiantes)) - 1
            if 0 <= indice < len(estudiantes):
                return estudiantes[indice]
    except:
        pass
    
    # Último recurso: primer estudiante
    return estudiantes[0]


