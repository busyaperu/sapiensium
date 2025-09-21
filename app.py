from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import os
import random
#from google.oauth2 import service_account
#from googleapiclient.discovery import build
import requests
import uuid
from datetime import datetime
import io
import re
import json
import flask
import base64

# Para PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Para Word
from docx import Document


# Configuración de la aplicación
#config = rx.Config(
#    app_name="exam_app",
#    db_url="postgresql://user:password@neon-db-url/exam_db",
#    api_url="/api",
#    env=rx.Env.DEV,
#    frontend_port=3000,
#    backend_port=8000,
#)

# Crear la aplicación
#app = rx.App(
#    stylesheets=[
#        "/css/styles.css",
#    ],
#    theme=rx.theme(
#        primary_color="blue",
#        font_family="Inter, sans-serif",
#    ),
#)

# Añadir páginas a la aplicación
#app.add_page(index.index, route="/")
#app.add_page(profesor.profesor, route="/profesor")
#app.add_page(alumno.alumno, route="/alumno")
#app.add_page(examen.examen, route="/examen")
#app.add_page(cargar.cargar, route="/cargar")
#app.add_page(evaluacion.evaluacion, route="/evaluacion")

# Compilar la aplicación
#app.compile()


app = Flask(__name__)

#SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
#SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')

#credentials = service_account.Credentials.from_service_account_file(
#    SERVICE_ACCOUNT_FILE, scopes=SCOPES
#)


# Para servir la página del generador de exámenes
@app.route('/generador_examenes.html')
def generador_examenes():
    return render_template('generador_examenes.html', 
                           toguether_ia_api_key_llama90=os.getenv("TOGUETHER_IA_API_KEY_LLAMA90"),
                           google_search_api_key=os.getenv("GOOGLE_SEARCH_API_KEY"),
                           google_cx=os.getenv("GOOGLE_CUSTOM_SEARCH_ID"))


@app.route('/api/generar-examen', methods=['POST'])
def generar_examen_ia():
    from flask import request as flask_request, jsonify as flask_jsonify
    try:
        data = flask_request.json
        prompt = data.get('prompt')
        tipo_pregunta = data.get('tipo_pregunta')
       
        
        num_opcion_multiple = data.get('num_opcion_multiple', 10)  # Valor predeterminado 10
        num_abiertas = data.get('num_abiertas', 3)                # Valor predeterminado 3
        num_casos_uso = data.get('num_casos_uso', 2)              # Valor predeterminado 2
        
        if not prompt:
            return flask_jsonify({"error": "Se requiere prompt y tipo de pregunta"}), 400
            
        api_key = os.getenv("DEEPSEEKV3_API_KEY")
        
        if not api_key:
            return jsonify({"error": "API key no configurada"}), 500
        
        # Definir prompts específicos según el tipo de pregunta
        prompts_por_tipo = {
            'opcion_multiple': f"""
                Genera EXACTAMENTE {num_opcion_multiple} preguntas de opción múltiple sobre {prompt} con la siguiente estructura:
                
                - Cada pregunta debe tener un número (1-15)
                - Exactamente 4 opciones por pregunta etiquetadas usando SOLO este formato preciso:
                  A) Primera opción
                  B) Segunda opción
                  C) Tercera opción
                  D) Cuarta opción
                
                RESTRICCIONES CRÍTICAS:
                - NO generes más ni menos de 15 preguntas
                - NO agregues explicaciones adicionales
                - Asegúrate de que las preguntas sean claras y concisas
                - NO incluyas la respuesta correcta marcada
            """,
            
            'abierta': f"""
                Genera EXACTAMENTE {num_abiertas} preguntas abiertas (de desarrollo) sobre {prompt} con la siguiente estructura:
                
                - Cada pregunta debe tener un número (1-5)
                - Las preguntas deben requerir respuestas desarrolladas
                - Nivel de dificultad variado (básico, intermedio, avanzado)
                
                RESTRICCIONES CRÍTICAS:
                - NO generes más ni menos de 5 preguntas
                - NO agregues explicaciones adicionales
                - Asegúrate de que las preguntas sean claras y requieran análisis
            """,
            
            'caso_uso': f"""
                Genera EXACTAMENTE {num_casos_uso} casos de uso prácticos sobre {prompt} con la siguiente estructura:
                
                - Cada caso debe tener un número (1-5)
                - Incluye un escenario práctico relacionado con {prompt}
                - Requisitos específicos de lo que debe implementar el estudiante
                - Sugerencias de herramientas o enfoques que podría utilizar
                
                RESTRICCIONES CRÍTICAS:
                - NO generes más ni menos de 5 casos de uso
                - NO agregues explicaciones adicionales
                - Asegúrate de que los casos sean relevantes y realistas
            """
        }
        
        # Seleccionar el prompt adecuado según el tipo
        prompt_completo = prompts_por_tipo.get(tipo_pregunta)
        
        if not prompt_completo:
            return flask_jsonify({"error": "Tipo de pregunta no válido"}), 400
        
        url = "https://api.together.xyz/v1/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "prompt": prompt_completo,
            "max_tokens": 10000,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        contenido_raw = result["choices"][0]["text"] if "choices" in result and result["choices"] else ""
        
        # Procesar el contenido para estructurarlo mejor
        examen_estructurado = procesar_examen(contenido_raw)
        
        # Generar ID único para el examen
        examen_id = str(uuid.uuid4())[:8]
        
        return jsonify({
            "examen": True, 
            "examenId": examen_id,
            "contenido": contenido_raw,
            "examen_estructurado": examen_estructurado,
            "titulo": examen_estructurado.get("titulo", "Examen Generado")
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return flask_jsonify({"error": str(e)}), 500
    


# Endpoint para obtener el examen para el alumno
@app.route('/api/examenes/<int:examen_id>/vista-alumno', methods=['GET'])
def obtener_examen_vista_alumno(examen_id):
    # En una implementación real, buscarías el examen en la base de datos
    # Para este ejemplo, usamos datos de prueba
    examen = {
        'id': examen_id,
        'titulo': 'Examen de Ingeniería de Software',
        'fecha': datetime.now().strftime('%d/%m/%Y'),
        'preguntas': [
            {
                'id': 1,
                'tipo': 'abierta',
                'texto': 'Explique el concepto de encapsulamiento en programación orientada a objetos y proporcione un ejemplo práctico.',
                'puntos': 10
            },
            {
                'id': 2,
                'tipo': 'opcion_multiple',
                'texto': '¿Cuál de los siguientes patrones de diseño se utiliza para crear objetos sin especificar la clase exacta del objeto?',
                'opciones': [
                    'A) Singleton',
                    'B) Factory Method',
                    'C) Observer',
                    'D) Decorator',
                    'E) Adapter'
                ],
                'puntos': 5
            }
        ]
    }
    
    return jsonify(examen)

# Endpoint para guardar las respuestas del alumno
@app.route('/api/examenes/<int:examen_id>/respuestas', methods=['POST'])
def guardar_respuestas_alumno(examen_id):
    respuestas = request.json.get('respuestas', [])
    nombre_estudiante = request.json.get('nombre_estudiante', 'Estudiante')
    
    # En una implementación real, guardarías estas respuestas en la base de datos
    # y las asociarías con el examen y el estudiante
    
    return jsonify({
        'mensaje': 'Respuestas guardadas correctamente',
        'examen_id': examen_id,
        'respuestas': respuestas,
        'nombre_estudiante': nombre_estudiante
    })

# Endpoint para exportar el examen a PDF
@app.route('/api/examenes/<int:examen_id>/exportar-pdf', methods=['POST'])
def exportar_examen_pdf(examen_id):
    # Obtener datos del examen y respuestas
    datos_examen = request.json
    
    # En una implementación real, buscarías el examen en la base de datos
    examen = {
        'id': examen_id,
        'titulo': 'Examen de Ingeniería de Software',
        'fecha': datetime.now().strftime('%d/%m/%Y'),
        'preguntas': [
            {
                'id': 1,
                'tipo': 'abierta',
                'texto': 'Explique el concepto de encapsulamiento en programación orientada a objetos y proporcione un ejemplo práctico.',
                'puntos': 10
            },
            {
                'id': 2,
                'tipo': 'opcion_multiple',
                'texto': '¿Cuál de los siguientes patrones de diseño se utiliza para crear objetos sin especificar la clase exacta del objeto?',
                'opciones': [
                    'A) Singleton',
                    'B) Factory Method',
                    'C) Observer',
                    'D) Decorator',
                    'E) Adapter'
                ],
                'puntos': 5
            }
        ]
    }
    
    # Combinar examen con respuestas
    for pregunta in examen['preguntas']:
        for respuesta in datos_examen.get('respuestas', []):
            if pregunta['id'] == respuesta.get('numero'):
                pregunta['respuesta'] = respuesta.get('respuesta')
    
    # Generar HTML para el PDF
    html_content = generar_html_examen(examen, datos_examen.get('nombre_estudiante', 'Estudiante'))
    
    # Ruta temporal para el archivo PDF
    temp_pdf_path = os.path.join(os.path.dirname(__file__), 'temp', f'examen_{examen_id}.pdf')
    os.makedirs(os.path.dirname(temp_pdf_path), exist_ok=True)
    
    # Generar PDF a partir del HTML
    pdfkit.from_string(html_content, temp_pdf_path)
    
    # Enviar el archivo al cliente
    return send_file(
        temp_pdf_path,
        as_attachment=True,
        download_name=f"Examen_{examen['titulo'].replace(' ', '_')}.pdf",
        mimetype='application/pdf'
    )

# Función auxiliar para generar el HTML del examen
def generar_html_examen(examen, nombre_estudiante):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{examen['titulo']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
            .pregunta {{ margin-bottom: 30px; border-left: 4px solid #007bff; padding-left: 15px; }}
            .pregunta-numero {{ font-weight: bold; }}
            .pregunta-texto {{ margin-bottom: 10px; }}
            .opciones {{ margin-left: 20px; }}
            .respuesta-abierta {{ margin-top: 10px; min-height: 100px; border: 1px solid #ccc; padding: 10px; }}
            .footer {{ margin-top: 50px; text-align: center; font-size: 0.8em; color: #666; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{examen['titulo']}</h1>
            <div>
                <p><strong>Fecha:</strong> {examen['fecha']}</p>
                <p><strong>Estudiante:</strong> {nombre_estudiante}</p>
            </div>
        </div>
        
        <div class="contenido">
    """
    
    for pregunta in examen['preguntas']:
        html += f"""
        <div class="pregunta">
            <div class="pregunta-header">
                <h3 class="pregunta-numero">{pregunta['id']}</h3>
                <span class="pregunta-puntos">{pregunta['puntos']} puntos</span>
            </div>
            <div class="pregunta-texto">{pregunta['texto']}</div>
        """
        
        if pregunta['tipo'] == 'opcion_multiple':
            html += '<div class="opciones">'
            for i, opcion in enumerate(pregunta['opciones']):
                checked = 'checked' if pregunta.get('respuesta') == i else ''
                html += f"""
                <div class="opcion">
                    <input type="radio" {checked} disabled> {opcion}
                </div>
                """
            html += '</div>'
        elif pregunta['tipo'] == 'abierta':
            respuesta = pregunta.get('respuesta', '')
            html += f"""
            <div class="respuesta-abierta">
                {respuesta}
            </div>
            """
        
        html += '</div>'
    
    html += """
        </div>
        
        <div class="footer">
            <p>Este documento es confidencial y contiene las respuestas oficiales del examen.</p>
        </div>
    </body>
    </html>
    """
    
    return html



# Endpoint para finalizar el examen
@app.route('/api/examenes/<int:examen_id>/finalizar', methods=['POST'])
def finalizar_examen(examen_id):
    # En una implementación real, marcarías el examen como completado en la base de datos
    
    return jsonify({
        'mensaje': 'Examen finalizado correctamente',
        'examen_id': examen_id
    })

def procesar_examen(contenido):
    """Procesa el contenido del examen para estructurarlo"""
    lineas = contenido.split('\n')
    examen = {
        "titulo": "",
        "preguntas": []
    }
    
    # Extraer título
    for linea in lineas[:5]:
        if linea.strip() and not linea.startswith(('#', '1.', '1)', 'Pregunta')):
            examen["titulo"] = linea.strip()
            break
    
    # Extraer preguntas
    pregunta_actual = None
    opciones = []
    
    for linea in lineas:
        # Detectar nueva pregunta
        if re.match(r'^\d+[\.\)]', linea) or linea.lower().startswith('pregunta'):
            # Guardar pregunta anterior si existe
            if pregunta_actual:
                pregunta_actual["opciones"] = opciones
                examen["preguntas"].append(pregunta_actual)
                opciones = []
            
            # Extraer número y texto de la pregunta
            match = re.match(r'^\d+[\.\)]', linea)
            if match:
                num = match.group(0)
                texto = linea[len(num):].strip()
            else:
                partes = linea.split(' ', 1)
                num = "1"
                texto = partes[1] if len(partes) > 1 else linea
            
            # Determinar tipo (por defecto abierta)
            tipo = "abierta"
            nivel = "Intermedio"
            puntos = 10
            
            # Buscar en las siguientes líneas información sobre tipo/nivel/puntos
            for i in range(lineas.index(linea)+1, min(lineas.index(linea)+5, len(lineas))):
                if i < len(lineas):
                    if "básico" in lineas[i].lower() or "basico" in lineas[i].lower():
                        nivel = "Básico"
                    elif "intermedio" in lineas[i].lower():
                        nivel = "Intermedio"
                    elif "avanzado" in lineas[i].lower():
                        nivel = "Avanzado"
                    
                    if "punto" in lineas[i].lower():
                        match = re.search(r'(\d+)\s*punto', lineas[i].lower())
                        if match:
                            puntos = int(match.group(1))
            
            pregunta_actual = {
                "numero": num.rstrip('.):'),
                "texto": texto,
                "tipo": tipo,
                "nivel": nivel,
                "puntos": puntos
            }
        
        # Detectar opciones de respuesta
        elif re.match(r'^[A-Da-d][\.\)]\s', linea):
            tipo = "opcion_multiple"
            if pregunta_actual:
                pregunta_actual["tipo"] = tipo
                opciones.append(linea.strip())
    
    # Añadir la última pregunta
    if pregunta_actual:
        pregunta_actual["opciones"] = opciones
        examen["preguntas"].append(pregunta_actual)
    
    return examen
    
    

@app.route('/generador/vista-estudiante/<examen_id>')
def vista_estudiante(examen_id):
    # Recuperar datos del examen
    return render_template('vista_estudiante.html', examen_id=examen_id)

@app.route('/generador/subir-examen-alumno')
def subir_examen_alumno():
    return render_template('subir_examen_alumno.html')

@app.route('/generador/procesando-examen/<examen_id>')
def procesando_examen(examen_id):
    return render_template('procesando_examen.html', examen_id=examen_id)  

@app.route('/evaluaciones.html')
def evaluaciones():
    return render_template('evaluaciones.html')

@app.route('/resultados.html')
def resultados():
    return render_template('resultados.html')



# API para generar exámenes con AI
#@app.route('/crear_examen_ai', methods=['POST'])
#def crear_examen_ai():
#    prompt_usuario = request.json.get('prompt', '')
#    if not prompt_usuario:
#        return jsonify({"error": "Se requiere un prompt para generar el examen"}), 400
    
#    preguntas = buscar_y_generar_examen(prompt_usuario)
#    return jsonify({"examen": preguntas})

# Rutas existentes
#@app.route('/crear_examen', methods=['GET'])
#def crear_examen():
    # Si quieres mantener la funcionalidad para generar examen como API
#    if request.headers.get('Accept') == 'application/json':
#        examen = generar_examen()
#        return jsonify(examen)
    # Si es una solicitud normal del navegador, renderiza la plantilla
#    return render_template('generador_examenes.html')


if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)

