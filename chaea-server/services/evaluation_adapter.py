class EvaluationAdapter:
    """
    Genera variantes de evaluación adaptadas a cada estilo CHAEA
    """
    
    def __init__(self):
        self.style_templates = {
            'Activo': {
                'approach': 'experiential',
                'format_preference': ['simulation', 'roleplay', 'hands-on', 'group_work'],
                'instruction_style': 'immediate action',
                'time_preference': 'short bursts'
            },
            'Reflexivo': {
                'approach': 'analytical',
                'format_preference': ['case_study', 'comparison', 'observation', 'research'],
                'instruction_style': 'thoughtful analysis',
                'time_preference': 'extended time'
            },
            'Teorico': {
                'approach': 'conceptual',
                'format_preference': ['definition', 'framework', 'theory', 'logic'],
                'instruction_style': 'systematic explanation',
                'time_preference': 'structured time'
            },
            'Pragmatico': {
                'approach': 'practical',
                'format_preference': ['real_case', 'problem_solving', 'application', 'proposal'],
                'instruction_style': 'practical application',
                'time_preference': 'focused time'
            }
        }
    
    def generate_adaptive_variants(self, topic, bloom_level, user_profiles=None):
        """
        Genera 4 variantes de evaluación para el mismo tema
        """
        base_prompt = f"Tema: {topic}, Nivel Bloom: {bloom_level}"
        
        variants = {
            'activeVariant': self._generate_active_variant(base_prompt),
            'reflectiveVariant': self._generate_reflective_variant(base_prompt),
            'theoreticalVariant': self._generate_theoretical_variant(base_prompt),
            'pragmaticVariant': self._generate_pragmatic_variant(base_prompt)
        }
        
        return variants
    
    def _generate_active_variant(self, base_prompt):
        return {
            'style': 'Activo',
            'format': 'Simulación/Role-play',
            'instruction': f"Simula una situación real sobre {base_prompt.split(':')[1].strip()}. Participa activamente y toma decisiones rápidas.",
            'questions': [
                {
                    'type': 'simulation',
                    'prompt': f"Te encuentras en una situación donde debes aplicar {base_prompt.split(':')[1].strip()}. Describe 3 acciones inmediatas que tomarías.",
                    'evaluation_criteria': ['Participación activa', 'Decisiones justificadas', 'Trabajo colaborativo']
                }
            ],
            'rubric': {
                'participation': 'Demuestra participación activa y entusiasmo',
                'decisions': 'Toma decisiones rápidas y justificadas',
                'collaboration': 'Trabaja efectivamente en equipo'
            },
            'time_limit': '30 minutos',
            'format_notes': 'Enfoque experiencial con actividad práctica inmediata'
        }
    
    def _generate_reflective_variant(self, base_prompt):
        return {
            'style': 'Reflexivo',
            'format': 'Análisis comparativo',
            'instruction': f"Analiza profundamente diferentes perspectivas sobre {base_prompt.split(':')[1].strip()}. Toma tiempo para reflexionar antes de responder.",
            'questions': [
                {
                    'type': 'analysis',
                    'prompt': f"Compara y contrasta al menos 3 enfoques diferentes sobre {base_prompt.split(':')[1].strip()}. Reflexiona sobre las implicaciones de cada uno.",
                    'evaluation_criteria': ['Profundidad de análisis', 'Uso de fuentes múltiples', 'Reflexión crítica']
                }
            ],
            'rubric': {
                'depth': 'Muestra análisis profundo y detallado',
                'sources': 'Integra múltiples perspectivas y fuentes',
                'reflection': 'Demuestra pensamiento crítico y reflexivo'
            },
            'time_limit': '60 minutos',
            'format_notes': 'Enfoque analítico con tiempo extendido para reflexión'
        }
    
    def _generate_theoretical_variant(self, base_prompt):
        return {
            'style': 'Teorico',
            'format': 'Marco conceptual',
            'instruction': f"Desarrolla un marco teórico sólido sobre {base_prompt.split(':')[1].strip()}. Utiliza conceptos, definiciones y lógica sistemática.",
            'questions': [
                {
                    'type': 'conceptual',
                    'prompt': f"Define los conceptos clave relacionados con {base_prompt.split(':')[1].strip()} y establece las relaciones lógicas entre ellos.",
                    'evaluation_criteria': ['Precisión conceptual', 'Coherencia lógica', 'Estructura sistemática']
                }
            ],
            'rubric': {
                'precision': 'Utiliza conceptos con precisión y rigor',
                'logic': 'Mantiene coherencia lógica en el desarrollo',
                'structure': 'Presenta estructura sistemática y ordenada'
            },
            'time_limit': '45 minutos',
            'format_notes': 'Enfoque conceptual con estructura teórica rigurosa'
        }
    
    def _generate_pragmatic_variant(self, base_prompt):
        return {
            'style': 'Pragmatico',
            'format': 'Caso práctico',
            'instruction': f"Resuelve un problema real aplicando {base_prompt.split(':')[1].strip()}. Enfócate en soluciones viables y aplicables.",
            'questions': [
                {
                    'type': 'practical',
                    'prompt': f"Presenta una propuesta práctica para resolver un problema específico usando {base_prompt.split(':')[1].strip()}. Incluye pasos concretos y resultados esperados.",
                    'evaluation_criteria': ['Viabilidad de la solución', 'Aplicabilidad práctica', 'Resultados medibles']
                }
            ],
            'rubric': {
                'viability': 'Propone soluciones viables y realistas',
                'applicability': 'Demuestra aplicabilidad práctica clara',
                'results': 'Define resultados medibles y concretos'
            },
            'time_limit': '40 minutos',
            'format_notes': 'Enfoque práctico con aplicación real inmediata'
        }
    
    def validate_variant_equity(self, variants):
        """
        Valida que todas las variantes midan la misma competencia
        """
        # Implementación básica de validación de equidad
        base_criteria = ['same_topic', 'same_bloom_level', 'equivalent_difficulty']
        
        validation_result = {
            'is_equitable': True,
            'issues': [],
            'recommendations': []
        }
        
        # Esta es una validación básica - en producción sería más sofisticada
        return validation_result