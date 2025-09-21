from flask import Flask, request, jsonify
from flask_cors import CORS
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID
import os
import logging
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración Appwrite
client = Client()
client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PAGOS_OPERACIONES_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_PAGOS_OPERACIONES_API_KEY'))

databases = Databases(client)
DATABASE_ID = os.getenv('APPWRITE_COMPRA_CREDITOS_DATABASE_ID')
USUARIOS_CREDITOS_COLLECTION_ID = os.getenv('APPWRITE_USUARIOS_CREDITOS_COLLECTION_ID')

# Configuración de email para notificaciones
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL')

def generar_codigo_promocional():
    """Generar código promocional único"""
    return 'DEMO' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def enviar_email_aprobacion(email, nombre, codigo_promocional):
    """Enviar email de aprobación con código promocional"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Demo Aprobada - ExamPro AI'
        msg['From'] = EMAIL_USER
        msg['To'] = email

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; color: white; text-align: center;">
                <h1>¡Demo Aprobada!</h1>
                <p>Tu solicitud de demo ha sido aprobada</p>
            </div>
            
            <div style="padding: 2rem;">
                <h2>Hola {nombre},</h2>
                
                <p>Nos complace informarte que tu solicitud de demo para ExamPro AI ha sido <strong>aprobada</strong>.</p>
                
                <div style="background: #f0f4f8; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0;">
                    <h3 style="color: #667eea; margin-top: 0;">Tu Código Promocional:</h3>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #2d3748; text-align: center; background: white; padding: 1rem; border-radius: 4px; letter-spacing: 2px;">
                        {codigo_promocional}
                    </div>
                </div>
                
                <h3>¿Qué incluye tu demo?</h3>
                <ul>
                    <li>5,000 créditos promocionales</li>
                    <li>Acceso completo a todas las funciones</li>
                    <li>Evaluación con múltiples modelos de IA</li>
                    <li>Soporte técnico incluido</li>
                    <li>Válido por 30 días</li>
                </ul>
                
                <h3>Próximos pasos:</h3>
                <ol>
                    <li>Regístrate en la plataforma usando tu email</li>
                    <li>Ingresa el código promocional: <strong>{codigo_promocional}</strong></li>
                    <li>¡Comienza a evaluar exámenes con IA!</li>
                </ol>
                
                <div style="text-align: center; margin: 2rem 0;">
                    <a href="http://localhost:5000/registro" style="background: #667eea; color: white; padding: 1rem 2rem; text-decoration: none; border-radius: 8px; font-weight: bold;">
                        Comenzar Demo
                    </a>
                </div>
                
                <p><strong>¿Necesitas ayuda?</strong><br>
                Contáctanos en soporte@exampro.ai o responde a este email.</p>
                
                <hr style="margin: 2rem 0; border: none; border-top: 1px solid #e2e8f0;">
                <p style="color: #718096; font-size: 0.9rem;">
                    Este email fue enviado porque solicitaste una demo de ExamPro AI.<br>
                    © 2025 ExamPro AI. Todos los derechos reservados.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, email, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        logger.error(f"Error enviando email de aprobación: {e}")
        return False

def enviar_email_rechazo(email, nombre, motivo=""):
    """Enviar email de rechazo"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Solicitud de Demo - ExamPro AI'
        msg['From'] = EMAIL_USER
        msg['To'] = email

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #f56565; padding: 2rem; color: white; text-align: center;">
                <h1>Solicitud Revisada</h1>
                <p>Información sobre tu solicitud de demo</p>
            </div>
            
            <div style="padding: 2rem;">
                <h2>Hola {nombre},</h2>
                
                <p>Gracias por tu interés en ExamPro AI. Después de revisar tu solicitud, no podemos aprobar la demo en este momento.</p>
                
                {f'<p><strong>Motivo:</strong> {motivo}</p>' if motivo else ''}
                
                <h3>¿Qué puedes hacer?</h3>
                <ul>
                    <li>Envía una nueva solicitud con más detalles</li>
                    <li>Contáctanos directamente para aclarar dudas</li>
                    <li>Visita nuestra página de precios para otras opciones</li>
                </ul>
                
                <p>Estamos aquí para ayudarte. No dudes en contactarnos en soporte@exampro.ai</p>
                
                <div style="text-align: center; margin: 2rem 0;">
                    <a href="http://localhost:5000/demo" style="background: #667eea; color: white; padding: 1rem 2rem; text-decoration: none; border-radius: 8px; font-weight: bold;">
                        Nueva Solicitud
                    </a>
                </div>
                
                <hr style="margin: 2rem 0; border: none; border-top: 1px solid #e2e8f0;">
                <p style="color: #718096; font-size: 0.9rem;">
                    © 2025 ExamPro AI. Todos los derechos reservados.
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, email, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        logger.error(f"Error enviando email de rechazo: {e}")
        return False

@app.route('/api/solicitudes', methods=['GET'])
def get_solicitudes():
    """Obtener todas las solicitudes de demo con filtros"""
    try:
        estado = request.args.get('estado', 'todos')
        limite = int(request.args.get('limite', 50))
        
        # Por ahora simular datos ya que la colección aún no existe
        # En producción, consultar desde Appwrite
        solicitudes_simuladas = [
            {
                '$id': 'sol_001',
                'nombre': 'Ana García López',
                'email': 'ana.garcia@universidad.edu',
                'empresa': 'Universidad Nacional',
                'cargo': 'Coordinadora Académica',
                'telefono': '+51 999 123 456',
                'tipo_institucion': 'universidad',
                'num_estudiantes': '500-1000',
                'descripcion': 'Queremos evaluar exámenes de ingeniería con IA para mejorar la objetividad.',
                'estado': 'pendiente',
                'fecha_solicitud': '2025-09-10T14:30:00Z',
                'fecha_revision': None,
                'revisor': None,
                'codigo_promocional': None,
                'motivo_rechazo': None
            },
            {
                '$id': 'sol_002',
                'nombre': 'Carlos Mendoza',
                'email': 'carlos@institutotech.com',
                'empresa': 'Instituto Tecnológico',
                'cargo': 'Director de Evaluación',
                'telefono': '+51 987 654 321',
                'tipo_institucion': 'instituto',
                'num_estudiantes': '100-500',
                'descripcion': 'Necesitamos automatizar la corrección de exámenes técnicos.',
                'estado': 'aprobada',
                'fecha_solicitud': '2025-09-08T10:15:00Z',
                'fecha_revision': '2025-09-09T09:30:00Z',
                'revisor': 'Admin',
                'codigo_promocional': 'DEMO123ABC',
                'motivo_rechazo': None
            },
            {
                '$id': 'sol_003',
                'nombre': 'María Rodríguez',
                'email': 'maria.rodriguez@colegio.edu',
                'empresa': 'Colegio San Martín',
                'cargo': 'Subdirectora',
                'telefono': '+51 912 345 678',
                'tipo_institucion': 'colegio',
                'num_estudiantes': '50-100',
                'descripcion': 'Información insuficiente',
                'estado': 'rechazada',
                'fecha_solicitud': '2025-09-07T16:45:00Z',
                'fecha_revision': '2025-09-08T11:00:00Z',
                'revisor': 'Admin',
                'codigo_promocional': None,
                'motivo_rechazo': 'Información incompleta sobre el proyecto'
            }
        ]
        
        # Filtrar por estado si se especifica
        if estado != 'todos':
            solicitudes_filtradas = [s for s in solicitudes_simuladas if s['estado'] == estado]
        else:
            solicitudes_filtradas = solicitudes_simuladas
        
        # Estadísticas
        total = len(solicitudes_simuladas)
        pendientes = len([s for s in solicitudes_simuladas if s['estado'] == 'pendiente'])
        aprobadas = len([s for s in solicitudes_simuladas if s['estado'] == 'aprobada'])
        rechazadas = len([s for s in solicitudes_simuladas if s['estado'] == 'rechazada'])
        
        return jsonify({
            'solicitudes': solicitudes_filtradas[:limite],
            'estadisticas': {
                'total': total,
                'pendientes': pendientes,
                'aprobadas': aprobadas,
                'rechazadas': rechazadas
            }
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo solicitudes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/solicitudes', methods=['POST'])
def crear_solicitud():
    """Crear nueva solicitud de demo"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['nombre', 'email', 'empresa', 'cargo', 'telefono', 'tipo_institucion', 'num_estudiantes', 'descripcion']
        for campo in campos_requeridos:
            if not data.get(campo):
                return jsonify({'error': f'Campo requerido: {campo}'}), 400
        
        # En producción, crear documento en Appwrite
        nueva_solicitud = {
            'id': 'sol_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)),
            'nombre': data['nombre'],
            'email': data['email'],
            'empresa': data['empresa'],
            'cargo': data['cargo'],
            'telefono': data['telefono'],
            'tipo_institucion': data['tipo_institucion'],
            'num_estudiantes': data['num_estudiantes'],
            'descripcion': data['descripcion'],
            'estado': 'pendiente',
            'fecha_solicitud': datetime.now().isoformat(),
            'fecha_revision': None,
            'revisor': None,
            'codigo_promocional': None,
            'motivo_rechazo': None
        }
        
        # Enviar notificación al admin (opcional)
        logger.info(f"Nueva solicitud de demo: {data['email']} - {data['empresa']}")
        
        return jsonify({
            'success': True,
            'message': 'Solicitud enviada correctamente',
            'solicitud_id': nueva_solicitud['id']
        })
        
    except Exception as e:
        logger.error(f"Error creando solicitud: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/solicitudes/<solicitud_id>/aprobar', methods=['POST'])
def aprobar_solicitud(solicitud_id):
    print(f"Aprobando solicitud: {solicitud_id}")
    """Aprobar solicitud y generar código promocional"""
    try:
        data = request.get_json()
        revisor = data.get('revisor', 'Admin')
        
        # Generar código promocional
        codigo_promocional = generar_codigo_promocional()
        
        # En producción, actualizar documento en Appwrite
        # Por ahora simular la aprobación
        
        # Datos simulados de la solicitud (en producción obtener de BD)
        solicitud_datos = {
            'nombre': 'Ana García López',
            'email': 'ana.garcia@universidad.edu',
            'empresa': 'Universidad Nacional'
        }
        
        # Crear usuario con créditos promocionales
        try:
            fecha_renovacion = (datetime.now() + timedelta(days=30)).isoformat()
            
            # Crear usuario en sistema de créditos con código promocional
            databases.create_document(
                database_id=DATABASE_ID,
                collection_id=USUARIOS_CREDITOS_COLLECTION_ID,
                document_id=ID.unique(),
                data={
                    'email': solicitud_datos['email'],
                    'saldo_actual': 5000,  # Créditos promocionales
                    'limite_mensual': 5000,
                    'fecha_renovacion': fecha_renovacion,
                    'saldo_real_together': 0,
                    'limite_real_together': 0,
                    'tipo_cuenta': 'demo',
                    'empresa_nombre': solicitud_datos['empresa'],
                    'codigo_promocional': codigo_promocional,
                    'estado': 'demo_activa'
                }
            )
            
            logger.info(f"Usuario demo creado: {solicitud_datos['email']} con código {codigo_promocional}")
            
        except Exception as e:
            logger.warning(f"Error creando usuario demo (puede existir): {e}")
        
        # Enviar email de aprobación
        email_enviado = enviar_email_aprobacion(
            solicitud_datos['email'], 
            solicitud_datos['nombre'], 
            codigo_promocional
        )
        
        return jsonify({
            'success': True,
            'message': 'Solicitud aprobada correctamente',
            'codigo_promocional': codigo_promocional,
            'email_enviado': email_enviado
        })
        
    except Exception as e:
        logger.error(f"Error aprobando solicitud: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/aprobar-demo-directo', methods=['POST'])
def aprobar_demo_directo():
    try:
        data = request.get_json()
        email = data.get('email')
        nombre = data.get('nombre', '')
        empresa = data.get('empresa', '')
        revisor = data.get('revisor', 'Sistema')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email requerido'
            }), 400
        
        # Configuración de créditos promocionales
        saldo_inicial = 12000  # Créditos iniciales
        limite_mensual = 12000
        tipo_cuenta = 'cliente_externo'
        
        # Crear documento en usuarios_creditos
        usuario_creditos = {
            'email': email,
            'saldo_actual': saldo_inicial,
            'limite_mensual': limite_mensual,
            'tipo_cuenta': tipo_cuenta,
            'fecha_renovacion': (datetime.now() + timedelta(days=30)).isoformat(),
            'saldo_real_together': saldo_inicial,
            'limite_real_together': limite_mensual,
            'empresa_nombre': empresa if empresa else 'N/A'
        }
        
        # Crear documento usando la configuración de Appwrite
        from appwrite.client import Client
        from appwrite.services.databases import Databases
        from appwrite.id import ID
        import os
        
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PAGOS_OPERACIONES_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_PAGOS_OPERACIONES_API_KEY'))
        
        databases = Databases(client)
        DATABASE_ID = os.getenv('APPWRITE_COMPRA_CREDITOS_DATABASE_ID')
        USUARIOS_CREDITOS_COLLECTION_ID = os.getenv('APPWRITE_USUARIOS_CREDITOS_COLLECTION_ID')
        
        # Crear el documento
        result = databases.create_document(
            database_id=DATABASE_ID,
            collection_id=USUARIOS_CREDITOS_COLLECTION_ID,
            document_id=ID.unique(),
            data=usuario_creditos
        )
        
        # Generar código promocional
        codigo_promocional = f'DEMO_{email[:5].upper()}_{datetime.now().strftime("%m%d")}'
        
        return jsonify({
            'success': True,
            'codigo_promocional': codigo_promocional,
            'mensaje': 'Créditos promocionales creados exitosamente',
            'creditos_asignados': saldo_inicial,
            'documento_id': result['$id']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/solicitudes/<solicitud_id>/rechazar', methods=['POST'])
def rechazar_solicitud(solicitud_id):
    """Rechazar solicitud"""
    try:
        data = request.get_json()
        motivo = data.get('motivo', '')
        revisor = data.get('revisor', 'Admin')
        
        # En producción, actualizar documento en Appwrite
        
        # Datos simulados de la solicitud
        solicitud_datos = {
            'nombre': 'María Rodríguez',
            'email': 'maria.rodriguez@colegio.edu'
        }
        
        # Enviar email de rechazo
        email_enviado = enviar_email_rechazo(
            solicitud_datos['email'], 
            solicitud_datos['nombre'], 
            motivo
        )
        
        return jsonify({
            'success': True,
            'message': 'Solicitud rechazada',
            'email_enviado': email_enviado
        })
        
    except Exception as e:
        logger.error(f"Error rechazando solicitud: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/codigos-promocionales', methods=['GET'])
def get_codigos_promocionales():
    """Obtener lista de códigos promocionales generados"""
    try:
        # En producción, consultar usuarios con códigos promocionales
        usuarios_result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=USUARIOS_CREDITOS_COLLECTION_ID
        )
        
        codigos = []
        for usuario in usuarios_result['documents']:
            if usuario.get('codigo_promocional'):
                codigos.append({
                    'codigo': usuario.get('codigo_promocional'),
                    'email': usuario.get('email'),
                    'empresa': usuario.get('empresa_nombre', ''),
                    'saldo_actual': usuario.get('saldo_actual', 0),
                    'tipo_cuenta': usuario.get('tipo_cuenta', ''),
                    'fecha_creacion': usuario.get('$createdAt'),
                    'estado': 'activo' if usuario.get('saldo_actual', 0) > 0 else 'agotado'
                })
        
        return jsonify({
            'codigos': codigos,
            'total': len(codigos),
            'activos': len([c for c in codigos if c['estado'] == 'activo']),
            'agotados': len([c for c in codigos if c['estado'] == 'agotado'])
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo códigos promocionales: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud"""
    return jsonify({
        'status': 'healthy',
        'service': 'solicitudes-demo',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("Servidor de solicitudes de demo iniciado")
    app.run(debug=False, host='0.0.0.0', port=5005)