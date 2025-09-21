from flask import Flask, request, jsonify
from google.cloud import storage
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
import tempfile
from dotenv import load_dotenv
import os
from together import Together
import json
import base64
import re
import fitz  
import traceback 
from appwrite.query import Query
from google.cloud import storage
from fnmatch import fnmatch
from openai import OpenAI 
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Limpiar variables de proxy
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None) 


# 1. AGREGAR AL INICIO (después de las importaciones existentes):
app = Flask(__name__)

load_dotenv()

# Obtener la clave API desde las variables de entorno
api_key = os.getenv('GOOGLE_GEMINI_PRO_API_KEY')

# Ahora puedes usar el cliente en tus funciones
# Por ejemplo, en una función de evaluación:
def evaluar_con_gemini(prompt):
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=prompt
    )
    return response.text

# --- Configuración ---
APPWRITE_ENDPOINT = os.getenv('APPWRITE_ENDPOINT')
APPWRITE_PROJECT = os.getenv('APPWRITE_PROJECT_ID')
APPWRITE_API_KEY = os.getenv('APPWRITE_API_KEY')
APPWRITE_DB_ID = os.getenv('APPWRITE_DATABASE_ID')
COLLECTION_EXAMEN_ALUMNO = os.getenv('APPWRITE_COLLECTION_ID')
BUCKET_EXAMEN_GENERADO = os.getenv('APPWRITE_BUCKET_EXAMEN_GENERADO')
GCS_BUCKET_NAME = os.getenv('APPWRITE_BUCKET_EXAMEN_ONLINEA')
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
COLLECTION_EXAMEN_PLANTILLA = os.getenv('APPWRITE_COLLECTION_EXAMEN_PLANTILLA_RESPUESTAS')
APPWRITE_COLLECTION_EXAMEN_PROFESOR_URL = os.getenv('APPWRITE_COLLECTION_EXAMEN_PROFESOR_URL')
APPWRITE_COLLECTION_EXAMEN_PLANTILLA_RESPUESTAS = os.getenv('APPWRITE_COLLECTION_EXAMEN_PLANTILLA_RESPUESTAS')
APPWRITE_GUARDAR_EVALUACION_MODELOS = os.getenv('APPWRITE_GUARDAR_EVALUACION_MODELOS')
APPWRITE_BUCKET_PLANTILLA_EXAMEN_RESPUESTAS = os.getenv('APPWRITE_BUCKET_PLANTILLA_EXAMEN_RESPUESTAS')
APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN = os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')
APPWRITE_GUARDAR_COMENTARIOS_EVALUACION = os.getenv('APPWRITE_GUARDAR_COMENTARIOS_EVALUACION')
GOOGLE_GEMINI_PDF_PRO_API_KEY = os.getenv('GOOGLE_GEMINI_PDF_PRO_API_KEY')
APPWRITE_COLECCION_BANCO_RUBRICAS_PROFESOR = os.getenv('APPWRITE_COLECCION_BANCO_RUBRICAS_PROFESOR')
APPWRITE_PUNTAJE_EVALUACION_EXAMEN = os.getenv('APPWRITE_PUNTAJE_EVALUACION_EXAMEN')


# Al inicio del archivo, después de las variables existentes:
APPWRITE_ENDPOINT_BANCO_DATOS = os.getenv('APPWRITE_ENDPOINT_BANCO_DATOS')
APPWRITE_PROJECT_ID_BANCO_DATOS = os.getenv('APPWRITE_PROJECT_ID_BANCO_DATOS')
APPWRITE_API_KEY_BANCO_DATOS = os.getenv('APPWRITE_API_KEY_BANCO_DATOS')
APPWRITE_COLECCION_BANCO_RUBRICAS = os.getenv('APPWRITE_COLECCION_BANCO_RUBRICAS')
APPWRITE_BANCO_PREGUNTAS_GENERAL = os.getenv('APPWRITE_BANCO_PREGUNTAS_GENERAL')

# Inicializar cliente para banco de datos separado
#client_banco = Client()
#client_banco.set_endpoint(APPWRITE_ENDPOINT_BANCO_DATOS).set_project(APPWRITE_PROJECT_ID_BANCO_DATOS).set_key(APPWRITE_API_KEY_BANCO_DATOS)
#db_banco = Databases(client_banco)

# ✅ AGREGAR ESTOS LOGS AQUÍ:
print(f"[BANCO] Endpoint: {APPWRITE_ENDPOINT_BANCO_DATOS}")
print(f"[BANCO] Project ID: {APPWRITE_PROJECT_ID_BANCO_DATOS}")
print(f"[BANCO] Database ID: {APPWRITE_BANCO_PREGUNTAS_GENERAL}")
print(f"[BANCO] Collection ID: {APPWRITE_COLECCION_BANCO_RUBRICAS}")
print(f"[BANCO] API Key: {APPWRITE_API_KEY_BANCO_DATOS[:20]}...")

print(f"[INIT] Bucket plantilla cargado: {APPWRITE_BUCKET_PLANTILLA_EXAMEN_RESPUESTAS}")
print(f"[INIT] Bucket examen generado: 67e579bd0018f15c73c3")

# --- 2. NUEVAS LISTAS DE MODELOS IA---
# (Clasifica según si son de texto o multimodales. Verifica nombres exactos en OpenRouter)

# Modelos clasificados por tipo
MODELOS_TEXTO_TOGETHER = [
    
    #Meta/LLaMA Models
    "meta-llama/Llama-Guard-4-12B",
    "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "meta-llama/Llama-3.2-3B-Instruct-Turbo",
    "meta-llama/Llama-Guard-3-11B-Vision-Turbo",
    "meta-llama/Meta-Llama-Guard-3-8B",
    "meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3-8B-Instruct-Lite",
    "meta-llama/Llama-3-70b-chat-hf",
    "meta-llama/LlamaGuard-2-8b",
    "meta-llama/Llama-2-70b-hf",
    
    #Qwen Models
    "Qwen/Qwen3-Next-80B-A3B-Thinking",
    "Qwen/Qwen3-235B-A22B-Thinking-2507",
    "Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8",
    "Qwen/Qwen3-235B-A22B-Instruct-2507-tput",
    "Qwen/Qwen2.5-VL-72B-Instruct",
    "Qwen/QwQ-32B",
    "Qwen/Qwen3-235B-A22B-fp8-tput",
    "Qwen/Qwen2.5-72B-Instruct-Turbo",
    "Qwen/Qwen2.5-7B-Instruct-Turbo",
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    
    #DeepSeek Models
    "deepseek-ai/DeepSeek-R1",
    "deepseek-ai/DeepSeek-V3",
    "deepseek-ai/DeepSeek-R1-0528-tput",
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
    
    #Mistral Models
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "mistralai/Mistral-7B-Instruct-v0.1",
    "mistralai/Mistral-Small-24B-Instruct-2501",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "mistralai/Mistral-7B-Instruct-v0.2",
    
    #Arcee AI Models
    "arcee_ai/arcee-spotlight",
    "arcee-ai/virtuoso-large",
    "arcee-ai/coder-large",
    "arcee-ai/maestro-reasoning",
    "arcee-ai/AFM-4.5B",
    
    #OpenAI Models
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "openai/whisper-large-v3",
    
    #Together Computer Models
    "togethercomputer/Refuel-Llm-V2-Small",
    "togethercomputer/Refuel-Llm-V2",
    "togethercomputer/m2-bert-80M-32k-retrieval",
    
    #BAAI Models
    "BAAI/bge-large-en-v1.5",
    "BAAI/bge-base-en-v1.5",
    
    #Other/Specialized Models
    "moonshotai/Kimi-K2-Instruct",
    "zai-org/GLM-4.5-Air-FP8",
    "lgai/exaone-3-5-32b-instruct",
    "lgai/exaone-deep-32b",
    "marin-community/marin-8b-instruct",
    "intfloat/multilingual-e5-large-instruct",
    "Alibaba-NLP/gte-modernbert-base",
    "scb10x/scb10x-typhoon-2-1-gemma3-12b",
    "arize-ai/qwen-2-1.5b-instruct",
    "deepcogito/cogito-v2-preview-llama-70B",
    "upstage/SOLAR-10.7B-Instruct-v1.0"
]

MODELOS_MULTIMODAL_TOGETHER = [
    "Qwen/Qwen2.5-VL-72B-Instruct",
    "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"
]
MODELOS_TEXTO_OPENROUTER = [
    "qwen/qwen3-32b:free",
    "deepseek/deepseek-chat-v3-0324",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.1-405b:free",
]

# Modelos de texto de Groq
MODELOS_TEXTO_GROQ = [
    "deepseek-r1-distill-llama-70b",
    "mistral-saba-24b", 
    "qwen-qwq-32b",
    "qwen/qwen3-32b"
]

# Modelos multimodales de Groq (soportan archivos)
MODELOS_MULTIMODAL_GROQ = [
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "meta-llama/llama-4-scout-17b-16e-instruct"
]

MODELOS_ESPECIALIZADOS_GROQ = {
    "prompt_guard": [
        "meta-llama/llama-prompt-guard-2-22m",
        "meta-llama/llama-prompt-guard-2-86m"
    ],
    "tts": [
        "playai-tts",
        "playai-tts-arabic"
    ]
}

MODELOS_MULTIMODAL_OPENROUTER = [
    "qwen/qwen2.5-vl-32b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "google/learnlm-1.5-pro-experimental:free",
    "meta-llama/llama-3.2-11b-vision-instruct:free",
]

# Agregar modelos Gemini
MODELOS_GEMINI = [
    {
        'id': 'gemini-2-5-pro',
        'model_id': 'gemini-2.5-pro-preview-05-06',
        'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
    },
    {
        'id': 'gemini-2-5-flash',
        'model_id': 'gemini-2.5-flash-preview-04-17',
        'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
    },
    {
        'id': 'gemini-2-0-flash',
        'model_id': 'gemini-2.0-flash',
        'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
    },
    {
        'id': 'gemini-1-5-flash',
        'model_id': 'gemini-1.5-flash',
        'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
    },
    {
        'id': 'gemini-1-5-pro',
        'model_id': 'gemini-1.5-pro',
        'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
    }
]
# --- FIN NUEVAS LISTAS ---

regex_json = re.compile(r'\{.*?\}', re.DOTALL) # agregar esto una vez al inicio

storage_client = storage.Client()

# Inicializar Appwrite
client = Client()
client.set_endpoint(APPWRITE_ENDPOINT).set_project(APPWRITE_PROJECT).set_key(APPWRITE_API_KEY)
db = Databases(client)
storage_appwrite = Storage(client)

# Inicializar cliente GCS
gcs_client = storage.Client()
gcs_bucket = gcs_client.bucket(GCS_BUCKET_NAME)


@app.route('/api/playground', methods=['POST'])
def playground_ia():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', '')
        modelo_ia = data.get('modelo_ia', 'gemini-2-5-flash')
        email = data.get('email', '')
        
        if not prompt_usuario:
            return jsonify({'error': 'Prompt requerido'}), 400
            
        # Enviar directamente al modelo IA sin modificaciones
        respuesta = generar_respuesta_con_modelo(prompt_usuario, modelo_ia)
        
        return jsonify({
            'success': True,
            'contenido': respuesta,
            'modelo': modelo_ia
        })
        
    except Exception as e:
        print(f"Error en playground: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generar_respuesta_con_modelo(prompt, modelo_seleccionado):
    """Función para generar respuesta usando TODOS los modelos disponibles"""
    try:
        print(f"[PLAYGROUND] Usando modelo: {modelo_seleccionado}")
        
        # ✅ 1. MODELOS GEMINI
        if modelo_seleccionado in [g['id'] for g in MODELOS_GEMINI]:
            gemini_info = next((g for g in MODELOS_GEMINI if g['id'] == modelo_seleccionado), None)
            if gemini_info:
                return evaluar_con_gemini_http(
                    prompt, 
                    gemini_info['model_id'],
                    os.environ.get(gemini_info['api_key_env'])
                )
        
        # ✅ 2. MODELOS OPENROUTER (TEXTO)
        elif modelo_seleccionado in MODELOS_TEXTO_OPENROUTER:
            openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY
            )
            completion = openrouter_client.chat.completions.create(
                model=modelo_seleccionado,
                messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content
        
        # ✅ 3. MODELOS OPENROUTER (MULTIMODAL)  
        elif modelo_seleccionado in MODELOS_MULTIMODAL_OPENROUTER:
            openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY
            )
            completion = openrouter_client.chat.completions.create(
                model=modelo_seleccionado,
                messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content
        
         # ✅ 4. AGREGAR ESTA SECCIÓN PARA GROQ (TEXTO)
        elif modelo_seleccionado in MODELOS_TEXTO_GROQ:
            groq_client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=os.getenv('GROQ_API_KEY')  # ← Necesitas esta variable
            )
            completion = groq_client.chat.completions.create(
                model=modelo_seleccionado,
                messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content
        
        # ✅ 5. AGREGAR ESTA SECCIÓN PARA GROQ (MULTIMODAL)
        elif modelo_seleccionado in MODELOS_MULTIMODAL_GROQ:
            groq_client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=os.getenv('GROQ_API_KEY')
            )
            completion = groq_client.chat.completions.create(
                model=modelo_seleccionado,
                messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content
        
        # ✅ 6. MODELOS GPT (si los tienes configurados)
        elif modelo_seleccionado in ['gpt-4o', 'gpt-4o-mini']:
            # Si tienes configuración de OpenAI directa
            if os.getenv('OPENAI_API_KEY'):
                openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                completion = openai_client.chat.completions.create(
                    model=modelo_seleccionado,
                    messages=[{"role": "user", "content": prompt}]
                )
                return completion.choices[0].message.content
            else:
                return "API Key de OpenAI no configurada"
        
        # ✅ 7. MODELOS TOGETHER (si los tienes)
        elif modelo_seleccionado in MODELOS_TEXTO_TOGETHER + MODELOS_MULTIMODAL_TOGETHER:
            # Si tienes configuración de Together
            if TOGETHER_API_KEY:
                together_client = OpenAI(
                    base_url="https://api.together.xyz/v1",
                    api_key=TOGETHER_API_KEY
                )
                completion = together_client.chat.completions.create(
                    model=modelo_seleccionado,
                    messages=[{"role": "user", "content": prompt}]
                )
                return completion.choices[0].message.content
            else:
                return "API Key de Together no configurada"
        
        else:
            return f"Modelo '{modelo_seleccionado}' no reconocido o no configurado"
            
    except Exception as e:
        print(f"[PLAYGROUND] Error con modelo {modelo_seleccionado}: {str(e)}")
        return f"Error generando respuesta: {str(e)}"



# ✅ POR ESTE:
@app.route('/api/rubricas/lista', methods=['POST'])
def obtener_lista_rubricas():
    try:
        data = request.get_json()
        email_profesor = data.get('email_profesor')
        
        print(f"[RUBRICAS] Buscando lista para: {email_profesor}")
        
        response = db.list_documents(
            database_id=APPWRITE_DB_ID,
            collection_id=APPWRITE_COLECCION_BANCO_RUBRICAS_PROFESOR,  # ← NUEVA COLECCIÓN
            queries=[Query.equal("email_profesor", email_profesor)]
        )
        
        print(f"[RUBRICAS] ✅ Documentos encontrados: {len(response['documents'])}")
        
        return jsonify({
            'success': True,
            'rubricas': response['documents']
        })
        
    except Exception as e:
        print(f"[RUBRICAS] ❌ Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rubricas/detalle/<rubrica_id>', methods=['GET'])
def obtener_detalle_rubrica(rubrica_id):
    try:
        response = db.get_document(
            database_id=APPWRITE_DB_ID,
            collection_id=APPWRITE_COLECCION_BANCO_RUBRICAS_PROFESOR,
            document_id=rubrica_id
        )
        
        return jsonify({
            'success': True,
            'rubrica': response
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rubricas/nueva', methods=['POST'])
def crear_nueva_rubrica():
    try:
        data = request.get_json()
        
        result = db.create_document(
            database_id=APPWRITE_DB_ID,
            collection_id=APPWRITE_COLECCION_BANCO_RUBRICAS_PROFESOR,
            document_id="unique()",
            data={
                'email_profesor': data.get('email_profesor'),
                'nombre_rubrica': data.get('nombre_rubrica'),
                'categoria': data.get('categoria'),
                'nivel': data.get('nivel'),
                'rubrica_marcar': data.get('rubrica_marcar', ''),
                'rubrica_libres': data.get('rubrica_libres', ''),
                'rubrica_casos': data.get('rubrica_casos', ''),
                'fecha_creacion': datetime.now().isoformat(),
                'activa': True
            }
        )
        
        return jsonify({'success': True, 'id': result['$id']})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def evaluar_con_gemini_http(prompt, modelo_id, api_key):
    """Evalúa usando la API HTTP directa de Gemini en lugar de la biblioteca"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_id}:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "role": "user", 
                "parts": [{"text": prompt}]
            }
        ],
        "generation_config": {
            "temperature": 0.7,
            "maxOutputTokens": 4000
        }
    }
    
    print(f"[DEBUG] Llamando Gemini: {modelo_id}")
    print(f"[DEBUG] Prompt length: {len(prompt)} caracteres")
    
    response = requests.post(url, headers=headers, json=payload)
    
    print(f"[DEBUG] Response status: {response.status_code}")
    print(f"[DEBUG] Response JSON: {response.json()}")
    
    if response.status_code == 200:
        result = response.json()
        if "candidates" in result and result["candidates"]:
            candidate = result["candidates"][0]
            
            # Verificar si se cortó por tokens
            if candidate.get("finishReason") == "MAX_TOKENS":
                return "Error: Respuesta cortada por límite de tokens"
                
            content = candidate.get("content", {})
            if "parts" in content and content["parts"]:
                return content["parts"][0].get("text", "")
            
        return "Error: Estructura de respuesta inesperada"
    else:
        return f"Error: {response.status_code}, {response.text}"
    
def extraer_comentario_pregunta(respuestas, numero_pregunta):
    """Extrae comentario usando los mismos patrones que funcionan en el VPS"""
    import re
    
    print(f"[DEBUG] Buscando comentario para P{numero_pregunta}")
    
    for modelo, respuesta in respuestas:
        if respuesta.startswith("Error:"):
            continue
        
        # Patrones del VPS adaptados a Python
        patrones = [
            # meta-llama: - **P1**: comentario **Puntaje: 0**
            rf'-\s*\*\*P{numero_pregunta}\*\*:\s*(.*?)\s*\*\*Puntaje:\s*([0-9.]+)\*\*',
            # gemini: P1: comentario (0 puntos)  
            rf'P{numero_pregunta}:\s*(.*?)\s*\(([0-9.]+)\s*punt[os]*\)',
            # Formato genérico: P1: comentario
            rf'P{numero_pregunta}:\s*([^P]+?)(?=P\d+:|$)'
        ]
        
        for patron in patrones:
            match = re.search(patron, respuesta, re.DOTALL)
            if match:
                comentario = match.group(1).strip()[:200]
                print(f"[DEBUG] Comentario encontrado para P{numero_pregunta}: {comentario}...")
                return comentario
    
    print(f"[DEBUG] No se encontró comentario para P{numero_pregunta}")
    return "Evaluación completada correctamente"

def evaluar_respuestas_multi_modelo(alumno_json, pdf_path, modelos=None, etiquetas=None, nivel_evaluacion=None, rubricas=None):
     
    # Al inicio de evaluar_respuestas_multi_modelo, agregar:
    if not etiquetas:
        etiquetas = {}
        print("[WARN] No se recibieron etiquetas, usando valores por defecto")
    
    # Unificar todos los modelos posibles SOLO si no se recibe lista
    if not modelos:  # Captura None, [], y listas vacías
        modelos = (
            MODELOS_TEXTO_OPENROUTER +
            [g['id'] for g in MODELOS_GEMINI] +
            MODELOS_MULTIMODAL_OPENROUTER
            # + agrega aquí otras fuentes si tienes más listas (OpenAI, Together, Sonnet)
        )
    print("Modelos recibidos para evaluar:", modelos)
    
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY, 
    )
    
    # Configurar cliente para Gemini
    # Configurar API key para Gemini
    gemini_api_key = os.getenv('GOOGLE_GEMINI_PRO_API_KEY')
    gemini_client = gemini_api_key is not None
    
    pdf_base64 = None # Inicializar
    if pdf_path and os.path.exists(pdf_path): # Solo intentar leer si pdf_path es válido
        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
                pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        except Exception as e_pdf_read:
            print(f"[⚠️] Error leyendo pdf_path '{pdf_path}': {e_pdf_read}")
            # pdf_base64 permanecerá None, afectando a modelos multimodales

    respuestas = []
    resumen_modelos = []

#-------INICIA EL CAMBIO--------------------------------------------------------------------------------------

    # ✅ NUEVO CÓDIGO UNIFICADO
    print("--- INICIANDO EVALUACIÓN DE MODELOS SELECCIONADOS ---")
    for modelo in modelos:  # Solo los modelos seleccionados
        try:
            print(f"[API CALL] Evaluando modelo: {modelo}")
            
            # Determinar tipo de modelo y generar prompt apropiado
            if modelo in [g['id'] for g in MODELOS_GEMINI]:
                # Evaluar con Gemini
                gemini_info = next((g for g in MODELOS_GEMINI if g['id'] == modelo), None)
                if gemini_info:
                    prompt = generar_prompt(alumno_json, pdf_base64, incluir_pdf=True, etiquetas=etiquetas, nivel_evaluacion=nivel_evaluacion)
                    prompt = agregar_rubricas_al_prompt(prompt, rubricas) #=======AGREGAR LINEA RUBRICA
                    respuesta_contenido = evaluar_con_gemini_http(prompt, gemini_info['model_id'], os.environ.get(gemini_info['api_key_env']))
                    # Extraer detalles de cada pregunta para el frontend
                    
                    if respuesta_contenido and not respuesta_contenido.startswith("Error:"):
                        respuestas.append((modelo, respuesta_contenido))
                        # Procesar JSON del resultado...
                    else:
                        respuestas.append((modelo, f"Error: {respuesta_contenido}"))
                        
            elif modelo in MODELOS_TEXTO_OPENROUTER:
                # Evaluar texto con OpenRouter
                prompt = generar_prompt(alumno_json, pdf_base64, incluir_pdf=True, etiquetas=etiquetas, nivel_evaluacion=nivel_evaluacion)
                prompt = agregar_rubricas_al_prompt(prompt, rubricas) #=======AGREGAR LINEA RUBRICA
                completion = openrouter_client.chat.completions.create(
                    model=modelo,
                    messages=[{"role": "user", "content": prompt}],
                )
                if completion and completion.choices and len(completion.choices) > 0:
                    respuesta_contenido = completion.choices[0].message.content
                    respuestas.append((modelo, respuesta_contenido))
                else:
                    respuestas.append((modelo, "Error: Respuesta vacía"))
                    
            elif modelo in MODELOS_MULTIMODAL_OPENROUTER:
                # Evaluar multimodal con OpenRouter (requiere PDF)
                if pdf_base64:
                    prompt = generar_prompt(alumno_json, None, incluir_pdf=False, etiquetas=etiquetas, nivel_evaluacion=nivel_evaluacion)
                    
                    mensajes_multimodal = [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:application/pdf;base64,{pdf_base64}"}}
                    ]
                    completion = openrouter_client.chat.completions.create(
                        model=modelo,
                        messages=[{"role": "user", "content": mensajes_multimodal}],
                    )
                    if completion and completion.choices and len(completion.choices) > 0:
                        respuesta_contenido = completion.choices[0].message.content
                        respuestas.append((modelo, respuesta_contenido))
                    else:
                        respuestas.append((modelo, "Error: Respuesta vacía"))
                else:
                    respuestas.append((modelo, "N/A - PDF no disponible"))
                
             # ✅ AGREGAR ESTAS DOS SECCIONES AQUÍ:
            elif modelo in MODELOS_TEXTO_GROQ:
                # Evaluar texto con Groq
                groq_client = OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=GROQ_API_KEY
                )
                prompt = generar_prompt(alumno_json, pdf_base64, incluir_pdf=True, etiquetas=etiquetas, nivel_evaluacion=nivel_evaluacion)
                prompt = agregar_rubricas_al_prompt(prompt, rubricas)
                completion = groq_client.chat.completions.create(
                    model=modelo,
                    messages=[{"role": "user", "content": prompt}],
                )
                if completion and completion.choices and len(completion.choices) > 0:
                    respuesta_contenido = completion.choices[0].message.content
                    respuestas.append((modelo, respuesta_contenido))
                else:
                    respuestas.append((modelo, "Error: Respuesta vacía"))
                    
            elif modelo in MODELOS_MULTIMODAL_GROQ:
                        # Evaluar multimodal con Groq
                        groq_client = OpenAI(
                            base_url="https://api.groq.com/openai/v1",
                            api_key=GROQ_API_KEY
                        )
                        prompt = generar_prompt(alumno_json, pdf_base64, incluir_pdf=True, etiquetas=etiquetas, nivel_evaluacion=nivel_evaluacion)
                        prompt = agregar_rubricas_al_prompt(prompt, rubricas)
                        completion = groq_client.chat.completions.create(
                            model=modelo,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        if completion and completion.choices and len(completion.choices) > 0:
                            respuesta_contenido = completion.choices[0].message.content
                            respuestas.append((modelo, respuesta_contenido))
                        else:
                            respuestas.append((modelo, "Error: Respuesta vacía"))    
                                     
             # ✅ AGREGAR ESTA SECCION AQUÍ:
            elif modelo in MODELOS_TEXTO_TOGETHER:
                # Evaluar texto con Together
                together_client = OpenAI(
                    base_url="https://api.together.xyz/v1",
                    api_key=TOGETHER_API_KEY
                )
                prompt = generar_prompt(alumno_json, pdf_base64, incluir_pdf=True, etiquetas=etiquetas, nivel_evaluacion=nivel_evaluacion)
                prompt = agregar_rubricas_al_prompt(prompt, rubricas)
                completion = together_client.chat.completions.create(
                    model=modelo,
                    messages=[{"role": "user", "content": prompt}],
                )
                if completion and completion.choices and len(completion.choices) > 0:
                    respuesta_contenido = completion.choices[0].message.content
                    respuestas.append((modelo, respuesta_contenido))
                else:
                    respuestas.append((modelo, "Error: Respuesta vacía"))    

            
            else:
                print(f"[WARN] Modelo {modelo} no reconocido")
                respuestas.append((modelo, "Error: Modelo no reconocido"))
                continue
            
                
            # Procesar resultado común para todos los modelos
            if len(respuestas) > 0 and not respuestas[-1][1].startswith("Error:") and not respuestas[-1][1].startswith("N/A"):
                try:
                # Solo procesar si no es error
                    response_text = respuestas[-1][1]
                    if not response_text.startswith("Error:"):
                        # Limpiar markdown
                        # Usar nueva función de extracción y limpieza
                        data = extraer_y_limpiar_json(response_text, alumno_json.get('plantilla_json'))
                        
                        if data:
                            resumen_modelos.append({
                                "modelo": modelo,
                                "marcar": data.get("preguntas_marcar", 0),
                                "libres": data.get("preguntas_libres", 0),
                                "casos": data.get("casos_uso", 0),
                                "total": data.get("total", 0),
                                "porcentaje": data.get("porcentaje", 0)
                            })
                        else:
                            resumen_modelos.append({"modelo": modelo, "error_proc_json": "No se encontró JSON válido"})
                    else:
                        resumen_modelos.append({"modelo": modelo, "error_api": response_text})
                except Exception as e_json:
                    print(f"[⚠️] Error procesando JSON de {modelo}: {e_json}")
                    resumen_modelos.append({"modelo": modelo, "error_proc_json": str(e_json)})
                    
        except Exception as e_api:
            print(f"[⚠️] EXCEPCIÓN con modelo {modelo}: {e_api}")
            respuestas.append((modelo, f"Error API: {str(e_api)}"))
            resumen_modelos.append({"modelo": modelo, "error_api": str(e_api)})
        
        #--------------FIN DEL CAMBIO------------------------------------------------------------------------------------------------------------

    print("\n--- RESPUESTAS DE MODELOS ---")
    for modelo, res in respuestas:
        print(f"\n[{modelo}]\n{res}")
    
    print("\nResumen de Resultados por Modelo")
    print("Modelo\tMarcar\tLibres\tCasos de Uso\tTotal\t%")
    for r_sum_item in resumen_modelos:
        print(f"{r_sum_item.get('modelo','?')}\t{r_sum_item.get('marcar','?')}\t{r_sum_item.get('libres','?')}\t{r_sum_item.get('casos','?')}\t{r_sum_item.get('total','?')}\t{r_sum_item.get('porcentaje','?')}%")

    # Extraer puntajes y calcular consenso
    puntajes = {"preguntas_marcar": [], "preguntas_libres": [], "casos_uso": [], "total": [], "porcentaje": []}
    plantilla_json = alumno_json.get('plantilla_json', {})
    
    for _, res_contenido_puntaje in respuestas:
        try:
            # Solo intentar parsear si no es un mensaje de error que nosotros mismos pusimos
            if isinstance(res_contenido_puntaje, str) and not res_contenido_puntaje.startswith("Error:"):
                # Intentar extraer el JSON de la respuesta
                #data_puntaje = json.loads(re.search(r"\{.*\}", res_contenido_puntaje, re.DOTALL).group())
                
                data_puntaje = extraer_y_limpiar_json(res_contenido_puntaje, plantilla_json)
                if data_puntaje:
                    print(f"[DEBUG] JSON extraído: {data_puntaje}")  # ← AQUÍ
                    for k in puntajes:
                        print(f"[DEBUG] Verificando clave '{k}': existe={k in data_puntaje}, tipo={type(data_puntaje.get(k))}, valor={data_puntaje.get(k)}")    
                        if k in data_puntaje and isinstance(data_puntaje[k], (int, float)):
                            puntajes[k].append(float(data_puntaje[k]))
                            print(f"[DEBUG] Agregado {data_puntaje[k]} a {k}")
                        else:
                            print(f"[DEBUG] NO agregado a {k}")          
                else:
                    print(f"[⚠️] Consenso: No se encontró JSON válido en respuesta de modelo.")
            else:
                print(f"[⚠️] Consenso: Ignorando respuesta de error: {res_contenido_puntaje[:50]}...")
        except Exception as e_json_consenso:
            print(f"[⚠️] Consenso: Error procesando JSON '{str(res_contenido_puntaje)[:50]}...': {e_json_consenso}")
            continue

    # Calcular consenso solo si hay respuestas válidas para cada categoría
    # Reorganizar para admitir multimodales con PDF adicional
        #puntajes = {
        #"preguntas_marcar": [],
        #"preguntas_libres": [],
        #"casos_uso": [],
        #"casos_de_uso_pdf": [],
        #"porcentaje": []
    #}
    
    print(f"[DEBUG] Puntajes recolectados: {puntajes}")
    print(f"[DEBUG] Longitudes: {[(k, len(v)) for k, v in puntajes.items()]}")
    
    # Calcular promedios
    consenso = {}
    for k, lista in puntajes.items():
        consenso[k] = round(sum(lista) / len(lista), 2) if lista else 0.0

    # Calcular totales separados
    consenso["total_texto"] = round(
    consenso["preguntas_marcar"] + consenso["preguntas_libres"] + consenso["casos_uso"], 2
    )
    consenso["total_pdf"] = round(consenso.get("casos_de_uso_pdf", 0.0), 2)
    consenso["total"] = round(consenso["total_texto"] + consenso["total_pdf"], 2)

    
# Definir variables de plantilla
    plantilla = alumno_json.get('plantilla_json', {})
    plantilla_libres = plantilla.get('preguntas_libres', [])
    plantilla_casos = plantilla.get('casos_uso', [])
                    
    detalles_preguntas = []
    for i, p in enumerate(alumno_json.get('preguntas_libres', [])):
                        
        print(f"[DEBUG] Creando detalle para pregunta libre {p.get('numero', i+1)}")
        comentario_extraido = extraer_comentario_pregunta(respuestas, p.get('numero', i+1))
        print(f"[DEBUG] Comentario obtenido: {comentario_extraido[:50]}...")
                        
        detalle_pregunta = {
            "numeroPregunta": p.get('numero', i+1),
            "textoPregunta": f"Pregunta Libre {p.get('numero', i+1)}",
            "respuestaAlumno": p.get('respuesta', ''),
            "puntajeObtenido": next((x.get('puntaje', 1.0) for x in plantilla_libres if x.get('numero') == p.get('numero')), 1.0),
            "puntajeTotal": next((x.get('puntaje', 1.0) for x in plantilla_libres if x.get('numero') == p.get('numero')), 1.0),
            "comentario": comentario_extraido,
            "tipo": "libre"
        }

        print(f"[DEBUG] Detalle creado: {detalle_pregunta}")
        detalles_preguntas.append(detalle_pregunta)

    for i, p in enumerate(alumno_json.get('casos_uso', [])):
                        
        print(f"[DEBUG] Creando detalle para caso de uso {p.get('numero', i+1)}")
        comentario_extraido = extraer_comentario_pregunta(respuestas, p.get('numero', i+1))
        print(f"[DEBUG] Comentario obtenido: {comentario_extraido[:50]}...")
                        
        detalle_pregunta = {
            "numeroPregunta": p.get('numero', i+1),
            "textoPregunta": f"Caso de Uso {p.get('numero', i+1)}",
            "respuestaAlumno": p.get('respuesta', ''),
            "puntajeObtenido": next((x.get('puntaje', 1.0) for x in plantilla_casos if x.get('numero') == p.get('numero')), 1.0),
            "puntajeTotal": next((x.get('puntaje', 1.0) for x in plantilla_casos if x.get('numero') == p.get('numero')), 1.0),
            "comentario": comentario_extraido,
            "tipo": "caso_uso"
        }

        print(f"[DEBUG] Detalle creado: {detalle_pregunta}")
        detalles_preguntas.append(detalle_pregunta) 
        
        # Agregar detalles de preguntas marcar
        for i, p in enumerate(alumno_json.get('preguntas_marcar', [])):
            numero = p.get('numero', i+1)
            
            # Buscar si fue correcta en los comentarios
            es_correcta = False
            for modelo, respuesta in respuestas:
                if f"P{numero}: VERDADERA" in respuesta.upper():
                    es_correcta = True
                    break
            
            puntaje_pregunta = next((x.get('puntaje', 0.5) for x in plantilla.get('preguntas_marcar', []) if x.get('numero') == numero), 0.5)
            
            detalle_pregunta = {
                "numeroPregunta": numero,
                "textoPregunta": p.get('texto', f"Pregunta {numero}"),
                "respuestaAlumno": p.get('respuesta', ''),
                "esCorrecta": es_correcta,
                "puntajeObtenido": puntaje_pregunta if es_correcta else 0,
                "puntajeTotal": puntaje_pregunta,
                "tipo": "marcar"
            }
            detalles_preguntas.append(detalle_pregunta)
        
    print(f"[DEBUG] detalles_preguntas final: {detalles_preguntas}")
    
    return {
        "consenso": consenso,
        "total_texto": consenso["total_texto"],
        "total_pdf": consenso["total_pdf"],
        "total": consenso["total"],
        "detalles": respuestas,
        "detalles_modelo": resumen_modelos,
        "detalle": detalles_preguntas 
    }

# ========== INICIO DEL PROMT ==========
    
def generar_prompt(alumno_json=None, pdf_base64=None, incluir_pdf=False, etiquetas=None, nivel_evaluacion="Normal"):

    # Validar entrada
    if not alumno_json:
        alumno_json = {}
        
    marcar = alumno_json.get('preguntas_marcar', [])
    libres = alumno_json.get('preguntas_libres', [])
    casos = alumno_json.get('casos_uso', [])
    
    print(f"[DEBUG] Buscando casos_uso en alumno_json")
    print(f"[DEBUG] Claves disponibles: {alumno_json.keys()}")
    print(f"[DEBUG] Valor de casos_uso: {alumno_json.get('casos_uso')}")
    print(f"[DEBUG] Valor de casos_de_uso: {alumno_json.get('casos_de_uso')}")
    
    plantilla = alumno_json.get('plantilla_json', {})
    plantilla_marcar = plantilla.get('preguntas_marcar', [])
    plantilla_libres = plantilla.get('preguntas_libres', [])  
    plantilla_casos = plantilla.get('casos_uso', [])
    plantilla_marcar = plantilla.get('preguntas_marcar', [])  
    
    # ========== MODIFICADO: EVALUAR PREGUNTAS MARCAR SIN COMPARACIÓN AUTOMÁTICA ==========
    
    # Evaluar preguntas marcar con puntajes reales
    evaluacion_marcar = []
    for p in marcar:
        num = p.get('numero')
        respuesta_alumno = p.get('respuesta')  

        def num_to_letter(num):
            return {0:"A", 1:"B", 2:"C", 3:"D", 4:"E"}.get(num, "?")
        
        respuesta_alumno_letra = num_to_letter(respuesta_alumno) if respuesta_alumno is not None else "Sin respuesta"  
        plantilla_p = next((x for x in plantilla_marcar if x.get('numero') == num), {})
        puntaje = plantilla_p.get('puntaje', 1.0)
        
        # Obtener texto de la pregunta desde alumno_json
        pregunta_data = next((x for x in marcar if x.get('numero') == num), {})
        texto_pregunta = pregunta_data.get('texto', 'Pregunta no encontrada')
        opciones = pregunta_data.get('opciones', [])

        # Construir texto completo con opciones
        opciones_texto = ""
        if opciones:
            for i, opcion in enumerate(opciones):
                letra = chr(65 + i)  # A, B, C, D, E
                opciones_texto += f"\n{letra}) {opcion}"

        evaluacion_marcar.append(f"P{num}: {texto_pregunta}{opciones_texto}\nRespuesta del alumno: {respuesta_alumno_letra} ({puntaje}pts)")
        
        print(f"[DEBUG] len(casos): {len(casos)}")
        print(f"[DEBUG] plantilla_casos: {plantilla_casos}")
        print(f"[DEBUG] casos data: {casos}")
        
        
@app.route('/api/rubricas/<email_profesor>', methods=['GET'])
def obtener_rubricas_profesor(email_profesor):
    try:
        print(f"[RUBRICAS] Buscando rúbricas para: {email_profesor}")
        
        # Usar cliente del banco de datos separado
        response = db.list_documents(
            database_id=APPWRITE_DB_ID,  # En el banco, database_id = project_id
            collection_id=APPWRITE_COLECCION_BANCO_RUBRICAS_PROFESOR,
            queries=[
                Query.equal("email_profesor", email_profesor),
                Query.equal("activa", True)
            ]
        )
        
        print(f"[RUBRICAS] Documentos encontrados: {len(response['documents'])}")
        
        if response['documents']:
            rubricas = response['documents'][0]
            print(f"[RUBRICAS] ✅ Rúbricas cargadas para {email_profesor}")
            
            return jsonify({
                'success': True,
                'rubricas': {
                    'rubrica_marcar': rubricas.get('rubrica_marcar', ''),
                    'rubrica_libres': rubricas.get('rubrica_libres', ''),
                    'rubrica_casos': rubricas.get('rubrica_casos', '')
                }
            })
        else:
            print(f"[RUBRICAS] ⚠️ No se encontraron rúbricas para {email_profesor}")
            return jsonify({
                'success': False, 
                'message': 'No se encontraron rúbricas'
            })
            
    except Exception as e:
        print(f"[RUBRICAS] ❌ Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rubricas', methods=['POST'])
def guardar_rubricas_profesor():
    try:
        data = request.get_json()
        email_profesor = data.get('email_profesor')
        
        print(f"[RUBRICAS] Guardando rúbricas para: {email_profesor}")
        
        # Verificar si ya existe rúbrica del profesor en el banco
        existing = db.list_documents(
            database_id=APPWRITE_DB_ID,
            collection_id=APPWRITE_COLECCION_BANCO_RUBRICAS_PROFESOR,
            queries=[Query.equal("email_profesor", email_profesor)]
        )
        
        if existing['documents']:
            # Actualizar existente
            doc_id = existing['documents'][0]['$id']
            print(f"[RUBRICAS] 🔄 Actualizando rúbrica existente: {doc_id}")
            
            db.update_document(
                database_id=APPWRITE_DB_ID,
                collection_id=APPWRITE_COLECCION_BANCO_RUBRICAS_PROFESOR,
                document_id=doc_id,
                data={
                    'rubrica_marcar': data.get('rubrica_marcar', ''),
                    'rubrica_libres': data.get('rubrica_libres', ''),
                    'rubrica_casos': data.get('rubrica_casos', ''),
                    'fecha_actualizacion': datetime.now().isoformat()
                }
            )
        else:
            # Crear nuevo
            print(f"[RUBRICAS] ✨ Creando nueva rúbrica")
            
            db.create_document(
                database_id=APPWRITE_DB_ID,
                collection_id=APPWRITE_COLECCION_BANCO_RUBRICAS_PROFESOR,
                document_id="unique()",
                data={
                    'email_profesor': email_profesor,
                    'rubrica_marcar': data.get('rubrica_marcar', ''),
                    'rubrica_libres': data.get('rubrica_libres', ''),
                    'rubrica_casos': data.get('rubrica_casos', ''),
                    'fecha_creacion': datetime.now().isoformat(),
                    'activa': True
                }
            )
        
        print(f"[RUBRICAS] ✅ Rúbricas guardadas exitosamente")
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"[RUBRICAS] ❌ Error guardando: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})        
        
    # ========== CONFIGURAR PROMT NIVEL DE EVALUACIÓN =================================================================
    
def generar_prompt(alumno_json=None, pdf_base64=None, incluir_pdf=False, etiquetas=None, nivel_evaluacion="Normal"):
    
    # Validar entrada
    if not alumno_json:
        alumno_json = {}
        
    marcar = alumno_json.get('preguntas_marcar', [])
    libres = alumno_json.get('preguntas_libres', [])
    casos = alumno_json.get('casos_uso', [])
    
    print(f"[DEBUG] Buscando casos_uso en alumno_json")
    print(f"[DEBUG] Claves disponibles: {alumno_json.keys()}")
    print(f"[DEBUG] Valor de casos_uso: {alumno_json.get('casos_uso')}")
    print(f"[DEBUG] Valor de casos_de_uso: {alumno_json.get('casos_de_uso')}")
    
    plantilla = alumno_json.get('plantilla_json', {})
    plantilla_marcar = plantilla.get('preguntas_marcar', [])
    plantilla_libres = plantilla.get('preguntas_libres', [])  
    plantilla_casos = plantilla.get('casos_uso', [])  
    
    # ========== MODIFICADO: EVALUAR PREGUNTAS MARCAR SIN COMPARACIÓN AUTOMÁTICA ==========
    
    # Evaluar preguntas marcar con puntajes reales
    evaluacion_marcar = []
    for p in marcar:
        num = p.get('numero')
        respuesta_alumno = p.get('respuesta')  

        def num_to_letter(num):
            return {0:"A", 1:"B", 2:"C", 3:"D", 4:"E"}.get(num, "?")
        
        respuesta_alumno_letra = num_to_letter(respuesta_alumno) if respuesta_alumno is not None else "Sin respuesta"  
        plantilla_p = next((x for x in plantilla_marcar if x.get('numero') == num), {})
        puntaje = plantilla_p.get('puntaje', 1.0)
        
        # Obtener texto de la pregunta desde alumno_json
        pregunta_data = next((x for x in marcar if x.get('numero') == num), {})
        texto_pregunta = pregunta_data.get('texto', 'Pregunta no encontrada')
        opciones = pregunta_data.get('opciones', [])

        # Construir texto completo con opciones
        opciones_texto = ""
        if opciones:
            for i, opcion in enumerate(opciones):
                letra = chr(65 + i)  # A, B, C, D, E
                opciones_texto += f"\n{letra}) {opcion}"

        evaluacion_marcar.append(f"P{num}: {texto_pregunta}{opciones_texto}\nRespuesta del alumno: {respuesta_alumno_letra} ({puntaje}pts)")
        
        print(f"[DEBUG] len(casos): {len(casos)}")
        print(f"[DEBUG] plantilla_casos: {plantilla_casos}")
        print(f"[DEBUG] casos data: {casos}")  
        
      # ========== CONFIGURAR NIVEL DE EVALUACIÓN ========================================================================================================      
    criterios_nivel = {
        "Normal": {
            "descripcion": "Evaluación con criterio académico estándar. Exige respuestas correctas y coherentes, pero permite pequeños errores menores.",
            "preguntas_marcar": "Para preguntas marcar: respuesta correcta = puntaje completo, respuesta incorrecta = 0 puntos. No hay puntos parciales.",
            "preguntas_libres": "Para preguntas libres: asigna puntaje completo si la respuesta es correcta y bien fundamentada. Descuenta 20-30% por errores menores o falta de precisión.",
            "casos_uso": "Para casos de uso: asigna puntaje completo si la respuesta es correcta y bien fundamentada. Descuenta 20-30% por errores menores o falta de precisión.",
            "exigencia": "Mantén estándares académicos serios, pero sé justo con estudiantes que demuestran comprensión básica del tema."
        },
        "Intermedia": {
            "descripcion": "Evaluación con criterio académico elevado. Exige precisión, claridad y fundamentos sólidos en las respuestas.",
            "preguntas_marcar": "Para preguntas marcar: respuesta correcta = puntaje completo, respuesta incorrecta = 0 puntos. No hay puntos parciales.",
            "preguntas_libres": "Para preguntas libres: asigna puntaje completo si la respuesta es correcta y bien fundamentada. Descuenta 40-50% por imprecisiones o falta de profundidad.",
            "casos_uso": "Para casos de uso: asigna puntaje completo si la respuesta es correcta y bien fundamentada. Descuenta 40-50% por imprecisiones o falta de profundidad.",
            "exigencia": "Sé más estricto con la calidad y precisión. Premia la excelencia académica y penaliza respuestas superficiales."
        },
        "Avanzada": {
            "descripcion": "Evaluación con criterio académico de excelencia. Exige dominio completo, análisis profundo y respuestas de alta calidad.",
            "preguntas_marcar": "Para preguntas marcar: respuesta correcta = puntaje completo, respuesta incorrecta = 0 puntos. No hay puntos parciales.",
            "preguntas_libres": "Para preguntas libres: asigna puntaje completo si la respuesta es correcta y bien fundamentada. Descuenta 60-70% por cualquier deficiencia significativa.",
            "casos_uso": "Para casos de uso: asigna puntaje completo si la respuesta es correcta y bien fundamentada. Descuenta 60-70% por cualquier deficiencia significativa.",
            "exigencia": "Aplica criterios de excelencia académica. Solo las respuestas excepcionales merecen puntaje completo."
        }
    }
    
    criterio = criterios_nivel.get(nivel_evaluacion, criterios_nivel["Normal"])

    # Construir listas de texto antes del f-string
    evaluacion_libres = []
    for i, p in enumerate(libres):
        numero = p.get('numero', i+1)
        respuesta = p.get('respuestaAlumno', p.get('respuesta', '')).strip() or 'Vacía'
        puntaje = next((x.get('puntaje', 1.0) for x in plantilla_libres if x.get('numero') == numero), 1.0)
        
        # Obtener texto de la pregunta
        pregunta_data = next((x for x in libres if x.get('numero') == numero), {})
        texto_pregunta = pregunta_data.get('texto', 'Pregunta no encontrada')

        evaluacion_libres.append(f"P{numero}: {texto_pregunta}\nRespuesta del alumno: '{respuesta}' ({puntaje}pts)")

    evaluacion_casos = []
    for i, p in enumerate(casos):
        numero = p.get('numero', i+1)
        respuesta = p.get('respuestaAlumno', p.get('respuesta', '')).strip() or 'Vacía'
        puntaje = next((x.get('puntaje', 1.0) for x in plantilla_casos if x.get('numero') == numero), 1.0)
        
        # Obtener descripción y pregunta del caso
        caso_data = next((x for x in casos if x.get('numero') == numero), {})
        descripcion = caso_data.get('descripcion', 'Caso no encontrado')
        pregunta_caso = caso_data.get('pregunta', '')

        evaluacion_casos.append(f"P{numero}: {descripcion}\nPregunta: {pregunta_caso}\nRespuesta del alumno: '{respuesta}' ({puntaje}pts)")

    return f'''Evalúa el examen como evaluador académico experto con NIVEL DE EVALUACIÓN: {nivel_evaluacion.upper()}

    CRITERIO DE EVALUACIÓN - {nivel_evaluacion.upper()}:
    {criterio["descripcion"]}

    PREGUNTAS MARCAR ({len(marcar)} preguntas, {sum(p.get('puntaje', 1.0) for p in plantilla_marcar)} puntos totales):
    {chr(10).join(evaluacion_marcar)}

    PREGUNTAS LIBRES ({len(libres)} preguntas, {sum(p.get('puntaje', 1.0) for p in plantilla_libres)} puntos totales):
    {chr(10).join(evaluacion_libres)}

    CASOS DE USO ({len(casos)} casos, {sum(p.get('puntaje', 1.0) for p in plantilla_casos)} puntos totales):
    {chr(10).join(evaluacion_casos)}

    REGLAS DE CALIFICACIÓN ESPECÍFICAS:
    - {criterio["preguntas_marcar"]}
    - {criterio["preguntas_libres"]}
    - {criterio["casos_uso"]}

    INSTRUCCIONES DE EXIGENCIA:
    {criterio["exigencia"]}

    IMPORTANTE: 
    - Aplica consistentemente el nivel {nivel_evaluacion.upper()} en toda la evaluación
    - Evalúa basándote en tu conocimiento académico experto
    - Para preguntas de opción múltiple, asigna EXACTAMENTE el puntaje completo asignado si es correcta o 0 puntos si es incorrecta. NO uses puntajes parciales ni decimales intermedios.
    - Justifica mentalmente cada puntaje según el nivel de exigencia requerido
    
    EJEMPLOS DE APLICACIÓN DEL NIVEL {nivel_evaluacion.upper()}:
    - Respuesta excelente y completa = {100 if nivel_evaluacion == "Normal" else 90 if nivel_evaluacion == "Intermedia" else 80}% del puntaje
    - Respuesta buena con errores menores = {80 if nivel_evaluacion == "Normal" else 60 if nivel_evaluacion == "Intermedia" else 40}% del puntaje  
    - Respuesta básica pero correcta = {60 if nivel_evaluacion == "Normal" else 40 if nivel_evaluacion == "Intermedia" else 20}% del puntaje
    - Respuesta incorrecta o vacía = 0% del puntaje

    ¡APLICA ESTRICTAMENTE EL NIVEL {nivel_evaluacion.upper()}!
    
    FORMATO DE RESPUESTA OBLIGATORIO:
    
    TÉRMINOS OBLIGATORIOS PARA PREGUNTAS MARCAR:
    - Para respuesta correcta: usar EXACTAMENTE la palabra "VERDADERA"
    - Para respuesta incorrecta: usar EXACTAMENTE la palabra "FALSA"
    - Ejemplo: "P1: VERDADERA - El alumno seleccionó correctamente..."
    - Ejemplo: "P2: FALSA - El alumno seleccionó incorrectamente..."

    IMPORTANTE: NO uses las palabras "correcta" o "incorrecta", usa únicamente "VERDADERA" o "FALSA".
    
    IMPORTANTE: Separa claramente los tipos de preguntas en los comentarios:

    === COMENTARIOS ===

    **PREGUNTAS MARCAR:**
    ''' + chr(10).join([f"P{p.get('numero')}: VERDADERA/FALSA - [explicación]" for p in marcar]) + f'''

    **PREGUNTAS LIBRES:**
    ''' + chr(10).join([f"P{p.get('numero')}: [explicación y puntaje]" for p in libres]) + f'''

    **CASOS DE USO:**
    ''' + chr(10).join([f"P{p.get('numero')}: [explicación y puntaje]" for p in casos]) + f'''

    === CALIFICACIÓN JSON ===

    IMPORTANTE: Para preguntas_marcar, suma ÚNICAMENTE los puntajes de las preguntas marcadas como VERDADERA.
    - VERDADERA = suma el puntaje asignado a esa pregunta
    - FALSA = NO sumes nada (0 puntos)


    CÁLCULO EXACTO para preguntas_marcar:
    - Cuenta SOLO las preguntas marcadas como VERDADERA
    - Multiplica por el puntaje asignado a cada pregunta VERDADERA
    - FALSA = 0 puntos (no sumes nada)

{{"preguntas_marcar": X, "preguntas_libres": Y, "casos_uso": Z, "casos_de_uso_pdf": 0, "total": T, "porcentaje": P}}

=== CALIFICACIÓN JSON ===
{{"preguntas_marcar": X, "preguntas_libres": Y, "casos_uso": Z, "casos_de_uso_pdf": 0, "total": T, "porcentaje": P}}

    1. PRIMERO proporciona COMENTARIOS DETALLADOS para cada pregunta:
    - Para cada pregunta libre: explica qué evalúas y por qué asignas ese puntaje
    - Para cada caso de uso: explica qué evalúas y por qué asignas ese puntaje
    
    2. DESPUÉS proporciona el JSON de calificación:
    
    EJEMPLO DE FORMATO:
    === COMENTARIOS ===
    P1 (Pregunta Libre): [Tu análisis detallado aquí]
    P2 (Caso de Uso): [Tu análisis detallado aquí]

    === CALIFICACIÓN JSON ===
    {{"preguntas_marcar": X, "preguntas_libres": Y, "casos_uso": Z, "casos_de_uso_pdf": 0, "total": T, "porcentaje": P}}
    
    CÁLCULO DEL PORCENTAJE:
    - Suma todos los puntajes totales: {sum(p.get('puntaje', 1.0) for p in plantilla_marcar) + sum(p.get('puntaje', 1.0) for p in plantilla_libres) + sum(p.get('puntaje', 1.0) for p in plantilla_casos)} puntos
    - Porcentaje = (total_obtenido / {sum(p.get('puntaje', 1.0) for p in plantilla_marcar) + sum(p.get('puntaje', 1.0) for p in plantilla_libres) + sum(p.get('puntaje', 1.0) for p in plantilla_casos)}) * 100
    
    IMPORTANTE: Debes seguir EXACTAMENTE este formato con comentarios + JSON.'''

# ========== FIN DEL PROMT =======================================================================================

# ========== INICIO DEL FUNCION PROMT RUBRICA ==========

def agregar_rubricas_al_prompt(prompt_base, rubricas):
    if not rubricas or not any(rubricas.values()):
        return prompt_base
    
    rubricas_texto = f"""

========== CRITERIOS ADICIONALES DEL PROFESOR ==========

RÚBRICA PREGUNTAS DE MARCAR:
{rubricas.get('preguntasMarcar', 'Usar criterios estándar')}

RÚBRICA PREGUNTAS LIBRES:
{rubricas.get('preguntasLibres', 'Usar criterios estándar')}

RÚBRICA CASOS DE USO:
{rubricas.get('casosUso', 'Usar criterios estándar')}

APLICA ESTOS CRITERIOS JUNTO CON LAS REGLAS ANTERIORES.
========================================================

"""
    
    return prompt_base + rubricas_texto

# ========== FIN DEL FUNCION PROMT RUBRICA ==========


@app.route('/evaluar/<id_examen>/<id_alumno>', methods=['GET', 'POST'])
def evaluar_manual(id_examen, id_alumno):
    if request.method == "POST":
        modelos = request.json.get("modelos")
        etiquetas = request.json.get("etiquetas", {})
        nivel_evaluacion = request.json.get("nivel_evaluacion", "Normal")
        rubricas = request.json.get("rubricas", {})  # ← AGREGAR ESTA LÍNEA RUBRICA  
        
        # Validar nivel de evaluación
        niveles_validos = ["Normal", "Intermedia", "Avanzada"]
        if nivel_evaluacion not in niveles_validos:
            print(f"[WARN] Nivel de evaluación '{nivel_evaluacion}' no válido. Usando 'Normal'")
            nivel_evaluacion = "Normal"
            
        print(f"[INFO] Iniciando evaluación con nivel: {nivel_evaluacion}")
    else:
        modelos = None
        etiquetas = {}
        nivel_evaluacion = "Normal"  # Default para GET requests
    # Validar email del profesor
    email_profesor = request.json.get('email_profesor') if request.method == "POST" else None
    if not email_profesor:
        return jsonify({'error': 'Email profesor requerido'}), 400

    plantilla_pdf_path = None  # Para limpiar en finally
    
    try:
        # --- 1. OBTENER DOCUMENTO DEL EXAMEN DEL ALUMNO ---
        print(f"[INFO] Buscando examen del alumno: Examen ID {id_examen}, Alumno ID {id_alumno} en Colección {COLLECTION_EXAMEN_ALUMNO}")
        res_alumno = db.list_documents(
            database_id=APPWRITE_DB_ID,
            collection_id=COLLECTION_EXAMEN_ALUMNO,
            queries=[
                Query.equal("examen_id", str(id_examen)),
                Query.equal("id_alumno", id_alumno)
            ]
        )

        if not res_alumno['documents']:
            print(f"[ERROR] No se encontró el examen del alumno: Examen ID {id_examen}, Alumno ID {id_alumno}")
            return jsonify({'error': f'No se encontró el examen del alumno {id_alumno} para el examen {id_examen}'}), 404
        
        doc_examen_alumno = res_alumno['documents'][0]
        
        # --- 2. OBTENER ESTRUCTURA COMPLETA DEL EXAMEN ---
        print(f"[INFO] Buscando estructura del examen en colección EXAMEN_PROFESOR_URL")

        res_examen_profesor = db.list_documents(
            database_id=APPWRITE_DB_ID,
            collection_id=APPWRITE_COLLECTION_EXAMEN_PROFESOR_URL,
            queries=[
                Query.equal("id_examen", str(id_examen))
            ]
        )

        if not res_examen_profesor['documents']:
            print(f"[ERROR] No se encontró la estructura del examen {id_examen}")
            return jsonify({'error': f'No se encontró la estructura del examen {id_examen}'}), 404

        doc_examen_profesor = res_examen_profesor['documents'][0]
        # Validar que el email coincide
        if doc_examen_profesor.get('email') != email_profesor:
            return jsonify({'error': 'Sin permisos para este examen'}), 403
                
        # Obtener la estructura completa del examen
        examen_data_json_str = doc_examen_profesor.get('examenDataJson')
        if not examen_data_json_str:
            print(f"[ERROR] No se encontró examenDataJson en el documento")
            return jsonify({'error': f'Estructura del examen no disponible'}), 404
        
        try:
            examen_estructura_completa = json.loads(examen_data_json_str)
            print(f"[INFO] Estructura del examen cargada exitosamente")
        except json.JSONDecodeError as e:
            print(f"[ERROR] Error parseando examenDataJson: {e}")
            return jsonify({'error': f'Error en la estructura del examen'}), 500

        # --- 3. CREAR PLANTILLA JSON ---
        plantilla_json = {
            "preguntas_marcar": [],
            "preguntas_libres": [],
            "casos_uso": []
        }

        # Extraer preguntas marcar con texto y opciones
        if examen_estructura_completa.get('preguntasMarcar'):
            for i, pregunta in enumerate(examen_estructura_completa['preguntasMarcar']):
                plantilla_json["preguntas_marcar"].append({
                    "numero": pregunta.get('numero', i+1),
                    "texto": pregunta.get('texto', ''),
                    "opciones": pregunta.get('opciones', []),
                    "respuestaCorrecta": pregunta.get('respuestaCorrectaIndex', 0),
                    "puntaje": pregunta.get('puntaje', 1.0)
                })

        # Extraer preguntas libres
        if examen_estructura_completa.get('preguntasLibres'):
            for i, pregunta in enumerate(examen_estructura_completa['preguntasLibres']):
                plantilla_json["preguntas_libres"].append({
                    "numero": pregunta.get('numero', i+1),
                    "texto": pregunta.get('texto', ''),
                    "puntaje": pregunta.get('puntaje', 1.0)
                })

        # Extraer casos de uso
        if examen_estructura_completa.get('casosUso'):
            for i, caso in enumerate(examen_estructura_completa['casosUso']):
                plantilla_json["casos_uso"].append({
                    "numero": caso.get('numero', i+1),
                    "descripcion": caso.get('descripcion', ''),
                    "pregunta": caso.get('pregunta', ''),
                    "puntaje": caso.get('puntaje', 1.0)
                })

        print(f"[INFO] Plantilla JSON creada: {len(plantilla_json['preguntas_marcar'])} marcar, {len(plantilla_json['preguntas_libres'])} libres, {len(plantilla_json['casos_uso'])} casos")
        
        # --- 4. DESCARGAR PDF DE PLANTILLA ---
        print(f"[INFO] Buscando plantilla PDF para modelos multimodales")

        archivos_plantilla = storage_appwrite.list_files(
            bucket_id="67e56632000fb32e3ce9"
        )
        
        plantilla_pdf_info = None
        nombre_plantilla_pdf = f"{id_examen}.pdf"
        
        for archivo in archivos_plantilla['files']:
            if archivo['name'] == nombre_plantilla_pdf:
                plantilla_pdf_info = archivo
                print(f"[INFO] Plantilla PDF encontrada: {archivo['name']}")
                break

        if plantilla_pdf_info:
            # Descargar PDF solo si se encontró
            plantilla_pdf_bytes = storage_appwrite.get_file_download(
                bucket_id="67e56632000fb32e3ce9",
                file_id=plantilla_pdf_info['$id']
            )

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_plantilla_file:
                temp_plantilla_file.write(plantilla_pdf_bytes)
                plantilla_pdf_path = temp_plantilla_file.name

            print(f"[INFO] PDF plantilla descargado: {len(plantilla_pdf_bytes)} bytes")
        else:
            print(f"[WARN] No se encontró PDF de plantilla, modelos multimodales pueden fallar")
            plantilla_pdf_path = None        

        # --- 5. PREPARAR DATOS DEL ALUMNO ---
        def _parse_json_field_local(value_str, field_name_debug):
            if value_str is None:
                return []
            elif isinstance(value_str, str):
                try:
                    return json.loads(value_str)
                except json.JSONDecodeError:
                    print(f"[WARN] Campo '{field_name_debug}' no es JSON válido")
                    return []
            elif isinstance(value_str, (list, dict)):
                return value_str
            print(f"[WARN] Campo '{field_name_debug}' tiene tipo inesperado: {type(value_str)}")
            return []

        # Obtener respuestas del alumno
        preguntas_marcar_alumno = _parse_json_field_local(doc_examen_alumno.get('preguntas_marcar'), "preguntas_marcar")
        preguntas_libres_alumno = _parse_json_field_local(doc_examen_alumno.get('preguntas_libres'), "preguntas_libres")
        casos_uso_alumno = _parse_json_field_local(doc_examen_alumno.get('casos_uso'), "casos_uso")

        # COMBINAR datos del alumno con estructura del examen
        alumno_json_para_evaluar = {
            'preguntas_marcar': [],
            'preguntas_libres': [],
            'casos_uso': [],
            'plantilla_json': plantilla_json
        }

        # Combinar preguntas marcar: texto de examen + respuesta de alumno
        for pregunta_estructura in examen_estructura_completa.get('preguntasMarcar', []):
            numero = pregunta_estructura.get('numero')
            respuesta_alumno = next((r.get('respuesta') for r in preguntas_marcar_alumno if r.get('numero') == numero), None)
            
            alumno_json_para_evaluar['preguntas_marcar'].append({
                'numero': numero,
                'texto': pregunta_estructura.get('texto', ''),
                'opciones': pregunta_estructura.get('opciones', []),
                'respuesta': respuesta_alumno
            })

        # Combinar preguntas libres: texto de examen + respuesta de alumno  
        for pregunta_estructura in examen_estructura_completa.get('preguntasLibres', []):
            numero = pregunta_estructura.get('numero')
            respuesta_alumno = next((r.get('respuesta') for r in preguntas_libres_alumno if r.get('numero') == numero), "")
            
            alumno_json_para_evaluar['preguntas_libres'].append({
                'numero': numero,
                'texto': pregunta_estructura.get('texto', ''),
                'respuestaAlumno': respuesta_alumno
            })

        # Combinar casos de uso: texto de examen + respuesta de alumno
        for caso_estructura in examen_estructura_completa.get('casosUso', []):
            numero = caso_estructura.get('numero')
            respuesta_alumno = next((r.get('respuesta') for r in casos_uso_alumno if r.get('numero') == numero), "")
            
            alumno_json_para_evaluar['casos_uso'].append({
                'numero': numero,
                'descripcion': caso_estructura.get('descripcion', ''),
                'pregunta': caso_estructura.get('pregunta', ''),
                'respuestaAlumno': respuesta_alumno
            })

        print(f"[INFO] Datos combinados: {len(alumno_json_para_evaluar['preguntas_marcar'])} marcar, {len(alumno_json_para_evaluar['preguntas_libres'])} libres, {len(alumno_json_para_evaluar['casos_uso'])} casos")        

        # --- 6. LLAMAR A LA EVALUACIÓN ---
        resultado_evaluacion = evaluar_respuestas_multi_modelo(
            alumno_json=alumno_json_para_evaluar,
            pdf_path=plantilla_pdf_path,
            modelos=modelos,
            etiquetas=etiquetas,
            nivel_evaluacion=nivel_evaluacion,
            rubricas=rubricas  # ← AGREGAR ESTA LÍNEA RUBRICAS
        )
        
        if not resultado_evaluacion or "consenso" not in resultado_evaluacion:
            print("[ERROR] La evaluación no devolvió un resultado válido.")
            return jsonify({'error': 'La evaluación no devolvió un resultado válido'}), 500

        print(f"[INFO] Evaluación completada. Consenso: {resultado_evaluacion.get('consenso')}")
        
        # --- 7. GUARDAR EVALUACIÓN POR MODELO ---
        coleccion_resultado_modelo = os.getenv("APPWRITE_GUARDAR_EVALUACION_MODELOS")

        for modelo, respuesta in resultado_evaluacion["detalles"]:
            try:
                data = extraer_y_limpiar_json(respuesta)
                if not data:
                    print(f"[ERROR] No se encontró JSON válido en respuesta del modelo {modelo}")
                    continue
                modelo_id = modelo
                tipo_modelo = "multimodal" if "pdf" in modelo_id.lower() else "texto"
                es_multimodal = tipo_modelo == "multimodal"

                calificacion_total_texto = (
                    float(data.get("preguntas_marcar", 0)) +
                    float(data.get("preguntas_libres", 0)) +
                    float(data.get("casos_uso", 0))
                )
                calificacion_pdf = float(data.get("casos_de_uso_pdf", 0)) if "casos_de_uso_pdf" in data else 0.0
                calificacion_total = calificacion_total_texto + calificacion_pdf
                
                print(f"[DEBUG] Datos a guardar: casos_uso={data.get('casos_uso')}")

                db.create_document(
                    database_id=APPWRITE_DB_ID,
                    collection_id=APPWRITE_GUARDAR_EVALUACION_MODELOS,
                    document_id="unique()",
                    data={
                        "email": email_profesor,  # ← AGREGAR ESTA LÍNEA
                        "id_examen": id_examen,
                        "id_alumno": id_alumno,
                        "nombre_alumno": doc_examen_alumno.get("nombre_alumno", ""),
                        "id_profesor": doc_examen_alumno.get("id_profesor", ""),
                        "nombre_profesor": doc_examen_alumno.get("nombre_profesor", ""),
                        "modelo_id": modelo_id,
                        "tipo_modelo": tipo_modelo,
                        "es_multimodal": es_multimodal,
                        "preguntas_marcar": str(data.get("preguntas_marcar", "0")),
                        "preguntas_libres": str(data.get("preguntas_libres", "0")),
                        "casos_uso": str(data.get("casos_uso", "0")),
                        "casos_uso_pdf": max(1.0, float(data.get("casos_uso_pdf", 0))),
                        "calificacion_total_texto": max(1.0, float(calificacion_total_texto)),
                        "calificacion_pdf": max(1.0, min(1000.0, float(calificacion_pdf))),
                        "calificacion_total": str(calificacion_total),
                        "porcentaje_respuesta": str(data.get("porcentaje", 0)) + "%",
                        "detalle_evaluacion_json": json.dumps(data),
                        "comentarios_detalle": data.get("comentarios_detalle", "[]")
                    }
                )
            except Exception as e_guardado_modelo:
                print(f"[ERROR] No se pudo guardar evaluación del modelo {modelo}: {e_guardado_modelo}")
                
        #=============================================================================================
        # NUEVO: Guardar comentarios completos
        try:
            comentarios_completos = {
                "respuestas_por_modelo": []
            }
            
            for modelo, respuesta in resultado_evaluacion["detalles"]:
                # Reemplazar JSON incorrecto con el corregido
                respuesta_corregida = respuesta
                
                if "=== CALIFICACIÓN JSON ===" in respuesta and not respuesta.startswith("Error:"):
                    # Extraer y validar JSON
                    json_original = extraer_y_limpiar_json(respuesta, alumno_json_para_evaluar.get('plantilla_json'))
                    
                    if json_original:
                        # El JSON ya fue validado y corregido por extraer_y_limpiar_json
                        # Reemplazar en el texto
                        partes = respuesta.split("=== CALIFICACIÓN JSON ===")
                        if len(partes) > 1:
                            respuesta_corregida = partes[0] + "=== CALIFICACIÓN JSON ===\n" + json.dumps(json_original, ensure_ascii=False)
                
                comentarios_completos["respuestas_por_modelo"].append({
                    "modelo": modelo,
                    "respuesta_completa": respuesta_corregida
                })
            
            db.create_document(
                database_id=APPWRITE_DB_ID,
                collection_id=APPWRITE_GUARDAR_COMENTARIOS_EVALUACION,
                document_id="unique()",
                data={
                    "email": email_profesor,  # ← AGREGAR ESTA LÍNEA
                    "id_examen": id_examen,
                    "id_alumno": id_alumno,
                    "modelos_respuestas": json.dumps(comentarios_completos)
                }
            )
            print(f"[INFO] Comentarios completos guardados")
            
        except Exception as e:
            print(f"[WARN] Error guardando comentarios: {e}")        
                
        #=============================================================================================

        # --- 8. RETORNAR RESULTADO ---
        return jsonify({
            'id_examen': id_examen,
            'id_alumno': id_alumno,
            'resultado': resultado_evaluacion
        })

    except Exception as e:
        print(f"[ERROR] Excepción general en evaluar_manual: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Error general en el servidor: {str(e)}'}), 500
    finally:
        if plantilla_pdf_path and os.path.exists(plantilla_pdf_path):
            try:
                os.unlink(plantilla_pdf_path)
                print(f"[INFO] Archivo PDF temporal eliminado: {plantilla_pdf_path}")
            except Exception as e_unlink:
                print(f"[ERROR] No se pudo eliminar el archivo PDF temporal {plantilla_pdf_path}: {e_unlink}")

@app.route('/api/obtener-examenes-evaluacion', methods=['GET'])
def obtener_examenes_evaluacion():
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({"error": "Email requerido"}), 400
        
        # Consultar exámenes evaluados
        evaluados = db.list_documents(
            database_id=APPWRITE_DB_ID,
            collection_id=APPWRITE_PUNTAJE_EVALUACION_EXAMEN,
            queries=[Query.equal("email", email)]
        )
        
        # Consultar exámenes originales
        originales = db.list_documents(
            database_id=APPWRITE_DB_ID,
            collection_id=COLLECTION_EXAMEN_ALUMNO, 
            queries=[Query.equal("email", email)]
        )
        
        return jsonify({
            "documents": evaluados['documents'],
            "documentsOriginal": originales['documents']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Webhook automático ---
@app.route('/webhook/examen-alumno-creado', methods=['POST'])
def webhook_nuevo_examen():
    data = request.json
    id_examen = data.get('examen_id')
    id_alumno = data.get('id_alumno')

    if not id_examen or not id_alumno:
        return jsonify({'error': 'Faltan id_examen o id_alumno'}), 400

    return evaluar_manual(id_examen, id_alumno)

# --- Buscar plantilla por ID examen ---
#def buscar_plantilla_por_id_examen(id_examen):
#    archivos = storage_appwrite.list_files(BUCKET_EXAMEN_GENERADO)
#    for archivo in archivos['files']:
#       if archivo['$id'].startswith(id_examen):
#            return archivo['$id']
#    raise Exception(f"Plantilla no encontrada para examen {id_examen}")


@app.after_request
def cors(response):
    origin = request.headers.get('Origin')
    allowed_origins = ['http://127.0.0.1:8080', 'http://localhost:8080']
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        response.headers.add('Access-Control-Max-Age', '3600')
    return response

@app.route('/submit-plantilla', methods=['POST', 'OPTIONS'])
def submit_plantilla():
    try:
        data = request.get_json()
        email_profesor = data.get("email_profesor")
        if not email_profesor:
            return jsonify({'error': 'Email profesor requerido'}), 400

        id_examen = data.get("id_examen")
        id_profesor = data.get("id_profesor")
        nombre_profesor = data.get("nombre_profesor")

        preguntas_marcar_str = json.dumps(data.get("preguntas_marcar", []))
        preguntas_libres_str = json.dumps(data.get("preguntas_libres", []))
        casos_uso_str = json.dumps(data.get("casos_uso", []))

        document_id = f"plantilla_{id_examen}"

        response = db.create_document(
            database_id=APPWRITE_DB_ID,
            collection_id=COLLECTION_EXAMEN_PLANTILLA,  # ✅ ahora con variable de entorno
            document_id=document_id,
            data={
                "id_examen": id_examen,
                "id_profesor": id_profesor,
                "nombre_profesor": nombre_profesor,
                "preguntas_marcar": preguntas_marcar_str,
                "preguntas_libres": preguntas_libres_str,
                "casos_uso": casos_uso_str
            }
        )

        return jsonify({"status": "ok", "document_id": response["$id"]}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def extraer_y_limpiar_json(respuesta_texto, plantilla_json=None):
    """Extrae y limpia JSON de respuestas de modelos"""
    try:
        # 1. Buscar JSON entre marcadores ```json y ```
        match_json_block = re.search(r'```json\s*(\{.*?\})\s*```', respuesta_texto, re.DOTALL)
        if match_json_block:
            json_text = match_json_block.group(1)
        else:
            # 2. Buscar JSON después de "=== CALIFICACIÓN JSON ==="
            match_calificacion = re.search(r'=== CALIFICACIÓN JSON ===\s*(\{.*?\})', respuesta_texto, re.DOTALL)
            if match_calificacion:
                json_text = match_calificacion.group(1)
            else:
                # 3. Buscar cualquier JSON válido (fallback)
                match_any_json = re.search(r'\{[^{}]*\}', respuesta_texto, re.DOTALL)
                if match_any_json:
                    json_text = match_any_json.group()
                else:
                    return None
        
        # Limpiar y evaluar expresiones matemáticas
        json_text = evaluar_expresiones_matematicas(json_text)
        
        # Parsear JSON
        json_extraido = json.loads(json_text)
        
        # ✅ AGREGAR VALIDACIÓN
        json_validado = validar_y_corregir_json(respuesta_texto, json_extraido, plantilla_json)
        
        # Parsear JSON
        return json_validado
        
    except Exception as e:
        print(f"[ERROR] No se pudo extraer JSON válido: {e}")
        return None

def validar_y_corregir_json(respuesta_texto, json_extraido, plantilla_json=None):
    """Valida que el JSON coincida con los comentarios y corrige inconsistencias"""
    
    if not json_extraido:
        return json_extraido
    if not plantilla_json:          # ← AGREGAR ESTA LÍNEA
        return json_extraido        # ← AGREGAR ESTA LÍNEA  
    
    try:
        
        # ✅ AGREGAR ESTOS DEBUGS:
        print(f"[VALIDACIÓN] 🚀 INICIANDO validación para JSON: {json_extraido}")
        print(f"[VALIDACIÓN] 🔍 Texto de respuesta (primeros 200 chars): {respuesta_texto[:200]}...")
        
        print(f"[VALIDACIÓN] Validando respuesta...")
        
        # Extraer comentarios de preguntas marcar
        comentarios = extraer_comentarios_preguntas_marcar(respuesta_texto)
        
        if comentarios:
            # Contar respuestas correctas/incorrectas según comentarios
            correctas = comentarios['correctas']
            total_comentarios = comentarios['total']
            
            # Calcular puntaje dinámico basado en preguntas correctas específicas
            preguntas_correctas = comentarios.get('preguntas_correctas', [])
            puntaje_calculado = 0.0
            for num_pregunta in preguntas_correctas:
                puntaje_pregunta = next((p.get('puntaje', 1.0) for p in plantilla_json.get('preguntas_marcar', []) if p.get('numero') == num_pregunta), 1.0)
                puntaje_calculado += puntaje_pregunta
            
            print(f"[VALIDACIÓN] Comentarios: {correctas}/{total_comentarios} correctas")
            print(f"[VALIDACIÓN] Puntaje calculado: {puntaje_calculado}")
            print(f"[VALIDACIÓN] JSON original: {json_extraido.get('preguntas_marcar', 0)}")
            
            # Si hay inconsistencia, corregir
            json_original = float(json_extraido.get('preguntas_marcar', 0))
            if abs(json_original - puntaje_calculado) > 0.1:  # Tolerancia de 0.1
                print(f"[VALIDACIÓN] ⚠️ INCONSISTENCIA DETECTADA")
                print(f"[VALIDACIÓN] Corrigiendo: {json_original} → {puntaje_calculado}")
                
                json_extraido['preguntas_marcar'] = puntaje_calculado
                
                # Recalcular total y porcentaje
                nuevo_total = (
                    puntaje_calculado + 
                    float(json_extraido.get('preguntas_libres', 0)) + 
                    float(json_extraido.get('casos_uso', 0))
                )
                json_extraido['total'] = nuevo_total
                
                # Recalcular porcentaje (asumiendo total de 20 puntos)
                puntaje_maximo = sum(p.get('puntaje', 1.0) for p in plantilla_json.get('preguntas_marcar', []))  # Ajustar según tu examen
                puntaje_maximo += sum(p.get('puntaje', 1.0) for p in plantilla_json.get('preguntas_libres', []))
                puntaje_maximo += sum(p.get('puntaje', 1.0) for p in plantilla_json.get('casos_uso', []))
                nuevo_porcentaje = (nuevo_total / puntaje_maximo) * 100
                json_extraido['porcentaje'] = round(nuevo_porcentaje, 2)
                
                print(f"[VALIDACIÓN] ✅ JSON corregido: {json_extraido}")
                
                print(f"[VALIDACIÓN] JSON en respuesta reemplazado")
            else:
                print(f"[VALIDACIÓN] ✅ JSON consistente")
                # AGREGAR:
                print(f"[VALIDACIÓN] 🎯 RETORNANDO JSON final: {json_extraido}")
        
        return json_extraido
        
    except Exception as e:
        print(f"[VALIDACIÓN] ❌ Error en validación: {e}")
        return json_extraido  # Retornar original si falla

def extraer_comentarios_preguntas_marcar(respuesta_texto):
    """Extrae información de comentarios sobre preguntas marcar"""
    try:
        # Buscar sección de comentarios
        comentarios_seccion = ""
        if "=== COMENTARIOS ===" in respuesta_texto:
            comentarios_seccion = respuesta_texto.split("=== COMENTARIOS ===")[1].split("=== CALIFICACIÓN JSON ===")[0]
        elif "#### PREGUNTAS MARCAR:" in respuesta_texto:
            # Formato específico de algunos modelos
            comentarios_seccion = respuesta_texto.split("#### **Preguntas de Marcar")[1].split("####")[0]
        
        if not comentarios_seccion:
            return None
        
        # Contar preguntas correctas e incorrectas
        correctas = 0
        total = 0
        preguntas_correctas = []  # ← AGREGAR ESTA LÍNEA
        
        lineas = comentarios_seccion.split('\n')
        for linea in lineas:
            linea_limpia = linea.strip()
            
            # Buscar patrones de preguntas (P1:, P2:, etc.)
            if ('P' in linea_limpia and ':' in linea_limpia and 
                any(char.isdigit() for char in linea_limpia)):
                
                total += 1
                
                 # ✅ CORRECCIÓN: Verificar PRIMERO si es incorrecta
                # Buscar indicadores de correcta/incorrecta
                match_numero = re.search(r'P(\d+)', linea_limpia)
                if match_numero:
                    numero_pregunta = int(match_numero.group(1))
                    
                    # Buscar indicadores de correcta/incorrecta
                    if any(indicador in linea_limpia.upper() for indicador in ['FALSA', 'INCORRECTA', 'ERRÓNEA', 'MAL', 'WRONG', 'INCORRECTO']):
                        print(f"[VALIDACIÓN] Detectada FALSA: {linea_limpia[:50]}...")
                    elif any(indicador in linea_limpia.upper() for indicador in ['VERDADERA', 'CORRECTA', 'ACERTÓ', 'BIEN', 'CORRECTO', 'TRUE']):
                        correctas += 1
                        preguntas_correctas.append(numero_pregunta)
                        print(f"[VALIDACIÓN] Detectada VERDADERA: {linea_limpia[:50]}...")
        
        return {
            'correctas': correctas,
            'total': total,
            'preguntas_correctas': preguntas_correctas
        }
        
    except Exception as e:
        print(f"[VALIDACIÓN] Error extrayendo comentarios: {e}")
        return None


def evaluar_expresiones_matematicas(json_text):
    """Evalúa expresiones matemáticas simples en JSON"""
    # Buscar patrones como (17.5 / 20) * 100
    patron_expresion = r'\((\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\)\s*\*\s*(\d+(?:\.\d+)?)'
    
    def calcular_expresion(match):
        numerador = float(match.group(1))
        denominador = float(match.group(2))
        multiplicador = float(match.group(3))
        resultado = (numerador / denominador) * multiplicador
        return str(round(resultado, 2))
    
    # Reemplazar expresiones matemáticas con sus resultados
    json_limpio = re.sub(patron_expresion, calcular_expresion, json_text)
    
    return json_limpio


@app.route('/guardar_evaluacion_profesor', methods=['POST'])
def guardar_evaluacion_profesor():
    try:
        data = request.get_json()
        email_profesor = data.get("email_profesor") 
        if not email_profesor:
            return jsonify({'error': 'Email profesor requerido'}), 400

        client = Client()
        client.set_endpoint(os.environ['APPWRITE_ENDPOINT']) \
              .set_project(os.environ['APPWRITE_PROJECT_ID']) \
              .set_key(os.environ['APPWRITE_API_KEY'])    

        databases = Databases(client)
        result = databases.create_document(
            database_id=os.environ['APPWRITE_DATABASE_ID'],
            collection_id=os.environ['APPWRITE_PUNTAJE_EVALUACION_EXAMEN'],
            document_id="unique()",
            data={
                "email": email_profesor,  # ← AGREGAR ESTA LÍNEA
                "id_examen": data["id_examen"],
                "id_alumno": data["id_alumno"],
                "nombre_alumno": data["nombre_alumno"],
                "id_profesor": data["id_profesor"],
                "nombre_profesor": data["nombre_profesor"],
                "preguntas_marcar": data.get("preguntas_marcar", 0),
                "preguntas_libres": data.get("preguntas_libres", 0),
                "casos_uso": data.get("casos_uso", 0),
                "calificacion_total": data["calificacion_total"],
                "prorcentaje_respuesta": data.get("porcentaje_respuesta", "0%"), # Confirma que esta es la clave que envía el frontend
            }
        )
        
        # ✅ AGREGAR ESTA LÍNEA:
        print(f"[DEBUG] Documento creado exitosamente: {result['$id']}")

        return jsonify({"status": "ok", "document_id": result["$id"]}), 200

    except Exception as e:
        # ✅ AGREGAR ESTAS LÍNEAS:
        print(f"[ERROR] Error al crear documento: {e}")
        print(f"[ERROR] Datos que se intentaron guardar: {data}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/enviar_resultado_email', methods=['POST'])
def enviar_resultado_email():
    try:
        data = request.get_json()
        email_profesor = data.get("email_profesor")
        if not email_profesor:
            return jsonify({'error': 'Email profesor requerido'}), 400
        
        # Obtener datos del resultado
        id_examen = data.get('id_examen')
        id_alumno = data.get('id_alumno')
        nombre_alumno = data.get('nombre_alumno')
        calificacion_total = data.get('calificacion_total')
        preguntas_marcar = data.get('preguntas_marcar', 0)
        preguntas_libres = data.get('preguntas_libres', 0)
        casos_uso = data.get('casos_uso', 0)
        
        # Buscar email del alumno en la base de datos
        # Conectar a la colección de datos_alumno para obtener el email
        response_alumno = db.list_documents(
            database_id=APPWRITE_DB_ID,
            collection_id=os.getenv('APPWRITE_COLLECTION_DATOS_ALUMNO'),  # Agregar esta variable
            queries=[
                Query.equal("id_alumno", id_alumno)
            ]
        )
        
        if not response_alumno['documents']:
            return jsonify({'error': 'No se encontró el email del alumno'}), 404
            
        email_alumno = response_alumno['documents'][0].get('email_alumno')
        if not email_alumno:
            return jsonify({'error': 'El alumno no tiene email registrado'}), 404
        
        # Configurar email
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        email_usuario = os.getenv('EMAIL_USUARIO')  # Tu email
        email_password = os.getenv('EMAIL_PASSWORD')  # Tu contraseña de app
        
        # Crear mensaje
        mensaje = MIMEMultipart()
        mensaje['From'] = email_usuario
        mensaje['To'] = email_alumno
        mensaje['Subject'] = f"Resultado Examen {id_examen} - ExamPro"
        
        # Cuerpo del email
        cuerpo = f"""
        Estimado/a {nombre_alumno},
        
        Su resultado del examen {id_examen} ha sido procesado:
        
        📊 CALIFICACIÓN FINAL: {calificacion_total}
        
        📋 DETALLE POR SECCIÓN:
        • Preguntas Marcar: {preguntas_marcar} puntos
        • Preguntas Libres: {preguntas_libres} puntos  
        • Casos de Uso: {casos_uso} puntos
        
        ¡Felicitaciones por completar el examen!
        
        Saludos cordiales,
        Sistema ExamPro
        """
        
        mensaje.attach(MIMEText(cuerpo, 'plain'))
        
        # Enviar email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_usuario, email_password)
            server.send_message(mensaje)
        
        return jsonify({"status": "enviado", "email_destino": email_alumno})
        
    except Exception as e:
        print(f"[ERROR] Error enviando email: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/comentarios/<id_examen>/<id_alumno>', methods=['GET'])
def obtener_comentarios(id_examen, id_alumno):
    try:
        email_profesor = request.args.get('email_profesor')
        if not email_profesor:
            return jsonify({'error': 'Email profesor requerido'}), 400
            
        response = db.list_documents(
            database_id=APPWRITE_DB_ID,
            collection_id=APPWRITE_GUARDAR_COMENTARIOS_EVALUACION,
            queries=[
                Query.equal("id_examen", id_examen),
                Query.equal("id_alumno", id_alumno),
                Query.equal("email", email_profesor)
            ]
        )
        
        if response['documents']:
            # Ordenar por fecha de creación (más reciente primero)
            documento_mas_reciente = sorted(response['documents'], key=lambda x: x['$createdAt'], reverse=True)[0]
            comentarios = json.loads(documento_mas_reciente['modelos_respuestas'])
            return jsonify({"comentarios": comentarios})
        else:
            return jsonify({"comentarios": None}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500    

@app.route('/', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path=None):
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, port=5001)
