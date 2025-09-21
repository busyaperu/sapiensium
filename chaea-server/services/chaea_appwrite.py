from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException
from config import Config
import uuid
from datetime import datetime

class CHAEAAppwriteService:
    def __init__(self):
        self.client = Client()
        self.client.set_endpoint(Config.APPWRITE_ENDPOINT)
        self.client.set_project(Config.APPWRITE_CHAEA_PROJECT_ID)
        self.client.set_key(Config.APPWRITE_CHAEA_API_KEY)
        self.databases = Databases(self.client)
    
    def save_consent(self, user_id, course_id, consent_given):
        try:
            data = {
                'userId': user_id,
                'courseId': course_id,
                'consentGiven': consent_given,
                'consentDate': datetime.now().isoformat(),
                'consentWithdrawn': False
            }
            
            result = self.databases.create_document(
                database_id=Config.APPWRITE_CHAEA_DATABASE_ID,
                collection_id=Config.APPWRITE_USER_CONSENTS_COLLECTION_ID,
                document_id=str(uuid.uuid4()),
                data=data
            )
            return result
        except AppwriteException as e:
            raise Exception(f"Error saving consent: {e}")
    
    def get_consent(self, user_id, course_id):
        try:
            from appwrite.query import Query
            result = self.databases.list_documents(
                database_id=Config.APPWRITE_CHAEA_DATABASE_ID,
                collection_id=Config.APPWRITE_USER_CONSENTS_COLLECTION_ID,
                queries=[
                    Query.equal('userId', user_id),
                    Query.equal('courseId', course_id),
                    Query.equal('consentWithdrawn', False)
                ]
            )
            return result['documents'][0] if result['documents'] else None
        except AppwriteException as e:
            return None

    def save_chaea_responses(self, user_id, course_id, session_id, responses):
        try:
            # Guardar cada respuesta individual
            for i, response in enumerate(responses):
                data = {
                    'userId': user_id,
                    'sessionId': session_id,
                    'questionNumber': i + 1,
                    'response': response,
                    'timestamp': datetime.now().isoformat(),
                    'courseId': course_id
                }
                
                self.databases.create_document(
                    database_id=Config.APPWRITE_CHAEA_DATABASE_ID,
                    collection_id=Config.APPWRITE_CHAEA_RESPONSES_COLLECTION_ID,
                    document_id=str(uuid.uuid4()),
                    data=data
                )
            return True
        except AppwriteException as e:
            raise Exception(f"Error saving CHAEA responses: {e}")

    def save_chaea_profile(self, user_id, course_id, scores):
        try:
            data = {
                'userId': user_id,
                'courseId': course_id,
                'activeScore': scores['activeScore'],
                'reflectiveScore': scores['reflectiveScore'],
                'theoreticalScore': scores['theoreticalScore'],
                'pragmaticScore': scores['pragmaticScore'],
                'primaryStyle': scores['primaryStyle'],
                'secondaryStyle': scores['secondaryStyle'],
                'profileDate': datetime.now().isoformat(),
                'isActive': True
            }
            
            result = self.databases.create_document(
                database_id=Config.APPWRITE_CHAEA_DATABASE_ID,
                collection_id=Config.APPWRITE_CHAEA_PROFILES_COLLECTION_ID,
                document_id=str(uuid.uuid4()),
                data=data
            )
            return result
        except AppwriteException as e:
            raise Exception(f"Error saving CHAEA profile: {e}")
        
    def get_chaea_profile(self, user_id, course_id):
        try:
            from appwrite.query import Query
            result = self.databases.list_documents(
                database_id=Config.APPWRITE_CHAEA_DATABASE_ID,
                collection_id=Config.APPWRITE_CHAEA_PROFILES_COLLECTION_ID,
                queries=[
                    Query.equal('userId', user_id),
                    Query.equal('courseId', course_id),
                    Query.equal('isActive', True)
                ]
            )
            return result['documents'][0] if result['documents'] else None
        except AppwriteException as e:
            return None

    def save_adaptive_evaluation(self, course_id, topic, bloom_level, variants, created_by):
        try:
            import json  # Agregar esta línea
            data = {
                'courseId': course_id,
                'topic': topic,
                'bloomLevel': bloom_level,
                'activeVariant': json.dumps(variants['activeVariant']),        # Convertir a string
                'reflectiveVariant': json.dumps(variants['reflectiveVariant']), # Convertir a string
                'theoreticalVariant': json.dumps(variants['theoreticalVariant']), # Convertir a string
                'pragmaticVariant': json.dumps(variants['pragmaticVariant']),   # Convertir a string
                'createdBy': created_by,
                'createdAt': datetime.now().isoformat()
            }
            
            result = self.databases.create_document(
                database_id=Config.APPWRITE_CHAEA_DATABASE_ID,
                collection_id=Config.APPWRITE_ADAPTIVE_EVALUATIONS_COLLECTION_ID,
                document_id=str(uuid.uuid4()),
                data=data
            )
            return result
        except AppwriteException as e:
            raise Exception(f"Error saving adaptive evaluation: {e}")
        
    def get_adaptive_evaluation(self, evaluation_id):
        try:
            result = self.databases.get_document(
                database_id=Config.APPWRITE_CHAEA_DATABASE_ID,
                collection_id=Config.APPWRITE_ADAPTIVE_EVALUATIONS_COLLECTION_ID,
                document_id=evaluation_id
            )
            return result
        except AppwriteException as e:
            return None        
                                
        