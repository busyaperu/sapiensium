# app_evaluador.py - API de Créditos para Evaluación de Exámenes
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import logging
from dotenv import load_dotenv
import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID
from server_generador_examen import obtener_usuario_creditos


load_dotenv()

# Configuración Appwrite
client = Client()
client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PAGOS_OPERACIONES_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_PAGOS_OPERACIONES_API_KEY'))

databases = Databases(client)
DATABASE_ID = os.getenv('APPWRITE_COMPRA_CREDITOS_DATABASE_ID')

# Configuraciones de Créditos - agregar después de DATABASE_ID
USUARIOS_CREDITOS_COLLECTION_ID = os.getenv('APPWRITE_USUARIOS_CREDITOS_COLLECTION_ID')
TRANSACCIONES_COLLECTION_ID = os.getenv('APPWRITE_TRANSACCIONES_COLLECTION_ID')
EVALUACIONES_COLLECTION_ID = os.getenv('APPWRITE_EVALUACIONES_COLLECTION_ID')

app = Flask(__name__)
CORS(app)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuración de créditos
CREDITO_POR_TOKEN = 5000  # 1 crédito = 5,000 tokens
LIMITE_CREDITOS_MENSUAL = 12000  # Plan $20 = 12,000 créditos
COSTO_EVALUAR_POR_MODELO = 15500  # tokens para evaluar con 1 modelo

# Modelos disponibles y sus costos relativos
MODELOS_DISPONIBLES = {
    "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8": {"costo_factor": 1.0, "plataforma": "Together"},
    "deepseek-ai/DeepSeek-V3": {"costo_factor": 2.7, "plataforma": "Together"},
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo": {"costo_factor": 3.0, "plataforma": "Together"},
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free": {"costo_factor": 0.8, "plataforma": "Together"},
    "mistralai/Mixtral-8x7B-Instruct-v0.1": {"costo_factor": 1.2, "plataforma": "Together"},
    "claude-sonnet-4": {"costo_factor": 3.0, "plataforma": "Anthropic"},
    "gpt-4-1": {"costo_factor": 2.5, "plataforma": "OpenAI"},
    "qwen/qwen3-32b:free": {"costo_factor": 0.0, "plataforma": "OpenRouter"},  # Gratis
    "deepseek/deepseek-chat-v3-0324": {"costo_factor": 0.5, "plataforma": "OpenRouter"},
    "nvidia/llama-3.1-nemotron-ultra-253b-v1:free": {"costo_factor": 0.0, "plataforma": "OpenRouter"},  # Gratis
    "deepseek-r1-distill-llama-70b": {"costo_factor": 0.6, "plataforma": "Groq"},
    "mistral-saba-24b": {"costo_factor": 0.4, "plataforma": "Groq"}
}

def calcular_costo_evaluacion(modelos_seleccionados, num_estudiantes=1):
    """Calcular el costo total de evaluación según modelos y estudiantes"""
    tokens_totales = 0
    creditos_totales = 0
    
    for modelo in modelos_seleccionados:
        if modelo in MODELOS_DISPONIBLES:
            factor_costo = MODELOS_DISPONIBLES[modelo]["costo_factor"]
            tokens_modelo = int(COSTO_EVALUAR_POR_MODELO * factor_costo * num_estudiantes)
            tokens_totales += tokens_modelo
            
            # Convertir a créditos
            creditos_modelo = tokens_modelo // CREDITO_POR_TOKEN
            if tokens_modelo % CREDITO_POR_TOKEN > 0:
                creditos_modelo += 1
            creditos_totales += creditos_modelo
    
    return tokens_totales, creditos_totales

@app.route('/api/dashboard/creditos/<email>', methods=['GET'])
def get_dashboard_creditos(email):
    """Obtener datos completos del dashboard de créditos"""
    try:
        usuario = obtener_usuario_creditos(email)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        saldo_actual = usuario['saldo_actual']
        limite_mensual = usuario['limite_mensual'] 
        fecha_renovacion = usuario['fecha_renovacion']

        
        # Obtener transacciones
        transacciones_result = databases.list_documents(
        database_id=DATABASE_ID,
        collection_id=TRANSACCIONES_COLLECTION_ID,
        queries=[Query.equal('email', email), Query.order_desc('$createdAt'), Query.limit(50)]
)
        
        # Obtener estadísticas de evaluaciones
        evaluaciones_result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=EVALUACIONES_COLLECTION_ID,
            queries=[Query.equal('email', email)]
        )
        
        
        # Calcular métricas
        creditos_usados = limite_mensual - saldo_actual
        porcentaje_usado = (creditos_usados / limite_mensual * 100) if limite_mensual > 0 else 0
        costo_usado = (creditos_usados / 12000) * 20  # $20 por 12,000 créditos
        
        # Actividades recientes para la tabla
        actividades = []
        for trans in transacciones_result['documents']:
            fecha = trans['$createdAt']
            tipo = trans['tipo']
            creditos = trans['creditos']
            tokens = trans['tokens_usados']
            descripcion = trans['descripcion']
            modelos_json = trans['modelos_usados']
            examen_id = trans['examen_id']
            num_estudiantes = trans['num_estudiantes']
            
            # Parsear modelos usados
            try:
                modelos_usados = json.loads(modelos_json) if modelos_json else []
                modelos_str = f"{len(modelos_usados)} modelos"
            except:
                modelos_str = "N/A"
            
            actividades.append({
                'fecha': fecha,
                'actividad': descripcion,
                'tipo': tipo,
                'creditos': creditos,
                'tokens': tokens,
                'modelos': modelos_str,
                'examen_id': examen_id,
                'estudiantes': num_estudiantes,
                'estado': 'Completado'
            })
        
        # Datos para gráficos
        datos_dia = generar_datos_grafico_dia(email)
        datos_semana = generar_datos_grafico_semana(email)
        datos_mes = generar_datos_grafico_mes(email)
        
        
        return jsonify({
            'saldo_actual': saldo_actual,
            'limite_mensual': limite_mensual,
            'creditos_usados': creditos_usados,
            'porcentaje_usado': round(porcentaje_usado, 1),
            'costo_usado': round(costo_usado, 2),
            'fecha_renovacion': fecha_renovacion,
            'estadisticas': {
                    'total_evaluaciones': len(evaluaciones_result['documents']),
                    'creditos_evaluaciones': sum(doc['creditos_totales'] for doc in evaluaciones_result['documents']),
                    'estudiantes_evaluados': sum(doc['num_estudiantes'] for doc in evaluaciones_result['documents'])
            },
            'actividades': actividades,
            'graficos': {
                'dia': datos_dia,
                'semana': datos_semana,
                'mes': datos_mes
            }
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo dashboard: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calcular-costo-evaluacion', methods=['POST'])
def calcular_costo_endpoint():
    """Calcular costo de evaluación antes de ejecutar"""
    try:
        data = request.get_json()
        modelos_seleccionados = data.get('modelos_seleccionados', [])
        num_estudiantes = data.get('num_estudiantes', 1)
        
        if not modelos_seleccionados:
            return jsonify({'error': 'Debe seleccionar al menos un modelo'}), 400
        
        tokens_totales, creditos_totales = calcular_costo_evaluacion(
            modelos_seleccionados, num_estudiantes
        )
        
        # Desglose por modelo
        desglose_modelos = []
        for modelo in modelos_seleccionados:
            if modelo in MODELOS_DISPONIBLES:
                factor_costo = MODELOS_DISPONIBLES[modelo]["costo_factor"]
                tokens_modelo = int(COSTO_EVALUAR_POR_MODELO * factor_costo * num_estudiantes)
                creditos_modelo = tokens_modelo // CREDITO_POR_TOKEN
                if tokens_modelo % CREDITO_POR_TOKEN > 0:
                    creditos_modelo += 1
                
                desglose_modelos.append({
                    'modelo': modelo,
                    'plataforma': MODELOS_DISPONIBLES[modelo]["plataforma"],
                    'factor_costo': factor_costo,
                    'tokens': tokens_modelo,
                    'creditos': creditos_modelo
                })
        
        return jsonify({
            'tokens_totales': tokens_totales,
            'creditos_totales': creditos_totales,
            'num_estudiantes': num_estudiantes,
            'num_modelos': len(modelos_seleccionados),
            'desglose_modelos': desglose_modelos,
            'costo_estimado_usd': round((creditos_totales / 12000) * 20, 2)
        })
        
    except Exception as e:
        logger.error(f"Error calculando costo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluar-examen', methods=['POST'])
def evaluar_examen():
    """Evaluar examen con múltiples modelos y consumir créditos"""
    try:
        data = request.get_json()
        email = data.get('email')
        examen_id = data.get('examen_id')
        modelos_seleccionados = data.get('modelos_seleccionados', [])
        num_estudiantes = data.get('num_estudiantes', 1)
        
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        if not modelos_seleccionados:
            return jsonify({'error': 'Debe seleccionar al menos un modelo'}), 400
        
        # Calcular costo total
        tokens_totales, creditos_totales = calcular_costo_evaluacion(
            modelos_seleccionados, num_estudiantes
        )
        
        # Verificar saldo suficiente
        usuario = obtener_usuario_creditos(email)
        email_db, saldo_actual, limite_mensual, fecha_renovacion, created_at = usuario
        
        if saldo_actual < creditos_totales:
            return jsonify({
                'error': 'Saldo insuficiente',
                'saldo_actual': saldo_actual,
                'creditos_necesarios': creditos_totales,
                'diferencia': creditos_totales - saldo_actual
            }), 400
        
        # Registrar transacción
        descripcion = f"Evaluación con {len(modelos_seleccionados)} modelos - {num_estudiantes} estudiantes"
        modelos_json = json.dumps(modelos_seleccionados)
        
        databases.create_document(
            database_id=DATABASE_ID,
            collection_id=TRANSACCIONES_COLLECTION_ID,
            document_id=ID.unique(),
            data={
                'email': email,
                'tipo': 'evaluacion',
                'creditos': creditos_totales,
                'tokens_usados': tokens_totales,
                'descripcion': descripcion,
                'modelos_usados': modelos_json,
                'examen_id': examen_id,
                'num_estudiantes': num_estudiantes
            }
        )
        
        # Registrar en evaluaciones
        databases.create_document(
            database_id=DATABASE_ID,
            collection_id=EVALUACIONES_COLLECTION_ID,
            document_id=ID.unique(),
            data={
                'email': email,
                'examen_id': examen_id,
                'modelos_usados': modelos_json,
                'num_estudiantes': num_estudiantes,
                'creditos_totales': creditos_totales,
                'tokens_totales': tokens_totales,
                'duracion_segundos': 0,
                'estado': 'completado'
            }
        )
        
        # Actualizar saldo del usuario
        databases.update_document(
            database_id=DATABASE_ID,
            collection_id=USUARIOS_CREDITOS_COLLECTION_ID,
            document_id=usuario['$id'],
            data={'saldo_actual': saldo_actual - creditos_totales}
        )
        
        # Obtener nuevo saldo
        usuario_actualizado = obtener_usuario_creditos(email)
        nuevo_saldo = usuario_actualizado[1]
        
        logger.info(f"Evaluación registrada - Email: {email}, Créditos: {creditos_totales}, Modelos: {len(modelos_seleccionados)}, Estudiantes: {num_estudiantes}")
        
        # Aquí irían las llamadas a los diferentes modelos de IA
        # Por ahora simulamos la respuesta
        resultados_evaluacion = simular_evaluacion_modelos(modelos_seleccionados, examen_id)
        
        return jsonify({
            'success': True,
            'examen_id': examen_id,
            'creditos_consumidos': creditos_totales,
            'tokens_usados': tokens_totales,
            'saldo_anterior': saldo_actual,
            'saldo_actual': nuevo_saldo,
            'modelos_usados': modelos_seleccionados,
            'num_estudiantes': num_estudiantes,
            'resultados': resultados_evaluacion
        })
        
    except Exception as e:
        logger.error(f"Error evaluando examen: {e}")
        return jsonify({'error': str(e)}), 500

def simular_evaluacion_modelos(modelos_seleccionados, examen_id):
    """Simular evaluación con múltiples modelos"""
    resultados = []
    
    for i, modelo in enumerate(modelos_seleccionados):
        resultado = {
            'modelo': modelo,
            'plataforma': MODELOS_DISPONIBLES.get(modelo, {}).get('plataforma', 'Unknown'),
            'calificacion_promedio': round(85 + (i * 2) % 15, 1),  # Simulado
            'tiempo_evaluacion': round(30 + (i * 5), 1),  # Simulado en segundos
            'estado': 'completado',
            'observaciones': f'Evaluación completada con {modelo}'
        }
        resultados.append(resultado)
    
    return resultados

@app.route('/api/saldo/<email>', methods=['GET'])
def get_saldo_creditos(email):
    """Consultar saldo actual de créditos desde Appwrite"""
    try:
        # Buscar usuario en Appwrite
        result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=USUARIOS_CREDITOS_COLLECTION_ID
        )
        
        # Buscar usuario por email
        usuario_encontrado = None
        for doc in result['documents']:
            if doc['email'] == email:
                usuario_encontrado = doc
                break
        
        if not usuario_encontrado:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'email': email,
            'saldo_actual': usuario_encontrado['saldo_actual'],
            'limite_mensual': usuario_encontrado['limite_mensual'],
            'fecha_renovacion': usuario_encontrado['fecha_renovacion']
        })
        
    except Exception as e:
        logger.error(f"Error consultando saldo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/modelos-disponibles', methods=['GET'])
def get_modelos_disponibles():
    """Obtener lista de modelos disponibles con sus costos"""
    try:
        modelos_info = []
        
        for modelo, info in MODELOS_DISPONIBLES.items():
            tokens_base = int(COSTO_EVALUAR_POR_MODELO * info["costo_factor"])
            creditos_base = tokens_base // CREDITO_POR_TOKEN
            if tokens_base % CREDITO_POR_TOKEN > 0:
                creditos_base += 1
            
            modelos_info.append({
                'modelo': modelo,
                'plataforma': info["plataforma"],
                'factor_costo': info["costo_factor"],
                'tokens_por_evaluacion': tokens_base,
                'creditos_por_evaluacion': creditos_base,
                'es_gratuito': info["costo_factor"] == 0.0
            })
        
        # Ordenar por costo
        modelos_info.sort(key=lambda x: x['factor_costo'])
        
        return jsonify({
            'modelos': modelos_info,
            'total_modelos': len(modelos_info),
            'modelos_gratuitos': len([m for m in modelos_info if m['es_gratuito']])
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo modelos: {e}")
        return jsonify({'error': str(e)}), 500

def generar_datos_grafico_dia(email):
    """Generar datos para gráfico del día"""
    # Implementar consultas específicas por horas
    return {
        'labels': ['08:00', '10:00', '14:00', '16:00', '18:00'],
        'data': [0, 2480, 1240, 7320, 3660]
    }

def generar_datos_grafico_semana(email):
    """Generar datos para gráfico de la semana"""
    return {
        'labels': ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'],
        'data': [7320, 2480, 3648, 736, 2432, 0, 0]
    }

def generar_datos_grafico_mes(email):
    """Generar datos para gráfico del mes"""
    return {
        'labels': ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
        'data': [5600, 6400, 3700, 2800]
    }

@app.route('/api/recargar-creditos', methods=['POST'])
def recargar_creditos():
    """Recargar créditos manualmente (para testing)"""
    try:
        data = request.get_json()
        email = data.get('email')
        creditos = data.get('creditos', LIMITE_CREDITOS_MENSUAL)
        descripcion = data.get('descripcion', 'Recarga manual de créditos')
        
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        # Registrar recarga
        databases.create_document(
            database_id=DATABASE_ID,
            collection_id=TRANSACCIONES_COLLECTION_ID,
            document_id=ID.unique(),
            data={
                'email': email,
                'tipo': 'recarga',
                'creditos': creditos,
                'tokens_usados': 0,
                'descripcion': descripcion,
                'modelos_usados': None,
                'examen_id': None,
                'num_estudiantes': 0
            }
        )
        
        # Actualizar saldo del usuario
        usuario = obtener_usuario_creditos(email)
        databases.update_document(
            database_id=DATABASE_ID,
            collection_id=USUARIOS_CREDITOS_COLLECTION_ID,
            document_id=usuario['$id'],
            data={'saldo_actual': usuario['saldo_actual'] + creditos}
        )

        # Obtener nuevo saldo
        usuario_actualizado = obtener_usuario_creditos(email)
        nuevo_saldo = usuario_actualizado['saldo_actual']
        
        logger.info(f"Recarga registrada - Email: {email}, Créditos: {creditos}, Nuevo saldo: {nuevo_saldo}")
        
        return jsonify({
            'success': True,
            'creditos_recargados': creditos,
            'saldo_actual': nuevo_saldo,
            'descripcion': descripcion
        })
        
    except Exception as e:
        logger.error(f"Error recargando créditos: {e}")
        return jsonify({'error': str(e)}), 500   
    
@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud"""
    return jsonify({
        'status': 'healthy',
        'service': 'app-evaluador-examenes',
        'timestamp': datetime.now().isoformat(),
        'modelos_disponibles': len(MODELOS_DISPONIBLES)
    })
        
if __name__ == '__main__':
    logger.info("Servidor evaluador de exámenes iniciado")
    app.run(debug=False, host='0.0.0.0', port=5007)