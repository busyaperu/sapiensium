from flask import Flask, request, jsonify, render_template_string
import requests
import os
import logging
import re
import uuid
import json
from dotenv import load_dotenv
import datetime
import random
import string
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.input_file import InputFile
from appwrite.services.storage import Storage # Servicio de Storage
from appwrite.exception import AppwriteException # Para capturar errores específicos
from google.cloud import storage  
from google.auth import default
from threading import Thread
from io import BytesIO
import traceback
from appwrite.exception import AppwriteException # <--- AÑADE ESTA LÍNEA
import time
from flask import Flask, request, jsonify, render_template_string, redirect
from appwrite.query import Query
import openai
import google.generativeai as genai
import anthropic
import tempfile
import subprocess
from playwright.sync_api import sync_playwright
import threading


# 1. Inicialización de Flask
app = Flask(__name__, static_folder='.', static_url_path='')


def limpiar_markdown(texto):  # ← AGREGAR AQUÍ
    """Elimina formato markdown del texto"""
    import re
    if not texto:
        return texto
    
    # Eliminar asteriscos de negritas (**texto** y ***texto***)
    texto = re.sub(r'\*{2,3}([^*]+)\*{2,3}', r'\1', texto)
    # Eliminar asteriscos simples (*texto*)
    texto = re.sub(r'\*([^*]+)\*', r'\1', texto)
    # Limpiar asteriscos sueltos
    texto = re.sub(r'\*+', '', texto)
    
    return texto.strip()

 # Mapeo de modelos a sus configuraciones
modelos = {
    
    # ===== TOGETHER AI =====
        'deepseek-v3': {
            'api': 'together',
            'model_id': 'deepseek-ai/DeepSeek-V3',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        
        'deepseek-r1': {
            'api': 'together',
            'model_id': 'deepseek-ai/DeepSeek-R1',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'llama-4-maverick': {
            'api': 'together',
            'model_id': 'meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'llama-4-scout': {
            'api': 'together',
            'model_id': 'meta-llama/Llama-4-Scout-Instruct',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'llama-3-1-405b': {
            'api': 'together',
            'model_id': 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'llama-3-3-70b': {
            'api': 'together',
            'model_id': 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'llama-3-8b-reference': {
            'api': 'together',
            'model_id': 'meta-llama/Meta-Llama-3-8B-Instruct',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'llama-vision-free': {
            'api': 'together',
            'model_id': 'meta-llama/Llama-Vision-Free',
            'api_key_env': 'TOGETHER_API_KEY'
            
        },
        'llama-3-2-90b': {
            'api': 'together',
            'model_id': 'meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'nemotron-ultra': {
            'api': 'together',
            'model_id': 'nvidia/llama-3.1-nemotron-ultra-253b-v1',
            'api_key_env': 'TOGETHER_API_KEY'
        },        
        'qwen-2-5-vl': {
            'api': 'together',
            'model_id': 'Qwen/Qwen2.5-VL-72B-Instruct',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'qwen-coder-32b': {
            'api': 'together',
            'model_id': 'Qwen/Qwen2.5-Coder-32B-Instruct',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'qwen-qwq-32b': {
            'api': 'together',
            'model_id': 'Qwen/QwQ-32B-Preview',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'llama-3-2-90b': {
            'api': 'together',
            'model_id': 'meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'qwen3-235b-thinking': {
            'api': 'together',
            'model_id': 'Qwen/Qwen3-235B-A22B-Thinking-2507',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'qwen3-235b-instruct': {
            'api': 'together',
            'model_id': 'Qwen/Qwen3-235B-A22B-Instruct-2507',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'qwen3-30b-thinking': {
            'api': 'together',
            'model_id': 'Qwen/Qwen3-30B-A3B-Thinking-2507',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'qwen3-30b-instruct': {
            'api': 'together',
            'model_id': 'Qwen/Qwen3-30B-A3B-Instruct-2507',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'mixtral-8x7b': {
            'api': 'together',
            'model_id': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'mistral-small-25': {
            'api': 'together',
            'model_id': 'mistralai/Mistral-Small-Instruct-2501',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'exaone-3-5-32b': {
            'api': 'together',
            'model_id': 'LG-AI-Research/exaone-3.5-32b-instruct',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'exaone-deep-32b': {
            'api': 'together',
            'model_id': 'LG-AI-Research/exaone-deep-32b',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'afm-4-5b': {
            'api': 'together',
            'model_id': 'Arcee-AI/AFM-4.5B-Preview',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'arcee-maestro': {
            'api': 'together',
            'model_id': 'Arcee-AI/Arcee-Maestro',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        
        'Kimi-K2-Instruct': {
            'api': 'together',
            'model_id': "moonshotai/Kimi-K2-Instruct",
            'api_key_env': 'TOGETHER_API_KEY'
        },
        
        'GLM-4.5-Air-FP8': {
            'api': 'together',
            'model_id': "zai-org/GLM-4.5-Air-FP8",
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'typhoon-2-70b': {
            'api': 'together',
            'model_id': 'SCB10X/Typhoon-2-70B-Instruct',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'solar-10-7b': {
            'api': 'together',
            'model_id': 'upstage/SOLAR-10.7B-Instruct-v1.0',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'nous-hermes-mixtral': {
            'api': 'together',
            'model_id': 'NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'deepseek-r1-turbo': {
            'api': 'together',
            'model_id': 'deepseek-ai/DeepSeek-R1-Turbo',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'qwen3-coder-480b': {
            'api': 'together',
            'model_id': 'Qwen/Qwen3-Coder-480B-A35B',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'exaone-deep-32b': {
            'api': 'together',
            'model_id': 'LG-AI-Research/exaone-deep-32b',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'kimi-k2-instruct': {
            'api': 'together',
            'model_id': 'moonshotai/Kimi-K2-Instruct',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        'glm-4-5-air-fp8': {
            'api': 'together',
            'model_id': 'zai-org/GLM-4.5-Air-FP8',
            'api_key_env': 'TOGETHER_API_KEY'
        },
        # ===== GOOGLE GEMINI =====
        'gemini-2-5-pro': {
            'api': 'google',
            'model_id': 'gemini-2.5-pro-preview-05-06',
            'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
        },
        'gemini-2-5-flash': {
            'api': 'google',
            'model_id': 'gemini-2.5-flash-preview-04-17',
            'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
        },
        'gemini-2-0-flash': {
            'api': 'google',
            'model_id': 'gemini-2.0-flash',
            'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
        },
        'gemini-1-5-flash': {
            'api': 'google',
            'model_id': 'gemini-1.5-flash',
            'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
        },
        'gemini-1-5-pro': {  
            'api': 'google',
            'model_id': 'gemini-1.5-pro', 
            'api_key_env': 'GOOGLE_GEMINI_PRO_API_KEY'
        },
        'claude-sonnet-4': {
            'api': 'anthropic',
            'model_id': 'claude-4-sonnet-20250514',
            'api_key_env': 'ANTHROPIC_API_KEY'
        },
        
        # ===== ANTHROPIC =====
        'claude-sonnet-4': {
            'api': 'anthropic',
            'model_id': 'claude-4-sonnet',  # O el ID correcto para Claude 4 Sonnet
            'api_key_env': 'ANTHROPIC_API_KEY'
        },
        
         # ===== OPENAI =====
        'gpt-4-1': {
            'api': 'openai',
            'model_id': 'gpt-4-turbo-preview',
            'api_key_env': 'OPENAI_API_KEY'
        },
        'gpt-4o': {
            'api': 'openai',
            'model_id': 'gpt-4o',
            'api_key_env': 'OPENAI_API_KEY'
        },
        'gpt-4o-mini': {
            'api': 'openai',
            'model_id': 'gpt-4o-mini',
            'api_key_env': 'OPENAI_API_KEY'
        },
        
        # ===== OPENROUTER =====
        'openrouter-generic': {
            'api': 'openrouter',
            'model_id': '',  # Se sobrescribe en tiempo de ejecución
            'api_key_env': 'OPENROUTER_API_KEY'
        }
    }

MODELOS_TEXTO_OPENROUTER = [
# Lista vacía - no se usará OpenRouter
]


# Estructura de recomendaciones de modelos por tipo de pregunta
RECOMENDACIONES_MODELOS = {
    'opcion_multiple': {
        'recomendados': [
    
	        {
                'modelo': 'Qwen/QwQ-32B-Preview',
                'nombre_display': 'Qwen QwQ-32B',
                'puntuacion': 3,
                'velocidad': 'media',
                'fortalezas': ['Preguntas específicas', 'Evaluación focalizada'],
                'limitaciones': ['Alcance limitado'],
                'tiempo_estimado': '18-25 segundos'
            },
            {
                'modelo': 'gemini-1-5-pro',
                'nombre_display': 'Gemini 1.5 Pro',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Estructura precisa', 'Opciones balanceadas', 'Consistencia alta'],
                'ideal_para': 'Preguntas técnicas con opciones claras y distintas',
                'tiempo_estimado': '15-25 segundos',
                'nota': 'Excelente para generar distractores convincentes'
            },
	        {
                'modelo': 'mistralai/Mistral-Small-Instruct-2501',
                'nombre_display': 'Mistral Small 25.01',
                'puntuacion': 3,
                'velocidad': 'media',
                'fortalezas': ['Equilibrado', 'Evaluación estándar'],
                'limitaciones': ['No especializado'],
                'tiempo_estimado': '15-22 segundos'
            },
            {
                'modelo': 'nvidia/llama-3.1-nemotron-ultra-253b-v1',
                'nombre_display': 'Llama 3.1 Nemotron 253B',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Test', 'Preguntas expertas', 'Evaluación experta'],
                'ideal_para': 'Testing y desarrollo con calidad alta',
                'tiempo_estimado': '20-30 segundos',
                'nota': 'GRATIS: El mejor modelo gratuito disponible'
            },
            {
                'modelo': 'meta-llama/llama-3.3-70b-instruct',
                'nombre_display': 'Meta Llama 3.3 70B',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Test', 'Rápido y preciso', 'Evaluación rápida'],
                'ideal_para': 'Generación masiva gratuita',
                'tiempo_estimado': '15-20 segundos',
                'nota': 'Test: Velocidad y calidad'
            },
            {
                'modelo': 'LG-AI-Research/exaone-3.5-32b-instruct',
                'nombre_display': 'EXAONE 3.5 32B Instruct',
                'puntuacion': 3,
                'velocidad': 'media',
                'fortalezas': ['Gratuito', 'Alternativa viable', 'Preguntas básicas'],
                'limitaciones': ['Calidad básica'],
                'tiempo_estimado': '15-20 segundos'
            },
            {
                'modelo': 'deepseek-ai/DeepSeek-R1-Distill-Llama-70B',
                'nombre_display': 'DeepSeek R1 Distill Llama 70B',
                'puntuacion': 3,
                'velocidad': 'rapida',
                'fortalezas': ['Test', 'Testing', 'Desarrollo'],
                'limitaciones': ['Versión simplificada'],
                'tiempo_estimado': '12-18 segundos'
            },
            {
                'modelo': 'Arcee-AI/AFM-4.5B-Preview',
                'nombre_display': 'AFM-4.5B-Preview',
                'puntuacion': 2,
                'velocidad': 'rapida',
                'fortalezas': ['Gratuito', 'Pruebas conceptuales'],
                'limitaciones': ['Muy básico', 'Solo pruebas'],
                'tiempo_estimado': '10-15 segundos'
            },
            {
                'modelo': 'deepseek-ai/DeepSeek-V3',
                'nombre_display': 'DeepSeek V3',
                'puntuacion': 5,
                'velocidad': 'rapida',
                'fortalezas': ['Lógica sólida', 'Opciones coherentes', 'Respuestas precisas'],
                'ideal_para': 'Preguntas de razonamiento y análisis',
                'tiempo_estimado': '10-15 segundos',
                'nota': 'Muy eficiente para preguntas de múltiple opción'
            },
            {
                'modelo': 'meta-llama/Llama-4-Scout-Instruct',
                'nombre_display': 'Llama 4 Scout Instruct',
                'puntuacion': 4,
                'velocidad': 'rapida',
                'fortalezas': ['Muy económico', 'Respuestas precisas', 'Velocidad alta'],
                'ideal_para': 'Generación masiva de preguntas básicas',
                'tiempo_estimado': '8-12 segundos',
                'nota': 'Mejor relación calidad-precio para volumen alto'
            }
        ],
        'aceptables': [
            {
                'modelo': 'mistralai/Mixtral-8x7B-Instruct-v0.1',
                'nombre_display': 'Mixtral-8x7B Instruct',
                'puntuacion': 4,
                'velocidad': 'rapida',
                'fortalezas': ['Múltiples preguntas simultáneas', 'Eficiencia alta'],
                'limitaciones': ['Menos profundidad individual'],
                'tiempo_estimado': '12-18 segundos'
            },
            {
                'modelo': 'meta-llama/Meta-Llama-3-8B-Instruct',
                'nombre_display': 'Meta Llama 3 8B Reference',
                'puntuacion': 3,
                'velocidad': 'muy_rapida',
                'fortalezas': ['Preguntas simples en masa', 'Muy económico'],
                'limitaciones': ['Complejidad limitada'],
                'tiempo_estimado': '5-8 segundos'
            },
            {
                'modelo': 'gemini-2-0-flash',
                'nombre_display': 'Gemini 2.0 Flash',
                'puntuacion': 3,
                'velocidad': 'rapida',
                'fortalezas': ['Velocidad excelente', 'Respuestas directas'],
                'limitaciones': ['Menos profundidad', 'Opciones más simples'],
                'tiempo_estimado': '5-10 segundos'
            },
 	        {
                'modelo': 'LG-AI-Research/exaone-deep-32b',
                'nombre_display': 'EXAONE Deep 32B',
                'puntuacion': 3,
                'velocidad': 'media',
                'fortalezas': ['Gratuito', 'Análisis detallado'],
                'limitaciones': ['Menos precisión'],
                'tiempo_estimado': '18-25 segundos'
            }
        ],
        'no_recomendados': [
            
            {
                'modelo': 'qwen-2-5-vl',
                'razon': 'Optimizado para contenido visual, no para texto puro',
                'alternativa': 'gemini-2-5-pro'
            },
            
            {
                'modelo': 'gemini-2-5-pro',
                'nombre_display': 'Gemini 2.5 Pro',
                'puntuacion': 5,
                'velocidad': 'media',
                'fortalezas': ['Estructura precisa', 'Opciones balanceadas', 'Consistencia alta'],
                'ideal_para': 'Preguntas técnicas con opciones claras y distintas',
                'tiempo_estimado': '15-25 segundos',
                'nota': 'Excelente para generar distractores convincentes'
            },
            {
                'modelo': 'deepseek-ai/DeepSeek-R1',
                'nombre_display': 'DeepSeek R1-0528',
                'puntuacion': 5,
                'velocidad': 'media',
                'fortalezas': ['Máxima precisión', 'Lógica excepcional', 'Calidad premium'],
                'ideal_para': 'Preguntas complejas que requieren máxima precisión',
                'tiempo_estimado': '20-30 segundos',
                'nota': 'Premium: Máxima calidad para evaluaciones críticas'
            },
            {
                'modelo': 'gpt-4-1',
                'nombre_display': 'GPT-4 Turbo',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Creatividad controlada', 'Variedad de opciones', 'Buena estructura'],
                'ideal_para': 'Preguntas creativas pero estructuradas',
                'tiempo_estimado': '20-30 segundos',
                'nota': 'Confiable para la mayoría de temas'
            },
            {
                'modelo': 'meta-llama/llama-3.1-405b:free',
                'nombre_display': 'Llama 3.1 405B',
                'puntuacion': 4,
                'velocidad': 'lenta',
                'fortalezas': ['Conocimiento amplio', 'Respuestas detalladas'],
                'limitaciones': ['Puede ser verbose', 'Tiempo de respuesta alto'],
                'tiempo_estimado': '30-45 segundos'
            }
        ]
    },
    
    'abierta': {
        'recomendados': [
            {
                'modelo': 'claude-sonnet-4',
                'nombre_display': 'Claude Sonnet 4',
                'puntuacion': 5,
                'velocidad': 'media',
                'fortalezas': ['Análisis profundo', 'Pensamiento crítico', 'Preguntas reflexivas'],
                'ideal_para': 'Preguntas que requieren análisis y síntesis',
                'tiempo_estimado': '20-30 segundos',
                'nota': 'Excelente para preguntas académicas complejas'
            },
            {
                'modelo': 'deepseek-ai/DeepSeek-R1',
                'nombre_display': 'DeepSeek R1-0528',
                'puntuacion': 5,
                'velocidad': 'media',
                'fortalezas': ['Máxima calidad evaluativa', 'Análisis profundo', 'Precisión excepcional'],
                'ideal_para': 'Evaluaciones de máxima calidad y complejidad',
                'tiempo_estimado': '25-35 segundos',
                'nota': 'Premium: Máxima calidad para evaluación de respuestas'
            },
            {
                'modelo': 'gemini-1-5-flash',
                'nombre_display': 'Gemini 1.5 Flash',
                'puntuacion': 3,
                'velocidad': 'rapida',
                'fortalezas': ['Velocidad excelente', 'Económico', 'Respuestas claras'],
                'ideal_para': 'Preguntas básicas de opción múltiple',
                'tiempo_estimado': '5-10 segundos',
                'nota': 'Opción económica para preguntas simples'
            },
            {
                'modelo': 'meta-llama/Llama-4-Maverick-Instruct',
                'nombre_display': 'Llama 4 Maverick Instruct',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Buena relación calidad', 'Evaluación equilibrada'],
                'ideal_para': 'Preguntas de desarrollo con presupuesto controlado',
                'tiempo_estimado': '18-25 segundos',
                'nota': 'Excelente balance entre calidad y recursos'
            },
            {
                'modelo': 'meta-llama/llama-3.1-405b:free',
                'nombre_display': 'Llama 3.1 405B',
                'puntuacion': 4,
                'velocidad': 'lenta',
                'fortalezas': ['Conocimiento extenso', 'Detalles técnicos', 'Profundidad'],
                'ideal_para': 'Preguntas técnicas especializadas',
                'tiempo_estimado': '30-45 segundos',
                'nota': 'Ideal para temas muy específicos'
            }
        ],
        'aceptables': [
            {
                'modelo': 'SCB10X/Typhoon-2-70B-Instruct',
                'nombre_display': 'Typhoon 2 70B Instruct',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Exámenes internacionales', 'Multiidioma'],
                'limitaciones': ['Menos especialización local'],
                'tiempo_estimado': '20-28 segundos'
            },
            {
                'modelo': 'Arcee-AI/Arcee-Maestro',
                'nombre_display': 'Arcee AI Maestro',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Chat experto', 'Análisis profundo'],
                'limitaciones': ['Nuevo modelo'],
                'tiempo_estimado': '20-30 segundos'
            },
            {
                'modelo': 'deepseek-ai/DeepSeek-V3',
                'nombre_display': 'DeepSeek V3',
                'puntuacion': 4,
                'velocidad': 'rapida',
                'fortalezas': ['Eficiencia alta', 'Lógica clara'],
                'limitaciones': ['Menos creatividad', 'Enfoque más directo'],
                'tiempo_estimado': '10-15 segundos'
            },
            {
                'modelo': 'gpt-4-1',
                'nombre_display': 'GPT-4 Turbo',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Balance general', 'Flexibilidad'],
                'limitaciones': ['Menos especialización'],
                'tiempo_estimado': '20-30 segundos'
            },
            {
                'modelo': 'LG-AI-Research/exaone-deep-32b',
                'nombre_display': 'EXAONE Deep 32B',
                'puntuacion': 3,
                'velocidad': 'media',
                'fortalezas': ['Gratuito', 'Análisis detallado'],
                'limitaciones': ['Calidad básica'],
                'tiempo_estimado': '18-25 segundos',
                'nota': 'GRATIS: Para análisis detallado gratuito'
            }
        ],
        'no_recomendados': [
            {
                'modelo': 'gemini-2-0-flash',
                'razon': 'Optimizado para respuestas rápidas, no para profundidad',
                'alternativa': 'gemini-2-5-pro'
            },
            {
                'modelo': 'gemini-2-5-flash',
                'nombre_display': 'Gemini 2.5 Flash',
                'puntuacion': 4,
                'velocidad': 'rapida',
                'fortalezas': ['Velocidad alta', 'Respuestas directas', 'Eficiencia'],
                'ideal_para': 'Generación rápida de preguntas estándar',
                'tiempo_estimado': '5-12 segundos',
                'nota': 'Ideal para volumen alto con buena calidad'
            },
            
            {
                'modelo': 'gemini-2-5-pro',
                'nombre_display': 'Gemini 2.5 Pro',
                'puntuacion': 5,
                'velocidad': 'media',
                'fortalezas': ['Estructura precisa', 'Opciones balanceadas', 'Consistencia alta'],
                'ideal_para': 'Preguntas técnicas con opciones claras y distintas',
                'tiempo_estimado': '15-25 segundos',
                'nota': 'Excelente para generar distractores convincentes'
            },
        ]
    },
    
    'caso_uso': {
        'recomendados': [
            {
                'modelo': 'deepseek-ai/DeepSeek-V3',
                'nombre_display': 'DeepSeek V3',
                'puntuacion': 5,
                'velocidad': 'rapida',
                'fortalezas': ['Escenarios realistas', 'Lógica práctica', 'Contexto coherente'],
                'ideal_para': 'Casos de uso técnicos y empresariales',
                'tiempo_estimado': '10-15 segundos',
                'nota': 'Excelente para situaciones del mundo real'
            },
            {
                'modelo': 'Qwen/Qwen2.5-VL-72B-Instruct',
                'nombre_display': 'Qwen 2.5 VL 72B',
                'puntuacion': 5,
                'velocidad': 'media',
                'fortalezas': ['Casos con imágenes', 'Evalúa multimedia', 'Contexto visual'],
                'ideal_para': 'Casos de uso con elementos visuales',
                'tiempo_estimado': '20-30 segundos',
                'nota': 'Premium: Para preguntas con imágenes y multimedia'
            },
            {
                'modelo': 'gemini-2-5-pro',
                'nombre_display': 'Gemini 2.5 Pro',
                'puntuacion': 5,
                'velocidad': 'media',
                'fortalezas': ['Narrativa rica', 'Detalles realistas', 'Complejidad adecuada'],
                'ideal_para': 'Casos multifacéticos con múltiples variables',
                'tiempo_estimado': '15-25 segundos',
                'nota': 'Perfecto para casos complejos e interdisciplinarios'
            },
            {
                'modelo': 'Qwen/Qwen2.5-Coder-32B-Instruct',
                'nombre_display': 'Qwen 2.5 Coder 32B',
                'puntuacion': 5,
                'velocidad': 'rapida',
                'fortalezas': ['Casos de programación', 'Evalúa código', 'Escenarios técnicos'],
                'ideal_para': 'Casos de uso de programación y desarrollo',
                'tiempo_estimado': '12-18 segundos',
                'nota': 'Especializado: Para preguntas de programación'
            },
            {
                'modelo': 'claude-sonnet-4',
                'nombre_display': 'Claude Sonnet 4',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Análisis contextual', 'Consideraciones éticas', 'Profundidad'],
                'ideal_para': 'Casos que requieren análisis ético o social',
                'tiempo_estimado': '20-30 segundos',
                'nota': 'Ideal para casos con implicaciones éticas'
            }
        ],
        'aceptables': [
            {
                'modelo': 'upstage/SOLAR-10.7B-Instruct-v1.0',
                'nombre_display': 'Upstage SOLAR Instruct v1',
                'puntuacion': 4,
                'velocidad': 'rapida',
                'fortalezas': ['Casos científicos/técnicos', 'Evaluación especializada'],
                'limitaciones': ['Dominio específico'],
                'tiempo_estimado': '15-20 segundos'
            },
            {
                'modelo': 'Qwen/QwQ-32B-Preview',
                'nombre_display': 'Qwen QwQ-32B',
                'puntuacion': 3,
                'velocidad': 'media',
                'fortalezas': ['Preguntas específicas', 'Evaluación focalizada'],
                'limitaciones': ['Alcance limitado'],
                'tiempo_estimado': '18-25 segundos'
            },
            {
                'modelo': 'mistralai/Mistral-Small-Instruct-2501',
                'nombre_display': 'Mistral Small 25.01',
                'puntuacion': 3,
                'velocidad': 'media',
                'fortalezas': ['Equilibrado', 'Evaluación estándar'],
                'limitaciones': ['No especializado'],
                'tiempo_estimado': '15-22 segundos'
            },
            {
                'modelo': 'meta-llama/llama-3.1-405b:free',
                'nombre_display': 'Llama 3.1 405B',
                'puntuacion': 4,
                'velocidad': 'lenta',
                'fortalezas': ['Detalle exhaustivo', 'Conocimiento técnico'],
                'limitaciones': ['Puede ser muy extenso', 'Tiempo alto'],
                'tiempo_estimado': '30-45 segundos'
            },
            {
                'modelo': 'gpt-4-1',
                'nombre_display': 'GPT-4 Turbo',
                'puntuacion': 3,
                'velocidad': 'media',
                'fortalezas': ['Versatilidad general', 'Creatividad'],
                'limitaciones': ['Menos especialización en casos prácticos'],
                'tiempo_estimado': '20-30 segundos'
            },
            {
                'modelo': 'meta-llama/Llama-Vision-Free',
                'nombre_display': 'Meta Llama Vision',
                'puntuacion': 3,
                'velocidad': 'media',
                'fortalezas': ['Gratuito', 'Casos con imágenes básicos'],
                'limitaciones': ['Calidad básica'],
                'tiempo_estimado': '18-25 segundos',
                'nota': 'GRATIS: Para preguntas con imágenes'
            }
        ],
        'no_recomendados': [
            {
                'modelo': 'gemini-2-0-flash',
                'razon': 'Los casos de uso requieren más detalle del que puede proporcionar',
                'alternativa': 'deepseek-ai/DeepSeek-V3'
            },
            {
                'modelo': 'gemini-1-5-flash',
                'nombre_display': 'Gemini 1.5 Flash',
                'puntuacion': 3,
                'velocidad': 'rapida',
                'fortalezas': ['Velocidad excelente', 'Económico', 'Respuestas claras'],
                'ideal_para': 'Preguntas básicas de opción múltiple',
                'tiempo_estimado': '5-10 segundos',
                'nota': 'Opción económica para preguntas simples'
            }
        ]
    },

    # Nuevas categorías agregadas
    'evaluacion_respuestas': {
        'recomendados': [
            {
                'modelo': 'deepseek-ai/DeepSeek-R1',
                'nombre_display': 'DeepSeek R1-0528',
                'puntuacion': 5,
                'velocidad': 'media',
                'fortalezas': ['Máxima precisión evaluativa', 'Análisis profundo', 'Calidad premium'],
                'ideal_para': 'Evaluaciones críticas que requieren máxima precisión',
                'tiempo_estimado': '25-35 segundos',
                'nota': 'Premium: La mejor opción para evaluar respuestas complejas'
            },
            {
                'modelo': 'claude-sonnet-4',
                'nombre_display': 'Claude Sonnet 4',
                'puntuacion': 5,
                'velocidad': 'media',
                'fortalezas': ['Análisis contextual profundo', 'Evaluación ética', 'Pensamiento crítico'],
                'ideal_para': 'Evaluación de ensayos y respuestas complejas',
                'tiempo_estimado': '20-30 segundos',
                'nota': 'Excelente para evaluación académica avanzada'
            },
            {
                'modelo': 'Arcee-AI/Arcee-Maestro',
                'nombre_display': 'Arcee AI Maestro',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Evaluación experta', 'Calificación profesional'],
                'ideal_para': 'Evaluación especializada de alto nivel',
                'tiempo_estimado': '22-30 segundos',
                'nota': 'Para evaluaciones que requieren expertise'
            }
        ],
        'aceptables': [
            {
                'modelo': 'gemini-2-5-pro',
                'nombre_display': 'Gemini 2.5 Pro',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Evaluación versátil', 'Buen balance'],
                'limitaciones': ['Menos especializado que los premium'],
                'tiempo_estimado': '15-25 segundos'
            },
            {
                'modelo': 'meta-llama/Llama-4-Maverick-Instruct',
                'nombre_display': 'Llama 4 Maverick Instruct',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Evaluación equilibrada', 'Buena relación calidad-recursos'],
                'limitaciones': ['Menos profundidad que premium'],
                'tiempo_estimado': '18-25 segundos'
            }
        ]
    },

    'modelos_test': {
        'mejor_test': [
            {
                'modelo': 'nvidia/llama-3.1-nemotron-ultra-253b-v1',
                'nombre_display': 'Llama 3.1 Nemotron 253B',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Test', 'Preguntas expertas', 'Evaluación experta'],
                'ideal_para': 'Testing y desarrollo con calidad alta',
                'tiempo_estimado': '20-30 segundos',
                'nota': 'GRATIS: El mejor modelo gratuito disponible'
            },
            {
                'modelo': 'meta-llama/llama-3.1-405b:free',
                'nombre_display': 'Meta Llama 3.1 405B',
                'puntuacion': 4,
                'velocidad': 'lenta',
                'fortalezas': ['Test', 'Máxima capacidad', 'Evaluación experta'],
                'ideal_para': 'Evaluaciones complejas sin costo',
                'tiempo_estimado': '30-45 segundos',
                'nota': 'Test: Capacidad premium'
            },
            {
                'modelo': 'meta-llama/llama-3.3-70b-instruct',
                'nombre_display': 'Meta Llama 3.3 70B',
                'puntuacion': 4,
                'velocidad': 'media',
                'fortalezas': ['Test', 'Rápido y preciso', 'Evaluación rápida'],
                'ideal_para': 'Generación masiva gratuita',
                'tiempo_estimado': '15-20 segundos',
                'nota': 'Test: Velocidad y calidad'
            }
        ],
        'alternativos_test': [
            {
                'modelo': 'LG-AI-Research/exaone-3.5-32b-instruct',
                'nombre_display': 'EXAONE 3.5 32B Instruct',
                'puntuacion': 3,
                'velocidad': 'media',
                'fortalezas': ['Gratuito', 'Alternativa viable', 'Preguntas básicas'],
                'limitaciones': ['Calidad básica'],
                'tiempo_estimado': '15-20 segundos'
            },
            {
                'modelo': 'LG-AI-Research/exaone-deep-32b',
                'nombre_display': 'EXAONE Deep 32B',
                'puntuacion': 3,
                'velocidad': 'media',
                'fortalezas': ['Gratuito', 'Análisis detallado'],
                'limitaciones': ['Menos precisión'],
                'tiempo_estimado': '18-25 segundos'
            },
            {
                'modelo': 'meta-llama/Llama-Vision-Free',
                'nombre_display': 'Meta Llama Vision',
                'puntuacion': 3,
                'velocidad': 'media',
                'fortalezas': ['Test', 'Preguntas con imágenes'],
                'limitaciones': ['Calidad multimedia básica'],
                'tiempo_estimado': '18-25 segundos'
            },
            {
                'modelo': 'deepseek-ai/DeepSeek-R1-Distill-Llama-70B',
                'nombre_display': 'DeepSeek R1 Distill Llama 70B',
                'puntuacion': 3,
                'velocidad': 'rapida',
                'fortalezas': ['Test', 'Testing', 'Desarrollo'],
                'limitaciones': ['Versión simplificada'],
                'tiempo_estimado': '12-18 segundos'
            },
            {
                'modelo': 'Arcee-AI/AFM-4.5B-Preview',
                'nombre_display': 'AFM-4.5B-Preview',
                'puntuacion': 2,
                'velocidad': 'rapida',
                'fortalezas': ['Gratuito', 'Pruebas conceptuales'],
                'limitaciones': ['Muy básico', 'Solo pruebas'],
                'tiempo_estimado': '10-15 segundos'
            }
        ]
    }
}

MODELOS_MULTIMODAL_OPENROUTER = [
   # Lista vacía - no se usará OpenRouter
]

MODELOS_MULTIMODAL = [
    "meta-llama/Llama-Vision-Free",
    "Qwen/Qwen2.5-VL-72B-Instruct", 
    "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"
]


# Obtiene las credenciales y el proyecto por defecto
cred, project = default()

storage_client = storage.Client(credentials=cred, project=project)


load_dotenv()  # Esto leerá las variables definidas en .env

# Recuperar variables de entorno
APPWRITE_ENDPOINT = os.getenv('APPWRITE_ENDPOINT')
APPWRITE_PROJECT_ID = os.getenv('APPWRITE_PROJECT_ID')
APPWRITE_API_KEY = os.getenv('APPWRITE_API_KEY')
APPWRITE_DATABASE_ID = os.getenv('APPWRITE_DATABASE_ID')
APPWRITE_COLLECTION_ID = os.getenv('APPWRITE_COLLECTION_ID')
APPWRITE_COLLECTION_EXAMEN_PROFESOR_URL = os.getenv('APPWRITE_COLLECTION_EXAMEN_PROFESOR_URL')
APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN = os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')
APPWRITE_COLLECTION_EXAMEN_DISPONIBLES =  os.getenv('APPWRITE_COLLECTION_EXAMEN_DISPONIBLES')
APPWRITE_BUCKET_PLANTILLA_EXAMEN_RESPUESTAS = os.getenv('APPWRITE_BUCKET_PLANTILLA_EXAMEN_RESPUESTAS')
FRONTEND_BASE_URL = os.getenv('FRONTEND_URL', 'http://127.0.0.1:8080')


appwrite_client = Client()
appwrite_client.set_endpoint(APPWRITE_ENDPOINT)
appwrite_client.set_project(APPWRITE_PROJECT_ID)
appwrite_client.set_key(APPWRITE_API_KEY)

# Inicializar Storage de Appwrite
storage = Storage(appwrite_client)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/')
def landing_page():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

def procesar_examen(contenido_raw):
    """
    Procesa el texto crudo generado por la IA y lo estructura en un formato útil
    según el tipo de contenido detectado (opción múltiple, preguntas abiertas o casos de uso)
    """
    resultado = {
        "titulo": "Examen Generado",
        "preguntas": []
    }
    
    # Determinar el tipo de contenido
    if re.search(r'\d+\)\s', contenido_raw):  # Detecta formato de opción múltiple
        tipo = "opcion_multiple"
        # Modificar este patrón para separar correctamente las preguntas
        preguntas_raw = re.split(r'\n\s*\d+\)', contenido_raw)
        
        # Procesar cada pregunta individualmente
        for i, pregunta_texto in enumerate(preguntas_raw[1:]):  # Skip first empty element
            # Limpiar la pregunta - Tomar solo la primera línea como texto de la pregunta
            lineas = pregunta_texto.strip().split('\n')
            texto_pregunta = lineas[0].strip()
            
            # Extraer opciones buscando patrones como A), B), C)
            opciones = []
            for j, linea in enumerate(lineas[1:]):
                if re.match(r'[A-E]\)', linea.strip()):
                    opcion_texto = re.sub(r'^[A-E]\)\s*', '', linea.strip())
                    opciones.append(opcion_texto)
            
            pregunta = {
                "id": i + 1,
                "texto": texto_pregunta,
                "opciones": opciones
            }
            resultado["preguntas"].append(pregunta)
    
    elif re.search(r'caso\s*\d+', contenido_raw, re.IGNORECASE) or "caso de uso" in contenido_raw.lower():
        tipo = "caso_uso"
        # Patrón para casos de uso
        casos_raw = re.split(r'\n\s*(?:Caso|CASO)\s*\d+', contenido_raw)
        if len(casos_raw) > 1:
            casos_raw = casos_raw[1:]
            
        for i, caso_texto in enumerate(casos_raw):
            caso = {
                "id": i + 1,
                "texto": caso_texto.strip(),
                "requisitos": re.findall(r'Requisitos?:(.*?)(?=\n\s*\n|\n\s*Sugerencias|$)', caso_texto, re.DOTALL),
                "sugerencias": re.findall(r'Sugerencias?:(.*?)(?=\n\s*\n|$)', caso_texto, re.DOTALL)
            }
            resultado["preguntas"].append(caso)
    
    else:  # Preguntas abiertas por defecto
        tipo = "abierta"
        # Patrón para preguntas abiertas
        preguntas_raw = re.split(r'\n\s*\d+\.', contenido_raw)
        if len(preguntas_raw) > 1:
            preguntas_raw = preguntas_raw[1:]
            
        for i, pregunta_texto in enumerate(preguntas_raw):
            pregunta = {
                "id": i + 1,
                "texto": pregunta_texto.strip()
            }
            resultado["preguntas"].append(pregunta)
            
    # Limitar cantidad de preguntas según el tipo
    if tipo == "opcion_multiple" and len(resultado["preguntas"]) > 10:
        resultado["preguntas"] = resultado["preguntas"][:10]
    elif tipo == "abierta" and len(resultado["preguntas"]) > 5:
        resultado["preguntas"] = resultado["preguntas"][:5]
    elif tipo == "caso_uso" and len(resultado["preguntas"]) > 5:
        resultado["preguntas"] = resultado["preguntas"][:5]
    
    # Asegurar numeración correcta
    for i, pregunta in enumerate(resultado["preguntas"]):
        pregunta["id"] = i + 1
    
    resultado["tipo"] = tipo
    return resultado

@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.path}")
    logger.info(f"Headers: {dict(request.headers)}")
    if request.method == 'POST':
        if request.is_json:
            logger.info(f"JSON Body: {request.json}")
        elif request.files:
            logger.info(f"Files: {list(request.files.keys())}")
        elif request.form:
            logger.info(f"Form Data: {dict(request.form)}")

@app.route('/api/generar-examen', methods=['POST'])
def generar_examen_ia():
    try:
        data = request.json
        prompt = data.get('prompt')
        tipo_pregunta = data.get('tipo_pregunta')
        
        
        num_opcion_multiple = data.get('num_opcion_multiple', 10)  # Valor predeterminado 10
        num_abiertas = data.get('num_abiertas', 5)                # Valor predeterminado 3
        num_casos_uso = data.get('num_casos_uso', 5)              # Valor predeterminado 2
        
        if not prompt:
            return jsonify({"error": "Se requiere prompt y tipo de pregunta"}), 400
            
        # Obtener la API Key de Together.ai desde las variables de entorno
        api_key = os.getenv("TOGETHER_API_KEY")
        print(f"API Key existe: {api_key is not None}")
        print(f"API Key primeros 10 chars: {api_key[:10] if api_key else 'None'}")
        
        if not api_key:
            return jsonify({"error": "Together.ai API key no configurada"}), 500
        
        # Definir prompts específicos según el tipo de pregunta
        prompts_por_tipo = {
            'opcion_multiple': f"""
                Genera EXACTAMENTE 10 preguntas de opción múltiple sobre {prompt} con la siguiente estructura:
                
                - Cada pregunta debe tener un número único (1-10)
                - Exactamente 5 opciones por pregunta etiquetadas usando SOLO este formato preciso:
                  A) Primera opción
                  B) Segunda opción
                  C) Tercera opción
                  D) Cuarta opción
                  E) Quinta opción
                
                RESTRICCIONES CRÍTICAS:
                - Genera EXACTAMENTE 10 preguntas, ni más ni menos
                - Asegúrate de que cada pregunta sea ÚNICA y no se repita en contenido ni formato
                - NO agregues explicaciones adicionales
                - Asegúrate de que las preguntas sean claras y concisas
                - NO incluyas la respuesta correcta marcada
                - Usa numeración secuencial (1, 2, 3, ...) para las preguntas
            """,
            
            'abierta': f"""
                Genera EXACTAMENTE 5 preguntas abiertas (de desarrollo) sobre {prompt} con la siguiente estructura:
                
                - Cada pregunta debe tener un número único (1-5)
                - Las preguntas deben requerir respuestas desarrolladas
                - Nivel de dificultad variado (básico, intermedio, avanzado)
                
                RESTRICCIONES CRÍTICAS:
                - Genera EXACTAMENTE 5 preguntas, ni más ni menos
                - Asegúrate de que cada pregunta sea ÚNICA y no se repita en contenido con las otras
                - NO repetir o duplicar preguntas en diferentes formatos
                - NO agregues explicaciones adicionales
                - Asegúrate de que las preguntas sean claras y requieran análisis
                - Usa numeración secuencial (1, 2, 3, ...) para las preguntas
            """,
            
            'caso_uso': f"""
                Genera EXACTAMENTE 5 casos de uso prácticos sobre {prompt} con la siguiente estructura:
                
                - Cada caso debe tener un número único (1-5)
                - Incluye un escenario práctico detallado relacionado con {prompt}
                - Requisitos específicos de lo que debe implementar el estudiante
                - Sugerencias de herramientas o enfoques que podría utilizar
                
                RESTRICCIONES CRÍTICAS:
                - Genera EXACTAMENTE 5 casos de uso, ni más ni menos
                - Asegúrate de que cada caso sea ÚNICO y completamente diferente del otro
                - NO repetir escenarios ni requisitos entre los casos
                - NO agregues explicaciones adicionales
                - Asegúrate de que los casos sean relevantes, realistas y detallados
                - Usa numeración secuencial (1, 2) para los casos 
            """
        }
        
        # Seleccionar el prompt adecuado según el tipo
        prompt_completo = prompts_por_tipo.get(tipo_pregunta)
        
        if not prompt_completo:
            return jsonify({"error": "Tipo de pregunta no válido"}), 400
        
        # Obtener el modelo seleccionado del request, usar deepseek-v3 como valor predeterminado
        modelo_seleccionado = data.get('modelo_ia', 'deepseek-v3')
        print(f"Modelo recibido: {modelo_seleccionado}")
        config_modelo = modelos.get(modelo_seleccionado)
        # Agregar esta lógica:
        if config_modelo is None:
            # Buscar por model_id si no se encuentra por clave
            for _, config in modelos.items():
                if config.get('model_id') == modelo_seleccionado:
                    config_modelo = config
                    break
        print(f"Config modelo: {config_modelo}")
        
        # Si no está en el diccionario `modelos`, verificar si es OpenRouter (sin afectar los demás)
        if config_modelo is None:
            if modelo_seleccionado in MODELOS_TEXTO_OPENROUTER + MODELOS_MULTIMODAL_OPENROUTER:
                config_modelo = modelos.get('openrouter-generic', {}).copy()
                config_modelo['model_id'] = modelo_seleccionado
                
        # Si aún no se reconoce el modelo, devolver error claro
        if config_modelo is None:
            return jsonify({"error": f"Modelo '{modelo_seleccionado}' no encontrado o no soportado"}), 400        
        
        #if not config_modelo:
            #return jsonify({"error": f"Modelo '{modelo_seleccionado}' no encontrado"}), 400

        if config_modelo.get('activo') is False:
            return jsonify({"error": "Modelo no activado - Por favor contacte al administrador"}), 400

        # Obtener la API Key desde las variables de entorno según el proveedor
        api_key_env = config_modelo.get('api_key_env')
        api_key = os.getenv(api_key_env)

        if not api_key:
            return jsonify({"error": f"API key para {modelo_seleccionado} no configurada"}), 500

        # Definir prompts específicos según el tipo de pregunta
        # [Mantener el código de prompts_por_tipo que ya tienes]

        # Seleccionar el prompt adecuado según el tipo
        prompt_completo = prompts_por_tipo.get(tipo_pregunta)

        if not prompt_completo:
            return jsonify({"error": "Tipo de pregunta no válido"}), 400

        # Configurar solicitud según el proveedor de API
        api_provider = config_modelo.get('api')
        model_id = config_modelo.get('model_id')

        if api_provider == 'together':
            # API de Together.ai
            url = "https://api.together.xyz/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "Eres un asistente especializado en crear exámenes educativos."},
                    {"role": "user", "content": prompt_completo}
                ],
                "max_tokens": 4000,
                "temperature": 0.7
            }
            
        elif api_provider == 'openai':
            # API de OpenAI
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "Eres un asistente especializado en crear exámenes educativos."},
                    {"role": "user", "content": prompt_completo}
                ],
                "max_tokens": 4000,
                "temperature": 0.7
            }
            
        elif api_provider == 'anthropic':
            # API de Anthropic
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
            payload = {
                "model": model_id,
                "messages": [
                    {"role": "user", "content": prompt_completo}
                ],
                "max_tokens": 4000,
                "system": "Eres un asistente especializado en crear exámenes educativos."
            }
            
        elif api_provider == 'google':
            # API de Google Gemini
            url = "https://generativelanguage.googleapis.com/v1beta/models/" + model_id + ":generateContent"
            headers = {
                "Content-Type": "application/json"
            }
            # Añadir clave API como parámetro en la URL
            url += f"?key={api_key}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt_completo}]
                    }
                ],
                "generation_config": {
                    "temperature": 0.7,
                    "maxOutputTokens": 4000
                }
            }
            
        elif api_provider == 'openrouter':
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost:8080",  # Requerido por OpenRouter si usas plan free
                "X-Title": "GeneradorExamenIA"            # Título del proyecto visible en OpenRouter
            }
            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "Eres un asistente especializado en crear exámenes educativos."},
                    {"role": "user", "content": prompt_completo}
                ],
                "max_tokens": 2048,
                "temperature": 0.7,
                "HTTP-Referer": "http://localhost:8080",  # Requerido por OpenRouter si usas plan free
                "X-Title": "GeneradorExamenIA"            # Título del proyecto visible en OpenRouter
            }

        else:
            return jsonify({"error": f"Proveedor de API '{api_provider}' no soportado"}), 400

        # Realizar la solicitud HTTP a la API correspondiente
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        response.raise_for_status()

        # Procesar la respuesta según el proveedor de API
        if api_provider == 'together' or api_provider == 'openai':
            result = response.json()
            contenido_raw = result["choices"][0]["message"]["content"] if "choices" in result and result["choices"] else ""
        elif api_provider == 'anthropic':
            result = response.json()
            contenido_raw = result["content"][0]["text"] if "content" in result and result["content"] else ""
        elif api_provider == 'google':
            result = response.json()
            contenido_raw = result["candidates"][0]["content"]["parts"][0]["text"] if "candidates" in result and result["candidates"] else ""
        elif api_provider == 'openrouter':
            result = response.json()
            if "choices" in result and result["choices"]:
                contenido_raw = result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"Respuesta inválida de OpenRouter: {json.dumps(result)}")

        # Procesar el contenido para estructurarlo mejor
        #examen_estructurado = procesar_examen(contenido_raw)
                
        #response = requests.post(url, headers=headers, json=payload)
        #response.raise_for_status()
                
        #result = response.json()
        # La estructura de respuesta es diferente en la API de chat
        #contenido_raw = result["choices"][0]["message"]["content"] if "choices" in result and result["choices"] else ""
                
        # Procesar el contenido para estructurarlo mejor
        examen_estructurado = procesar_examen(contenido_raw)
                
        # Obtener el examenId enviado por el frontend
        examen_id = data.get('examenId') # Intenta obtenerlo del JSON inicial

        # Si por alguna razón no vino, genera uno (opcional)
        if not examen_id:
                    
            examen_id = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                
            return jsonify({
                    "examen": True, 
                    "examenId": examen_id,
                    "contenido": contenido_raw,
                    "examen_estructurado": examen_estructurado,
                    "titulo": examen_estructurado.get("titulo", "Examen Generado")
                })
                
    except Exception as e:
                logger.error(traceback.format_exc())
                return jsonify({"error": str(e)}), 500
    
@app.route('/api/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    # --- Verificación inicial (sin cambios) ---
    if 'file' not in request.files:
        logger.warning("No se encontró 'file' en request.files")
        return jsonify({'error': 'No se proporcionó ningún archivo'}), 400

    upload_file = request.files['file']
    if not upload_file or not upload_file.filename:
        logger.warning("Archivo recibido pero sin nombre de archivo válido.")
        return jsonify({'error': 'Nombre de archivo inválido o archivo vacío'}), 400

    # --- Obtener datos adicionales del formulario (sin cambios) ---
    examen_id = request.form.get('examenId')
    caso_numero = request.form.get('casoNumero')
    nombre_alumno = request.form.get('nombreAlumno')
    id_alumno = request.form.get('idAlumno')
    student_filename = upload_file.filename # Guardar nombre original
    logger.info(f"Recibida solicitud de subida para examen: {examen_id}, caso: {caso_numero}, alumno: {id_alumno} ({nombre_alumno}), archivo: {student_filename}")

    # --- Validación de extensión (sin cambios) ---
    allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}
    filename_lower = student_filename.lower()
    if '.' not in filename_lower or filename_lower.rsplit('.', 1)[1] not in allowed_extensions:
        logger.warning(f"Intento de subir archivo con extensión no permitida: {student_filename}")
        return jsonify({'error': 'Tipo de archivo no permitido. Solo PDF, JPG, PNG, DOC, DOCX'}), 400

    new_filename = None # O podrías usar new_filename = ""
    try:
        # --- Lógica de Appwrite para subir ---

        # 1. Inicializar Cliente Appwrite
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT)
        client.set_project(APPWRITE_PROJECT_ID)
        client.set_key(APPWRITE_API_KEY)
        storage_service = Storage(client)

        # 2. Definir el Bucket ID de destino
        target_bucket_id = '67e579bd0018f15c73c3' # Bucket examen_alumno_documento
        
        # --- INICIO: Construcción del nuevo nombre de archivo ---
        # Separar el nombre base y la extensión del archivo original (USANDO student_filename)
        base_name, extension = os.path.splitext(student_filename) # <-- Usa student_filename

        # Limpiar el nombre base original (reemplazar espacios)
        safe_base_name = base_name.replace(' ', '_')

        # Crear el nuevo nombre del archivo: examenId_idAlumno_casoNum_nombreBaseOriginalLimpio.extension
        new_filename = f"{str(examen_id)}_{str(id_alumno)}_{str(caso_numero)}_{safe_base_name}{extension}"

        # Actualizamos el log para indicar qué nombre se usará para guardar
        logger.info(f"Nombre original (student_filename): '{student_filename}', Nuevo nombre para guardar: '{new_filename}'")
        # --- FIN: Construcción del nuevo nombre de archivo ---

        # 3. Preparar el archivo para Appwrite
        # Leemos el contenido del archivo UNA SOLA VEZ
        file_bytes = upload_file.read()
        
        # Opcional: Verificar si realmente se leyeron bytes
        if not file_bytes:
             logger.warning(f"El archivo '{student_filename}' parece estar vacío o no se pudo leer correctamente. Se subirá como archivo vacío.")
             # Considera si quieres devolver un error aquí en lugar de subir un archivo vacío
        
        
        # Usamos ID.unique() para la llamada API, pero pasamos el nombre original
        appwrite_api_call_id = ID.unique()
        
        # Creamos InputFile USANDO los bytes que ya leímos
        appwrite_file = InputFile.from_bytes(
            file_bytes,             # <--- USA LA VARIABLE file_bytes
            #upload_file.filename, # <--- ESTA ES LA LÍNEA A CAMBIAR
            new_filename,         # <--- USA EL NUEVO NOMBRE CONSTRUIDO
            upload_file.content_type
        )


        # 4. Llamar a Appwrite para crear el archivo
        logger.info(f"Intentando subir '{student_filename}' a Appwrite Bucket ID: {target_bucket_id} con API Call ID: {appwrite_api_call_id}")
        result_storage = storage_service.create_file(
            bucket_id=target_bucket_id,
            file_id=appwrite_api_call_id, # Usar el ID único para la llamada
            file=appwrite_file
            # Añadir permisos si es necesario
        )

        # 5. Obtener el ID REAL único asignado por Appwrite
        actual_file_id = result_storage['$id']
        logger.info(f"Archivo '{student_filename}' subido exitosamente a Appwrite. ID asignado: {actual_file_id}")

        # 6. (Opcional) Generar URL de vista si el frontend la necesita inmediatamente
        file_url_str = None
        try:
            file_view_url_obj = storage_service.get_file_view(target_bucket_id, actual_file_id)
            file_url_str = str(file_view_url_obj)
            logger.info(f"URL de vista generada: {file_url_str}")
        except Exception as url_error:
            logger.warning(f"No se pudo generar la URL de vista para el archivo {actual_file_id}: {url_error}")


        # 7. Devolver respuesta JSON al frontend (IMPORTANTE: devolver actual_file_id)
        return jsonify({
            'success': True,
            'fileId': actual_file_id,  # <-- ID ÚNICO de Appwrite para que el frontend lo use (ej: para borrar)
            'examenId': examen_id,
            'casoNumero': caso_numero,
            'fileUrl': file_url_str,     # URL opcional
            'publicUrl': file_url_str    # Clave 'publicUrl' con la misma URL opcional
        })

    except AppwriteException as ae:
        # Usa new_filename directamente, sabiendo que al menos es None si falló antes
        log_filename_attempt = new_filename if new_filename else "[Renombrado no completado]"
        logger.error(f"Error de Appwrite al subir archivo (original: '{student_filename}', intento: '{log_filename_attempt}'): {ae.message} (Código: {ae.code}, Tipo: {ae.type})", exc_info=True)
        return jsonify({'error': f'Error del servidor (Appwrite) al subir archivo: {ae.message}'}), 500
    
    except Exception as e:
        # Usa new_filename directamente, sabiendo que al menos es None si falló antes
        log_filename_attempt = new_filename if new_filename else "[Renombrado no completado]"
        logger.error(f"Error de Appwrite al subir archivo (original: '{student_filename}', intento: '{log_filename_attempt}'): {ae.message} (Código: {ae.code}, Tipo: {ae.type})", exc_info=True)
        return jsonify({'error': f'Error interno del servidor al subir archivo: {str(e)}'}), 500

@app.route('/api/publishPlantilla', methods=['POST'])
def publish_plantilla():
    
    print(f"[DEBUG] Datos completos recibidos: {request.get_json()}")  # ← AGREGAR ESTA LÍNEA

    try:
        data = request.get_json(force=True)
        print("💬 JSON recibido:", data)
        plantilla_data = data.get('plantilla_data')
        config = data.get('config', {})
        
        if not plantilla_data:
            return jsonify({"error": "Se requieren datos del plantilla del examen"}), 400
        
        # Generar un ID único para la publicación
        publication_id = str(uuid.uuid4())[:8]
        
        # Estructura para guardar
        publication = {
            "id": publication_id,
            "examenData": plantilla_data,
            "createdAt": datetime.datetime.now().isoformat(),
            "expiration": config.get('expiration'),
            "publicAccess": config.get('publicAccess', True)
        }
        
        # Aquí implementaríamos el almacenamiento del examen
        # Para desarrollo local, lo guardamos en un archivo JSON
        publications_dir = os.path.join(os.path.dirname(__file__), 'publications')
        if not os.path.exists(publications_dir):
            os.makedirs(publications_dir)
            
        file_path = os.path.join(publications_dir, f"{publication_id}.json")
        
        with open(file_path, 'w') as f:
            json.dump(publication, f)
        
        # Generar URL para acceso
        # En producción, esto sería tu URL de Google Run
        base_url = "http://127.0.0.1:5000"  # Para desarrollo local
        access_url = f"{base_url}/plantilla/{publication_id}"
        
        return jsonify({
            "success": True,
            "publicationId": publication_id,
            "url": access_url,
            "expiration": config.get('expiration')
        })
        
    except Exception as e:
        logger.error(f"Publication error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# --- REEMPLAZA LA FUNCIÓN publish_exam CON ESTO ---
@app.route('/api/publish', methods=['POST'])
def publish_exam():
    print("🔥🔥🔥 PUBLISH_EXAM EJECUTÁNDOSE 🔥🔥🔥")  # ← AGREGAR
    logger.info("🔥🔥🔥 PUBLISH_EXAM EJECUTÁNDOSE 🔥🔥🔥")  # ← AGREGAR
    logger.info("Recibida petición en /api/publish")
    logger.info("Recibida petición en /api/publish")
    try:
        # 1. Inicializar Cliente Appwrite
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT)
        client.set_project(APPWRITE_PROJECT_ID)
        client.set_key(APPWRITE_API_KEY)
        databases = Databases(client)

        # 2. Obtener datos del request
        data = request.json
        if not data or 'examenData' not in data:
            logger.warning("Request JSON inválido o falta 'examenData'")
            return jsonify({"error": "Faltan datos del examen en la solicitud"}), 400
        
        examen_data = data['examenData']
        
        # DEBUG: Verificar que archivos adjuntos se están guardando
        print(f"[DEBUG PUBLISH] Guardando examen {examen_data.get('id')}:")
        for i, pregunta in enumerate(examen_data.get('preguntasLibres', [])):
            print(f"  Pregunta {i+1} archivoId: {pregunta.get('archivoId')}")
            
            # Corregir URLs de archivos adjuntos antes de guardar
            for pregunta in examen_data.get('preguntasLibres', []):
                if pregunta.get('archivoUrl') and 'APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN' in pregunta['archivoUrl']:
                    pregunta['archivoUrl'] = pregunta['archivoUrl'].replace(
                        'APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN', 
                        os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')
                    )
                    print(f"[DEBUG] URL corregida para pregunta: {pregunta['archivoUrl']}")

            for caso in examen_data.get('casosUso', []):
                if caso.get('archivoUrl') and 'APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN' in caso['archivoUrl']:
                    caso['archivoUrl'] = caso['archivoUrl'].replace(
                        'APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN', 
                        os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')
                    )
                    print(f"[DEBUG] URL corregida para caso: {caso['archivoUrl']}")
        
        # AGREGAR AQUÍ: Procesar archivos adjuntos antes de guardar
        # Asegurar que se mantenga la información de archivos adjuntos
        for pregunta in examen_data.get('preguntasLibres', []):
            if pregunta.get('archivoId'):
                # Mantener toda la información del archivo adjunto
                pregunta['archivoNombre'] = pregunta.get('archivoNombre', '')
                pregunta['archivoUrl'] = pregunta.get('archivoUrl', '')
                pregunta['archivoTamaño'] = pregunta.get('archivoTamaño', 0)
                pregunta['archivoTipo'] = pregunta.get('archivoTipo', '')

        for caso in examen_data.get('casosUso', []):
            if caso.get('archivoId'):
                # Mantener toda la información del archivo adjunto
                caso['archivoNombre'] = caso.get('archivoNombre', '')
                caso['archivoUrl'] = caso.get('archivoUrl', '')
                caso['archivoTamaño'] = caso.get('archivoTamaño', 0)
                caso['archivoTipo'] = caso.get('archivoTipo', '')

        # 3. Obtener/Validar ID del examen
        examen_id = examen_data.get('id')
        

        # 3. Obtener/Validar ID del examen
        examen_id = examen_data.get('id')
        if not examen_id:
            examen_id = str(uuid.uuid4())[:8]
            examen_data['id'] = examen_id
        
        logger.info(f"Procesando publicación para examen ID: {examen_id}")

        # 4. Generar la URL del Frontend
        access_url = f"http://127.0.0.1:5000/examen/{examen_id}"
        logger.info(f"URL del frontend generada: {access_url}")

        # 5. Preparar los datos para guardar en el formato requerido por la colección
        datos_para_guardar = {
            "email": data.get('email'),  # ← AGREGAR ESTA LÍNEA email
            "id_examen": examen_id,
            "id_profesor": examen_data.get('profesorId', 'PROF_INDEFINIDO'),
            "nombre_profesor": examen_data.get('profesor', 'N/A'),
            "nombre_examen": examen_data.get('nombreExamen', f"Examen {examen_id}"),
            "url_examen": access_url,
            "fecha_emision": datetime.datetime.now().isoformat(),
            "examenDataJson": json.dumps(examen_data)  # Guardar examen completo como JSON
        }

        # 6. Guardar o Actualizar en Appwrite (probando primero si existe)
        try:
            # No intentaremos buscar el documento por examen_id
            # En su lugar, creamos un nuevo registro cada vez
            link_id = f"link_{examen_id}_{int(time.time())}"
            
            # Agregar ANTES de databases.create_document():
            logger.info(f"Datos a guardar: {json.dumps(datos_para_guardar, indent=2)}")
            logger.info(f"Database ID: {APPWRITE_DATABASE_ID}")
            logger.info(f"Collection ID: {APPWRITE_COLLECTION_EXAMEN_PROFESOR_URL}")
            logger.info(f"Document ID que se usará: {link_id}")
            
            # Crear documento con un ID único
            result = databases.create_document(
                database_id=APPWRITE_DATABASE_ID,
                collection_id=APPWRITE_COLLECTION_EXAMEN_PROFESOR_URL,
                document_id=link_id,
                data=datos_para_guardar
            )
            logger.info(f"Examen guardado con ID: {link_id}")
            logger.info(f"Documento creado exitosamente - ID: {result['$id']}")
            logger.info(f"URL guardada en Appwrite: {result.get('url_examen')}")
        except AppwriteException as ae:
            logger.error(f"Error Appwrite al guardar: Código={ae.code}, Tipo={ae.type}, Mensaje={ae.message}")
            raise Exception(f"Error Appwrite: {ae.message}")
        except Exception as create_error:
            logger.error(f"Error general al guardar examen: {create_error}", exc_info=True)
            raise Exception(f"Error de base de datos al guardar: {str(create_error)}")

        # 7. Devolver respuesta exitosa al Frontend
        return jsonify({
            "success": True,
            "publicationId": examen_id,
            "url": access_url
        })

    except Exception as e:
        logger.error(f"Error crítico en /api/publish: {e}", exc_info=True)
        return jsonify({'error': f'Error interno del servidor al publicar: {str(e)}'}), 500
    
@app.route('/examen.html')
def serve_student_exam():
    try:
        # Obtener el ID del examen de la URL
        examen_id = request.args.get('id')
        if not examen_id:
            return "Error: No se proporcionó un ID de examen", 400
        
        # Redireccionar a la aplicación Vue.js principal con el ID
        return redirect(f"{FRONTEND_BASE_URL}/#/examen?id={examen_id}")
        
    except Exception as e:
        logger.error(f"Error al redireccionar al examen: {str(e)}")
        return f"Error al redireccionar al examen: {str(e)}", 500


@app.route('/api/examen/<examen_id>', methods=['GET'])
def get_examen_data(examen_id):
    try:
        # Inicializar cliente Appwrite
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT)
        client.set_project(APPWRITE_PROJECT_ID)
        client.set_key(APPWRITE_API_KEY)
        databases = Databases(client)
        
        logger.info(f"Buscando examen con ID: {examen_id}")
        
        # Usar el formato correcto de consulta para Appwrite
        response = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_EXAMEN_PROFESOR_URL,
            queries=[
                Query.equal("id_examen", examen_id)
            ]
        )
        
        # Verificar si se encontró algún documento
        if len(response['documents']) == 0:
            logger.error(f"No se encontró examen con ID: {examen_id}")
            return jsonify({
                "error": "No se encontró el examen con el ID proporcionado"
            }), 404
            
        # Obtener el primer documento (debería ser el único)
        examen_doc = response['documents'][0]
        
        # Extraer los datos del examen desde el JSON almacenado
        examen_data = json.loads(examen_doc['examenDataJson'])
        
        # DEBUG: Verificar archivos adjuntos
        for i, pregunta in enumerate(examen_data.get('preguntasLibres', [])):
            print(f"[DEBUG] Pregunta {i+1}:")
            print(f"  - archivoId: {pregunta.get('archivoId')}")
            print(f"  - archivoUrl: {pregunta.get('archivoUrl')}")
            print(f"  - archivoNombre: {pregunta.get('archivoNombre')}")
        
        # AGREGAR DEBUG AQUÍ:
        print(f"[DEBUG] Datos cargados para examen {examen_id}:")
        print(f"[DEBUG] preguntasLibres: {examen_data.get('preguntasLibres', [])}")
        
        # AGREGAR ESTE BLOQUE COMPLETO AQUÍ:
        # Corregir URLs de archivos adjuntos al cargar
        for pregunta in examen_data.get('preguntasLibres', []):
            if pregunta.get('archivoUrl') and 'APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN' in pregunta['archivoUrl']:
                pregunta['archivoUrl'] = pregunta['archivoUrl'].replace(
                    'APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN', 
                    os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')
                ).replace(
                    '67e565df00172171560',  # Project ID incorrecto
                    os.getenv('APPWRITE_PROJECT_ID')
                )
                print(f"[DEBUG] URL corregida pregunta: {pregunta['archivoUrl']}")

        for caso in examen_data.get('casosUso', []):
            if caso.get('archivoUrl') and 'APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN' in caso['archivoUrl']:
                caso['archivoUrl'] = caso['archivoUrl'].replace(
                    'APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN', 
                    os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')
                ).replace(
                    '67e565df00172171560',  # Project ID incorrecto
                    os.getenv('APPWRITE_PROJECT_ID')
                )
                print(f"[DEBUG] URL corregida caso: {caso['archivoUrl']}")
        
        # Devolver los datos del examen como JSON
        return jsonify({
            "success": True,
            "examenDataJson": examen_doc['examenDataJson'] 
        })
        
    except Exception as e:
        logger.error(f"Error al obtener datos del examen: {str(e)}", exc_info=True)
        return jsonify({
            "error": f"Error al cargar el examen: {str(e)}"
        }), 500  


@app.route('/examen/<examen_id>', methods=['GET'])
def mostrar_examen_estudiante(examen_id):
    try:
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT)
        client.set_project(APPWRITE_PROJECT_ID)
        client.set_key(APPWRITE_API_KEY)
        databases = Databases(client)
        
        result = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_EXAMEN_PROFESOR_URL,
            queries=[Query.equal('id_examen', examen_id)]
        )
        
        if result['total'] == 0:
            return "<h1>Examen no encontrado</h1>"
        
        documento = result['documents'][0]
        examen_data = json.loads(documento['examenDataJson'])
        
        # Calcular puntaje total=====================================
        puntaje_total = 0
        for pregunta in examen_data.get('preguntasMarcar', []):
            puntaje_total += float(pregunta.get('puntaje', 0))
        for pregunta in examen_data.get('preguntasLibres', []):
            puntaje_total += float(pregunta.get('puntaje', 0))
        for caso in examen_data.get('casosUso', []):
            puntaje_total += float(caso.get('puntaje', 0))
        #=============================================================
        
        # FORMULARIO CON DATOS DEL ALUMNO
        formulario_alumno = f"""
        <form method="POST" action="/submit-exam" enctype="multipart/form-data">
            <input type="hidden" name="examenId" value="{examen_id}">
            <input type="hidden" name="id_profesor" value="{examen_data.get('profesorId', '')}">
            <input type="hidden" name="nombre_profesor" value="{examen_data.get('profesor', '')}">
            <input type="hidden" name="nombre_examen" value="{examen_data.get('nombreExamen', '')}">
            <input type="hidden" name="tipo_examen" value="{examen_data.get('tipoExamen', 'Evaluación')}">
            
            <div class="datos-alumno">
                <h3>Datos del Alumno</h3>
                <div class="campo">
                    <label for="id_alumno"><strong>ID del Alumno:</strong></label>
                    <input type="text" id="id_alumno" name="id-alumno" required>
                </div>
                <div class="campo">
                    <label for="nombre_alumno"><strong>Nombre del Alumno:</strong></label>
                    <input type="text" id="nombre_alumno" name="nombreAlumno" required>
                </div>
            </div>
        """
        
        # GENERAR HTML DE PREGUNTAS
        contenido_preguntas = ""
        numero_pregunta_global = 1  # ← AGREGAR ESTA VARIABLE
        
        # Preguntas de opción múltiple
        if examen_data.get('preguntasMarcar'):
            contenido_preguntas += "<h2>Preguntas de Opción Múltiple</h2>"
            for i, pregunta in enumerate(examen_data['preguntasMarcar']):
                texto_pregunta = limpiar_markdown(pregunta.get('texto', ''))
                
                contenido_preguntas += f"""
                <div class="pregunta">
                    <div style="margin-bottom: 15px; font-weight: bold; color: #2c3e50;">
                        {numero_pregunta_global}. ({pregunta.get('puntaje', 1)} pts) {texto_pregunta}
                    </div>
                    <div class="opciones" style="margin-left: 20px; line-height: 1.8;">
                """
                for j, opcion in enumerate(pregunta.get('opciones', [])):
                    letra = chr(65 + j)  # A, B, C, D, E
                    
                    # MANEJAR AMBOS FORMATOS Y UNIFICAR
                    if isinstance(opcion, dict):
                        texto_opcion = opcion.get('texto', '')
                    else:
                        texto_opcion = str(opcion)
                    
                    # LIMPIAR texto: quitar (A), (B), etc. del inicio si existen
                    import re
                    texto_limpio = re.sub(r'^\([A-E]\)\s*', '', texto_opcion.strip())
                    
                    contenido_preguntas += f"""
                        <div class="opcion" style="margin: 8px 0; padding: 5px;">
                            <label style="cursor: pointer; display: flex; align-items: center;">
                                <input type="radio" name="pregunta-{numero_pregunta_global}" value="{j}" style="margin-right: 10px;">
                                <span style="font-weight: bold; margin-right: 8px;">{letra})</span>
                                <span>{texto_limpio}</span>
                            </label>
                        </div>
                    """
                contenido_preguntas += """
                    </div>
                </div>
                """
                numero_pregunta_global += 1  # ← INCREMENTAR
        
        # Preguntas libres
        if examen_data.get('preguntasLibres'):
            contenido_preguntas += "<h2>Preguntas de Desarrollo</h2>"
            for i, pregunta in enumerate(examen_data['preguntasLibres']):
                texto_limpio = limpiar_markdown(pregunta.get('texto', ''))
                contenido_preguntas += f"""
                <div class="pregunta">
                    <div style="margin-bottom: 15px; font-weight: bold; color: #2c3e50;">
                        {numero_pregunta_global}. ({pregunta.get('puntaje', 5)} pts) {texto_limpio}
                    </div>
                """
                if pregunta.get('archivoNombre'):
                    contenido_preguntas += f"""
                    <p><a href="{pregunta.get('archivoUrl', '')}" target="_blank">📎 {pregunta.get('archivoNombre', '')}</a></p>
                    """
                contenido_preguntas += f"""
                    <div style="background: #fff3cd; padding: 8px; margin: 8px 0; border-left: 4px solid #ffc107; font-size: 0.9em;">
                📝 <strong>Importante:</strong> Si adjunta archivo, nómbrelo como: <code>[ID_Examen]_[ID_Alumno]</code><br>
                <strong>Ejemplo:</strong> <code>{examen_id}_[TU_ID_ALUMNO].pdf</code>
            </div>
                    <textarea name="libre-{numero_pregunta_global}" placeholder="Escriba su respuesta aquí..." rows="6" 
                            class="protected-textarea"
                            spellcheck="false"
                            autocomplete="off"
                            style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 5px; font-family: Arial, sans-serif; line-height: 1.5;"></textarea>
                    <div class="archivo-upload">
                        <label>Adjuntar archivo (opcional):</label>
                        <input type="file" name="archivo-libre-{numero_pregunta_global}" accept=".pdf,.doc,.docx,.jpg,.png" onchange="mostrarArchivo(this)">
                        <div id="archivo-info-libre-{numero_pregunta_global}" style="display:none; margin-top: 10px; padding: 8px; background: #e8f5e8; border-radius: 5px;">
                            <span id="nombre-archivo-libre-{numero_pregunta_global}"></span>
                            <button type="button" onclick="eliminarArchivo('libre-{numero_pregunta_global}')" style="margin-left: 10px; background: none; border: none; color: red; cursor: pointer; font-size: 16px;" title="Eliminar archivo">🗑️</button>
                        </div> 
                    </div>        
                </div>
                """
                numero_pregunta_global += 1  # ← INCREMENTAR
        
        # Casos de uso
        if examen_data.get('casosUso'):
            contenido_preguntas += "<h2>Casos de Uso</h2>"
            for i, caso in enumerate(examen_data['casosUso']):
                descripcion_raw = limpiar_markdown(caso.get('descripcion', ''))
                pregunta_raw = limpiar_markdown(caso.get('pregunta', ''))
                
                # FORMATEAR DESCRIPCIÓN CON SALTOS DE LÍNEA
                descripcion_formateada = descripcion_raw.replace('**Escenario:**', '<br><strong>Escenario:</strong>')
                descripcion_formateada = descripcion_formateada.replace('**Requisitos:**', '<br><br><strong>Requisitos:</strong>')
                descripcion_formateada = descripcion_formateada.replace('**Sugerencias:**', '<br><br><strong>Sugerencias:</strong>')
                
                # FORMATEAR PREGUNTAS CON SALTOS DE LÍNEA
                pregunta_formateada = pregunta_raw.replace('**Preguntas:**', '<br><strong>Preguntas:</strong>')
                pregunta_formateada = pregunta_formateada.replace('1.', '<br>1.')
                pregunta_formateada = pregunta_formateada.replace('2.', '<br>2.')
                pregunta_formateada = pregunta_formateada.replace('3.', '<br>3.')
                pregunta_formateada = pregunta_formateada.replace('4.', '<br>4.')
                pregunta_formateada = pregunta_formateada.replace('5.', '<br>5.')
        
                contenido_preguntas += f"""
                <div class="pregunta">
                    <p><strong>{numero_pregunta_global}. ({caso.get('puntaje', 10)} pts)</strong></p>
                    <div style="margin: 15px 0; line-height: 1.6;">
                        <strong>Descripción:</strong>{descripcion_formateada}
                    </div>
                    <div style="margin: 15px 0; line-height: 1.6;">
                        <strong>Pregunta:</strong>{pregunta_formateada}
                    </div>
                """
                if caso.get('archivoNombre'):
                    contenido_preguntas += f"""
                    <p><a href="{caso.get('archivoUrl', '')}" target="_blank">📎 {caso.get('archivoNombre', '')}</a></p>
                    """
                contenido_preguntas += f"""
                    <div style="background: #fff3cd; padding: 8px; margin: 8px 0; border-left: 4px solid #ffc107; font-size: 0.9em;">
                        📝 <strong>Importante:</strong> Si adjunta archivo, nómbrelo como: <code>[ID_Examen]_[ID_Alumno]</code><br>
                        <strong>Ejemplo:</strong> <code>{examen_id}_[TU_ID_ALUMNO].pdf</code>
                    </div>
                    <textarea name="caso-{numero_pregunta_global}" placeholder="Escriba su respuesta aquí..." rows="8"
                            class="protected-textarea"
                            spellcheck="false"
                            autocomplete="off"></textarea>
                    <div class="archivo-upload">
                        <label>Adjuntar archivo (opcional):</label>
                        <input type="file" name="archivo-caso-{numero_pregunta_global}" accept=".pdf,.doc,.docx,.jpg,.png" onchange="mostrarArchivo(this)">
                        <div id="archivo-info-caso-{numero_pregunta_global}" style="display:none; margin-top: 10px; padding: 8px; background: #e8f5e8; border-radius: 5px;">
                            <span id="nombre-archivo-caso-{numero_pregunta_global}"></span>
                            <button type="button" onclick="eliminarArchivo('caso-{numero_pregunta_global}')" style="margin-left: 10px; background: none; border: none; color: red; cursor: pointer; font-size: 16px;" title="Eliminar archivo">🗑️</button>
                        </div>
                    </div>
                </div>
                """
                numero_pregunta_global += 1  # ← INCREMENTAR
        
        # BOTÓN DE ENVÍO
        boton_envio = """
            <div class="envio-container">
                <button type="submit" class="btn-enviar">Enviar Examen</button>
            </div>
        </form>
        """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{examen_data.get('nombreExamen', 'Examen')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
                h1 {{ text-align: center; color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #2980b9; margin-top: 30px; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }}
                h3 {{ color: #34495e; margin-top: 20px; }}
                .info-examen {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 25px; }}
                .datos-alumno {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin-bottom: 25px; }}
                .campo {{ margin-bottom: 15px; }}
                .campo label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                .campo input[type="text"] {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 3px; }}
                .pregunta {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background: #f9f9f9; }}
                .opciones {{ margin: 10px 0; }}
                .opcion {{ margin: 8px 0 8px 20px; }}
                textarea {{ width: 100%; height: 100px; margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 3px; resize: vertical; }}
                .archivo-upload {{ margin-top: 10px; }}
                .archivo-upload label {{ display: block; margin-bottom: 5px; }}
                .archivo-upload input[type="file"] {{ width: 100%; padding: 5px; }}
                .envio-container {{ text-align: center; margin-top: 40px; }}
                .btn-enviar {{ background: #27ae60; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }}
                .btn-enviar:hover {{ background: #219a52; }}

            </style>
        </head>
        <body>
            <h1>{examen_data.get('nombreExamen', 'Examen')}</h1>
            
            <div class="info-examen">
                <p><strong>Profesor:</strong> {examen_data.get('profesor', '')}</p>
                <p><strong>ID del Examen:</strong> {examen_id}</p>
                <p><strong>ID del Profesor:</strong> {examen_data.get('profesorId', '')}</p>
                <p><strong>Tipo de Examen:</strong> {examen_data.get('tipoExamen', 'Evaluación')}</p>
                <p><strong>Puntaje Total:</strong> {puntaje_total} pts</p>  <!-- ← AGREGAR ESTA LÍNEA -->
            </div>
            
            {formulario_alumno}
            {contenido_preguntas}
            {boton_envio}
            
            <div style="text-align: center; margin-top: 40px; color: #7f8c8d;">
                <p>Sistema de Exámenes en Línea</p>
            </div>
            
           <script>
            function mostrarArchivo(input) {{
                const inputName = input.name;
                const preguntaId = inputName.replace('archivo-', '');
                const infoDiv = document.getElementById('archivo-info-' + preguntaId);
                const nombreSpan = document.getElementById('nombre-archivo-' + preguntaId);
                
                if (input.files && input.files[0]) {{
                    const archivo = input.files[0];
                    nombreSpan.innerHTML = '📎 <strong>' + archivo.name + '</strong>';
                    infoDiv.style.display = 'block';
                }}
            }}

            function eliminarArchivo(preguntaId) {{
                const input = document.querySelector('input[name="archivo-' + preguntaId + '"]');
                const infoDiv = document.getElementById('archivo-info-' + preguntaId);
                
                if (input) {{
                    input.value = '';
                    infoDiv.style.display = 'none';
                }}
            }}
            </script>
            
        </body>
        </html>
        """
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return f"<h1>Error: {str(e)}</h1>"




# Endpoint para servir el examen publicado
@app.route('/plantilla/<publication_id>', methods=['GET'])
def serve_plantilla(publication_id):
    try:
        # Buscar el archivo de publicación
        publications_dir = os.path.join(os.path.dirname(__file__), 'publications')
        file_path = os.path.join(publications_dir, f"{publication_id}.json")
        
        if not os.path.exists(file_path):
            return render_template_string("""
                <html>
                <head>
                    <title>Error - Plantilla no encontrada</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; text-align: center; }
                        .error { color: red; margin: 20px 0; }
                    </style>
                </head>
                <body>
                    <h1>Plantilla no encontrada</h1>
                    <p class="error">La plantilla solicitada no existe o ha sido eliminado.</p>
                    <p><a href="/">Volver a la página principal</a></p>
                </body>
                </html>
            """)
            
        with open(file_path, 'r') as f:
            publication = json.load(f)
            examen_data = publication['examenData']  # ✅ Esta es la que sí se usa en todo el HTML
            
            
            # Capturar respuestas del formulario y actualizar examen_data
            # Actualizar preguntas de marcar
            if examen_data.get('preguntas_marcar'):
                for pregunta in examen_data['preguntas_marcar']:
                    form_name = f"pregunta-{pregunta['numero']}"
                    if form_name in request.form:
                        pregunta['respuestaSeleccionada'] = int(request.form[form_name])

            # Actualizar preguntas libres  
            if examen_data.get('preguntas_libres'):
                for pregunta in examen_data['preguntas_libres']:
                    form_name = f"libre-{pregunta['numero']}"
                    if form_name in request.form:
                        pregunta['respuestaAlumno'] = request.form[form_name]

            # Actualizar casos de uso
            if examen_data.get('casos_uso'):
                for caso in examen_data['casos_uso']:
                    form_name = f"caso-{caso['numero']}"
                    if form_name in request.form:
                        caso['respuestaAlumno'] = request.form[form_name]

            # Guardar el examen_data actualizado de vuelta al archivo JSON
            publication['examenData'] = examen_data
            with open(file_path, 'w') as f:
                json.dump(publication, f)
                
        if publication.get('expiration'):
            expiration = datetime.datetime.fromisoformat(publication['expiration'])
            now = datetime.datetime.now(datetime.timezone.utc)  # Añadir zona horaria
            
            # Convertir tanto now como expiration al mismo formato 
            if expiration.tzinfo is not None:
                now = now.replace(tzinfo=expiration.tzinfo)
            else:
                expiration = expiration.replace(tzinfo=now.tzinfo)
                
            if now > expiration:
                
                return render_template_string("""
                    <html>
                    <head>
                        <title>Error - Examen expirado</title>
                        <style>
                            body { font-family: Arial, sans-serif; padding: 20px; text-align: center; }
                            .error { color: red; margin: 20px 0; }
                        </style>
                    </head>
                    <body>
                        <h1>Examen expirado</h1>
                        <p class="error">Esta plantilla ha expirado y ya no está disponible.</p>
                        <p><a href="/">Volver a la página principal</a></p>
                    </body>
                    </html>
                """)

        # Inicio del formulario para enviar respuestas
        form_html = f"""
        <form id="plantilla-form" method="post" action="/submit-plantilla" enctype="multipart/form-data">
            <input type="hidden" name="publication_id" value="{publication_id}">
        <div class="info-examen">
            <p><strong>ID del Examen:</strong> {examen_data.get('examen_id', '')}</p>
            <p><strong>Fecha:</strong> {examen_data.get('fecha', '')}</p>
            <p><strong>Profesor:</strong> {examen_data.get('nombre_profesor', 'No especificado')}</p>
            <div class="form-group">
                <label for="profesor-id"><strong>ID del Profesor:</strong></label>
                <input type="text" id="profesor-id" name="profesor-id" class="form-control" value="{examen_data.get('profesor_id', '')}" required>
            </div>
            <div class="form-group">
                <label for="nombre-examen"><strong>Nombre del Examen:</strong></label>
                <input type="text" id="nombre-examen" name="nombre-examen" class="form-control" value="{examen_data.get('nombre_examen', '')}" required>
            </div>
            <div class="form-group">
                <label for="tipo-examen"><strong>Tipo de Examen:</strong></label>
                <input type="text" id="tipo-examen" name="tipo-examen" class="form-control" value="{examen_data.get('tipo_examen', '')}" required>
            </div>
        </div>
        """

        # Generar HTML para las preguntas de opción múltiple
        preguntas_marcar_html = ""
        if examen_data.get('preguntas_marcar'):
            preguntas_marcar_html = """
            <h2>Preguntas para Marcar</h2>
            """
            for pregunta in examen_data['preguntas_marcar']:
                preguntas_marcar_html += f"""
                <div class="pregunta">
                    <p><strong>{pregunta.get('numero')}. ({pregunta.get('puntaje')} pts)</strong> {pregunta.get('texto')}</p>
                """
                
                # Agregar opciones (sin disabled para permitir selección)
                for i, opcion in enumerate(pregunta.get('opciones', [])):
                    checked = "checked" if pregunta.get('respuestaSeleccionada') == i else ""
                    preguntas_marcar_html += f"""
                    <div class="opcion">
                        <label>
                            <input type="radio" name="pregunta-{pregunta.get('numero')}" value="{i}" {checked}>
                            {opcion.get('texto')}
                        </label>
                    </div>
                    """
                preguntas_marcar_html += "</div>"

        # Generar HTML para preguntas abiertas
        preguntas_libres_html = ""
        if examen_data.get('preguntas_libres'):
            preguntas_libres_html = """
            <h2>Preguntas Libres</h2>
            """
            for pregunta in examen_data['preguntas_libres']:
                preguntas_libres_html += f"""
                <div class="pregunta">
                    <p><strong>{pregunta.get('numero')}. ({pregunta.get('puntaje')} pts)</strong> {pregunta.get('texto')}</p>
                """
                
                # AGREGAR: Mostrar archivo adjunto si existe
                if pregunta.get('archivoId') and pregunta.get('archivoUrl'):
                    preguntas_libres_html += f"""
                    <div class="archivo-adjunto" style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 10px; margin: 10px 0;">
                        <i class="fas fa-file-pdf" style="color: #dc3545; margin-right: 8px;"></i>
                        <span>{pregunta.get('archivoNombre', 'Archivo adjunto')}</span>
                        <button type="button" onclick="window.open('{pregunta.get('archivoUrl')}', '_blank')" 
                                style="margin-left: 10px; padding: 5px 10px; background: #007bff; color: white; border: none; border-radius: 3px;">
                            Ver PDF
                        </button>
                    </div>
                    """
                
                preguntas_libres_html += f"""
                    <div class="form-group">
                        <label for="libre-{pregunta.get('numero')}">Tu respuesta:</label>
                        <textarea id="libre-{pregunta.get('numero')}" name="libre-{pregunta.get('numero')}" 
                                rows="5" class="form-control">{pregunta.get('respuestaAlumno', '')}</textarea>
                    </div>
                </div>
                """
                
        # Generar HTML para casos de uso
        casos_uso_html = ""
        if examen_data.get('casos_uso'):
            casos_uso_html = """
            <h2>Casos de Uso</h2>
            """
            for caso in examen_data['casos_uso']:
                casos_uso_html += f"""
                <div class="pregunta">
                    <p><strong>{caso.get('numero')}. ({caso.get('puntaje')} pts)</strong></p>
                    <p><strong>Descripción:</strong> {caso.get('descripcion')}</p>
                    <p><strong>Pregunta:</strong> {caso.get('pregunta')}</p>
                """
                
                # AGREGAR: Mostrar archivo adjunto si existe
                if caso.get('archivoId') and caso.get('archivoUrl'):
                    casos_uso_html += f"""
                    <div class="archivo-adjunto" style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 10px; margin: 10px 0;">
                        <i class="fas fa-file-pdf" style="color: #dc3545; margin-right: 8px;"></i>
                        <span>{caso.get('archivoNombre', 'Archivo adjunto')}</span>
                        <button type="button" onclick="window.open('{caso.get('archivoUrl')}', '_blank')" 
                                style="margin-left: 10px; padding: 5px 10px; background: #007bff; color: white; border: none; border-radius: 3px;">
                            Ver PDF
                        </button>
                    </div>
                    """
                
                casos_uso_html += f"""
                    <div class="form-group">
                        <label for="caso-{caso.get('numero')}">Tu respuesta:</label>
                        <textarea id="caso-{caso.get('numero')}" name="caso-{caso.get('numero')}" 
                                rows="5" class="form-control">{caso.get('respuestaAlumno', '')}</textarea>
                    </div>
                    <div class="form-group">
                        <label for="archivo-{caso.get('numero')}">Adjuntar archivo (opcional):</label>
                        <input type="file" id="archivo-{caso.get('numero')}" name="archivo-{caso.get('numero')}" 
                            class="form-control-file">
                    </div>
                """

                if caso.get('archivoSubido'):
                    casos_uso_html += f"""
                    <p class="info-archivo">
                        <strong>Archivo ya adjunto:</strong> {caso.get('nombreArchivo')}
                    </p>
                    """
                casos_uso_html += "</div>"

        # Botón para enviar respuestas
        submit_button = """
            <div class="submit-container" style="margin-top: 30px; text-align: center;">
                <button type="submit" class="btn btn-primary btn-lg">Guardar Respuestas</button>
            </div>
        </form>
        """
        
        # Plantilla HTML completa
        html_template = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Examen: {examen_data.get('id')}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    padding: 20px; 
                    max-width: 800px; 
                    margin: 0 auto; 
                    line-height: 1.6;
                }}
                h1 {{ 
                    text-align: center; 
                    color: #2c3e50;
                    margin-bottom: 30px;
                }}
                h2 {{ 
                    margin-top: 30px; 
                    border-bottom: 2px solid #3498db; 
                    padding-bottom: 5px;
                    color: #2980b9;
                }}
                .info-examen {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .pregunta {{ 
                    margin-bottom: 30px; 
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 5px;
                }}
                .opcion {{ 
                    margin: 10px 0 10px 20px; 
                }}
                .respuesta {{ 
                    border: 1px solid #ddd; 
                    padding: 10px; 
                    min-height: 50px; 
                    margin-top: 10px; 
                    background-color: #fff;
                    border-radius: 3px;
                }}
                .info-archivo {{ 
                    font-style: italic; 
                    color: #666; 
                    margin-top: 10px;
                }}
                .footer {{
                    margin-top: 50px;
                    text-align: center;
                    font-size: 14px;
                    color: #7f8c8d;
                }}
            </style>
        </head>
        <body>
          <h1>{examen_data.get('examen_id', 'Examen')} - Examen</h1>
            
            {form_html}
            {preguntas_marcar_html}
            {preguntas_libres_html}
            {casos_uso_html}
            {submit_button}
            
            <div class="footer">
                <p>Este examen fue creado utilizando el Sistema de Exámenes en Línea</p>
                <p>ID de publicación: {publication_id}</p>
            </div>
        </body>
        </html>
        """
        
        return html_template
        
    except Exception as e:
        logger.error(f"Error serving exam: {str(e)}")
        return render_template_string("""
            <html>
            <head>
                <title>Error</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; text-align: center; }
                    .error { color: red; margin: 20px 0; }
                </style>
            </head>
            <body>
                <h1>Error al cargar el examen</h1>
                <p class="error">Ha ocurrido un error al intentar cargar este examen.</p>
                <p><a href="/">Volver a la página principal</a></p>
            </body>
            </html>
        """)
 

# Funcion generar respuesta del examen para la plantilla profesor
@app.route('/api/generar-respuestas', methods=['POST'])
def generar_respuestas():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        examen_data = data.get('examenData', {})
        # Ignoramos el modelo_ia enviado por el cliente y usamos siempre Gemini
        modelo_ia_solicitado = data.get('modelo_ia', 'gemini-2-5-pro')
        
        # --- INICIO MODIFICACIÓN ---
        if "2.5-pro" in modelo_ia_solicitado.lower(): 
             # Usar el identificador preliminar de Gemini 2.5 Pro
            modelo_ia = "gemini-2.5-pro-preview-03-25"
        elif "flash" in modelo_ia_solicitado.lower(): # Captura 'gemini-2.0-flash'
             # Usar el identificador de Gemini 2.0 Flash
            modelo_ia = "gemini-2.0-flash"
        else: # Por defecto o si se pide Gemini 1.5 Pro
             # Usar el identificador de Gemini 1.5 Pro
            modelo_ia = "gemini-1.5-pro" # <- Ya no usamos '-latest' si quieres la versión específica
        # --- FIN MODIFICACIÓN ---
        
        print(f"Modelo solicitado: {modelo_ia_solicitado}, Usando modelo: {modelo_ia}")
        
        # Clonar los datos del examen para no modificar el original
        examen_con_respuestas = json.loads(json.dumps(examen_data))
        
        # Configurar el modelo de Gemini
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 8096,
        }
        
        api_key = os.environ.get("GOOGLE_GEMINI_PRO_API_KEY")
        if not api_key:
            # --- MODIFICAR ESTA LÍNEA (para que el error sea más claro si falta la key) ---
            return jsonify({"error": "GOOGLE_GEMINI_PRO_API_KEY no configurada en el entorno."}), 500
            # --- FIN MODIFICACIÓN ---

        # --- CON ESTAS ---
        # Construye la URL CON la API key como parámetro
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_ia}:generateContent?key={api_key}"
        # Los encabezados ahora solo necesitan el Content-Type
        headers = {
            "Content-Type": "application/json"
        }
        
        # Generar respuestas para preguntas de opción múltiple
        if examen_con_respuestas.get('preguntasMarcar'):
            for pregunta in examen_con_respuestas['preguntasMarcar']:
                # Usar Gemini para determinar la respuesta correcta si no hay respuesta seleccionada
                if pregunta.get('respuestaSeleccionada') is None and pregunta.get('opciones'):
                    num_opciones = len(pregunta['opciones'])
                    if num_opciones > 0:
                        # Usar Gemini para determinar la respuesta correcta
                        texto_pregunta = pregunta.get('texto', '')
                        opciones_texto = [f"{chr(65+i)}) {opcion}" for i, opcion in enumerate(pregunta['opciones'])]
                        prompt = f"Pregunta: {texto_pregunta}\nOpciones:\n{chr(10).join(opciones_texto)}\nResponde solo con el índice numérico (0,1,2,etc.) de la respuesta correcta:"
                        
                        try:
                            model = genai.GenerativeModel(modelo_ia)
                            response = model.generate_content(prompt, generation_config=generation_config)
                            respuesta_index = int(response.text.strip())
                            pregunta['respuestaCorrectaIndex'] = respuesta_index if 0 <= respuesta_index < num_opciones else 0
                        except:
                            pregunta['respuestaCorrectaIndex'] = 0  # Fallback en caso de error
                            
                        if 'respuestaSeleccionada' in pregunta: del pregunta['respuestaSeleccionada'] # Limpia campo viejo
        
        # Generar respuestas para preguntas abiertas
        if examen_con_respuestas.get('preguntasLibres'):
            for pregunta in examen_con_respuestas['preguntasLibres']:
                if not pregunta.get('respuestaAlumno'):
                    prompt = f"""
                    Eres un profesor experto generando respuestas modelo para exámenes. 
                    Genera una respuesta solida y consistente con el SIGUIENTE RANGO (máximo 150-160 palabras) para la siguiente pregunta:
                    
                    Pregunta: {pregunta.get('texto', '')}
                    
                    Tu respuesta debe ser completa, bien estructurada y servir como modelo para un estudiante.
                    """
                    
                    try:
                        payload = {
                            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                            "generation_config": generation_config
                        }

                        response = requests.post(url, headers=headers, json=payload)
                        # --- INICIO: AGREGAR LOGGING Y VERIFICACIÓN ---
                        print(f"Gemini Status (Libre {pregunta.get('numero')}): {response.status_code}") # Imprime el código HTTP
                        result = response.json()
                        print(f"Gemini Response (Libre {pregunta.get('numero')}): {json.dumps(result, indent=2)}") # Imprime la respuesta completa
                        
                        # Verifica si la respuesta es exitosa Y contiene 'candidates'
                        if response.status_code == 200 and 'candidates' in result and result['candidates']:
                            respuesta_texto = result["candidates"][0]["content"]["parts"][0]["text"]
                        else:
                            # Si hay error o no hay candidates, genera un mensaje de error detallado
                            error_info = result.get('error', {}).get('message', 'Respuesta inesperada de la API')
                            if 'promptFeedback' in result and result['promptFeedback'].get('blockReason'):
                                error_info = f"Bloqueado por seguridad: {result['promptFeedback']['blockReason']}"
                            print(f"Error API Gemini (Libre {pregunta.get('numero')}): {error_info}")
                            respuesta_texto = f"Error al generar respuesta: {error_info}"

                        pregunta['respuestaProfesor'] = respuesta_texto
                        # --- FIN: AGREGAR LOGGING Y VERIFICACIÓN ---
                        
                        if 'respuestaAlumno' in pregunta: del pregunta['respuestaAlumno'] # Limpia campo viejo
                    except Exception as e:
                        print(f"Excepción al procesar respuesta para pregunta libre: {e}") # <-- Mejor loguear la excepción completa
                        pregunta['respuestaProfesor'] = f"Excepción al generar respuesta: {str(e)}" # Mensaje más técnico
        
        # Generar respuestas para casos de uso
        if examen_con_respuestas.get('casosUso'):
            for caso in examen_con_respuestas['casosUso']:
                if not caso.get('respuestaAlumno'):
                    prompt = f"""
                    Eres un profesor experto generando respuestas modelo para casos de uso en exámenes.
                    
                    Descripción del caso: {caso.get('descripcion', '')}
                    Pregunta: {caso.get('pregunta', '')}
                    
                    Genera una respuesta solida y consistente con el SIGUIENTE RANGO (máximo 300-310 palabras) completa que aborde todos los aspectos del caso y responda correctamente a la pregunta.
                    La respuesta debe ser detallada, bien estructurada y servir como modelo para un estudiante.
                    """

                    try:
                        payload = {
                            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                            "generation_config": generation_config
                        }

                        response = requests.post(url, headers=headers, json=payload)
                        
                        # --- INICIO: AGREGAR LOGGING Y VERIFICACIÓN ---
                        print(f"Gemini Status (Caso {caso.get('numero')}): {response.status_code}") # Imprime el código HTTP
                        result = response.json()
                        print(f"Gemini Response (Caso {caso.get('numero')}): {json.dumps(result, indent=2)}") # Imprime la respuesta completa

                        # Verifica si la respuesta es exitosa Y contiene 'candidates'
                        if response.status_code == 200 and 'candidates' in result and result['candidates']:
                            respuesta_texto = result["candidates"][0]["content"]["parts"][0]["text"]
                        else:
                             # Si hay error o no hay candidates, genera un mensaje de error detallado
                            error_info = result.get('error', {}).get('message', 'Respuesta inesperada de la API')
                            if 'promptFeedback' in result and result['promptFeedback'].get('blockReason'):
                                error_info = f"Bloqueado por seguridad: {result['promptFeedback']['blockReason']}"
                            print(f"Error API Gemini (Caso {caso.get('numero')}): {error_info}")
                            respuesta_texto = f"Error al generar respuesta: {error_info}"

                        caso['respuestaProfesor'] = respuesta_texto
                        # --- FIN: AGREGAR LOGGING Y VERIFICACIÓN ---
                        
                        if 'respuestaAlumno' in caso: del caso['respuestaAlumno'] # Limpia campo viejo
                    except Exception as e:
                        print(f"Excepción al procesar respuesta para caso de uso: {e}") # <-- Mejor loguear la excepción completa
                        caso['respuestaProfesor'] = f"Excepción al generar respuesta: {str(e)}" # Mensaje más técnico
        
        return jsonify({
            "examen_con_respuestas": examen_con_respuestas,
            "modelo_usado": modelo_ia
        })
        
    except Exception as e:
        print(f"Error en generar_respuestas: {str(e)}")
        return jsonify({"error": f"Error al generar respuestas: {str(e)}"}), 500 
    
    
# **** INICIO DEL BLOQUE COMENTADO ****
@app.route('/api/guardar-respuestas-profesor', methods=['POST'])
def guardar_respuestas_profesor():
    try:
        data = request.get_json()
        
        # Inicializar cliente Appwrite
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT)
        client.set_project(APPWRITE_PROJECT_ID)
        client.set_key(APPWRITE_API_KEY)
        databases = Databases(client)
        
        # Convertir arrays a JSON strings
        preguntas_marcar_str = json.dumps(data.get('preguntas_marcar', []), ensure_ascii=False)
        preguntas_libres_str = json.dumps(data.get('preguntas_libres', []), ensure_ascii=False)
        casos_uso_str = json.dumps(data.get('casos_uso', []), ensure_ascii=False)
        
        # Crear documento
        document_id = f"prof_resp_{data.get('examen_id')}_{int(time.time())}"
        
        response = databases.create_document(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=os.getenv('APPWRITE_COLLECTION_EXAMEN_PLANTILLA_RESPUESTAS'),
            document_id=document_id,
            data={
                "email": data.get('email'),  # ← AGREGAR ESTA LÍNEA email
                "examen_id": data.get('examen_id'),
                "nombre_profesor": data.get('nombre_profesor'),
                "profesor_id": data.get('profesor_id'),
                "nombre_examen": data.get('nombre_examen'),
                "tipo_examen": data.get('tipo_examen'),
                "preguntas_marcar": preguntas_marcar_str,
                "preguntas_libres": preguntas_libres_str,
                "casos_uso": casos_uso_str
            }
        )
        
        return jsonify({"success": True, "message": "Respuestas guardadas correctamente"})
        
    except Exception as e:
        logger.error(f"Error al guardar respuestas del profesor: {str(e)}")
        return jsonify({"error": str(e)}), 500

# **** FIN DEL BLOQUE COMENTADO ****
    
def upload_file_to_gcs(file):
    """
    Sube archivos PDF a Appwrite Storage en segundo plano.
    """
    try:
        # Inicializar Cliente Appwrite
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT)
        client.set_project(APPWRITE_PROJECT_ID)
        client.set_key(APPWRITE_API_KEY)
        storage_service = Storage(client)
        target_bucket_id = APPWRITE_BUCKET_PLANTILLA_EXAMEN_RESPUESTAS
        
        # Preparar archivo para Appwrite
        file_bytes = file.read()
        appwrite_file_id = ID.unique()
        appwrite_file = InputFile.from_bytes(
            file_bytes,
            file.filename,
            file.content_type
        )
        
        # Subir a Appwrite
        result_storage = storage_service.create_file(
            bucket_id=target_bucket_id,
            file_id=appwrite_file_id,
            file=appwrite_file
        )
        
        logger.info(f"Subida completada: {file.filename}. File ID: {result_storage['$id']}")
          
    except Exception as e:
        logger.error(f"Error en la subida del archivo: {str(e)}", exc_info=True)
        
@app.route('/api/subir-pdf', methods=['POST'])
def subir_pdf():
    try:
        file = request.files.get('file')
        if file:
            # Llamar la función existente que ya funciona
            threading.Thread(target=upload_file_to_gcs, args=(file,)).start()
            return jsonify({"success": True})
        return jsonify({"error": "No se encontró archivo"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500        
        
@app.route('/subir_anexo_examen', methods=['POST'])
def subir_anexo_examen():
    try:
        if 'archivo' not in request.files:
            return jsonify({'error': 'No se encontró archivo'}), 400
        
        archivo = request.files['archivo']
        id_examen = request.form.get('id_examen')
        
        if archivo.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        # Validar tamaño (10MB máximo)
        if len(archivo.read()) > 10 * 1024 * 1024:
            return jsonify({'error': 'Archivo muy grande (máximo 10MB)'}), 400
        
        archivo.seek(0)  # Resetear puntero después de leer
        
        # Subir a Appwrite Storage
        response = storage.create_file(
            bucket_id=os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN'),
            file_id=f"anexo_{id_examen}_{int(time.time())}",
            file=InputFile.from_bytes(archivo.read(), archivo.filename)
        )
        
        return jsonify({
            'file_id': response['$id'], 
            'filename': archivo.filename,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"[ERROR] Error subiendo anexo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/vincular-adjunto', methods=['POST'])
def vincular_adjunto():
    try:
        file_id = request.form.get('fileId')  # ID del archivo existente en bucket
        tipo = request.form.get('tipo')       # 'libres' o 'casos'
        numero = request.form.get('numero')   # número de pregunta
        
        if not file_id:
            return jsonify({'error': 'No se especificó archivo'}), 400
        
        # Generar URL de descarga del archivo existente
        file_url = f"https://cloud.appwrite.io/v1/storage/buckets/{os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')}/files/{file_id}/view?project={os.getenv('APPWRITE_PROJECT_ID')}"
        
        # Aquí podrías obtener info del archivo si necesitas el nombre
        file_info = storage.get_file(
            bucket_id=os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN'),
            file_id=file_id
        )
        
        return jsonify({
            'success': True,
            'url': file_url,
            'filename': file_info['name'],
            'fileId': file_id
        })
        
    except Exception as e:
        print(f"[ERROR] Error vinculando adjunto: {e}")
        return jsonify({'error': str(e)}), 500    
 
@app.route('/api/generar-imagen', methods=['POST'])
def generar_imagen():
   try:
       data = request.get_json()
       prompt = data.get('prompt')
       modelo = data.get('modelo', 'gpt-4-1')
       
       if not prompt:
           return jsonify({'error': 'Prompt requerido'}), 400
       
       # Modelos que generan HTML (existentes)
       if modelo.startswith('gpt-'):
           html_code = generar_html_con_openai(prompt, modelo)
           imagen_url = renderizar_html_a_imagen(html_code)
           return jsonify({
               'success': True,
               'imagen_url': imagen_url,
               'html_generado': html_code,
               'modelo_usado': modelo
           })
       elif modelo.startswith('gemini-'):
           html_code = generar_html_con_gemini(prompt, modelo)
           imagen_url = renderizar_html_a_imagen(html_code)
           return jsonify({
               'success': True,
               'imagen_url': imagen_url,
               'html_generado': html_code,
               'modelo_usado': modelo
           })
       elif modelo.startswith('claude-'):
           html_code = generar_html_con_claude(prompt, modelo)
           imagen_url = renderizar_html_a_imagen(html_code)
           return jsonify({
               'success': True,
               'imagen_url': imagen_url,
               'html_generado': html_code,
               'modelo_usado': modelo
           })
       elif modelo.startswith('deepseek-'):
           html_code = generar_html_con_deepseek(prompt, modelo)
           imagen_url = renderizar_html_a_imagen(html_code)
           return jsonify({
               'success': True,
               'imagen_url': imagen_url,
               'html_generado': html_code,
               'modelo_usado': modelo
           })
       # Nuevos modelos que generan imágenes directamente
       elif modelo in ['flux-1-pro', 'flux']:
           imagen_path = generar_imagen_flux(prompt)
           imagen_url = subir_imagen_generada_a_bucket(imagen_path)
           return jsonify({
               'success': True,
               'imagen_url': imagen_url,
               'modelo_usado': modelo
           })
       elif modelo in ['kling-ai', 'kling']:
           imagen_path = generar_imagen_kling(prompt)
           imagen_url = subir_imagen_generada_a_bucket(imagen_path)
           return jsonify({
               'success': True,
               'imagen_url': imagen_url,
               'modelo_usado': modelo
           })
       elif modelo == 'ideogram':
           imagen_path = generar_imagen_ideogram(prompt)
           imagen_url = subir_imagen_generada_a_bucket(imagen_path)
           return jsonify({
               'success': True,
               'imagen_url': imagen_url,
               'modelo_usado': modelo
           })
       elif modelo in ['dall-e-3', 'dalle3']:
           imagen_path = generar_imagen_dalle3(prompt)
           imagen_url = subir_imagen_generada_a_bucket(imagen_path)
           return jsonify({
               'success': True,
               'imagen_url': imagen_url,
               'modelo_usado': modelo
           })
       elif modelo in ['leonardo-ai', 'leonardo']:
           imagen_path = generar_imagen_leonardo(prompt)
           imagen_url = subir_imagen_generada_a_bucket(imagen_path)
           return jsonify({
               'success': True,
               'imagen_url': imagen_url,
               'modelo_usado': modelo
           })
       else:
           return jsonify({'error': f'Modelo {modelo} no soportado'}), 400
       
   except Exception as e:
       print(f"[ERROR] Error generando imagen: {e}")
       return jsonify({'error': str(e)}), 500


def generar_html_con_openai(prompt, modelo):
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        prompt_html = f"""
        Genera HTML completo con SVG que dibuje exactamente: {prompt}
        
        REQUISITOS:
        - HTML completo con estructura DOCTYPE
        - SVG de 800x600px, fondo blanco
        - Medidas, ángulos y etiquetas precisas
        - Texto legible (fuente 14px mínimo)
        - Líneas negras, colores suaves para rellenos
        - Centrado en el canvas
        
        RESPONDE SOLO CON CÓDIGO HTML, SIN EXPLICACIONES.
        """
        
        response = client.chat.completions.create(
            model="gpt-4" if modelo == "gpt-4-1" else "gpt-4o",
            messages=[{"role": "user", "content": prompt_html}],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Error con OpenAI: {str(e)}")

def generar_html_con_gemini(prompt, modelo):
    try:

        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Seleccionar modelo específico
        if modelo == "gemini-2-5-pro":
            model = genai.GenerativeModel('gemini-1.5-pro')
        elif modelo == "gemini-2-0-flash":
            model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            model = genai.GenerativeModel('gemini-2.5-pro')  # Por defecto
        
        prompt_html = f"""
        Genera HTML completo con SVG que dibuje exactamente: {prompt}
        
        REQUISITOS ESPECÍFICOS:
        - HTML5 completo con DOCTYPE, head y body
        - SVG de exactamente 800x600 píxeles
        - Fondo blanco (#FFFFFF)
        - Figuras geométricas con precisión matemática
        - Medidas, ángulos y etiquetas claramente visibles
        - Fuente Arial o similar, tamaño mínimo 14px
        - Líneas color negro (#000000), grosor 2px
        - Rellenos con colores suaves (lightblue, lightgreen, etc.)
        - Elementos centrados en el canvas
        - Coordenadas exactas basadas en las medidas solicitadas
        
        IMPORTANTE: Responde ÚNICAMENTE con código HTML válido, sin explicaciones ni texto adicional.
        El HTML debe ser renderizable directamente en un navegador.
        """
        
        response = model.generate_content(
            prompt_html,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Baja temperatura para precisión
                max_output_tokens=3000,
            )
        )
        
        html_content = response.text
        
        # Limpiar markdown si viene envuelto en ```html
        if html_content.startswith('```html'):
            html_content = html_content.replace('```html', '').replace('```', '').strip()
        elif html_content.startswith('```'):
            html_content = html_content.replace('```', '').strip()
        
        return html_content
        
    except Exception as e:
        print(f"[ERROR] Error con Gemini: {e}")
        raise Exception(f"Error generando HTML con Gemini: {str(e)}")

def generar_html_con_claude(prompt, modelo):
    try:
        
        client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
        # Seleccionar modelo específico
        if modelo == "claude-sonnet-4":
            model_name = "claude-sonnet-4-20250514"
        elif modelo == "claude-3-5-sonnet":
            model_name = "claude-3-5-sonnet-20241022"
        else:
            model_name = "claude-sonnet-4-20250514"  # Por defecto
        
        prompt_html = f"""
        Genera HTML completo con SVG que dibuje exactamente: {prompt}
        
        ESPECIFICACIONES TÉCNICAS:
        - Documento HTML5 válido y completo
        - SVG con dimensiones exactas: 800x600px
        - Fondo blanco, viewport centrado
        - Precisión matemática en todas las medidas
        - Etiquetas y texto con fuente legible (Arial, 14px+)
        - Líneas definidas (stroke: black, stroke-width: 2)
        - Colores de relleno suaves y académicos
        - Coordenadas calculadas matemáticamente
        - Elementos proporcionalmente distribuidos
        
        FORMATO DE RESPUESTA:
        Proporciona únicamente código HTML válido, sin comentarios adicionales.
        El HTML debe renderizarse correctamente al abrirse en navegador.
        """
        
        response = client.messages.create(
            model=model_name,
            max_tokens=3000,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": prompt_html
                }
            ]
        )
        
        html_content = response.content[0].text
        
        # Limpiar markdown si viene envuelto
        if html_content.startswith('```html'):
            html_content = html_content.replace('```html', '').replace('```', '').strip()
        elif html_content.startswith('```'):
            html_content = html_content.replace('```', '').strip()
        
        return html_content
        
    except Exception as e:
        print(f"[ERROR] Error con Claude: {e}")
        raise Exception(f"Error generando HTML con Claude: {str(e)}")
    
def generar_html_con_deepseek(prompt, modelo):
    try:

        # API endpoint de OpenRouter
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Seleccionar modelo específico de DeepSeek en OpenRouter
        if modelo == "deepseek-v3":
            model_name = "deepseek/deepseek-chat"
        elif modelo == "deepseek-chat":
            model_name = "deepseek/deepseek-chat"
        else:
            model_name = "deepseek/deepseek-chat"  # Por defecto
        
        prompt_html = f"""
        Genera HTML completo con SVG que dibuje exactamente: {prompt}
        
        ESPECIFICACIONES TÉCNICAS:
        - Documento HTML5 válido y completo
        - SVG con dimensiones exactas: 800x600px
        - Fondo blanco, viewport centrado
        - Precisión matemática en todas las medidas
        - Etiquetas y texto con fuente legible (Arial, 14px+)
        - Líneas definidas (stroke: black, stroke-width: 2)
        - Colores de relleno suaves y académicos
        - Coordenadas calculadas matemáticamente
        - Elementos proporcionalmente distribuidos
        
        FORMATO DE RESPUESTA:
        Proporciona únicamente código HTML válido, sin comentarios adicionales.
        El HTML debe renderizarse correctamente al abrirse en navegador.
        """
        
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",  # Requerido por OpenRouter
            "X-Title": "ExamPro Image Generator"       # Opcional
        }
        
        data = {
            "model": model_name,
            "messages": [
                {
                    "role": "user", 
                    "content": prompt_html
                }
            ],
            "max_tokens": 3000,
            "temperature": 0.1
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        html_content = result['choices'][0]['message']['content']
        
        # Limpiar markdown si viene envuelto
        if html_content.startswith('```html'):
            html_content = html_content.replace('```html', '').replace('```', '').strip()
        elif html_content.startswith('```'):
            html_content = html_content.replace('```', '').strip()
        
        return html_content
        
    except Exception as e:
        print(f"[ERROR] Error con DeepSeek via OpenRouter: {e}")
        raise Exception(f"Error generando HTML con DeepSeek: {str(e)}")
    
# ============================================
# 1. FLUX.1 PRO - Mejor para contenido técnico
# ============================================

def generar_imagen_flux(prompt):
    """
    Genera imagen usando Flux.1 Pro
    Mejor modelo para contenido técnico y académico
    """
    try:
        flux_api_key = os.getenv('FLUX_API_KEY')
        if not flux_api_key:
            raise Exception("FLUX_API_KEY no configurada en .env")
        
        headers = {
            'Authorization': f'Bearer {flux_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "prompt": prompt,
            "model": "flux-pro-1.1",
            "width": 1024,
            "height": 1024,
            "steps": 25,
            "guidance": 3.5,
            "safety_tolerance": 2
        }
        
        response = requests.post(
            'https://api.bfl.ml/v1/flux-pro-1.1',
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result['id']
            
            # Esperar resultado
            return _poll_flux_result(task_id, flux_api_key)
        else:
            raise Exception(f"Error Flux API: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Flux.1 Pro: {e}")
        raise Exception(f"Error generando imagen con Flux: {str(e)}")

def _poll_flux_result(task_id, api_key):
    """Obtener resultado de Flux"""
    headers = {'Authorization': f'Bearer {api_key}'}
    
    for attempt in range(30):  # 30 intentos máximo
        try:
            response = requests.get(
                f'https://api.bfl.ml/v1/get_result?id={task_id}',
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['status'] == 'Ready':
                    return _download_image_from_url(result['result']['sample'])
                elif result['status'] == 'Error':
                    raise Exception(f"Flux generation failed: {result.get('error', 'Unknown error')}")
            
            time.sleep(2)  # Esperar 2 segundos
        except Exception as e:
            if attempt == 29:  # Último intento
                raise e
    
    raise Exception("Timeout esperando resultado de Flux")

# ============================================
# 2. KLING AI - Especializado en educativo
# ============================================

def generar_imagen_kling(prompt):
    """
    Genera imagen usando Kling AI
    Especializado en contenido educativo
    """
    try:
        kling_api_key = os.getenv('KLING_API_KEY')
        if not kling_api_key:
            raise Exception("KLING_API_KEY no configurada en .env")
        
        headers = {
            'Authorization': f'Bearer {kling_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "prompt": prompt,
            "model": "kling-v1",
            "aspect_ratio": "1:1",
            "image_count": 1,
            "mode": "standard"
        }
        
        response = requests.post(
            'https://api.klingai.com/v1/images/generations',
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            
            # Esperar resultado
            return _poll_kling_result(task_id, kling_api_key)
        else:
            raise Exception(f"Error Kling API: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Kling AI: {e}")
        raise Exception(f"Error generando imagen con Kling: {str(e)}")

def _poll_kling_result(task_id, api_key):
    """Obtener resultado de Kling"""
    headers = {'Authorization': f'Bearer {api_key}'}
    
    for attempt in range(40):  # 40 intentos máximo
        try:
            response = requests.get(
                f'https://api.klingai.com/v1/images/generations/{task_id}',
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['task_status'] == 'succeed':
                    return _download_image_from_url(result['task_result']['images'][0]['url'])
                elif result['task_status'] == 'failed':
                    raise Exception(f"Kling generation failed: {result.get('task_status_msg', 'Unknown error')}")
            
            time.sleep(3)  # Esperar 3 segundos
        except Exception as e:
            if attempt == 39:  # Último intento
                raise e
    
    raise Exception("Timeout esperando resultado de Kling")

# ============================================
# 3. IDEOGRAM - Excelente con texto y diagramas
# ============================================

def generar_imagen_ideogram(prompt):
    """
    Genera imagen usando Ideogram
    Excelente para diagramas con texto y etiquetas
    """
    try:
        ideogram_api_key = os.getenv('IDEOGRAM_API_KEY')
        if not ideogram_api_key:
            raise Exception("IDEOGRAM_API_KEY no configurada en .env")
        
        headers = {
            'Api-Key': ideogram_api_key,
            'Content-Type': 'application/json'
        }
        
        data = {
            "image_request": {
                "prompt": prompt,
                "model": "V_2",
                "magic_prompt_option": "AUTO",
                "aspect_ratio": "ASPECT_1_1",
                "style_type": "REALISTIC"
            }
        }
        
        response = requests.post(
            'https://api.ideogram.ai/generate',
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            image_url = result['data'][0]['url']
            return _download_image_from_url(image_url)
        else:
            raise Exception(f"Error Ideogram API: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Ideogram: {e}")
        raise Exception(f"Error generando imagen con Ideogram: {str(e)}")

# ============================================
# 4. DALL-E 3 - Respaldo confiable
# ============================================

def generar_imagen_dalle3(prompt):
    """
    Genera imagen usando DALL-E 3 de OpenAI
    Respaldo confiable y estable
    """
    try:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise Exception("OPENAI_API_KEY no configurada en .env")
        
        headers = {
            'Authorization': f'Bearer {openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "hd",
            "style": "natural"
        }
        
        response = requests.post(
            'https://api.openai.com/v1/images/generations',
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            image_url = result['data'][0]['url']
            return _download_image_from_url(image_url)
        else:
            raise Exception(f"Error DALL-E 3 API: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] DALL-E 3: {e}")
        raise Exception(f"Error generando imagen con DALL-E 3: {str(e)}")

# ============================================
# 5. LEONARDO AI - Buena alternativa
# ============================================

def generar_imagen_leonardo(prompt):
    """
    Genera imagen usando Leonardo AI
    Buena alternativa con calidad profesional
    """
    try:
        leonardo_api_key = os.getenv('LEONARDO_API_KEY')
        if not leonardo_api_key:
            raise Exception("LEONARDO_API_KEY no configurada en .env")
        
        headers = {
            'Authorization': f'Bearer {leonardo_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "prompt": prompt,
            "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",  # Leonardo Kino XL
            "width": 1024,
            "height": 1024,
            "num_images": 1,
            "guidance_scale": 7,
            "num_inference_steps": 15,
            "presetStyle": "CINEMATIC"
        }
        
        response = requests.post(
            'https://cloud.leonardo.ai/api/rest/v1/generations',
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            generation_id = result['sdGenerationJob']['generationId']
            
            # Esperar resultado
            return _poll_leonardo_result(generation_id, leonardo_api_key)
        else:
            raise Exception(f"Error Leonardo API: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Leonardo AI: {e}")
        raise Exception(f"Error generando imagen con Leonardo: {str(e)}")

def _poll_leonardo_result(generation_id, api_key):
    """Obtener resultado de Leonardo"""
    headers = {'Authorization': f'Bearer {api_key}'}
    
    for attempt in range(30):  # 30 intentos máximo
        try:
            response = requests.get(
                f'https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}',
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['generations_by_pk']['status'] == 'COMPLETE':
                    image_url = result['generations_by_pk']['generated_images'][0]['url']
                    return _download_image_from_url(image_url)
                elif result['generations_by_pk']['status'] == 'FAILED':
                    raise Exception("Leonardo generation failed")
            
            time.sleep(2)  # Esperar 2 segundos
        except Exception as e:
            if attempt == 29:  # Último intento
                raise e
    
    raise Exception("Timeout esperando resultado de Leonardo")

# =============================================
# ENDPOINT PARA LISTAR EXAMEN PUBLICADOS APPWRITE
# Agregar a tu Flask app
# =============================================
@app.route('/api/obtener-examenes-profesor', methods=['GET'])
def obtener_examenes_profesor():
    try:
        # Obtener email del query parameter o session
        email = request.args.get('email')
        if not email:
            return jsonify({"error": "Email requerido"}), 400
        
        # Inicializar cliente Appwrite
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT)
        client.set_project(APPWRITE_PROJECT_ID)
        client.set_key(APPWRITE_API_KEY)
        databases = Databases(client)
        
        # Consultar documentos del profesor
        response = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_EXAMEN_PROFESOR_URL,
            queries=[Query.equal("email", email)]
        )
        
        return jsonify({
            "success": True,
            "documents": response['documents']
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo exámenes: {str(e)}")
        return jsonify({"error": str(e)}), 500
# =============================================
# ENDPOINT BACKEND PARA LISTAR ARCHIVOS APPWRITE
# Agregar a tu Flask app
# =============================================

@app.route('/api/listar-archivos-bucket', methods=['GET'])
def listar_archivos_bucket():
    
    print("[DEBUG] Iniciando listar_archivos_bucket")
    """
    Lista todos los archivos del bucket APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN
    """
    try:
        data = request.get_json()  # ← AGREGAR ESTA LÍNEA email
        user_email = data.get('email')  # ← AGREGAR ESTA LÍNEA email
        bucket_id = os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')
        # Obtener archivos del bucket
        bucket_id = os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')
        
        if not bucket_id:
            print("[DEBUG] Bucket ID no encontrado")
            return jsonify({
                'error': 'APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN no configurado'
            }), 500

        print("[DEBUG] Llamando storage.list_files")
        response = storage.list_files(bucket_id=bucket_id)
        print(f"[DEBUG] Respuesta storage: {response}")
        
        archivos = response['files']
        print(f"[DEBUG] Total archivos encontrados: {len(archivos)}")
        
        # Filtrar y formatear archivos
        archivos_formateados = []
        for archivo in archivos:
            if user_email in archivo['name']:  # ← AGREGAR ESTA CONDICIÓN email
                print(f"[DEBUG] Procesando archivo: {archivo['name']}")
                archivos_formateados.append({
                    '$id': archivo['$id'],
                    'name': archivo['name'],
                    'mimeType': archivo['mimeType'],
                    'sizeOriginal': archivo['sizeOriginal'],
                    '$createdAt': archivo['$createdAt'],
                    '$updatedAt': archivo['$updatedAt'],
                    'url': f"https://cloud.appwrite.io/v1/storage/buckets/{bucket_id}/files/{archivo['$id']}/view?project={os.getenv('APPWRITE_PROJECT_ID')}"
                })
            
            print(f"[DEBUG] Archivos formateados: {len(archivos_formateados)}")
        
        return jsonify({
            'success': True,
            'archivos': archivos_formateados,
            'total': len(archivos_formateados)
        })
        
    except Exception as e:
        print(f"[ERROR] Error listando archivos bucket: {e}")
        return jsonify({
            'error': f'Error al listar archivos: {str(e)}'
        }), 500   
        

# =============================================
# ENDPOINT OPCIONAL: OBTENER INFO DE UN ARCHIVO
# =============================================

@app.route('/api/archivo-info/<file_id>', methods=['GET'])
def obtener_info_archivo(file_id):
    """
    Obtiene información detallada de un archivo específico
    """
    try:
        bucket_id = os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')
        
        # Obtener información del archivo
        archivo = storage.get_file(
            bucket_id=bucket_id,
            file_id=file_id
        )
        
        return jsonify({
            'success': True,
            'archivo': {
                '$id': archivo['$id'],
                'name': archivo['name'],
                'mimeType': archivo['mimeType'],
                'sizeOriginal': archivo['sizeOriginal'],
                '$createdAt': archivo['$createdAt'],
                '$updatedAt': archivo['$updatedAt'],
                'url': f"https://cloud.appwrite.io/v1/storage/buckets/{bucket_id}/files/{file_id}/view?project={os.getenv('APPWRITE_PROJECT_ID')}",
                'downloadUrl': f"https://cloud.appwrite.io/v1/storage/buckets/{bucket_id}/files/{file_id}/download?project={os.getenv('APPWRITE_PROJECT_ID')}"
            }
        })
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo info archivo: {e}")
        return jsonify({
            'error': f'Error al obtener información del archivo: {str(e)}'
        }), 500
        
# =============================================
# FUNCIONES AUXILIARES APPWRITE
# =============================================

def validar_archivo_appwrite(file_id):
    """
    Valida que un archivo existe en el bucket
    """
    try:
        bucket_id = os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')
        archivo = storage.get_file(bucket_id=bucket_id, file_id=file_id)
        return True, archivo
    except Exception:
        return False, None

def generar_url_archivo_appwrite(file_id, tipo='view'):
    """
    Genera URL para ver o descargar archivo de Appwrite
    tipo: 'view' o 'download'
    """
    bucket_id = os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')
    project_id = os.getenv('APPWRITE_PROJECT_ID')
    
    return f"https://cloud.appwrite.io/v1/storage/buckets/{bucket_id}/files/{file_id}/{tipo}?project={project_id}"        
                
    
def _download_image_from_url(url):
    """Descargar imagen desde URL y guardar en archivo temporal"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
            
    except Exception as e:
        raise Exception(f"Error descargando imagen: {str(e)}")
    

def renderizar_html_a_imagen(html_code):
    try:

        # Crear archivo HTML temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_code)
            html_path = f.name
        
        # Crear archivo de imagen temporal
        imagen_path = tempfile.mktemp(suffix='.png')
        
        # Usar Playwright para renderizar HTML a imagen
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Configurar viewport
            page.set_viewport_size({"width": 800, "height": 600})
            
            # Cargar HTML
            page.goto(f"file://{html_path}")
            
            # Esperar que se renderice completamente
            page.wait_for_timeout(1000)
            
            # Capturar screenshot
            page.screenshot(path=imagen_path, full_page=True)
            
            browser.close()
        
        # Subir imagen al bucket de Appwrite
        imagen_url = subir_imagen_generada_a_bucket(imagen_path)
        
        # Limpiar archivos temporales
        os.unlink(html_path)
        os.unlink(imagen_path)
        
        return imagen_url
        
    except Exception as e:
        print(f"[ERROR] Error renderizando HTML: {e}")
        raise Exception(f"Error convirtiendo HTML a imagen: {str(e)}")

def subir_imagen_generada_a_bucket(imagen_path):
    try:
        
        # Leer archivo de imagen
        with open(imagen_path, 'rb') as f:
            file_content = f.read()
        
        # Generar ID único
        file_id = f"imagen_generada_{int(time.time())}"
        
        # Subir a Appwrite Storage
        response = storage.create_file(
            bucket_id=os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN'),
            file_id=file_id,
            file=InputFile.from_bytes(file_content, filename=f"{file_id}.png")
        )
        
        # Generar URL de acceso público
        imagen_url = f"https://cloud.appwrite.io/v1/storage/buckets/{os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')}/files/{response['$id']}/view?project={os.getenv('APPWRITE_PROJECT_ID')}"
        
        return imagen_url
        
    except Exception as e:
        print(f"[ERROR] Error subiendo imagen: {e}")
        raise Exception(f"Error subiendo imagen al bucket: {str(e)}")    
      
@app.route('/submit-plantilla', methods=['POST'])
def submit_plantilla():
    try:
        # Obtener datos del formulario tal como lo hace submit_exam
        publication_id = request.form.get('publication_id')
        
        if not publication_id:
            return "Error: ID de examen no especificado", 400
        
        # Cargar los datos existentes del examen (igual que en submit_exam)
        publications_dir = os.path.join(os.path.dirname(__file__), 'publications')
        file_path = os.path.join(publications_dir, f"{publication_id}.json")
        
        if not os.path.exists(file_path):
            return "Error: Plantilla no encontrada", 404
            
        with open(file_path, 'r') as f:
            publication = json.load(f)
            
        examen_data = publication['examenData']
        
        # Preparar datos para Appwrite
        preguntas_marcar_str = json.dumps(examen_data.get('preguntas_marcar', []), ensure_ascii=False)
        preguntas_libres_str = json.dumps(examen_data.get('preguntas_libres', []), ensure_ascii=False)
        casos_uso_str = json.dumps(examen_data.get('casos_uso', []), ensure_ascii=False)

        # Crear cliente Appwrite (como lo hace submit_exam)
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT) \
              .set_project(APPWRITE_PROJECT_ID) \
              .set_key(APPWRITE_API_KEY)

        databases = Databases(client)
        
        # Usar el ID del examen desde examen_data
        examen_id = examen_data.get('examen_id', publication_id)
        
        # Crear documento en Appwrite (siguiendo el mismo patrón de submit_exam)
        document_id = f"plantilla_{publication_id}"
        response = databases.create_document(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=os.getenv('APPWRITE_COLLECTION_EXAMEN_PLANTILLA_RESPUESTAS'),
            document_id=document_id,
            data={
                "examen_id": examen_id,  # Campo requerido que faltaba
                "profesor_id": examen_data.get('profesor_id', ""),
                "nombre_profesor": examen_data.get('nombre_profesor', ""),
                "nombre_examen": examen_data.get('nombre_examen', ""),
                "tipo_examen": examen_data.get('tipo_examen', "Plantilla"),
                "preguntas_marcar": preguntas_marcar_str,
                "preguntas_libres": preguntas_libres_str,
                "casos_uso": casos_uso_str
            }
        )
        
        return jsonify({"status": "ok", "id": response["$id"]})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/examenes-disponibles', methods=['GET'])
def obtener_examenes_disponibles():
    try:
        curso = request.args.get('curso')
        nombre_profesor = request.args.get('nombre_profesor') 
        institucion = request.args.get('institucion')

        # Validar parámetros requeridos
        if not curso or not nombre_profesor or not institucion:
            return jsonify({
                'error': 'Faltan parámetros: curso, nombre_profesor, institucion son requeridos'
            }), 400

        # Inicializar cliente Appwrite
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT)
        client.set_project(APPWRITE_PROJECT_ID)
        client.set_key(APPWRITE_API_KEY)
        databases = Databases(client)
        
        email = request.args.get('email')
        if not email:
            return jsonify({'error': 'Email requerido'}), 400

        # Buscar examen publicado que coincida con los datos del alumno
        examenes = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_EXAMEN_DISPONIBLES,
            
            queries=[
                Query.equal('curso', curso),
                Query.equal('institucion', institucion),
                Query.equal('email', email)
            ]
        )

        if len(examenes['documents']) == 0:
            return jsonify({
                'error': 'No hay examen disponible para este curso y profesor',
                'message': 'Su profesor aún no ha publicado un examen para este curso'
            }), 404

        # Retornar el primer examen encontrado
        examen = examenes['documents'][0]
        
        # Verificar que el examen no haya expirado
        fecha_limite = datetime.datetime.fromisoformat(examen['fecha_limite'])
        ahora = datetime.datetime.now()
        
        if fecha_limite <= ahora:
            return jsonify({
                'error': 'Examen expirado',
                'message': 'La fecha límite para este examen ya pasó',
                'fecha_limite': examen['fecha_limite']
            }), 410

        return jsonify({
            'success': True,
            'examen': {
                'nombre_examen': examen['nombre_examen'],
                'id_examen': examen['id_examen'],
                'url_examen': examen['url_examen'],
                'curso': examen['curso'],
                'fecha_limite': examen['fecha_limite'],
                'institucion': examen['institucion'],
                'tiempo_restante': max(0, int((fecha_limite - ahora).total_seconds() / 60))
            }
        })

    except Exception as error:
        logger.error(f'Error obteniendo examen disponible: {error}')
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'No se pudo obtener el examen disponible'
        }), 500

@app.route('/submit-exam', methods=['POST'])
def submit_exam():
    logger.info("Recibida petición en /submit-exam (Modificado para buscar solo en Appwrite)")
    try:
        # Obtener datos del formulario
        examen_id = request.form.get('examenId')
        nombre_alumno = request.form.get('nombreAlumno')
        id_alumno = request.form.get('id-alumno')
        nombre_profesor = request.form.get('nombre_profesor')
        id_profesor = request.form.get('id_profesor')
        nombre_examen = request.form.get('nombre_examen')
        tipo_examen = request.form.get('tipo_examen')
        # --- FIN LÍNEAS A AGREGAR ---
        
        if not examen_id:
            logger.error("Falta examenId en el formulario de envío.")
            return jsonify({"success": False, "error": "ID de examen no especificado"}), 400
        if not id_alumno:
            logger.error("Falta id_alumno en el formulario de envío.")
            return jsonify({"success": False, "error": "ID de alumno no especificado"}), 400
        
        # Inicializar cliente Appwrite para buscar el examen
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT)
        client.set_project(APPWRITE_PROJECT_ID)
        client.set_key(APPWRITE_API_KEY)
        databases = Databases(client)
        
        logger.info(f"Buscando examen con ID: {examen_id} en Appwrite")
        
        # Buscar el examen ÚNICAMENTE en la colección examen_profesor_url
        try:
            examen_doc = databases.list_documents(
                database_id=APPWRITE_DATABASE_ID,
                collection_id='67f82fac00345dbf7b06',  # ID de la colección examen_profesor_url
                queries=[
                    Query.equal("id_examen", examen_id)
                ]
            )
            
            if len(examen_doc['documents']) == 0:
                logger.error(f"No se encontró el examen con ID {examen_id} en Appwrite")
                return jsonify({"success": False, "error": f"No se encontró el examen con ID: {examen_id}"}), 404
            
            # Extraer datos del examen
            examen_doc = examen_doc['documents'][0]
            # Obtener email del profesor desde la colección examen_profesor_url
            email_profesor = examen_doc.get('email', 'email_no_encontrado')  # Esta colección SÍ tiene el email correcto
            #examen_data = json.loads(examen_doc['examenDataJson'])
            
        except Exception as e:
            logger.error(f"Error al buscar examen en Appwrite: {str(e)}", exc_info=True)
            return jsonify({"success": False, "error": f"Error al cargar el examen: {str(e)}"}), 500
        
        logger.info(f"Procesando envío para Examen: {examen_id}, Alumno: {id_alumno} ({nombre_alumno})")
        
        # Procesar respuestas de opción múltiple
        respuestas_marcar = []
        form_keys = [k for k in request.form.keys() if k.startswith('pregunta-')]
        for key in form_keys:
            numero = key.split('-')[1]
            valor = request.form.get(key)
            respuestas_marcar.append({
                "numero": int(numero),
                "respuesta": int(valor) if valor else None
            })

        # Procesar respuestas libres
        respuestas_libres = []
        form_keys = [k for k in request.form.keys() if k.startswith('libre-')]
        for key in form_keys:
            numero = key.split('-')[1]
            valor = request.form.get(key)
            respuestas_libres.append({
                "numero": int(numero),
                "respuesta": valor or ""
            })

        # Procesar respuestas de casos
        respuestas_casos = []
        form_keys = [k for k in request.form.keys() if k.startswith('caso-')]
        for key in form_keys:
            numero = key.split('-')[1]
            valor = request.form.get(key)
            respuestas_casos.append({
                "numero": int(numero),
                "respuesta": valor or ""
            })
        
        #=========================INICIO: Procesar archivos adjuntos**
        
        # **NUEVO: Procesar archivos adjuntos**
        archivos_adjuntos = []
        logger.info(f"Archivos recibidos: {list(request.files.keys())}")
        
        for key in request.files:
            if key.startswith('archivo-'):
                archivo = request.files[key]
                if archivo and archivo.filename:
                    try:
                        # Extraer tipo y número de pregunta
                        pregunta_info = key.replace('archivo-', '')  # ej: "libre-6" o "caso-10"
                        
                        logger.info(f"Procesando archivo: {archivo.filename} para {pregunta_info}")
                        
                        # Subir archivo a Appwrite
                        resultado_archivo = subir_archivo_estudiante(
                            archivo, examen_id, id_alumno, pregunta_info
                        )
                        
                        archivos_adjuntos.append({
                            "pregunta": pregunta_info,
                            "nombre_original": resultado_archivo['nombre_original'],
                            "nombre_guardado": resultado_archivo['nombre_guardado'],
                            "file_id": resultado_archivo['file_id'],
                            "tamaño": resultado_archivo['tamaño'],
                            "tipo": resultado_archivo['tipo'],
                            "url": resultado_archivo['url']
                        })
                        
                        logger.info(f"Archivo guardado exitosamente: {resultado_archivo['file_id']}")
                        
                    except Exception as e:
                        logger.error(f"Error procesando archivo {archivo.filename}: {str(e)}")
                        # Continuar con otros archivos en caso de error
                        archivos_adjuntos.append({
                            "pregunta": key.replace('archivo-', ''),
                            "nombre_original": archivo.filename,
                            "error": str(e)
                        })
        
        #=========================**FIN: Procesar archivos adjuntos**
        
        # Convertir respuestas a JSON
        preguntas_marcar_str = json.dumps(respuestas_marcar, ensure_ascii=False)
        preguntas_libres_str = json.dumps(respuestas_libres, ensure_ascii=False)
        casos_uso_str = json.dumps(respuestas_casos, ensure_ascii=False)
        archivos_adjuntos_str = json.dumps(archivos_adjuntos, ensure_ascii=False)  # **NUEVO**  
        
        # Crear documento en Appwrite (colección examen_alumno)
        target_collection_id = APPWRITE_COLLECTION_ID  # 67f517c00027fc5b40be
        document_id = f"sub_{examen_id}_{id_alumno}_{int(time.time())}"
        
        document_data = {
            "email": email_profesor,   # ← AGREGAR ESTA LÍNEA email
            "examen_id": examen_id,
            "id_alumno": id_alumno,
            "nombre_alumno": nombre_alumno,
            "nombre_profesor": nombre_profesor,
            "id_profesor": id_profesor,
            "nombre_examen": nombre_examen,
            "tipo_examen": tipo_examen,
            "preguntas_marcar": preguntas_marcar_str,
            "preguntas_libres": preguntas_libres_str,
            "casos_uso": casos_uso_str
        }
        
        try:
            response = databases.create_document(
                database_id=APPWRITE_DATABASE_ID,
                collection_id=target_collection_id,
                document_id=document_id,
                data=document_data
            )
            logger.info(f"Documento de respuestas creado: {response['$id']}")
            logger.info(f"Archivos adjuntos guardados: {len(archivos_adjuntos)}")

            # CREAR HTML COMO VARIABLE SEPARADA (sin f-string)
            html_response = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>🎉 Examen Enviado Exitosamente</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    
                    body { 
                        font-family: 'Arial', sans-serif; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        overflow-x: hidden;
                    }
                    
                    .container {
                        background: white;
                        border-radius: 20px;
                        padding: 40px;
                        text-align: center;
                        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                        max-width: 500px;
                        width: 90%;
                        position: relative;
                        animation: bounceIn 0.8s ease-out;
                    }
                    
                    @keyframes bounceIn {
                        0% { transform: scale(0.3); opacity: 0; }
                        50% { transform: scale(1.05); }
                        70% { transform: scale(0.9); }
                        100% { transform: scale(1); opacity: 1; }
                    }
                    
                    .success-icon {
                        font-size: 80px;
                        margin-bottom: 20px;
                        animation: pulse 2s infinite;
                    }
                    
                    @keyframes pulse {
                        0% { transform: scale(1); }
                        50% { transform: scale(1.1); }
                        100% { transform: scale(1); }
                    }
                    
                    h1 {
                        color: #28a745;
                        font-size: 2.5rem;
                        margin-bottom: 20px;
                        font-weight: bold;
                    }
                    
                    .subtitle {
                        color: #6c757d;
                        font-size: 1.2rem;
                        margin-bottom: 30px;
                    }
                    
                    .details {
                        background: #f8f9fa;
                        border-radius: 15px;
                        padding: 25px;
                        margin: 30px 0;
                        text-align: left;
                        border-left: 5px solid #28a745;
                    }
                    
                    .detail-item {
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 12px;
                        padding: 8px 0;
                        border-bottom: 1px solid #e9ecef;
                    }
                    
                    .detail-item:last-child {
                        border-bottom: none;
                    }
                    
                    .label {
                        font-weight: bold;
                        color: #495057;
                    }
                    
                    .value {
                        color: #28a745;
                        font-weight: 600;
                    }
                    
                    .countdown {
                        background: #e7f3ff;
                        border: 2px solid #b3d9ff;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 20px 0;
                        font-size: 1.1rem;
                        color: #0066cc;
                    }
                    
                    .confetti {
                        position: fixed;
                        width: 10px;
                        height: 10px;
                        background: #f1c40f;
                        animation: confetti-fall 3s linear infinite;
                    }
                    
                    @keyframes confetti-fall {
                        0% {
                            transform: translateY(-100vh) rotate(0deg);
                            opacity: 1;
                        }
                        100% {
                            transform: translateY(100vh) rotate(720deg);
                            opacity: 0;
                        }
                    }
                    
                    .footer {
                        margin-top: 30px;
                        color: #6c757d;
                        font-size: 0.9rem;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success-icon">🎉</div>
                    <h1>¡Examen Enviado!</h1>
                    <p class="subtitle">Tu examen ha sido guardado exitosamente</p>
                    
                    <div class="details">
                        <div class="detail-item">
                            <span class="label">👤 Alumno:</span>
                            <span class="value">NOMBRE_ALUMNO</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">🆔 ID Alumno:</span>
                            <span class="value">ID_ALUMNO</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">📋 Examen:</span>
                            <span class="value">NOMBRE_EXAMEN</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">📄 ID de Envío:</span>
                            <span class="value">SUBMISSION_ID</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">📅 Fecha y Hora:</span>
                            <span class="value">FECHA_HORA</span>
                        </div>
                    </div>
                    
                    <div class="countdown">
                        ⏱️ Confirmando envío en <span id="countdown">10</span> segundos...
                    </div>
                    
                    <div class="footer">
                        ✅ Tu profesor revisará las respuestas<br>
                        🔒 No es posible volver a modificar el examen
                    </div>
                </div>

                <script>
                    function createConfetti() {
                        const colors = ['#f1c40f', '#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#e67e22'];
                        
                        for (let i = 0; i < 50; i++) {
                            setTimeout(() => {
                                const confetti = document.createElement('div');
                                confetti.className = 'confetti';
                                confetti.style.left = Math.random() * 100 + 'vw';
                                confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                                confetti.style.animationDelay = Math.random() * 3 + 's';
                                confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
                                document.body.appendChild(confetti);
                                
                                setTimeout(() => {
                                    confetti.remove();
                                }, 6000);
                            }, i * 100);
                        }
                    }
                    
                    let timeLeft = 10;
                    const countdownElement = document.getElementById('countdown');
                    
                    const timer = setInterval(() => {
                        timeLeft--;
                        countdownElement.textContent = timeLeft;
                        
                        if (timeLeft <= 0) {
                            clearInterval(timer);
                            document.querySelector('.countdown').innerHTML = '✅ <strong>Examen enviado exitosamente</strong><br>Puedes cerrar esta ventana';
                            document.querySelector('.countdown').style.background = '#d4edda';
                            document.querySelector('.countdown').style.border = '2px solid #28a745';
                            document.querySelector('.countdown').style.color = '#155724';
                        }
                    }, 1000);
                    
                    createConfetti();
                    setInterval(createConfetti, 2000);
                    
                    window.history.pushState(null, null, window.location.href);
                    window.onpopstate = () => {
                        window.history.pushState(null, null, window.location.href);
                    };
                    
                    window.addEventListener('beforeunload', (e) => {
                        e.preventDefault();
                        e.returnValue = '';
                    });
                </script>
            </body>
            </html>
            """

            # REEMPLAZAR PLACEHOLDERS CON DATOS REALES
            html_response = html_response.replace('NOMBRE_ALUMNO', nombre_alumno)
            html_response = html_response.replace('ID_ALUMNO', id_alumno)
            html_response = html_response.replace('NOMBRE_EXAMEN', nombre_examen)
            html_response = html_response.replace('SUBMISSION_ID', response['$id'])
            html_response = html_response.replace('TOTAL_ARCHIVOS', str(len(archivos_adjuntos)))
            html_response = html_response.replace('FECHA_HORA', datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

            return html_response
            
        except Exception as e:
            logger.error(f"Error al guardar documento de respuestas: {str(e)}", exc_info=True)
            return jsonify({"success": False, "error": f"Error al guardar respuestas: {str(e)}"}), 500
    
    except Exception as e:
        logger.error(f"Error general en submit_exam: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": f"Error interno del servidor: {str(e)}"}), 500

# =================INICIO GUARDAR ADJUNTO=======================================================    

def subir_archivo_estudiante(archivo, examen_id, id_alumno, pregunta_id):
    """
    Sube archivo de estudiante al bucket APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN
    """
    try:
        # Inicializar Cliente Appwrite
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT)
        client.set_project(APPWRITE_PROJECT_ID)
        client.set_key(APPWRITE_API_KEY)
        storage_service = Storage(client)
        
        # Obtener bucket ID desde variable de entorno
        target_bucket_id = os.getenv('APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN')
        
        if not target_bucket_id:
            raise Exception("APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN no configurado")
        
        # Construir nombre del archivo: examenId_alumnoId_pregunta_nombreOriginal
        base_name, extension = os.path.splitext(archivo.filename)
        safe_base_name = base_name.replace(' ', '_')
        nuevo_nombre = f"{examen_id}_{id_alumno}_{pregunta_id}_{safe_base_name}{extension}"
        
        # Leer contenido del archivo
        file_bytes = archivo.read()
        
        # Generar ID único para Appwrite
        file_id = ID.unique()
        
        # Crear InputFile
        appwrite_file = InputFile.from_bytes(
            file_bytes,
            nuevo_nombre,
            archivo.content_type
        )
        
        # Subir archivo a Appwrite
        result = storage_service.create_file(
            bucket_id=target_bucket_id,
            file_id=file_id,
            file=appwrite_file
        )
        
        logger.info(f"Archivo estudiante subido: {nuevo_nombre} -> ID: {result['$id']}")
        
        return {
            'file_id': result['$id'],
            'nombre_original': archivo.filename,
            'nombre_guardado': nuevo_nombre,
            'tamaño': len(file_bytes),
            'tipo': archivo.content_type,
            'url': f"https://cloud.appwrite.io/v1/storage/buckets/{target_bucket_id}/files/{result['$id']}/view?project={os.getenv('APPWRITE_PROJECT_ID')}"
        }
        
    except Exception as e:
        logger.error(f"Error subiendo archivo estudiante: {str(e)}")
        raise Exception(f"Error al subir archivo: {str(e)}")

# =================FIN GUARDAR ADJUNTO=======================================================    
    
    
# =================INICIO DEBUG=======================================================

@app.route('/debug/<examen_id>/<id_alumno>', methods=['GET'])
def debug_respuestas(examen_id, id_alumno):
    try:
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT)
        client.set_project(APPWRITE_PROJECT_ID)
        client.set_key(APPWRITE_API_KEY)
        databases = Databases(client)
        
        # Buscar respuestas del alumno
        respuestas = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_ID,
            queries=[
                Query.equal('examen_id', examen_id),
                Query.equal('id_alumno', id_alumno)
            ]
        )
        
        if respuestas['total'] > 0:
            respuesta_doc = respuestas['documents'][0]
            
            return f"""
            <h1>Debug - Respuestas Encontradas</h1>
            <h3>Datos del documento:</h3>
            <pre>{json.dumps(respuesta_doc, indent=2, ensure_ascii=False)}</pre>
            
            <h3>Preguntas Marcar:</h3>
            <pre>{respuesta_doc.get('preguntas_marcar', 'No encontrado')}</pre>
            
            <h3>Preguntas Libres:</h3>
            <pre>{respuesta_doc.get('preguntas_libres', 'No encontrado')}</pre>
            
            <h3>Casos Uso:</h3>
            <pre>{respuesta_doc.get('casos_uso', 'No encontrado')}</pre>
            """
        else:
            return "<h1>No se encontraron respuestas para este examen/alumno</h1>"
            
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

# =================FIN DEBUG=======================================================

# =================INICIO DEBUG 2 =======================================================

@app.route('/debug-examen/<examen_id>', methods=['GET'])
def debug_examen_original(examen_id):
    try:
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT)
        client.set_project(APPWRITE_PROJECT_ID)
        client.set_key(APPWRITE_API_KEY)
        databases = Databases(client)
        
        # Buscar examen original
        result = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_EXAMEN_PROFESOR_URL,
            queries=[
                Query.equal('id_examen', examen_id),
            ]
        )
        
        if result['total'] > 0:
            documento = result['documents'][0]
            examen_data = json.loads(documento['examenDataJson'])
            
            return f"""
            <h1>Debug - Estructura del Examen Original</h1>
            <h3>Preguntas Marcar:</h3>
            <pre>{json.dumps(examen_data.get('preguntasMarcar', []), indent=2, ensure_ascii=False)}</pre>
            
            <h3>Preguntas Libres:</h3>
            <pre>{json.dumps(examen_data.get('preguntasLibres', []), indent=2, ensure_ascii=False)}</pre>
            
            <h3>Casos Uso:</h3>
            <pre>{json.dumps(examen_data.get('casosUso', []), indent=2, ensure_ascii=False)}</pre>
            """
        else:
            return "<h1>No se encontró el examen original</h1>"
            
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

# =================FIN DEBUG 2 =======================================================

# =================INICIO DEBUG 3 =======================================================


# =================FIN DEBUG 3 =======================================================

# =================INICIO MOSTRAR PDF EXAMEN RESPONDIDO =======================================================

@app.route('/examen/<examen_id>/<id_alumno>', methods=['GET'])
def mostrar_examen_con_respuestas(examen_id, id_alumno):
    try:
        client = Client()
        client.set_endpoint(APPWRITE_ENDPOINT)
        client.set_project(APPWRITE_PROJECT_ID)
        client.set_key(APPWRITE_API_KEY)
        databases = Databases(client)
        
        # 1. Buscar examen original
        result = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_EXAMEN_PROFESOR_URL,
            queries=[
                Query.equal('id_examen', examen_id)
            ]
        )
        
        if result['total'] == 0:
            return "<h1>Examen no encontrado</h1>"
        
        documento = result['documents'][0]
        examen_data = json.loads(documento['examenDataJson'])
        
        # 2. Buscar respuestas del alumno
        respuestas = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_ID,
            queries=[
                Query.equal('examen_id', examen_id),
                Query.equal('id_alumno', id_alumno)
            ]
        )
        
        # 3. Mapear respuestas si existen
        if respuestas['total'] > 0:
            respuesta_doc = respuestas['documents'][0]
            
            # Parsear respuestas JSON
            preguntas_marcar = json.loads(respuesta_doc.get('preguntas_marcar', '[]'))
            preguntas_libres = json.loads(respuesta_doc.get('preguntas_libres', '[]'))
            casos_uso = json.loads(respuesta_doc.get('casos_uso', '[]'))
            
            # MAPEO CORREGIDO - Preguntas múltiples (1-5 → 1-5)
            if examen_data.get('preguntasMarcar'):
                for pregunta in examen_data['preguntasMarcar']:
                    respuesta_encontrada = next(
                        (r for r in preguntas_marcar if r['numero'] == pregunta['numero']), 
                        None
                    )
                    if respuesta_encontrada:
                        pregunta['respuestaSeleccionada'] = respuesta_encontrada['respuesta']
            
            # MAPEO CORREGIDO - Preguntas libres (1-4 → 6-9)
            if examen_data.get('preguntasLibres'):
                for i, pregunta in enumerate(examen_data['preguntasLibres']):
                    numero_pregunta = pregunta.get('numero')  # ✅ Usar número real (10,11,12,13)
                    respuesta_encontrada = next(
                        (r for r in preguntas_libres if r['numero'] == numero_pregunta), 
                        None
                    )
                    if respuesta_encontrada:
                        pregunta['respuestaAlumno'] = respuesta_encontrada['respuesta']
            
            # MAPEO CORREGIDO - Casos de uso (1 → 10)
            if examen_data.get('casosUso'):
                for i, caso in enumerate(examen_data['casosUso']):
                    numero_pregunta = caso.get('numero')  # ✅ Usar número real
                    respuesta_encontrada = next(
                        (r for r in casos_uso if r['numero'] == numero_pregunta), 
                        None
                    )
                    if respuesta_encontrada:
                        caso['respuestaAlumno'] = respuesta_encontrada['respuesta']
        
        # 4. Obtener datos del alumno
        alumno_nombre = respuesta_doc.get('nombre_alumno', 'N/A') if respuestas['total'] > 0 else 'N/A'
        
        # 5. Generar HTML completo mejorado
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Examen Respondido - {examen_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
                h1 {{ text-align: center; color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #2980b9; margin-top: 30px; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }}
                .pregunta {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background: #f9f9f9; }}
                .respuesta {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin-top: 10px; white-space: pre-wrap; border-left: 4px solid #28a745; }}
                .opcion {{ margin: 5px 0 5px 20px; padding: 5px; }}
                .opcion.selected {{ background: #d4edda; border-radius: 3px; font-weight: bold; border-left: 3px solid #28a745; }}
                .info {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .sin-respuesta {{ background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; font-style: italic; }}
            </style>
        </head>
        <body>
            <h1>📋 Examen Respondido - {examen_id}</h1>
            
            <div class="info">
                <p><strong>👤 Alumno:</strong> {alumno_nombre}</p>
                <p><strong>🆔 ID Alumno:</strong> {id_alumno}</p>
                <p><strong>📅 Fecha de consulta:</strong> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </div>
        """
        
        # Preguntas de opción múltiple
        if examen_data.get('preguntasMarcar'):
            html_content += """<h2>📝 Preguntas de Opción Múltiple</h2>"""
            for pregunta in examen_data.get('preguntasMarcar', []):
                html_content += f"""
                <div class="pregunta">
                    <p><strong>Pregunta #{pregunta['numero']} ({pregunta.get('puntaje', 1)} pts):</strong></p>
                    <p>{pregunta.get('texto', 'Sin texto')}</p>
                """
                
                # Mostrar opciones con la seleccionada marcada
                if pregunta.get('opciones'):
                    for i, opcion in enumerate(pregunta['opciones']):
                        es_seleccionada = pregunta.get('respuestaSeleccionada') == i
                        clase = 'opcion selected' if es_seleccionada else 'opcion'
                        texto_opcion = opcion.get('texto', opcion) if isinstance(opcion, dict) else str(opcion)
                        html_content += f"""
                        <div class="{clase}">
                            {chr(65 + i)}) {texto_opcion}
                            {' ← SELECCIONADA' if es_seleccionada else ''}
                        </div>
                        """
                else:
                    html_content += '<p class="sin-respuesta">Sin opciones disponibles</p>'
                
                html_content += "</div>"
        
        # Preguntas libres  
        if examen_data.get('preguntasLibres'):
            html_content += """<h2>✍️ Preguntas de Desarrollo</h2>"""
            for pregunta in examen_data.get('preguntasLibres', []):
                respuesta_alumno = pregunta.get('respuestaAlumno', '').strip()
                html_content += f"""
                <div class="pregunta">
                    <p><strong>Pregunta #{pregunta['numero']} ({pregunta.get('puntaje', 1)} pts):</strong></p>
                    <p>{pregunta.get('texto', 'Sin texto')}</p>
                """
                
                if respuesta_alumno:
                    html_content += f"""
                    <div class="respuesta">
                        <strong>Respuesta del alumno:</strong><br>
                        {respuesta_alumno}
                    </div>
                    """
                else:
                    html_content += '<div class="sin-respuesta">El alumno no respondió esta pregunta</div>'
                
                html_content += "</div>"
        
        # Casos de uso
        if examen_data.get('casosUso'):
            html_content += """<h2>💼 Casos de Uso</h2>"""
            for caso in examen_data.get('casosUso', []):
                respuesta_alumno = caso.get('respuestaAlumno', '').strip()
                html_content += f"""
                <div class="pregunta">
                    <p><strong>Caso #{caso['numero']} ({caso.get('puntaje', 1)} pts):</strong></p>
                    <p><strong>Descripción:</strong> {caso.get('descripcion', 'Sin descripción')}</p>
                    <p><strong>Pregunta:</strong> {caso.get('pregunta', 'Sin pregunta')}</p>
                """
                
                if respuesta_alumno:
                    html_content += f"""
                    <div class="respuesta">
                        <strong>Respuesta del alumno:</strong><br>
                        {respuesta_alumno}
                    </div>
                    """
                else:
                    html_content += '<div class="sin-respuesta">El alumno no respondió este caso</div>'
                
                html_content += "</div>"
        
        html_content += """
            <div style="text-align: center; margin-top: 40px; color: #7f8c8d;">
                <p>Sistema de Exámenes en Línea</p>
            </div>
            </body>
            </html>
        """
        
        return html_content
        
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1><p>Detalles: {traceback.format_exc()}</p>"

# =================FIN MOSTRAR PDF EXAMEN RESPONDIDO =======================================================
databases = Databases(appwrite_client)

@app.route('/api/buscar-examenes', methods=['POST'])
def buscar_examenes():
    try:
        data = request.get_json()
        termino = data.get('termino', '').lower()
        email = data.get('email')
        
        if not termino:
            return jsonify({'error': 'Término de búsqueda requerido'}), 400
            
        # Buscar en tu base de datos existente
        resultados = databases.list_documents(
            database_id=APPWRITE_DATABASE_ID,
            collection_id=APPWRITE_COLLECTION_EXAMEN_PROFESOR_URL,
            queries=[
                Query.equal('email', email),
            ]
        )
        
        examenes_encontrados = []
        for doc in resultados['documents']:
            data = json.loads(doc['examenDataJson'])
            examenes_encontrados.append({
                'id': data.get('id'),
                'nombre': data.get('nombreExamen'),
                'profesor': data.get('profesor'),
                'fecha': data.get('fecha'),
                'tipo': data.get('tipoExamen')
            })
            
        return jsonify({
            'success': True,
            'resultados': examenes_encontrados
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    # Este endpoint ya no se utilizará, redirigimos a generar-examen
    return jsonify({
        "status": "deprecated",
        "message": "Este endpoint está obsoleto. Utiliza /api/generar-examen en su lugar."
    }), 308  # 308 Permanent Redirect

@app.after_request
def cors(response):
    # Obtener el origen de la solicitud
    origin = request.headers.get('Origin')
    allowed_origins = ['http://127.0.0.1:8080', 'http://localhost:8080']
    
    # Comprobar si el origen está permitido
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        response.headers.add('Access-Control-Max-Age', '3600')
    return response

@app.route('/', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path=None):
    return '', 204  # No content response for OPTIONS requests

#==================INICIO RECOMENDACION MODELOS=================================================

@app.route('/api/recomendaciones-modelos/<tipo_pregunta>', methods=['GET'])
def obtener_recomendaciones_modelos(tipo_pregunta):
    """
    Endpoint que devuelve recomendaciones de modelos según el tipo de pregunta
    Tipos válidos: opcion_multiple, abierta, caso_uso
    """
    try:
        if tipo_pregunta not in RECOMENDACIONES_MODELOS:
            return jsonify({
                'error': f'Tipo de pregunta no válido: {tipo_pregunta}',
                'tipos_validos': list(RECOMENDACIONES_MODELOS.keys())
            }), 400
        
        recomendaciones = RECOMENDACIONES_MODELOS[tipo_pregunta]
        
        # Agregar información adicional de disponibilidad
        for categoria in ['recomendados', 'aceptables']:
            if categoria in recomendaciones:
                for modelo_info in recomendaciones[categoria]:
                    modelo_key = modelo_info['modelo']
                    # Verificar si el modelo está disponible en nuestra configuración
                    #modelo_disponible = modelo_key in modelos or modelo_key in MODELOS_TEXTO_OPENROUTER + MODELOS_MULTIMODAL_OPENROUTER
                    modelo_disponible = True
                    modelo_info['disponible'] = modelo_disponible
                    
                    # Agregar configuración específica si está disponible
                    if modelo_key in modelos:
                        config = modelos[modelo_key]
                        modelo_info['api_provider'] = config.get('api', 'unknown')
                        modelo_info['activo'] = config.get('activo', True)
        
        return jsonify({
            'success': True,
            'tipo_pregunta': tipo_pregunta,
            'recomendaciones': recomendaciones,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo recomendaciones para {tipo_pregunta}: {str(e)}")
        return jsonify({
            'error': f'Error interno del servidor: {str(e)}'
        }), 500

@app.route('/api/recomendaciones-modelos', methods=['GET'])
def obtener_todas_recomendaciones():
    """
    Endpoint que devuelve todas las recomendaciones de modelos
    """
    try:
        return jsonify({
            'success': True,
            'recomendaciones': RECOMENDACIONES_MODELOS,
            'tipos_disponibles': list(RECOMENDACIONES_MODELOS.keys()),
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo todas las recomendaciones: {str(e)}")
        return jsonify({
            'error': f'Error interno del servidor: {str(e)}'
        }), 500
                

if __name__ == '__main__':
    app.run(debug=True, port=5002)