import os
import uuid
import hashlib
from flask import current_app, request
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from app.models import db
from app.models.certificado import Certificado
from app.models.estudiante import Estudiante 
from app.models.log_verificacion import LogVerificacion 

class CertificadoService:
    """Servicio para generar, guardar y gestionar los certificados PDF."""

    @staticmethod
    def _calcular_hash_archivo(filepath: str) -> str | None:
        """
        Calcula el hash SHA256 de un archivo para usarlo como firma digital.
        """
        try:
            hash_sha256 = hashlib.sha256()
            with open(filepath, 'rb') as f:
                # Lee el archivo en bloques para manejar archivos grandes
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except FileNotFoundError:
            current_app.logger.error(f"Archivo no encontrado: {filepath}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error al calcular hash: {str(e)}")
            return None

    @staticmethod
    # CORRECCIÓN CLAVE: Tipo de retorno ahora incluye 4 valores (bool, str, str | None, str | None)
    def generar_y_guardar_certificado(estudiante_id: int, titulo_certificado: str) -> tuple[bool, str, str | None, str | None]:
        """
        Genera el PDF del certificado, calcula su hash (firma) y lo guarda en la DB.
        Retorna: (success, message, codigo_unico, url_certificado)
        """
        # Generar código único al inicio para usarlo en el retorno de errores
        codigo_unico = str(uuid.uuid4())
        
        estudiante = Estudiante.query.get(estudiante_id)

        if not estudiante:
            # CORRECCIÓN 1: Devolver 4 valores (el código único está disponible, los demás son None)
            return False, "Estudiante no encontrado.", codigo_unico, None
        
        # Validación: Usamos la matrícula para nombrar el archivo
        if not estudiante.matricula:
            # CORRECCIÓN 2: Devolver 4 valores
            return False, "El estudiante no tiene matrícula registrada.", codigo_unico, None


        # 1. Preparar datos y códigos
        fecha_emision = datetime.utcnow()
        
        # 2. Rutas de almacenamiento
        try:
            output_dir = current_app.config['CERTIFICADOS_FOLDER']
            os.makedirs(output_dir, exist_ok=True)
            
            # Usar matrícula y código único para el nombre de archivo
            filename = f"certificado_{estudiante.matricula}_{codigo_unico[:8]}.pdf"
            filepath = os.path.join(output_dir, filename)
            
        except Exception as e:
            # CORRECCIÓN 3: Devolver 4 valores
            return False, f"Error de configuración de carpeta: {str(e)}", codigo_unico, None


        # 3. GENERACIÓN DEL PDF con ReportLab
        try:
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter

            styles = getSampleStyleSheet()
            style_title = ParagraphStyle(
                'TitleStyle', parent=styles['Title'], fontSize=24, textColor=colors.darkblue, alignment=1, spaceAfter=20
            )
            style_body = ParagraphStyle(
                'BodyStyle', parent=styles['Normal'], fontSize=14, textColor=colors.black, alignment=1, leading=20
            )

            # --- Contenido del Certificado ---
            title = Paragraph(f"CERTIFICADO DE FINALIZACIÓN", style_title)
            title.wrapOn(c, width - 100, height)
            title.drawOn(c, 50, height - 80)
            
            text_lines = [
                f"La institución educativa certifica que:",
                "",
                # CORRECCIÓN CLAVE: Usar la propiedad nombre_completo
                f"<font size=20 color=red>{estudiante.nombre_completo}</font>", 
                f"con matrícula: <b>{estudiante.matricula}</b>",
                "",
                f"ha completado satisfactoriamente el programa de:",
                f"<b>{titulo_certificado}</b>",
                "",
                f"Emitido el {fecha_emision.strftime('%d/%m/%Y')} en conformidad con los estándares educativos.",
                "",
                f"Código Único de Verificación:",
                f"<font size=12 color=gray>{codigo_unico}</font>",
            ]
            
            y_position = height - 150
            for line in text_lines:
                p = Paragraph(line, style_body)
                p.wrapOn(c, width - 100, height)
                p.drawOn(c, 50, y_position)
                y_position -= p.height + 5

            c.line(width/4, 150, 3*width/4, 150)
            c.drawString(width/2 - 50, 135, "Firma del Director/Autoridad")

            c.save()

        except Exception as e:
            # CORRECCIÓN 4: Devolver 4 valores
            return False, f"Error ReportLab al generar PDF: {str(e)}", codigo_unico, None


        # 4. CALCULAR HASH (Firma Digital)
        pdf_hash = CertificadoService._calcular_hash_archivo(filepath)
        if not pdf_hash:
            # CORRECCIÓN 5: Devolver 4 valores
            return False, "Error al calcular el hash del certificado.", codigo_unico, None
        
        # 5. Guardar la metadata en la Base de Datos
        try:
            nuevo_certificado = Certificado(
                estudiante_id=estudiante_id,
                codigo_unico=codigo_unico,
                hash_firma=pdf_hash,
                fecha_emision=fecha_emision,
                titulo=titulo_certificado,
                ruta_archivo=filepath, 
            )
            db.session.add(nuevo_certificado)
            db.session.commit()
            
            # URL pública para que el cliente pueda descargarlo
            base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
            public_url = f"{base_url}/api/v1/certificados/archivo/{filename}"   
            
            # CORRECCIÓN 6: Retorno EXITOSO de 4 valores
            return True, "Certificado generado y registrado exitosamente.", codigo_unico, public_url
        
        except Exception as e:
            db.session.rollback()
            # Si falla la DB, intentar eliminar el archivo PDF generado previamente
            if os.path.exists(filepath):
                os.remove(filepath)
            # CORRECCIÓN 7: Devolver 4 valores
            return False, f"Error DB al registrar certificado: {str(e)}", codigo_unico, None

    @staticmethod
    def verificar_integridad(codigo_unico: str) -> tuple[bool, str, dict | None]:
        """
        [T11: Verificación de Integridad]
        Busca el certificado por código, recalcula el hash del archivo y 
        lo compara con la firma digital almacenada.
        """
        certificado = Certificado.query.filter_by(codigo_unico=codigo_unico).first()

        if not certificado:
            # Registrar intento fallido
            LogVerificacion.registrar(codigo_unico=codigo_unico, es_valido=False, notas="Código no encontrado")
            return False, "Código de certificado no encontrado o inválido.", None

        try:
            # 1. Recalcular el hash del archivo almacenado (Verificación de Integridad)
            hash_actual = CertificadoService._calcular_hash_archivo(certificado.ruta_archivo)
            
            # 2. Verificar la integridad y el estado
            integridad_valida = hash_actual == certificado.hash_firma
            estado_valido = certificado.estado == 'Válido'

            es_valido_final = integridad_valida and estado_valido
            
            # 3. Registrar la verificación
            LogVerificacion.registrar(
                codigo_unico=codigo_unico, 
                es_valido=es_valido_final, 
                notas=f"Integridad: {integridad_valida}. Estado: {certificado.estado}",
                # certificado_id=certificado.id # Asumiendo que LogVerificacion tiene un FK
            )
            
            if not integridad_valida:
                 return False, "La integridad del documento ha sido comprometida (Hash no coincide).", None
            
            if not estado_valido:
                return False, f"Certificado encontrado, pero su estado es: {certificado.estado}.", None

            # Éxito:
            data = {
                # CORRECCIÓN CLAVE: Usar la propiedad nombre_completo
                "estudiante": certificado.estudiante.nombre_completo,
                "titulo": certificado.titulo,
                "emision": certificado.fecha_emision.strftime("%d/%m/%Y"),
                "codigo_unico": certificado.codigo_unico,
                "firma_digital_db": certificado.hash_firma[:15] + "...",
                "estado": certificado.estado,
                "url_descarga_publica": f"{current_app.config['BASE_URL']}/certificados/{os.path.basename(certificado.ruta_archivo)}"
            }
            return True, "Certificado verificado. La integridad y el estado son válidos.", data

        except FileNotFoundError:
            LogVerificacion.registrar(codigo_unico=codigo_unico, es_valido=False, notas="Archivo PDF no encontrado en el servidor.")
            return False, "Error interno: El archivo físico del certificado no se encuentra en el servidor.", None
        
        except Exception as e:
            LogVerificacion.registrar(codigo_unico=codigo_unico, es_valido=False, notas=f"Error inesperado durante la verificación: {str(e)}")
            return False, f"Error inesperado durante la verificación: {str(e)}", None