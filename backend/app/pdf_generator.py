from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
from datetime import datetime

def generate_simple_certificate(cert_data):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    
    # Contenido del certificado
    content = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=1,  
        textColor=colors.darkblue,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle', 
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=1,
        textColor=colors.darkblue
    )
    
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=0  
    )
    
    name_style = ParagraphStyle(
        'NameStyle',
        parent=content_style,
        fontSize=16,
        textColor=colors.darkred,
        spaceAfter=20,
        alignment=1,  
        fontName='Helvetica-Bold'
    )
    
    # Encabezado
    content.append(Paragraph("CENTRO EDUCATIVO BREÑA", title_style))
    content.append(Paragraph("Institución Educativa Privada", subtitle_style))
    content.append(Spacer(1, 20))
    
    content.append(Paragraph("CERTIFICADO DE ESTUDIOS", title_style))
    content.append(Spacer(1, 30))
    
    # Cuerpo del certificado
    content.append(Paragraph("Se hace constar por medio del presente documento que:", content_style))
    content.append(Spacer(1, 15))
    
    # Nombre del estudiante (destacado)
    content.append(Paragraph(cert_data['nombre_completo'], name_style))
    content.append(Spacer(1, 15))
    
    content.append(Paragraph("ha culminado satisfactoriamente sus estudios de educación secundaria en nuestra institución educativa, habiendo demostrado dedicación, compromiso y excelencia académica durante su formación.", content_style))
    content.append(Spacer(1, 25))
    
    content.append(Paragraph("Este certificado se expide a solicitud del interesado para los fines que estime conveniente.", content_style))
    content.append(Spacer(1, 30))
    
    # Información del certificado en tabla
    info_data = [
        ['Código del certificado:', cert_data['codigo']],
        ['Fecha de emisión:', cert_data['fecha_emision']],
        ['Título otorgado:', cert_data['titulo']],
        ['Estado del certificado:', 'VÁLIDO']
    ]
    
    info_table = Table(info_data, colWidths=[2.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    content.append(info_table)
    content.append(Spacer(1, 40))
    
    # Firma y sello
    firma_data = [
        ['', ''],
        ['_________________________', '_________________________'],
        ['Director Académico', 'Secretaria General'],
        ['Centro Educativo Breña', 'Centro Educativo Breña']
    ]
    
    firma_table = Table(firma_data, colWidths=[2.5*inch, 2.5*inch])
    firma_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    content.append(firma_table)
    content.append(Spacer(1, 20))
    
    # Pie de página
    content.append(Paragraph("Lima, Perú", content_style))
    content.append(Spacer(1, 10))
    content.append(Paragraph("Documento generado", 
                           ParagraphStyle('Footer', parent=content_style, fontSize=9, textColor=colors.grey)))
    
    # Construir PDF
    doc.build(content)
    buffer.seek(0)
    return buffer