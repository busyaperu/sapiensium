from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.query import Query
import time

load_dotenv()

app = Flask(__name__)
CORS(app, origins="*")

# Configuración Appwrite
client = Client()
client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_API_KEY'))

databases = Databases(client)

APPWRITE_DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
APPWRITE_COLLECTION_CONFIGURACION_EXAMENES = os.getenv('APPWRITE_COLLECTION_CONFIGURACION_EXAMENES')
APPWRITE_COLLECTION_ASISTENCIA_EXAMENES = os.getenv('APPWRITE_COLLECTION_ASISTENCIA_EXAMENES')

@app.route('/api/guardar-configuracion-examen', methods=['POST'])
def guardar_configuracion_examen():
    try:
        data = request.get_json()
        
        # Campos requeridos
        required_fields = ['id_examen', 'nombre_profesor', 'id_profesor', 'url_examen']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Crear documento de configuración
        configuracion = {
            'id_examen': data['id_examen'],
            'nombre_profesor': data['nombre_profesor'],
            'id_profesor': data['id_profesor'],
            'fecha_examen': data.get('fecha_examen', ''),
            'url_examen': data['url_examen'],
            'timestamp_configuracion': time.strftime('%Y-%m-%d %H:%M:%S'),
            'activo': True
        }
        
        # Guardar en Appwrite
        resultado = databases.create_document(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_CONFIGURACION_EXAMENES,
            document_id=ID.unique(),
            data=configuracion
        )
        
        return jsonify({
            'success': True,
            'message': 'Configuración guardada exitosamente',
            'document_id': resultado['$id']
        }), 201
        
    except Exception as e:
        print(f"Error guardando configuración: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/obtener-configuracion-examen', methods=['GET'])
def obtener_configuracion_examen():
    try:
        url_examen = request.args.get('url_examen')
        
        if not url_examen:
            return jsonify({'error': 'URL del examen requerida'}), 400
        
        response = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_CONFIGURACION_EXAMENES,
            queries=[
                Query.equal('url_examen', url_examen),
                Query.equal('activo', True)
            ]
        )
        
        if response['documents']:
            configuracion = response['documents'][0]
            return jsonify({
                'success': True,
                'configuracion': configuracion
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No se encontró configuración'
            }), 404
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Error interno'}), 500

@app.route('/api/registrar-asistencia', methods=['POST'])
def registrar_asistencia():
    try:
        data = request.get_json()
        
        # Datos requeridos
        required_fields = ['nombre_alumno', 'id_alumno', 'email_alumno', 'curso', 
                          'institucion', 'nombre_profesor', 'id_profesor', 
                          'id_examen', 'fecha_examen', 'url_examen']
        
        # Validar campos requeridos
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Crear documento de asistencia
        documento_asistencia = {
            'nombre_alumno': data['nombre_alumno'],
            'id_alumno': data['id_alumno'],
            'email_alumno': data['email_alumno'],
            'curso': data['curso'],
            'institucion': data['institucion'],
            'nombre_profesor': data['nombre_profesor'],
            'id_profesor': data['id_profesor'],
            'id_examen': data['id_examen'],
            'fecha_examen': data['fecha_examen'],
            'url_examen': data['url_examen'],
            'timestamp_ingreso': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Guardar en Appwrite
        resultado = databases.create_document(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_ASISTENCIA_EXAMENES,
            document_id=ID.unique(),
            data=documento_asistencia
        )
        
        return jsonify({
            'success': True, 
            'message': 'Asistencia registrada exitosamente',
            'document_id': resultado['$id']
        }), 201
        
    except Exception as e:
        print(f"Error registrando asistencia: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/examen-actual', methods=['GET'])
def examen_actual():
    try:
        email_profesor = request.args.get('email_profesor')
        if not email_profesor:
            return jsonify({'error': 'Email del profesor requerido'}), 400
        
        response = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_CONFIGURACION_EXAMENES,
            queries=[
                Query.equal('id_profesor', email_profesor),
                Query.equal('activo', True)
            ]
        )
        
        if response['documents']:
            examen = response['documents'][0]
            return jsonify({'examen': examen}), 200
        else:
            return jsonify({'examen': None}), 200
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Error interno'}), 500
    
@app.route('/publicar-examen', methods=['POST'])
def publicar_examen():
    try:
        data = request.get_json()
        email_profesor = data.get('email_profesor')
        
        if not email_profesor:
            return jsonify({'error': 'Email del profesor requerido'}), 400
        
        documento_examen = {
            'email_profesor': email_profesor,
            'nombre_examen': data.get('nombre_examen'),
            'id_examen': data.get('id_examen'),
            'url_examen': data.get('url_examen'),
            'curso': data.get('curso'),
            'fecha_limite': data.get('fecha_limite'),
            'institucion': data.get('institucion'),
            'activo': True,
            'timestamp_publicacion': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        resultado = databases.create_document(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_CONFIGURACION_EXAMENES,
            document_id=ID.unique(),
            data=documento_examen
        )
        
        return jsonify({'success': True, 'message': 'Examen publicado exitosamente'}), 201
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    
@app.route('/despublicar-examen', methods=['POST'])
def despublicar_examen():
    try:
        data = request.get_json()
        email_profesor = data.get('email_profesor')
        
        if not email_profesor:
            return jsonify({'error': 'Email del profesor requerido'}), 400
        
        response = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_CONFIGURACION_EXAMENES,
            queries=[
                Query.equal('email_profesor', email_profesor),
                Query.equal('activo', True)
            ]
        )
        
        if response['documents']:
            examen = response['documents'][0]
            databases.update_document(
                database_id=APPWRITE_DATABASE_ID,
                collection_id=APPWRITE_COLLECTION_CONFIGURACION_EXAMENES,
                document_id=examen['$id'],
                data={'activo': False, 'timestamp_despublicacion': time.strftime('%Y-%m-%d %H:%M:%S')}
            )
            return jsonify({'success': True, 'message': 'Examen despublicado exitosamente'}), 200
        else:
            return jsonify({'error': 'No se encontró examen activo'}), 404
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500            

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)