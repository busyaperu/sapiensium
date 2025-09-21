from flask import Blueprint, request, jsonify
from services.chaea_appwrite import CHAEAAppwriteService
from services.evaluation_adapter import EvaluationAdapter
from utils.validators import validate_required_fields

adaptive_bp = Blueprint('adaptive', __name__)
appwrite_service = CHAEAAppwriteService()
evaluation_adapter = EvaluationAdapter()

@adaptive_bp.route('/generate-evaluation', methods=['POST'])
def generate_evaluation():
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['topic', 'bloomLevel', 'courseId']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return jsonify({'error': validation_error}), 400
        
        # Obtener perfiles de usuarios (si se especifican)
        user_profiles = []
        if 'userIds' in data and data['userIds']:
            for user_id in data['userIds']:
                profile = appwrite_service.get_chaea_profile(user_id, data['courseId'])
                if profile:
                    user_profiles.append(profile)
        
        # Generar 4 variantes adaptativas
        variants = evaluation_adapter.generate_adaptive_variants(
            topic=data['topic'],
            bloom_level=data['bloomLevel'],
            user_profiles=user_profiles
        )
        
        # Guardar evaluación en base de datos
        evaluation_result = appwrite_service.save_adaptive_evaluation(
            course_id=data['courseId'],
            topic=data['topic'],
            bloom_level=data['bloomLevel'],
            variants=variants,
            created_by=data.get('createdBy', 'system')
        )
        
        return jsonify({
            'success': True,
            'evaluationId': evaluation_result['$id'],
            'variants': variants
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@adaptive_bp.route('/get-user-variant/<user_id>/<evaluation_id>', methods=['GET'])
def get_user_variant(user_id, evaluation_id):
    try:
        # Obtener evaluación
        evaluation = appwrite_service.get_adaptive_evaluation(evaluation_id)
        if not evaluation:
            return jsonify({'error': 'Evaluation not found'}), 404
        
        # Obtener perfil del usuario
        profile = appwrite_service.get_chaea_profile(user_id, evaluation['courseId'])
        
        # Determinar variante apropiada
        if profile:
            primary_style = profile['primaryStyle']
            variant_key = f"{primary_style.lower()}Variant"
        else:
            # Si no hay perfil, usar variante teórica como default
            variant_key = "theoreticalVariant"
        
        user_variant = evaluation.get(variant_key, evaluation['theoreticalVariant'])
        
        return jsonify({
            'success': True,
            'variant': user_variant,
            'styleUsed': primary_style if profile else 'Teorico (default)',
            'hasProfile': bool(profile)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@adaptive_bp.route('/evaluation/<evaluation_id>', methods=['GET'])
def get_evaluation(evaluation_id):
    try:
        evaluation = appwrite_service.get_adaptive_evaluation(evaluation_id)
        
        if not evaluation:
            return jsonify({'error': 'Evaluation not found'}), 404
        
        return jsonify({
            'success': True,
            'evaluation': {
                'id': evaluation['$id'],
                'topic': evaluation['topic'],
                'bloomLevel': evaluation['bloomLevel'],
                'courseId': evaluation['courseId'],
                'createdAt': evaluation['createdAt'],
                'variants': {
                    'active': evaluation['activeVariant'],
                    'reflective': evaluation['reflectiveVariant'],
                    'theoretical': evaluation['theoreticalVariant'],
                    'pragmatic': evaluation['pragmaticVariant']
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500