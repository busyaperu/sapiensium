from flask import Blueprint, request, jsonify
from services.chaea_appwrite import CHAEAAppwriteService
from utils.validators import validate_required_fields

consent_bp = Blueprint('consent', __name__)
appwrite_service = CHAEAAppwriteService()

@consent_bp.route('/grant', methods=['POST'])
def grant_consent():
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['userId', 'courseId', 'consentGiven']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return jsonify({'error': validation_error}), 400
        
        # Guardar consentimiento
        result = appwrite_service.save_consent(
            user_id=data['userId'],
            course_id=data['courseId'],
            consent_given=data['consentGiven']
        )
        
        return jsonify({
            'success': True,
            'message': 'Consent saved successfully',
            'consentId': result['$id']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@consent_bp.route('/check/<user_id>/<course_id>', methods=['GET'])
def check_consent(user_id, course_id):
    try:
        consent = appwrite_service.get_consent(user_id, course_id)
        
        if consent:
            return jsonify({
                'hasConsent': True,
                'consentGiven': consent['consentGiven'],
                'consentDate': consent['consentDate']
            }), 200
        else:
            return jsonify({
                'hasConsent': False,
                'consentGiven': False
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500