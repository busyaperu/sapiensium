from flask import Flask, request, jsonify
from flask_cors import CORS
from appwrite.client import Client
from appwrite.services.databases import Databases
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración Appwrite
client = Client()
client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PAGOS_OPERACIONES_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_PAGOS_OPERACIONES_API_KEY'))

databases = Databases(client)
DATABASE_ID = os.getenv('APPWRITE_COMPRA_CREDITOS_DATABASE_ID')

@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    """Obtener lista completa de usuarios con créditos y pagos"""
    try:
        # Obtener usuarios de créditos
        usuarios_result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=os.getenv('APPWRITE_USUARIOS_CREDITOS_COLLECTION_ID')
        )
        
        usuarios_completos = []
        for usuario in usuarios_result['documents']:
            # Obtener transacciones del usuario
            transacciones_result = databases.list_documents(
                database_id=DATABASE_ID,
                collection_id=os.getenv('APPWRITE_TRANSACCIONES_COLLECTION_ID')
            )
            
            # Filtrar transacciones del usuario actual
            transacciones_usuario = [t for t in transacciones_result['documents'] 
                                   if t.get('email') == usuario.get('email')]
            
            usuario_completo = {
                'email': usuario.get('email'),
                'saldo_actual': usuario.get('saldo_actual', 0),
                'limite_mensual': usuario.get('limite_mensual', 12000),
                'fecha_renovacion': usuario.get('fecha_renovacion'),
                'tipo_cuenta': usuario.get('tipo_cuenta', 'individual'),
                'empresa_nombre': usuario.get('empresa_nombre', ''),
                'creditos_usados': usuario.get('limite_mensual', 12000) - usuario.get('saldo_actual', 0),
                'total_transacciones': len(transacciones_usuario),
                'ultima_actividad': max([t.get('$createdAt', '') for t in transacciones_usuario]) if transacciones_usuario else None,
                'estado': 'activo' if usuario.get('saldo_actual', 0) > 0 else 'inactivo'
            }
            usuarios_completos.append(usuario_completo)
        
        return jsonify({
            'usuarios': usuarios_completos,
            'total': len(usuarios_completos),
            'activos': len([u for u in usuarios_completos if u['estado'] == 'activo']),
            'inactivos': len([u for u in usuarios_completos if u['estado'] == 'inactivo'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuario/<email>/historial', methods=['GET'])
def get_historial_usuario(email):
    """Obtener historial completo de un usuario"""
    try:
        # Obtener transacciones del usuario
        transacciones_result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=os.getenv('APPWRITE_TRANSACCIONES_COLLECTION_ID')
        )
        
        transacciones_usuario = [t for t in transacciones_result['documents'] 
                               if t.get('email') == email]
        
        # Obtener evaluaciones del usuario
        evaluaciones_result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=os.getenv('APPWRITE_EVALUACIONES_COLLECTION_ID')
        )
        
        evaluaciones_usuario = [e for e in evaluaciones_result['documents'] 
                              if e.get('email') == email]
        
        return jsonify({
            'email': email,
            'transacciones': transacciones_usuario,
            'evaluaciones': evaluaciones_usuario,
            'total_transacciones': len(transacciones_usuario),
            'total_evaluaciones': len(evaluaciones_usuario)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5004)