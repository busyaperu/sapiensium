from flask import Blueprint, request, jsonify
from services.chaea_appwrite import CHAEAAppwriteService
from services.chaea_scorer import CHAEAScorer
from utils.validators import validate_required_fields, validate_chaea_responses, validate_user_id, validate_course_id
import uuid
from datetime import datetime

chaea_bp = Blueprint('chaea', __name__)
appwrite_service = CHAEAAppwriteService()

@chaea_bp.route('/submit-responses', methods=['POST'])
def submit_responses():
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['userId', 'courseId', 'responses']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return jsonify({'error': validation_error}), 400
        
        # Validar IDs
        user_validation = validate_user_id(data['userId'])
        if user_validation:
            return jsonify({'error': user_validation}), 400
            
        course_validation = validate_course_id(data['courseId'])
        if course_validation:
            return jsonify({'error': course_validation}), 400
        
        # Validar respuestas CHAEA
        responses_validation = validate_chaea_responses(data['responses'])
        if responses_validation:
            return jsonify({'error': responses_validation}), 400
        
        # Verificar consentimiento
        consent = appwrite_service.get_consent(data['userId'], data['courseId'])
        if not consent or not consent['consentGiven']:
            return jsonify({'error': 'User consent required before processing CHAEA'}), 403
        
        # Calcular puntajes CHAEA
        scores = CHAEAScorer.calculate_scores(data['responses'])
        
        # Guardar respuestas individuales
        session_id = str(uuid.uuid4())
        appwrite_service.save_chaea_responses(
            user_id=data['userId'],
            course_id=data['courseId'],
            session_id=session_id,
            responses=data['responses']
        )
        
        # Guardar perfil calculado
        profile_result = appwrite_service.save_chaea_profile(
            user_id=data['userId'],
            course_id=data['courseId'],
            scores=scores
        )
        
        return jsonify({
            'success': True,
            'profileId': profile_result['$id'],
            'profile': {
                'primaryStyle': scores['primaryStyle'],
                'secondaryStyle': scores['secondaryStyle'],
                'scores': {
                    'active': scores['activeScore'],
                    'reflective': scores['reflectiveScore'],
                    'theoretical': scores['theoreticalScore'],
                    'pragmatic': scores['pragmaticScore']
                },
                'description': CHAEAScorer.get_style_description(scores['primaryStyle'])
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chaea_bp.route('/profile/<user_id>/<course_id>', methods=['GET'])
def get_profile(user_id, course_id):
    try:
        profile = appwrite_service.get_chaea_profile(user_id, course_id)
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify({
            'profile': {
                'primaryStyle': profile['primaryStyle'],
                'secondaryStyle': profile['secondaryStyle'],
                'scores': {
                    'active': profile['activeScore'],
                    'reflective': profile['reflectiveScore'],
                    'theoretical': profile['theoreticalScore'],
                    'pragmatic': profile['pragmaticScore']
                },
                'profileDate': profile['profileDate'],
                'description': CHAEAScorer.get_style_description(profile['primaryStyle'])
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500