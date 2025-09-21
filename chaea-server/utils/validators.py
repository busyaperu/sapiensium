def validate_required_fields(data, required_fields):
    """
    Valida que todos los campos requeridos estén presentes en los datos
    """
    if not data:
        return "No data provided"
    
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        return f"Missing required fields: {', '.join(missing_fields)}"
    
    return None

def validate_chaea_responses(responses):
    """
    Valida que las respuestas CHAEA sean válidas
    """
    if not isinstance(responses, list):
        return "Responses must be a list"
    
    if len(responses) != 80:
        return "CHAEA requires exactly 80 responses"
    
    for i, response in enumerate(responses):
        if not isinstance(response, bool):
            return f"Response {i+1} must be true or false"
    
    return None

def validate_user_id(user_id):
    """
    Valida formato básico del user_id
    """
    if not user_id or not isinstance(user_id, str):
        return "Invalid user ID"
    
    if len(user_id.strip()) < 3:
        return "User ID too short"
    
    return None

def validate_course_id(course_id):
    """
    Valida formato básico del course_id
    """
    if not course_id or not isinstance(course_id, str):
        return "Invalid course ID"
    
    if len(course_id.strip()) < 3:
        return "Course ID too short"
    
    return None