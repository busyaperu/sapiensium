class CHAEAScorer:
    """
    Calcula puntajes CHAEA basado en las 80 respuestas del cuestionario
    """
    
    # Mapeo de preguntas por estilo de aprendizaje (1-80)
    ACTIVE_QUESTIONS = [3, 5, 7, 9, 13, 20, 26, 27, 35, 37, 41, 43, 46, 48, 51, 61, 67, 74, 75, 77]
    REFLECTIVE_QUESTIONS = [10, 16, 18, 19, 28, 31, 32, 34, 36, 39, 42, 44, 49, 55, 58, 63, 65, 69, 70, 79]
    THEORETICAL_QUESTIONS = [2, 4, 6, 11, 15, 17, 21, 23, 25, 29, 33, 45, 50, 54, 60, 64, 66, 71, 78, 80]
    PRAGMATIC_QUESTIONS = [1, 8, 12, 14, 22, 24, 30, 38, 40, 47, 52, 53, 56, 57, 59, 62, 68, 72, 73, 76]
    
    @staticmethod
    def calculate_scores(responses):
        """
        Calcula puntajes para cada estilo basado en respuestas
        
        Args:
            responses: Lista de 80 booleanos (True/False)
            
        Returns:
            dict: Puntajes por estilo y perfil determinado
        """
        if len(responses) != 80:
            raise ValueError("Se requieren exactamente 80 respuestas")
        
        # Calcular puntajes (sumar respuestas True para cada estilo)
        active_score = sum(1 for i in CHAEAScorer.ACTIVE_QUESTIONS if responses[i-1])
        reflective_score = sum(1 for i in CHAEAScorer.REFLECTIVE_QUESTIONS if responses[i-1])
        theoretical_score = sum(1 for i in CHAEAScorer.THEORETICAL_QUESTIONS if responses[i-1])
        pragmatic_score = sum(1 for i in CHAEAScorer.PRAGMATIC_QUESTIONS if responses[i-1])
        
        # Determinar estilo primario y secundario
        scores_dict = {
            'Activo': active_score,
            'Reflexivo': reflective_score,
            'Teorico': theoretical_score,
            'Pragmatico': pragmatic_score
        }
        
        sorted_styles = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
        primary_style = sorted_styles[0][0]
        secondary_style = sorted_styles[1][0]
        
        return {
            'activeScore': active_score,
            'reflectiveScore': reflective_score,
            'theoreticalScore': theoretical_score,
            'pragmaticScore': pragmatic_score,
            'primaryStyle': primary_style,
            'secondaryStyle': secondary_style,
            'scores_breakdown': scores_dict
        }
    
    @staticmethod
    def get_style_description(primary_style):
        """
        Retorna descripción básica del estilo de aprendizaje
        """
        descriptions = {
            'Activo': 'Aprende mejor experimentando, participando y trabajando en equipo',
            'Reflexivo': 'Aprende mejor observando, analizando y reflexionando antes de actuar',
            'Teorico': 'Aprende mejor con conceptos, modelos teóricos y pensamiento lógico',
            'Pragmatico': 'Aprende mejor aplicando ideas de forma práctica y resolviendo problemas reales'
        }
        return descriptions.get(primary_style, 'Estilo no reconocido')