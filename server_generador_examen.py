# app_evaluador_examenes.py - API de Créditos para Evaluación de Exámenes
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import logging

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración Appwrite
client = Client()
client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PAGOS_OPERACIONES_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_PAGOS_OPERACIONES_API_KEY'))

databases = Databases(client)
DATABASE_ID = os.getenv('APPWRITE_COMPRA_CREDITOS_DATABASE_ID')


app = Flask(__name__)
CORS(app)


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de créditos
CREDITO_POR_TOKEN = 5000  # 1 crédito = 5,000 tokens
LIMITE_CREDITOS_MENSUAL = 12000  # Plan $20 = 12,000 créditos
COSTO_EVALUAR_POR_MODELO = 15500  # tokens para evaluar con 1 modelo


# Modelos disponibles y sus costos relativos - VERSIÓN COMPLETA
MODELOS_DISPONIBLES = {
    # ===== TOGETHER AI =====
    "deepseek-ai/DeepSeek-V3": {"costo_factor": 2.7, "plataforma": "Together"},
    "deepseek-ai/DeepSeek-R1": {"costo_factor": 4.5, "plataforma": "Together"},  # Premium
    "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8": {"costo_factor": 1.0, "plataforma": "Together"},
    "meta-llama/Llama-4-Scout-Instruct": {"costo_factor": 0.6, "plataforma": "Together"},  # Muy económico
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo": {"costo_factor": 3.0, "plataforma": "Together"},
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free": {"costo_factor": 0.8, "plataforma": "Together"},
    "meta-llama/Meta-Llama-3-8B-Instruct": {"costo_factor": 0.3, "plataforma": "Together"},
    "meta-llama/Llama-Vision-Free": {"costo_factor": 0.9, "plataforma": "Together"},  # Multimodal económico
    "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo": {"costo_factor": 2.8, "plataforma": "Together"},  # Multimodal grande
    "nvidia/llama-3.1-nemotron-ultra-253b-v1": {"costo_factor": 3.5, "plataforma": "Together"},  # 253B parámetros
    "Qwen/Qwen2.5-VL-72B-Instruct": {"costo_factor": 3.2, "plataforma": "Together"},  # Multimodal premium
    "Qwen/Qwen2.5-Coder-32B-Instruct": {"costo_factor": 1.8, "plataforma": "Together"},  # Especializado código
    "Qwen/QwQ-32B-Preview": {"costo_factor": 1.5, "plataforma": "Together"},
    "mistralai/Mixtral-8x7B-Instruct-v0.1": {"costo_factor": 1.2, "plataforma": "Together"},
    "mistralai/Mistral-Small-Instruct-2501": {"costo_factor": 1.3, "plataforma": "Together"},
    "LG-AI-Research/exaone-3.5-32b-instruct": {"costo_factor": 0.8, "plataforma": "Together"},
    "LG-AI-Research/exaone-deep-32b": {"costo_factor": 0.9, "plataforma": "Together"},
    "Arcee-AI/AFM-4.5B-Preview": {"costo_factor": 0.4, "plataforma": "Together"},  # Muy pequeño
    "Arcee-AI/Arcee-Maestro": {"costo_factor": 2.2, "plataforma": "Together"},  # Especializado evaluación

    # ===== GOOGLE GEMINI =====
    "gemini-2.5-pro-preview-05-06": {"costo_factor": 3.8, "plataforma": "Google"},  # Premium más reciente
    "gemini-2.5-flash-preview-04-17": {"costo_factor": 1.8, "plataforma": "Google"},  # Flash más reciente
    "gemini-2.0-flash": {"costo_factor": 1.0, "plataforma": "Google"},
    "gemini-1.5-flash": {"costo_factor": 0.8, "plataforma": "Google"},  # Más económico
    "gemini-1.5-pro": {"costo_factor": 2.5, "plataforma": "Google"},

    # ===== ANTHROPIC =====
    "claude-4-sonnet-20250514": {"costo_factor": 3.0, "plataforma": "Anthropic"},
    # Alias para mantener compatibilidad
    "claude-sonnet-4": {"costo_factor": 3.0, "plataforma": "Anthropic"},

    # ===== OPENAI =====
    "gpt-4-turbo-preview": {"costo_factor": 2.5, "plataforma": "OpenAI"},
    "gpt-4o": {"costo_factor": 3.0, "plataforma": "OpenAI"},
    "gpt-4o-mini": {"costo_factor": 1.0, "plataforma": "OpenAI"},
    # Alias para mantener compatibilidad
    "gpt-4-1": {"costo_factor": 2.5, "plataforma": "OpenAI"},

    # ===== OPENROUTER - MODELOS DE TEXTO GRATUITOS =====
    "qwen/qwen3-32b:free": {"costo_factor": 0.0, "plataforma": "OpenRouter"},
    "deepseek/deepseek-chat-v3-0324": {"costo_factor": 0.5, "plataforma": "OpenRouter"},
    "google/gemma-3-27b-it:free": {"costo_factor": 0.0, "plataforma": "OpenRouter"},
    "mistralai/mistral-small-3.1-24b-instruct:free": {"costo_factor": 0.0, "plataforma": "OpenRouter"},
    "nvidia/llama-3.1-nemotron-ultra-253b-v1:free": {"costo_factor": 0.0, "plataforma": "OpenRouter"},
    "meta-llama/llama-3.3-70b-instruct:free": {"costo_factor": 0.0, "plataforma": "OpenRouter"},
    "meta-llama/llama-3.1-405b:free": {"costo_factor": 0.0, "plataforma": "OpenRouter"},

    # ===== OPENROUTER - MODELOS MULTIMODALES GRATUITOS =====
    "qwen/qwen2.5-vl-32b-instruct:free": {"costo_factor": 0.0, "plataforma": "OpenRouter"},
    "google/gemini-2.0-flash-exp:free": {"costo_factor": 0.0, "plataforma": "OpenRouter"},
    "google/learnlm-1.5-pro-experimental:free": {"costo_factor": 0.0, "plataforma": "OpenRouter"},
    "meta-llama/llama-3.2-11b-vision-instruct:free": {"costo_factor": 0.0, "plataforma": "OpenRouter"},

    # ===== GROQ =====
    "deepseek-r1-distill-llama-70b": {"costo_factor": 0.6, "plataforma": "Groq"},
    "mistral-saba-24b": {"costo_factor": 0.4, "plataforma": "Groq"},  # Verificar si existe

    # ===== MODELOS ADICIONALES MENCIONADOS EN RECOMENDACIONES =====
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B": {"costo_factor": 0.7, "plataforma": "Together"},  # Versión destilada
    "SCB10X/Typhoon-2-70B-Instruct": {"costo_factor": 2.0, "plataforma": "Together"},  # Si está disponible
    "upstage/SOLAR-10.7B-Instruct-v1.0": {"costo_factor": 1.1, "plataforma": "Together"},  # Si está disponible

    # ===== CONFIGURACIÓN GENÉRICA OPENROUTER =====
    "openrouter-generic": {"costo_factor": 1.0, "plataforma": "OpenRouter"},  # Configurable
}

# Categorías de modelos por costo
MODELOS_POR_COSTO = {
    "gratuitos": [
        "qwen/qwen3-32b:free",
        "google/gemma-3-27b-it:free", 
        "mistralai/mistral-small-3.1-24b-instruct:free",
        "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "meta-llama/llama-3.1-405b:free",
        "qwen/qwen2.5-vl-32b-instruct:free",
        "google/gemini-2.0-flash-exp:free",
        "google/learnlm-1.5-pro-experimental:free",
        "meta-llama/llama-3.2-11b-vision-instruct:free"
    ],
    "economicos": [  # costo_factor <= 1.0
        "meta-llama/Meta-Llama-3-8B-Instruct",
        "Arcee-AI/AFM-4.5B-Preview",
        "deepseek/deepseek-chat-v3-0324",
        "mistral-saba-24b",
        "deepseek-r1-distill-llama-70b",
        "meta-llama/Llama-4-Scout-Instruct",
        "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "LG-AI-Research/exaone-3.5-32b-instruct",
        "LG-AI-Research/exaone-deep-32b",
        "meta-llama/Llama-Vision-Free",
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gpt-4o-mini",
        "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
    ],
    "medios": [  # 1.0 < costo_factor <= 2.5
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "mistralai/Mistral-Small-Instruct-2501", 
        "Qwen/QwQ-32B-Preview",
        "Qwen/Qwen2.5-Coder-32B-Instruct",
        "gemini-2.5-flash-preview-04-17",
        "SCB10X/Typhoon-2-70B-Instruct",
        "Arcee-AI/Arcee-Maestro",
        "gemini-1.5-pro",
        "gpt-4-turbo-preview",
        "gpt-4-1"
    ],
    "premium": [  # costo_factor > 2.5
        "deepseek-ai/DeepSeek-V3",
        "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "claude-4-sonnet-20250514",
        "claude-sonnet-4",
        "gpt-4o",
        "Qwen/Qwen2.5-VL-72B-Instruct",
        "nvidia/llama-3.1-nemotron-ultra-253b-v1",
        "nvidia/llama-3.1-nemotron-ultra-253b-v1",
        "gemini-2.5-pro-preview-05-06",
        "deepseek-ai/DeepSeek-R1"
    ]
}

# Modelos multimodales
MODELOS_MULTIMODALES = [
    "meta-llama/Llama-Vision-Free",
    "Qwen/Qwen2.5-VL-72B-Instruct", 
    "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
    "qwen/qwen2.5-vl-32b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "google/learnlm-1.5-pro-experimental:free",
    "meta-llama/llama-3.2-11b-vision-instruct:free"
]

# Modelos especializados
MODELOS_ESPECIALIZADOS = {
    "codigo": [
        "Qwen/Qwen2.5-Coder-32B-Instruct"
    ],
    "evaluacion": [
        "deepseek-ai/DeepSeek-R1",
        "claude-4-sonnet-20250514",
        "Arcee-AI/Arcee-Maestro"
    ],
    "test_desarrollo": [
        "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "meta-llama/llama-3.1-405b:free",
        "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        "Arcee-AI/AFM-4.5B-Preview"
    ]
}

def init_database():
    """Verificar colecciones Appwrite (ya deben estar creadas)"""
    try:
        databases.get_collection(DATABASE_ID, '68c19ba15c0d1a8461b3')
        databases.get_collection(DATABASE_ID, '68c19c78d65e58f658fd') 
        databases.get_collection(DATABASE_ID, '68c19d6a6239cdd915bd')
        logger.info("Colecciones Appwrite verificadas")
    except Exception as e:
        logger.error(f"Error verificando colecciones: {e}")

@app.route('/api/verificar-tipo-cuenta/<email>', methods=['GET'])
def verificar_tipo_cuenta(email):
    """Verificar si usuario es individual o empresa"""
    try:
        usuario = obtener_usuario_creditos(email)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        tipo_cuenta = usuario.get('tipo_cuenta', 'individual')
        empresa_admin = usuario.get('empresa_admin', '')
        empresa_nombre = usuario.get('empresa_nombre', '')
        
        return jsonify({
            'tipo_cuenta': tipo_cuenta,
            'empresa_admin': empresa_admin,
            'empresa_nombre': empresa_nombre,
            'es_empresa': tipo_cuenta == 'empresa',
            'es_usuario_empresa': tipo_cuenta == 'asignado_empresa'
        })
        
    except Exception as e:
        logger.error(f"Error verificando tipo cuenta: {e}")
        return jsonify({'error': str(e)}), 500

def obtener_usuario_creditos(email):
    """Obtener información de créditos del usuario"""
    try:
        # Buscar usuario existente
        result = databases.list_documents(
            DATABASE_ID, 
            '68c19ba15c0d1a8461b3',
        )
        # Buscar manualmente en los resultados
        usuario_encontrado = None
        for doc in result['documents']:
            if doc['email'] == email:
                usuario_encontrado = doc
                break

        if usuario_encontrado:
            return usuario_encontrado
        else:
            # Crear usuario nuevo
            fecha_renovacion = (datetime.now() + timedelta(days=30)).isoformat()
            nuevo_usuario = databases.create_document(
                DATABASE_ID,
                '68c19ba15c0d1a8461b3',
                'unique()',
                {
                    'email': email,
                    'saldo_actual': 12000,
                    'limite_mensual': 12000,
                    'fecha_renovacion': fecha_renovacion,
                    'saldo_real_together': 3030,
                    'limite_real_together': 3030,
                    'tipo_cuenta': 'individual',
                    'empresa_nombre': ''
                }
            )
            return nuevo_usuario
    except Exception as e:
        print(f"ERROR APPWRITE: {e}")
        print(f"DATABASE_ID: {DATABASE_ID}")
        logger.error(f"Error obteniendo usuario: {e}")
        return None

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
        print(f"DEBUG: Iniciando dashboard para {email}")
        usuario = obtener_usuario_creditos(email)
        print(f"DEBUG: Usuario obtenido: {usuario is not None}")
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        saldo_actual = usuario['saldo_actual']
        limite_mensual = usuario['limite_mensual'] 
        fecha_renovacion = usuario['fecha_renovacion']
        
        print("DEBUG: Obteniendo transacciones...")
        # Obtener historial de transacciones (últimos 30 días)
        fecha_limite = (datetime.now() - timedelta(days=30)).isoformat()
        print(f"DEBUG: Fecha límite: {fecha_limite}")
        
        # Obtener todas las transacciones del usuario (sin filtro de fecha por ahora)
        transacciones_result = databases.list_documents(
            DATABASE_ID,
            '68c19c78d65e58f658fd'  # ID de transacciones_creditos
        )

        # Filtrar manualmente por email
        transacciones_usuario = []
        for doc in transacciones_result['documents']:
            if doc.get('email') == email:
                transacciones_usuario.append(doc)

        transacciones_result = {'documents': transacciones_usuario}
        
        # Obtener estadísticas de evaluaciones
        evaluaciones_result = databases.list_documents(
            DATABASE_ID,
            '68c19d6a6239cdd915bd'  # ID de evaluaciones
        )

        # Filtrar manualmente por email
        evaluaciones_usuario = []
        for doc in evaluaciones_result['documents']:
            if doc.get('email') == email:
                evaluaciones_usuario.append(doc)

        evaluaciones_result = {'documents': evaluaciones_usuario}
        
        # Calcular estadísticas
        stats_evaluaciones = [
            len(evaluaciones_result['documents']),
            sum([doc.get('creditos_totales', 0) for doc in evaluaciones_result['documents']]),
            sum([doc.get('num_estudiantes', 0) for doc in evaluaciones_result['documents']])
        ]

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
            
            # Datos para gráficos  
            datos_dia = generar_datos_grafico_dia(email)
            datos_semana = generar_datos_grafico_semana(email)
            datos_mes = generar_datos_grafico_mes(email)
            
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
                'total_evaluaciones': stats_evaluaciones[0],
                'creditos_evaluaciones': stats_evaluaciones[1],
                'estudiantes_evaluados': stats_evaluaciones[2]
            },
            'actividades': actividades,
            'graficos': {
                'dia': datos_dia,
                'semana': datos_semana,
                'mes': datos_mes
            }
        })
        
    except Exception as e:
        print(f"ERROR DASHBOARD DETALLADO: {e}")
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
        saldo_actual = usuario['saldo_actual']
        
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
        
        # Registrar en transacciones
        databases.create_document(
            DATABASE_ID,
            '68c19c78d65e58f658fd',
            'unique()',
            {
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
            DATABASE_ID,
            '68c19d6a6239cdd915bd',
            'unique()',
            {
                'email': email,
                'examen_id': examen_id,
                'modelos_usados': modelos_json,
                'num_estudiantes': num_estudiantes,
                'creditos_totales': creditos_totales,
                'tokens_totales': tokens_totales
            }
        )
        
        # Actualizar saldo del usuario
        nuevo_saldo = usuario['saldo_actual'] - creditos_totales
        databases.update_document(
            DATABASE_ID,
            '68c19ba15c0d1a8461b3',
            usuario['$id'],
            {'saldo_actual': nuevo_saldo}
        )
        
        # El nuevo saldo ya lo calculamos arriba
        # nuevo_saldo = usuario['saldo_actual'] - creditos_totales
        
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
    """Consultar saldo actual de créditos"""
    try:
        usuario = obtener_usuario_creditos(email)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        saldo_actual = usuario['saldo_actual']
        limite_mensual = usuario['limite_mensual']
        fecha_renovacion = usuario['fecha_renovacion']
        
        return jsonify({
            'email': email,
            'saldo_actual': saldo_actual,
            'limite_mensual': limite_mensual,
            'fecha_renovacion': fecha_renovacion
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
        
        # Obtener usuario actual
        usuario = obtener_usuario_creditos(email)
        
        if not usuario:
            return jsonify({'error': 'No se pudo crear/obtener usuario'}), 400
        
        # Registrar recarga
        databases.create_document(
            DATABASE_ID,
            '68c19c78d65e58f658fd',
            'unique()',
            {
                'email': email,
                'tipo': 'recarga',
                'creditos': creditos,
                'tokens_usados': 0,
                'descripcion': descripcion,
                'modelos_usados': None,
                'num_estudiantes': 0
            }
        )
        
        # Actualizar saldo del usuario
        nuevo_saldo = usuario['saldo_actual'] + creditos
        databases.update_document(
            DATABASE_ID,
            '68c19ba15c0d1a8461b3',
            usuario['$id'],
            {'saldo_actual': nuevo_saldo}
        )
        
        # El nuevo saldo ya lo calculamos arriba
        # nuevo_saldo = usuario['saldo_actual'] + creditos
        
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
    init_database()
    logger.info("Servidor evaluador de exámenes iniciado")
    app.run(debug=False, host='0.0.0.0', port=5002)