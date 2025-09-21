from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
import os
import logging
import csv
import io
from datetime import datetime, timedelta
from collections import defaultdict
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
TRANSACCIONES_COLLECTION_ID = os.getenv('APPWRITE_TRANSACCIONES_COLLECTION_ID')
EVALUACIONES_COLLECTION_ID = os.getenv('APPWRITE_EVALUACIONES_COLLECTION_ID')
TRANSACCIONES_PAGOS_COLLECTION_ID = os.getenv('APPWRITE_TRANSACCIONES_COLLECTION_ID')

@app.route('/api/analytics/dashboard', methods=['GET'])
def get_analytics_dashboard():
    print(f"DATABASE_ID: {DATABASE_ID}")
    print(f"USUARIOS_CREDITOS_COLLECTION_ID: {USUARIOS_CREDITOS_COLLECTION_ID}")
    """Obtener métricas consolidadas para el dashboard"""
    try:
        periodo = request.args.get('periodo', '30')  # días
        fecha_inicio = datetime.now() - timedelta(days=int(periodo))
        
        # Obtener datos de todas las fuentes
        usuarios_data = databases.list_documents(DATABASE_ID, USUARIOS_CREDITOS_COLLECTION_ID)
        transacciones_data = databases.list_documents(DATABASE_ID, TRANSACCIONES_COLLECTION_ID)
        evaluaciones_data = databases.list_documents(DATABASE_ID, EVALUACIONES_COLLECTION_ID)
        pagos_data = databases.list_documents(DATABASE_ID, TRANSACCIONES_PAGOS_COLLECTION_ID)
        
        # Calcular métricas financieras
        ingresos_totales = sum(float(pago.get('amount', 0)) for pago in pagos_data['documents'])
        
        # Métricas de uso
        total_evaluaciones = len(evaluaciones_data['documents'])
        total_estudiantes = sum(int(eval.get('num_estudiantes', 0)) for eval in evaluaciones_data['documents'])
        creditos_totales_distribuidos = sum(int(usuario.get('limite_mensual', 0)) for usuario in usuarios_data['documents'])
        creditos_usados_totales = sum(int(transac.get('creditos', 0)) for transac in transacciones_data['documents'] if transac.get('tipo') == 'evaluacion')
        
        # Conversión demo a pago
        usuarios_demo = len([u for u in usuarios_data['documents'] if u.get('tipo_cuenta') == 'demo'])
        usuarios_pagos = len([u for u in usuarios_data['documents'] if u.get('tipo_cuenta') in ['individual', 'empresa']])
        tasa_conversion = (usuarios_pagos / max(usuarios_demo + usuarios_pagos, 1)) * 100
        
        # Fondos Together.ai
        fondos_together = 0
        for pago in pagos_data['documents']:
            amount = float(pago.get('amount', 0))
            if amount >= 20:
                multiplier = amount // 20
                fondos_together += multiplier * 4
        
        # Usuarios activos (con actividad en últimos 30 días)
        usuarios_activos = 0
        for usuario in usuarios_data['documents']:
            if usuario.get('saldo_actual', 0) < usuario.get('limite_mensual', 0):
                usuarios_activos += 1
        
        # Modelos más utilizados
        modelos_stats = defaultdict(int)
        for evaluacion in evaluaciones_data['documents']:
            try:
                modelos = eval(evaluacion.get('modelos_usados', '[]'))
                for modelo in modelos:
                    modelos_stats[modelo] += 1
            except:
                pass
        
        modelos_top = sorted(modelos_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Evolución temporal (últimos 7 días)
        evolucion_diaria = []
        for i in range(7):
            fecha = datetime.now() - timedelta(days=i)
            fecha_str = fecha.strftime('%Y-%m-%d')
            
            evaluaciones_dia = len([e for e in evaluaciones_data['documents'] 
                                  if e.get('$createdAt', '').startswith(fecha_str)])
            
            creditos_dia = sum(int(t.get('creditos', 0)) for t in transacciones_data['documents'] 
                             if t.get('$createdAt', '').startswith(fecha_str) and t.get('tipo') == 'evaluacion')
            
            evolucion_diaria.append({
                'fecha': fecha_str,
                'evaluaciones': evaluaciones_dia,
                'creditos_usados': creditos_dia
            })
        
        evolucion_diaria.reverse()  # Ordenar cronológicamente
        
        return jsonify({
            'metricas_financieras': {
                'ingresos_totales': round(ingresos_totales, 2),
                'fondos_together': round(fondos_together, 2),
                'roi_creditos': round((ingresos_totales / max(creditos_totales_distribuidos * 0.002, 1)) * 100, 1),  # Asumiendo $0.002 por crédito
                'tasa_conversion': round(tasa_conversion, 1)
            },
            'metricas_uso': {
                'total_evaluaciones': total_evaluaciones,
                'total_estudiantes': total_estudiantes,
                'creditos_distribuidos': creditos_totales_distribuidos,
                'creditos_usados': creditos_usados_totales,
                'porcentaje_uso_creditos': round((creditos_usados_totales / max(creditos_totales_distribuidos, 1)) * 100, 1)
            },
            'metricas_usuarios': {
                'total_usuarios': len(usuarios_data['documents']),
                'usuarios_activos': usuarios_activos,
                'usuarios_demo': usuarios_demo,
                'usuarios_pagos': usuarios_pagos,
                'tasa_retencion': round((usuarios_activos / max(len(usuarios_data['documents']), 1)) * 100, 1)
            },
            'modelos_populares': [{'modelo': modelo, 'usos': usos} for modelo, usos in modelos_top],
            'evolucion_temporal': evolucion_diaria,
            'periodo_analizado': periodo,
            'fecha_generacion': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generando analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/usuarios-detalle', methods=['GET'])
def get_usuarios_detalle():
    """Análisis detallado de usuarios"""
    try:
        usuarios_data = databases.list_documents(DATABASE_ID, USUARIOS_CREDITOS_COLLECTION_ID)
        transacciones_data = databases.list_documents(DATABASE_ID, TRANSACCIONES_COLLECTION_ID)
        
        usuarios_detalle = []
        
        for usuario in usuarios_data['documents']:
            email = usuario.get('email')
            
            # Transacciones del usuario
            transacciones_usuario = [t for t in transacciones_data['documents'] if t.get('email') == email]
            
            creditos_usados = sum(int(t.get('creditos', 0)) for t in transacciones_usuario if t.get('tipo') == 'evaluacion')
            recargas = sum(int(t.get('creditos', 0)) for t in transacciones_usuario if t.get('tipo') == 'recarga')
            
            # Última actividad
            ultima_actividad = None
            if transacciones_usuario:
                fechas = [t.get('$createdAt') for t in transacciones_usuario if t.get('$createdAt')]
                if fechas:
                    ultima_actividad = max(fechas)
            
            usuarios_detalle.append({
                'email': email,
                'empresa': usuario.get('empresa_nombre', ''),
                'tipo_cuenta': usuario.get('tipo_cuenta', 'individual'),
                'saldo_actual': usuario.get('saldo_actual', 0),
                'limite_mensual': usuario.get('limite_mensual', 0),
                'creditos_usados': creditos_usados,
                'recargas_totales': recargas,
                'total_transacciones': len(transacciones_usuario),
                'ultima_actividad': ultima_actividad,
                'fecha_registro': usuario.get('$createdAt'),
                'eficiencia_uso': round((creditos_usados / max(usuario.get('limite_mensual', 1), 1)) * 100, 1)
            })
        
        # Ordenar por uso de créditos
        usuarios_detalle.sort(key=lambda x: x['creditos_usados'], reverse=True)
        
        return jsonify({
            'usuarios': usuarios_detalle,
            'total': len(usuarios_detalle),
            'usuarios_activos': len([u for u in usuarios_detalle if u['creditos_usados'] > 0]),
            'promedio_uso': round(sum(u['creditos_usados'] for u in usuarios_detalle) / max(len(usuarios_detalle), 1), 0)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo detalle usuarios: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/evaluaciones-stats', methods=['GET'])
def get_evaluaciones_stats():
    """Estadísticas detalladas de evaluaciones"""
    try:
        evaluaciones_data = databases.list_documents(DATABASE_ID, EVALUACIONES_COLLECTION_ID)
        
        # Análisis por modelos
        modelos_stats = defaultdict(lambda: {'usos': 0, 'creditos': 0, 'estudiantes': 0})
        
        # Análisis temporal
        evaluaciones_por_mes = defaultdict(int)
        estudiantes_por_mes = defaultdict(int)
        
        for evaluacion in evaluaciones_data['documents']:
            # Modelos utilizados
            try:
                modelos = eval(evaluacion.get('modelos_usados', '[]'))
                creditos = int(evaluacion.get('creditos_totales', 0))
                estudiantes = int(evaluacion.get('num_estudiantes', 0))
                
                for modelo in modelos:
                    modelos_stats[modelo]['usos'] += 1
                    modelos_stats[modelo]['creditos'] += creditos // len(modelos)  # Distribuir créditos
                    modelos_stats[modelo]['estudiantes'] += estudiantes
            except:
                pass
            
            # Análisis temporal
            fecha_creacion = evaluacion.get('$createdAt', '')
            if fecha_creacion:
                try:
                    fecha = datetime.fromisoformat(fecha_creacion.replace('Z', '+00:00'))
                    mes_key = fecha.strftime('%Y-%m')
                    evaluaciones_por_mes[mes_key] += 1
                    estudiantes_por_mes[mes_key] += int(evaluacion.get('num_estudiantes', 0))
                except:
                    pass
        
        # Top modelos
        modelos_ranking = sorted(
            [{'modelo': modelo, **stats} for modelo, stats in modelos_stats.items()],
            key=lambda x: x['usos'],
            reverse=True
        )
        
        # Tendencia temporal
        tendencia_temporal = []
        for mes in sorted(evaluaciones_por_mes.keys()):
            tendencia_temporal.append({
                'mes': mes,
                'evaluaciones': evaluaciones_por_mes[mes],
                'estudiantes': estudiantes_por_mes[mes]
            })
            
        # Agregar consulta de usuarios
        usuarios_data = databases.list_documents(DATABASE_ID, USUARIOS_CREDITOS_COLLECTION_ID)
        
        return jsonify({
            'metricas_financieras': {
                'ingresos_totales': 0,  # calcular desde pagos_data
                'fondos_together': 0,   # calcular desde transacciones_data
                'roi_creditos': 0,
                'tasa_conversion': 0
            },
            'metricas_uso': {
                'total_evaluaciones': len(evaluaciones_data['documents']),
                'total_estudiantes': 0,
                'creditos_distribuidos': 0,
                'creditos_usados': 0,
                'porcentaje_uso_creditos': 0
            },
            'metricas_usuarios': {
                'total_usuarios': len(usuarios_data['documents']),
                'usuarios_activos': 0,
                'usuarios_demo': 0,
                'usuarios_pagos': 0,
                'tasa_retencion': 0
            },
            'evolucion_temporal': tendencia_temporal,
            'modelos_populares': modelos_ranking
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo stats evaluaciones: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/exportar/<tipo>', methods=['GET'])
def exportar_datos(tipo):
    """Exportar datos en formato CSV"""
    try:
        if tipo == 'usuarios':
            usuarios_data = databases.list_documents(DATABASE_ID, USUARIOS_CREDITOS_COLLECTION_ID)
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Headers
            writer.writerow(['Email', 'Empresa', 'Tipo Cuenta', 'Saldo Actual', 'Límite Mensual', 'Fecha Registro'])
            
            # Datos
            for usuario in usuarios_data['documents']:
                writer.writerow([
                    usuario.get('email', ''),
                    usuario.get('empresa_nombre', ''),
                    usuario.get('tipo_cuenta', ''),
                    usuario.get('saldo_actual', 0),
                    usuario.get('limite_mensual', 0),
                    usuario.get('$createdAt', '')
                ])
            
        elif tipo == 'evaluaciones':
            evaluaciones_data = databases.list_documents(DATABASE_ID, EVALUACIONES_COLLECTION_ID)
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            writer.writerow(['Email', 'Fecha', 'Modelos', 'Estudiantes', 'Créditos', 'Tokens', 'Duración'])
            
            for evaluacion in evaluaciones_data['documents']:
                writer.writerow([
                    evaluacion.get('email', ''),
                    evaluacion.get('$createdAt', ''),
                    evaluacion.get('modelos_usados', ''),
                    evaluacion.get('num_estudiantes', 0),
                    evaluacion.get('creditos_totales', 0),
                    evaluacion.get('tokens_totales', 0),
                    evaluacion.get('duracion_segundos', 0)
                ])
        
        elif tipo == 'transacciones':
            transacciones_data = databases.list_documents(DATABASE_ID, TRANSACCIONES_COLLECTION_ID)
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            writer.writerow(['Email', 'Fecha', 'Tipo', 'Créditos', 'Tokens', 'Descripción'])
            
            for transaccion in transacciones_data['documents']:
                writer.writerow([
                    transaccion.get('email', ''),
                    transaccion.get('$createdAt', ''),
                    transaccion.get('tipo', ''),
                    transaccion.get('creditos', 0),
                    transaccion.get('tokens_usados', 0),
                    transaccion.get('descripcion', '')
                ])
        
        else:
            return jsonify({'error': 'Tipo de exportación no válido'}), 400
        
        # Preparar respuesta
        output.seek(0)
        
        return {
            'data': output.getvalue(),
            'filename': f'{tipo}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            'content_type': 'text/csv'
        }
        
    except Exception as e:
        logger.error(f"Error exportando {tipo}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/comparativa', methods=['GET'])
def get_comparativa_periodos():
    """Comparativa entre períodos"""
    try:
        periodo_actual = int(request.args.get('periodo_actual', 30))
        periodo_anterior = int(request.args.get('periodo_anterior', 30))
        
        fecha_fin_actual = datetime.now()
        fecha_inicio_actual = fecha_fin_actual - timedelta(days=periodo_actual)
        fecha_fin_anterior = fecha_inicio_actual
        fecha_inicio_anterior = fecha_fin_anterior - timedelta(days=periodo_anterior)
        
        # Obtener datos
        evaluaciones_data = databases.list_documents(DATABASE_ID, EVALUACIONES_COLLECTION_ID)
        transacciones_data = databases.list_documents(DATABASE_ID, TRANSACCIONES_COLLECTION_ID)
        
        def filtrar_por_periodo(datos, inicio, fin):
            return [d for d in datos if inicio <= datetime.fromisoformat(d.get('$createdAt', '').replace('Z', '+00:00')) < fin]
        
        # Período actual
        eval_actual = filtrar_por_periodo(evaluaciones_data['documents'], fecha_inicio_actual, fecha_fin_actual)
        trans_actual = filtrar_por_periodo(transacciones_data['documents'], fecha_inicio_actual, fecha_fin_actual)
        
        # Período anterior
        eval_anterior = filtrar_por_periodo(evaluaciones_data['documents'], fecha_inicio_anterior, fecha_fin_anterior)
        trans_anterior = filtrar_por_periodo(transacciones_data['documents'], fecha_inicio_anterior, fecha_fin_anterior)
        
        # Calcular métricas
        def calcular_metricas(evaluaciones, transacciones):
            return {
                'evaluaciones': len(evaluaciones),
                'estudiantes': sum(int(e.get('num_estudiantes', 0)) for e in evaluaciones),
                'creditos_usados': sum(int(t.get('creditos', 0)) for t in transacciones if t.get('tipo') == 'evaluacion'),
                'usuarios_activos': len(set(e.get('email') for e in evaluaciones))
            }
        
        metricas_actual = calcular_metricas(eval_actual, trans_actual)
        metricas_anterior = calcular_metricas(eval_anterior, trans_anterior)
        
        # Calcular variaciones
        def calcular_variacion(actual, anterior):
            if anterior == 0:
                return 100 if actual > 0 else 0
            return round(((actual - anterior) / anterior) * 100, 1)
        
        variaciones = {}
        for metrica in metricas_actual:
            variaciones[metrica] = calcular_variacion(
                metricas_actual[metrica], 
                metricas_anterior[metrica]
            )
        
        return jsonify({
            'periodo_actual': {
                'inicio': fecha_inicio_actual.isoformat(),
                'fin': fecha_fin_actual.isoformat(),
                'metricas': metricas_actual
            },
            'periodo_anterior': {
                'inicio': fecha_inicio_anterior.isoformat(),
                'fin': fecha_fin_anterior.isoformat(),
                'metricas': metricas_anterior
            },
            'variaciones': variaciones,
            'tendencia_general': 'positiva' if sum(variaciones.values()) > 0 else 'negativa'
        })
        
    except Exception as e:
        logger.error(f"Error en comparativa: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud"""
    return jsonify({
        'status': 'healthy',
        'service': 'analytics-reportes',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("Servidor de Analytics y Reportes iniciado")
    app.run(debug=False, host='0.0.0.0', port=5006)