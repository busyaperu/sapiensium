from flask import Flask, jsonify
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


@app.route('/api/together-dashboard', methods=['GET'])
def get_together_dashboard():
    try:
        result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=os.getenv('APPWRITE_TRANSACCIONES_COLLECTION_ID')
        )
        
        print(f"Documentos encontrados: {len(result['documents'])}")
        for doc in result['documents']:
            print(f"Documento: {doc}")
        
        fondos_disponibles = 0
        transacciones_procesadas = 0
        fondos_history = []
        
        for doc in result['documents']:
            amount = float(doc.get('monto', 0))
            fondos_disponibles += amount
            transacciones_procesadas += 1
            

            # Agregar al historial
            fondos_history.append({
                'id': f"fund_{doc.get('$id', '')[:8]}",
                'source': doc.get('email_id', 'N/A'),
                'amount': amount,
                'status': 'available',
                'created': doc.get('$createdAt', ''),
                'notes': f"Generado desde pago ${amount} de {doc.get('customerEmail', 'usuario')}"
            })
        
        return jsonify({
            'fondos_disponibles': fondos_disponibles,
            'transacciones_procesadas': transacciones_procesadas,
            'tasa_conversion': 20.0,
            'ready_for_purchase': fondos_disponibles >= 4.00,
            'fondos_history': fondos_history[:10]  # Últimos 10
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500    

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5003)