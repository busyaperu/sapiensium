from flask import Flask, request, jsonify
from flask_cors import CORS
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
import os
import logging
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración Appwrite
client = Client()
client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PAGOS_OPERACIONES_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_PAGOS_OPERACIONES_API_KEY'))

databases = Databases(client)
DATABASE_ID = os.getenv('APPWRITE_COMPRA_CREDITOS_DATABASE_ID')
USUARIOS_CREDITOS_COLLECTION_ID = os.getenv('APPWRITE_USUARIOS_CREDITOS_COLLECTION_ID')

@app.route('/api/dashboard/creditos', methods=['GET'])
def get_dashboard_creditos():
    """Obtener métricas principales del dashboard"""
    try:
        # Obtener todos los usuarios con créditos
        usuarios_result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=USUARIOS_CREDITOS_COLLECTION_ID
        )
        
        # Calcular métricas totales
        total_saldo = 0
        total_limite = 0
        usuarios_activos = 0
        
        for usuario in usuarios_result['documents']:
            saldo = usuario.get('saldo_actual', 0)
            limite = usuario.get('limite_mensual', 0)
            
            total_saldo += saldo
            total_limite += limite
            
            if saldo > 0:
                usuarios_activos += 1
        
        total_usado = total_limite - total_saldo
        porcentaje_usado = round((total_usado / max(total_limite, 1)) * 100, 1)
        
        # Calcular costo aproximado (asumiendo $20 por 12,000 créditos)
        costo_usado = round((total_usado / 12000) * 20, 2)
        
        # Proyección simple basada en uso actual
        proyeccion = round(total_usado * 1.1)
        
        return jsonify({
            'saldo_actual': total_saldo,
            'limite_creditos': total_limite,
            'creditos_usados': total_usado,
            'porcentaje_usado': porcentaje_usado,
            'costo_usado': costo_usado,
            'proyeccion': proyeccion,
            'usuarios_activos': usuarios_activos,
            'total_usuarios': len(usuarios_result['documents'])
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de créditos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/actividades', methods=['GET'])
def get_dashboard_actividades():
    """Obtener actividades recientes"""
    try:
        limite = int(request.args.get('limite', 10))
        
        # Obtener transacciones recientes
        result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id='transacciones_creditos',
            queries=[
                Query.order_desc('$createdAt'),
                Query.limit(limite)
            ]
        )
        
        actividades = []
        for trans in result['documents']:
            # Determinar tipo de actividad basado en la cantidad
            cantidad = trans.get('cantidad', 0)
            if cantidad < 0:
                tipo = 'Uso de créditos'
            else:
                tipo = 'Recarga de créditos'
            
            actividades.append({
                'fecha': trans.get('$createdAt'),
                'actividad': trans.get('descripcion', tipo),
                'email': trans.get('email', 'Usuario'),
                'modelos': trans.get('modelos_usados', 1),
                'creditos': abs(cantidad),
                'tipo': 'uso' if cantidad < 0 else 'recarga',
                'estado': 'Completado'
            })
        
        return jsonify({
            'actividades': actividades,
            'total': len(actividades)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo actividades: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/graficos', methods=['GET'])
def get_dashboard_graficos():
    """Obtener datos para gráficos"""
    try:
        periodo = request.args.get('periodo', 'dia')  # dia, semana, mes
        
        # Obtener transacciones del período
        if periodo == 'dia':
            fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif periodo == 'semana':
            fecha_inicio = datetime.now() - timedelta(days=7)
        else:  # mes
            fecha_inicio = datetime.now() - timedelta(days=30)
        
        result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id='transacciones_creditos',
            queries=[
                Query.greater_than('$createdAt', fecha_inicio.isoformat()),
                Query.order_asc('$createdAt')
            ]
        )
        
        # Procesar datos según el período
        if periodo == 'dia':
            # Agrupar por horas
            datos = procesar_datos_dia(result['documents'])
        elif periodo == 'semana':
            # Agrupar por días
            datos = procesar_datos_semana(result['documents'])
        else:
            # Agrupar por semanas
            datos = procesar_datos_mes(result['documents'])
        
        # Obtener distribución por tipo de evaluación
        distribucion = obtener_distribucion_tipos(result['documents'])
        
        return jsonify({
            'periodo': periodo,
            'datos_principales': datos,
            'distribucion': distribucion
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo datos de gráficos: {e}")
        return jsonify({'error': str(e)}), 500

def procesar_datos_dia(transacciones):
    """Procesar datos para vista diaria (por horas)"""
    horas = {}
    
    for trans in transacciones:
        try:
            fecha = datetime.fromisoformat(trans.get('$createdAt', '').replace('Z', '+00:00'))
            hora_key = fecha.strftime('%H:00')
            cantidad = abs(trans.get('cantidad', 0))
            
            if hora_key not in horas:
                horas[hora_key] = 0
            horas[hora_key] += cantidad
        except:
            continue
    
    # Generar datos para las últimas 8 horas
    labels = []
    data = []
    
    for i in range(8):
        hora = (datetime.now() - timedelta(hours=7-i)).strftime('%H:00')
        labels.append(hora)
        data.append(horas.get(hora, 0))
    
    return {
        'labels': labels,
        'datasets': [{
            'label': 'Créditos Usados',
            'data': data,
            'borderColor': '#3b82f6',
            'backgroundColor': 'rgba(59, 130, 246, 0.1)',
            'tension': 0.4,
            'fill': True
        }]
    }

def procesar_datos_semana(transacciones):
    """Procesar datos para vista semanal (por días)"""
    dias = {}
    
    for trans in transacciones:
        try:
            fecha = datetime.fromisoformat(trans.get('$createdAt', '').replace('Z', '+00:00'))
            dia_key = fecha.strftime('%a')
            cantidad = abs(trans.get('cantidad', 0))
            
            if dia_key not in dias:
                dias[dia_key] = 0
            dias[dia_key] += cantidad
        except:
            continue
    
    labels = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']
    data = [dias.get(dia, 0) for dia in labels]
    
    return {
        'labels': labels,
        'datasets': [{
            'label': 'Créditos Usados',
            'data': data,
            'backgroundColor': '#3b82f6'
        }]
    }

def procesar_datos_mes(transacciones):
    """Procesar datos para vista mensual (por semanas)"""
    semanas = {}
    acumulado = {}
    
    for trans in transacciones:
        try:
            fecha = datetime.fromisoformat(trans.get('$createdAt', '').replace('Z', '+00:00'))
            # Calcular número de semana
            inicio_mes = fecha.replace(day=1)
            semana = ((fecha - inicio_mes).days // 7) + 1
            semana_key = f'Sem {semana}'
            cantidad = abs(trans.get('cantidad', 0))
            
            if semana_key not in semanas:
                semanas[semana_key] = 0
            semanas[semana_key] += cantidad
        except:
            continue
    
    # Generar datos para 4 semanas
    labels = ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4']
    data_semanal = [semanas.get(sem, 0) for sem in labels]
    
    # Calcular acumulado
    data_acumulado = []
    total = 0
    for valor in data_semanal:
        total += valor
        data_acumulado.append(total)
    
    return {
        'labels': labels,
        'datasets': [
            {
                'label': 'Créditos Semanales',
                'data': data_semanal,
                'borderColor': '#3b82f6',
                'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                'tension': 0.4,
                'fill': False
            },
            {
                'label': 'Acumulado',
                'data': data_acumulado,
                'borderColor': '#10b981',
                'backgroundColor': 'rgba(16, 185, 129, 0.1)',
                'tension': 0.4,
                'fill': False
            }
        ]
    }

def obtener_distribucion_tipos(transacciones):
    """Obtener distribución por tipos de evaluación"""
    tipos = {
        'Quiz Semanal': 0,
        'Parciales': 0,
        'Examen Final': 0,
        'Trabajos': 0
    }
    
    for trans in transacciones:
        descripcion = trans.get('descripcion', '').lower()
        cantidad = abs(trans.get('cantidad', 0))
        
        if 'quiz' in descripcion:
            tipos['Quiz Semanal'] += cantidad
        elif 'parcial' in descripcion:
            tipos['Parciales'] += cantidad
        elif 'final' in descripcion or 'examen' in descripcion:
            tipos['Examen Final'] += cantidad
        else:
            tipos['Trabajos'] += cantidad
    
    return {
        'labels': list(tipos.keys()),
        'datasets': [{
            'data': list(tipos.values()),
            'backgroundColor': ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c'],
            'borderWidth': 2,
            'borderColor': '#fff'
        }]
    }

@app.route('/api/dashboard/estadisticas', methods=['GET'])
def get_estadisticas_generales():
    """Obtener estadísticas generales del sistema"""
    try:
        periodo_dias = int(request.args.get('periodo', 30))
        fecha_inicio = datetime.now() - timedelta(days=periodo_dias)
        
        # Estadísticas de usuarios
        usuarios_result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=USUARIOS_CREDITOS_COLLECTION_ID
        )
        
        # Estadísticas de transacciones
        transacciones_result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id='transacciones_creditos',
            queries=[
                Query.greater_than('$createdAt', fecha_inicio.isoformat())
            ]
        )
        
        # Calcular métricas
        total_transacciones = len(transacciones_result['documents'])
        creditos_totales_usados = sum(
            abs(t.get('cantidad', 0)) 
            for t in transacciones_result['documents'] 
            if t.get('cantidad', 0) < 0
        )
        
        usuarios_activos = len([
            u for u in usuarios_result['documents'] 
            if u.get('saldo_actual', 0) > 0
        ])
        
        return jsonify({
            'periodo_dias': periodo_dias,
            'total_usuarios': len(usuarios_result['documents']),
            'usuarios_activos': usuarios_activos,
            'total_transacciones': total_transacciones,
            'creditos_usados_periodo': creditos_totales_usados,
            'promedio_uso_diario': round(creditos_totales_usados / max(periodo_dias, 1), 2)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas generales: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/usuarios', methods=['GET'])
def get_usuarios_resumen():
    """Obtener resumen de usuarios"""
    try:
        result = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=USUARIOS_CREDITOS_COLLECTION_ID,
            queries=[Query.order_desc('saldo_actual')]
        )
        
        usuarios = []
        for usuario in result['documents']:
            usuarios.append({
                'email': usuario.get('email'),
                'saldo_actual': usuario.get('saldo_actual', 0),
                'limite_mensual': usuario.get('limite_mensual', 0),
                'tipo_cuenta': usuario.get('tipo_cuenta', 'individual'),
                'porcentaje_usado': round(
                    ((usuario.get('limite_mensual', 0) - usuario.get('saldo_actual', 0)) / 
                     max(usuario.get('limite_mensual', 1), 1)) * 100, 1
                )
            })
        
        return jsonify({
            'usuarios': usuarios,
            'total': len(usuarios)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen de usuarios: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud"""
    return jsonify({
        'status': 'healthy',
        'service': 'dashboard-creditos',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("Servidor de Dashboard de Créditos iniciado")
    app.run(debug=True, host='0.0.0.0', port=5009)