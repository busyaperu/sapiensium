from appwrite.client import Client
from appwrite.services.databases import Databases
import os
from dotenv import load_dotenv

load_dotenv()

client = Client()
client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PAGOS_OPERACIONES_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_PAGOS_OPERACIONES_API_KEY'))

databases = Databases(client)
DATABASE_ID = os.getenv('APPWRITE_COMPRA_CREDITOS_DATABASE_ID')

# Test crear documento simple
try:
    print("Probando crear documento...")
    test_doc = databases.create_document(
        DATABASE_ID,
        '68c19ba15c0d1a8461b3',
        'unique()',
        {
            'email': 'test@test.com',
            'saldo_actual': 12000
        }
    )
    print("Documento creado exitosamente")
except Exception as e:
    print(f"Error creando documento: {e}")