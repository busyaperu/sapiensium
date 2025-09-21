from flask import Flask, request, jsonify
from flask_cors import CORS
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json
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
NOTIFICACIONES_COLLECTION_ID = os.getenv('APPWRITE_NOTIFICACIONES_COLLECTION_ID')  

# Configuración de email
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
ADMIN_EMAIL = os.getenv('NOTIFICATION_EMAIL')

# Tipos de notificaciones
TIPOS_NOTIFICACION = {
    'creditos_bajos': {
        'titulo': 'Créditos Bajos',
        'icono': 'fas fa-exclamation-triangle',
        'color': '#ed8936'
    },
    'demo_expirando': {
        'titulo': 'Demo Expirando',
        'icono': 'fas fa-clock',
        'color': '#f56565'
    },
    'usuario_inactivo': {
        'titulo': 'Usuario Inactivo',
        'icono': 'fas fa-user-clock',
        'color': '#718096'
    },
    'pago_recibido': {
        'titulo': 'Pago Recibido',
        'icono': 'fas fa-dollar-sign',
        'color': '#48bb78'
    },
    'sistema': {
        'titulo': 'Sistema',
        'icono': 'fas fa-server',
        'color': '#667eea'
    },
    'manual': {
        'titulo': 'Notificación Manual',
        'icono': 'fas fa-envelope',
        'color': '#667eea'
    }
}

def enviar_email(destinatario, asunto, contenido_html):
    """Enviar email de notificación"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = asunto
        msg['From'] = EMAIL_USER
        msg['To'] = destinatario

        msg.attach(MIMEText(contenido_html, 'html'))

        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, destinatario, msg.as_string())
        server.quit()

        return True
    except Exception as e:
        logger.error(f"Error enviando email a {destinatario}: {e}")
        return False

def crear_notificacion(tipo, destinatario, titulo, mensaje, datos_extra=None):
    """Crear notificación en base de datos"""
    try:
        notificacion_data = {
            'tipo': tipo,
            'destinatario': destinatario,
            'titulo': titulo,
            'mensaje': mensaje,
            'leida': False,
            'fecha_creacion': datetime.now().isoformat(),
            'datos_extra': json.dumps(datos_extra) if datos_extra else None
        }

        databases.create_document(
            database_id=DATABASE_ID,
            collection_id=NOTIFICACIONES_COLLECTION_ID,
            document_id=ID.unique(),
            data=notificacion_data
        )

        logger.info(f"Notificación creada: {tipo} para {destinatario}")
        return True
    except Exception as e:
        logger.error(f"Error creando notificación: {e}")
        return False

@app.route('/api/notificaciones', methods=['GET'])
def get_notificaciones():
    """Obtener notificaciones del usuario"""
    try:
        email = request.args.get('email')
        leidas = request.args.get('leidas', 'false') == 'true'
        limite = int(request.args.get('limite', 50))

        if not email:
            return jsonify({'error': 'Email requerido'}), 400

        # Consultar notificaciones
        queries = [Query.equal('destinatario', email)]
        if not leidas:
            queries.append(Query.equal('leida', False))

        result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=NOTIFICACIONES_COLLECTION_ID, 
            queries=queries + [Query.order_desc('$createdAt'), Query.limit(limite)]
        )

        # Procesar notificaciones
        notificaciones = []
        for notif in result['documents']:
            tipo_info = TIPOS_NOTIFICACION.get(notif.get('tipo', 'sistema'), TIPOS_NOTIFICACION['sistema'])
            
            notificaciones.append({
                'id': notif['$id'],
                'tipo': notif.get('tipo'),
                'titulo': notif.get('titulo'),
                'mensaje': notif.get('mensaje'),
                'leida': notif.get('leida', False),
                'fecha_creacion': notif.get('fecha_creacion'),
                'datos_extra': json.loads(notif.get('datos_extra', '{}')),
                'icono': tipo_info['icono'],
                'color': tipo_info['color']
            })

        return jsonify({
            'notificaciones': notificaciones,
            'total': len(notificaciones),
            'no_leidas': len([n for n in notificaciones if not n['leida']])
        })

    except Exception as e:
        logger.error(f"Error obteniendo notificaciones: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notificaciones/<notif_id>/marcar-leida', methods=['POST'])
def marcar_leida(notif_id):
    """Marcar notificación como leída"""
    try:
        databases.update_document(
            database_id=DATABASE_ID,
            collection_id=NOTIFICACIONES_COLLECTION_ID,
            document_id=notif_id,
            data={'leida': True}
        )

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error marcando como leída: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notificaciones/marcar-todas-leidas', methods=['POST'])
def marcar_todas_leidas():
    """Marcar todas las notificaciones como leídas"""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email requerido'}), 400

        # Obtener notificaciones no leídas
        result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=NOTIFICACIONES_COLLECTION_ID,
            queries=[
                Query.equal('destinatario', email),
                Query.equal('leida', False)
            ]
        )

        # Marcar todas como leídas
        for notif in result['documents']:
            databases.update_document(
                database_id=DATABASE_ID,
                collection_id=NOTIFICACIONES_COLLECTION_ID,
                document_id=notif['$id'],
                data={'leida': True}
            )

        return jsonify({
            'success': True,
            'marcadas': len(result['documents'])
        })

    except Exception as e:
        logger.error(f"Error marcando todas como leídas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notificaciones/enviar', methods=['POST'])
def enviar_notificacion_manual():
    """Enviar notificación manual"""
    try:
        data = request.get_json()
        destinatarios = data.get('destinatarios', [])
        titulo = data.get('titulo')
        mensaje = data.get('mensaje')
        enviar_email_flag = data.get('enviar_email', False)
        remitente = data.get('remitente', 'Admin')

        if not destinatarios or not titulo or not mensaje:
            return jsonify({'error': 'Destinatarios, título y mensaje son requeridos'}), 400

        enviados = 0
        errores = []

        for destinatario in destinatarios:
            # Crear notificación en sistema
            if crear_notificacion('manual', destinatario, titulo, mensaje, {'remitente': remitente}):
                enviados += 1

                # Enviar email si se solicita
                if enviar_email_flag:
                    contenido_html = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background: #667eea; padding: 2rem; color: white; text-align: center;">
                            <h1>{titulo}</h1>
                        </div>
                        <div style="padding: 2rem;">
                            <p>{mensaje}</p>
                            <hr style="margin: 2rem 0;">
                            <p style="color: #718096; font-size: 0.9rem;">
                                Enviado por: {remitente}<br>
                                ExamPro AI - Sistema de Notificaciones
                            </p>
                        </div>
                    </body>
                    </html>
                    """
                    
                    if not enviar_email(destinatario, titulo, contenido_html):
                        errores.append(f"Error enviando email a {destinatario}")
            else:
                errores.append(f"Error creando notificación para {destinatario}")

        return jsonify({
            'success': True,
            'enviados': enviados,
            'total': len(destinatarios),
            'errores': errores
        })

    except Exception as e:
        logger.error(f"Error enviando notificación manual: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notificaciones/automaticas/verificar', methods=['POST'])
def verificar_notificaciones_automaticas():
    """Verificar y enviar notificaciones automáticas"""
    try:
        # Obtener configuración desde el servidor de configuración
        try:
            import requests
            config_response = requests.get('http://127.0.0.1:5007/api/config/seccion/notificaciones')
            config_data = config_response.json()
            config_notif = config_data.get('configuracion', {})
        except:
            # Valores por defecto si no se puede obtener configuración
            config_notif = {
                'email_enabled': True,
                'notif_creditos_bajos_porcentaje': 20,
                'notif_demo_expiracion_dias': 7,
                'notif_inactividad_dias': 30
            }

        if not config_notif.get('email_enabled', True):
            return jsonify({'message': 'Notificaciones deshabilitadas'})

        # Obtener usuarios
        usuarios_result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=USUARIOS_CREDITOS_COLLECTION_ID
        )

        notificaciones_enviadas = 0

        for usuario in usuarios_result['documents']:
            email = usuario.get('email')
            saldo_actual = usuario.get('saldo_actual', 0)
            limite_mensual = usuario.get('limite_mensual', 12000)
            tipo_cuenta = usuario.get('tipo_cuenta', 'individual')
            fecha_renovacion = usuario.get('fecha_renovacion')

            # 1. Verificar créditos bajos
            porcentaje_uso = (saldo_actual / limite_mensual) * 100 if limite_mensual > 0 else 0
            umbral_creditos = config_notif.get('notif_creditos_bajos_porcentaje', 20)

            if porcentaje_uso <= umbral_creditos and saldo_actual > 0:
                # Verificar si ya se envió esta notificación recientemente
                notif_reciente = databases.list_documents(
                    database_id=DATABASE_ID,
                    collection_id=NOTIFICACIONES_COLLECTION_ID,
                    queries=[
                        Query.equal('destinatario', email),
                        Query.equal('tipo', 'creditos_bajos'),
                        Query.greater_than('$createdAt', (datetime.now() - timedelta(days=1)).isoformat())
                    ]
                )

                if not notif_reciente['documents']:
                    titulo = "Créditos Bajos"
                    mensaje = f"Te quedan {saldo_actual} créditos ({porcentaje_uso:.1f}%). Considera recargar tu cuenta."
                    
                    if crear_notificacion('creditos_bajos', email, titulo, mensaje, {'saldo': saldo_actual, 'porcentaje': porcentaje_uso}):
                        notificaciones_enviadas += 1

            # 2. Verificar demo expirando
            if tipo_cuenta == 'demo' and fecha_renovacion:
                try:
                    fecha_expiracion = datetime.fromisoformat(fecha_renovacion.replace('Z', '+00:00'))
                    dias_restantes = (fecha_expiracion - datetime.now()).days
                    umbral_dias = config_notif.get('notif_demo_expiracion_dias', 7)

                    if 0 <= dias_restantes <= umbral_dias:
                        titulo = "Demo Expirando"
                        mensaje = f"Tu cuenta demo expira en {dias_restantes} días. Actualiza a un plan de pago."
                        
                        if crear_notificacion('demo_expirando', email, titulo, mensaje, {'dias_restantes': dias_restantes}):
                            notificaciones_enviadas += 1
                except:
                    pass

            # 3. Verificar inactividad (usuarios sin transacciones recientes)
            try:
                transacciones_result = databases.list_documents(
                    database_id=DATABASE_ID,
                    collection_id='transacciones_creditos',
                    queries=[
                        Query.equal('email', email),
                        Query.greater_than('$createdAt', (datetime.now() - timedelta(days=config_notif.get('notif_inactividad_dias', 30))).isoformat())
                    ]
                )

                if not transacciones_result['documents'] and saldo_actual > 0:
                    titulo = "Cuenta Inactiva"
                    mensaje = f"No has usado tu cuenta en {config_notif.get('notif_inactividad_dias', 30)} días. ¿Necesitas ayuda?"
                    
                    if crear_notificacion('usuario_inactivo', email, titulo, mensaje):
                        notificaciones_enviadas += 1
            except:
                pass

        return jsonify({
            'success': True,
            'notificaciones_enviadas': notificaciones_enviadas,
            'usuarios_verificados': len(usuarios_result['documents'])
        })

    except Exception as e:
        logger.error(f"Error verificando notificaciones automáticas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notificaciones/estadisticas', methods=['GET'])
def get_estadisticas_notificaciones():
    """Obtener estadísticas de notificaciones"""
    try:
        periodo_dias = int(request.args.get('periodo', 30))
        fecha_inicio = datetime.now() - timedelta(days=periodo_dias)

        # Obtener todas las notificaciones del período
        result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=NOTIFICACIONES_COLLECTION_ID, 
            queries=[
                Query.greater_than('$createdAt', fecha_inicio.isoformat())
            ]
        )

        # Procesar estadísticas
        total_notificaciones = len(result['documents'])
        leidas = len([n for n in result['documents'] if n.get('leida', False)])
        no_leidas = total_notificaciones - leidas

        # Por tipo
        por_tipo = {}
        for notif in result['documents']:
            tipo = notif.get('tipo', 'sistema')
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

        # Por día (últimos 7 días)
        por_dia = {}
        for i in range(7):
            fecha = datetime.now() - timedelta(days=i)
            fecha_str = fecha.strftime('%Y-%m-%d')
            por_dia[fecha_str] = len([
                n for n in result['documents'] 
                if n.get('$createdAt', '').startswith(fecha_str)
            ])

        return jsonify({
            'total_notificaciones': total_notificaciones,
            'leidas': leidas,
            'no_leidas': no_leidas,
            'tasa_lectura': round((leidas / max(total_notificaciones, 1)) * 100, 1),
            'por_tipo': por_tipo,
            'por_dia': por_dia,
            'periodo_dias': periodo_dias
        })

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notificaciones/limpiar', methods=['POST'])
def limpiar_notificaciones_antiguas():
    """Limpiar notificaciones antiguas"""
    try:
        data = request.get_json()
        dias_antiguedad = data.get('dias', 90)
        
        fecha_limite = datetime.now() - timedelta(days=dias_antiguedad)

        # Obtener notificaciones antiguas
        result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=NOTIFICACIONES_COLLECTION_ID,
            queries=[
                Query.less_than('$createdAt', fecha_limite.isoformat())
            ]
        )

        # Eliminar notificaciones antiguas
        eliminadas = 0
        for notif in result['documents']:
            try:
                databases.delete_document(
                    database_id=DATABASE_ID,
                    collection_id=NOTIFICACIONES_COLLECTION_ID,
                    document_id=notif['$id']
                )
                eliminadas += 1
            except:
                pass

        return jsonify({
            'success': True,
            'eliminadas': eliminadas,
            'fecha_limite': fecha_limite.isoformat()
        })

    except Exception as e:
        logger.error(f"Error limpiando notificaciones: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud"""
    return jsonify({
        'status': 'healthy',
        'service': 'sistema-notificaciones',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("Servidor de Sistema de Notificaciones iniciado")
    app.run(debug=False, host='0.0.0.0', port=5008)