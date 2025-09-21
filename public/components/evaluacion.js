import { ref, reactive, inject } from 'vue';

export const EvaluacionComponent = {
    template: `
        <div class="section">
            <h1>Evaluación de Exámenes</h1>
            
            <div class="card">
                <h2>Filtrar Exámenes</h2>
                
                <div class="form-row" style="display: flex; gap: 20px;">
                    <div class="form-group" style="flex: 1;">
                        <label for="filtro-examen">ID Examen</label>
                        <input type="text" id="filtro-examen" v-model="filtros.idExamen">
                    </div>
                    
                    <div class="form-group" style="flex: 1;">
                        <label for="filtro-alumno">ID Alumno</label>
                        <input type="text" id="filtro-alumno" v-model="filtros.idAlumno">
                    </div>
                    
                    <div class="form-group" style="flex: 1;">
                        <label for="filtro-estado">Estado</label>
                        <select id="filtro-estado" v-model="filtros.estado">
                            <option value="">Todos</option>
                            <option value="pendiente">Pendiente</option>
                            <option value="evaluado">Evaluado</option>
                        </select>
                    </div>
                </div>
                
                <div class="btn-group">
                    <button class="btn" @click="buscarExamenes">Buscar</button>
                    <button class="btn" @click="limpiarFiltros">Limpiar Filtros</button>
                </div>
            </div>
            
            <div class="card" v-if="examenesPendientes.length > 0">
                <h2>Exámenes Pendientes de Evaluación</h2>
                
                <table>
                    <thead>
                        <tr>
                            <th>ID Examen</th>
                            <th>ID Alumno</th>
                            <th>Fecha de Carga</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(examen, index) in examenesPendientes" :key="index">
                            <td>{{ examen.idExamen }}</td>
                            <td>{{ examen.idAlumno }}</td>
                            <td>{{ formatearFecha(examen.fechaCarga) }}</td>
                            <td>
                                <button class="btn btn-success" @click="evaluarExamen(examen)">Evaluar</button>
                                <button class="btn" @click="verExamen(examen)">Ver PDF</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="card" v-if="examenesEvaluados.length > 0">
                <h2>Exámenes Evaluados</h2>
                
                <table>
                    <thead>
                        <tr>
                            <th>ID Examen</th>
                            <th>ID Alumno</th>
                            <th>Calificación</th>
                            <th>Fecha de Evaluación</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(examen, index) in examenesEvaluados" :key="index">
                            <td>{{ examen.idExamen }}</td>
                            <td>{{ examen.idAlumno }}</td>
                            <td>{{ examen.calificacion }}/{{ examen.puntajeTotal }}</td>
                            <td>{{ formatearFecha(examen.fechaEvaluacion) }}</td>
                            <td>
                                <button class="btn" @click="verResultadoDetallado(examen)">Ver Resultado</button>
                                <button class="btn" @click="enviarResultado(examen)">Enviar Resultado</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- Modal de Evaluación -->
            <div v-if="modalEvaluacion" class="modal-overlay">
                <div class="modal-container">
                    <div class="modal-header">
                        <h2>Evaluando Examen {{ examenActual.idExamen }}</h2>
                        <button class="modal-close" @click="cerrarModal">×</button>
                    </div>
                    
                    <div class="modal-body">
                        <div v-if="evaluando">
                            <p>Aplicando métodos de evaluación con IA...</p>
                            <div class="progress-bar">
                                <div class="progress" :style="{ width: progreso + '%' }"></div>
                            </div>
                            <p>{{ mensajeEvaluacion }}</p>
                        </div>
                        
                        <div v-else-if="resultadoEvaluacion">
                            <h3>Resultados de la Evaluación</h3>
                            
                            <div class="resultado-summary">
                                <div class="resultado-item">
                                    <span>Calificación Final:</span>
                                    <strong>{{ resultadoEvaluacion.calificacionFinal }}/{{ resultadoEvaluacion.puntajeTotal }}</strong>
                                </div>
                                <div class="resultado-item">
                                    <span>Porcentaje:</span>
                                    <strong>{{ (resultadoEvaluacion.calificacionFinal / resultadoEvaluacion.puntajeTotal * 100).toFixed(2) }}%</strong>
                                </div>
                            </div>
                            
                            <h4>Detalle por Pregunta</h4>
                            
                            <div v-for="(resultado, index) in resultadoEvaluacion.detalle" :key="index" class="resultado-pregunta">
                                <div class="pregunta-header">
                                    <h5>Pregunta {{ resultado.numeroPregunta }}</h5>
                                    <div class="puntaje">
                                        <span>{{ resultado.puntajeObtenido }}/{{ resultado.puntajeTotal }}</span>
                                    </div>
                                </div>
                                
                                <div class="pregunta-contenido">
                                    <p><strong>Pregunta:</strong> {{ resultado.textoPregunta }}</p>
                                    <p v-if="resultado.tipo === 'marcar'">
                                        <strong>Respuesta correcta:</strong> {{ resultado.respuestaCorrecta }}
                                    </p>
                                    <p v-if="resultado.tipo === 'marcar'">
                                        <strong>Respuesta del alumno:</strong> {{ resultado.respuestaAlumno }}
                                    </p>
                                    <div v-if="resultado.tipo !== 'marcar'">
                                        <p><strong>Respuesta del alumno:</strong></p>
                                        <div class="respuesta-texto">{{ resultado.respuestaAlumno }}</div>
                                    </div>
                                    <div v-if="resultado.comentario">
                                        <p><strong>Comentario:</strong></p>
                                        <div class="comentario">{{ resultado.comentario }}</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="btn-group">
                                <button class="btn btn-success" @click="guardarEvaluacion">Guardar Evaluación</button>
                                <button class="btn" @click="cerrarModal">Cancelar</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Modal de Resultado Detallado -->
            <div v-if="modalResultado" class="modal-overlay">
                <div class="modal-container">
                    <div class="modal-header">
                        <h2>Resultado Examen {{ examenResultado.idExamen }}</h2>
                        <button class="modal-close" @click="cerrarModalResultado">×</button>
                    </div>
                    
                    <div class="modal-body">
                        <div class="resultado-summary">
                            <div class="resultado-item">
                                <span>ID Alumno:</span>
                                <strong>{{ examenResultado.idAlumno }}</strong>
                            </div>
                            <div class="resultado-item">
                                <span>Calificación:</span>
                                <strong>{{ examenResultado.calificacion }}/{{ examenResultado.puntajeTotal }}</strong>
                            </div>
                            <div class="resultado-item">
                                <span>Porcentaje:</span>
                                <strong>{{ (examenResultado.calificacion / examenResultado.puntajeTotal * 100).toFixed(2) }}%</strong>
                            </div>
                        </div>
                        
                        <h4>Detalle por Pregunta</h4>
                        
                        <div v-for="(resultado, index) in examenResultado.detalle" :key="index" class="resultado-pregunta">
                            <div class="pregunta-header">
                                <h5>Pregunta {{ resultado.numeroPregunta }}</h5>
                                <div class="puntaje">
                                    <span>{{ resultado.puntajeObtenido }}/{{ resultado.puntajeTotal }}</span>
                                </div>
                            </div>
                            
                            <div class="pregunta-contenido">
                                <p><strong>Pregunta:</strong> {{ resultado.textoPregunta }}</p>
                                <p v-if="resultado.tipo === 'marcar'">
                                    <strong>Respuesta correcta:</strong> {{ resultado.respuestaCorrecta }}
                                </p>
                                <p v-if="resultado.tipo === 'marcar'">
                                    <strong>Respuesta del alumno:</strong> {{ resultado.respuestaAlumno }}
                                </p>
                                <div v-if="resultado.tipo !== 'marcar'">
                                    <p><strong>Respuesta del alumno:</strong></p>
                                    <div class="respuesta-texto">{{ resultado.respuestaAlumno }}</div>
                                </div>
                                <div v-if="resultado.comentario">
                                    <p><strong>Comentario:</strong></p>
                                    <div class="comentario">{{ resultado.comentario }}</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="btn-group">
                            <button class="btn" @click="cerrarModalResultado">Cerrar</button>
                            <button class="btn btn-success" @click="enviarResultadoDesdeModal">Enviar Resultado</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    setup() {
        const apiService = inject('apiService');
        
        const filtros = reactive({
            idExamen: '',
            idAlumno: '',
            estado: ''
        });
        
        const examenesPendientes = ref([]);
        const examenesEvaluados = ref([]);
        
        const modalEvaluacion = ref(false);
        const modalResultado = ref(false);
        const evaluando = ref(false);
        const progreso = ref(0);
        const mensajeEvaluacion = ref('');
        
        const examenActual = reactive({});
        const examenResultado = reactive({});
        const resultadoEvaluacion = ref(null);
        
        function buscarExamenes() {
            // Llamada a la API para buscar exámenes según filtros
            apiService.buscarExamenes(filtros)
                .then(response => {
                    // Separar los exámenes en pendientes y evaluados
                    const todos = response.data || [];
                    examenesPendientes.value = todos.filter(e => e.estado === 'pendiente');
                    examenesEvaluados.value = todos.filter(e => e.estado === 'evaluado');
                })
                .catch(error => {
                    console.error('Error al buscar exámenes:', error);
                });
        }
        
        function limpiarFiltros() {
            filtros.idExamen = '';
            filtros.idAlumno = '';
            filtros.estado = '';
            buscarExamenes();
        }
        
        function verExamen(examen) {
            apiService.obtenerPDFExamen(examen.idExamen, examen.idAlumno)
                .then(response => {
                    // Crear URL de objeto y abrir en nueva ventana
                    const blob = new Blob([response.data], { type: 'application/pdf' });
                    const url = URL.createObjectURL(blob);
                    window.open(url, '_blank');
                })
                .catch(error => {
                    console.error('Error al obtener el PDF:', error);
                    alert('Error al obtener el PDF del examen');
                });
        }
        
        function evaluarExamen(examen) {
            Object.assign(examenActual, examen);
            modalEvaluacion.value = true;
            evaluando.value = true;
            progreso.value = 0;
            mensajeEvaluacion.value = 'Iniciando evaluación...';
            
            // Simular progreso de evaluación (en una implementación real, esto sería asíncrono)
            const intervalo = setInterval(() => {
                progreso.value += 5;
                
                if (progreso.value < 30) {
                    mensajeEvaluacion.value = 'Aplicando método de evaluación 1...';
                } else if (progreso.value < 60) {
                    mensajeEvaluacion.value = 'Aplicando método de evaluación 2...';
                } else if (progreso.value < 90) {
                    mensajeEvaluacion.value = 'Aplicando método de evaluación 3...';
                } else {
                    mensajeEvaluacion.value = 'Consolidando resultados...';
                }
                
                if (progreso.value >= 100) {
                    clearInterval(intervalo);
                    finalizarEvaluacion();
                }
            }, 200);
            
            // En una implementación real, aquí iría la llamada a la API
            apiService.evaluarExamen(examen.idExamen, examen.idAlumno)
                .then(response => {
                    // Esto se procesaría cuando la API responda
                })
                .catch(error => {
                    console.error('Error al evaluar examen:', error);
                    clearInterval(intervalo);
                    mensajeEvaluacion.value = 'Error al evaluar examen: ' + error.message;
                });
        }
        
        function finalizarEvaluacion() {
            // Datos de ejemplo de resultado
            resultadoEvaluacion.value = {
                calificacionFinal: 16.5,
                puntajeTotal: 20,
                detalle: [
                    {
                        numeroPregunta: 1,
                        tipo: 'marcar',
                        textoPregunta: '¿Cuál es el lenguaje de programación más utilizado para desarrollo web?',
                        respuestaCorrecta: 'JavaScript',
                        respuestaAlumno: 'JavaScript',
                        puntajeTotal: 1,
                        puntajeObtenido: 1,
                        comentario: ''
                    },
                    {
                        numeroPregunta: 2,
                        tipo: 'marcar',
                        textoPregunta: '¿Qué significa HTML?',
                        respuestaCorrecta: 'Hyper Text Markup Language',
                        respuestaAlumno: 'Hyper Text Markup Language',
                        puntajeTotal: 1,
                        puntajeObtenido: 1,
                        comentario: ''
                    },
                    {
                        numeroPregunta: 3,
                        tipo: 'libre',
                        textoPregunta: 'Explique el concepto de programación orientada a objetos.',
                        respuestaAlumno: 'La programación orientada a objetos es un paradigma de programación que utiliza objetos, que son instancias de clases, para estructurar el código. Se basa en conceptos como encapsulamiento, herencia y polimorfismo.',
                        puntajeTotal: 2,
                        puntajeObtenido: 1.5,
                        comentario: 'Respuesta correcta pero falta mencionar la abstracción como uno de los conceptos fundamentales.'
                    },
                    {
                        numeroPregunta: 4,
                        tipo: 'caso',
                        textoPregunta: 'Diseñe una solución utilizando programación orientada a objetos para un sistema de carrito de compras.',
                        respuestaAlumno: `Clases:
1. Producto: Con atributos como id, nombre, precio, descripción.
2. CarritoCompra: Contiene métodos como agregarProducto(), eliminarProducto(), calcularTotal().
3. Usuario: Con datos del cliente.

La clase CarritoCompra tendría una colección de objetos Producto y métodos para manipularlos.`,
                        puntajeTotal: 3,
                        puntajeObtenido: 2,
                        comentario: 'Buena estructura general pero falta implementar detalles sobre la interacción entre clases y manejos de cantidades de productos.'
                    }
                ]
            };
            
            evaluando.value = false;
        }
        
        function guardarEvaluacion() {
            if (!resultadoEvaluacion.value) return;
            
            // Crear objeto con los datos de la evaluación
            const evaluacionFinal = {
                idExamen: examenActual.idExamen,
                idAlumno: examenActual.idAlumno,
                calificacion: resultadoEvaluacion.value.calificacionFinal,
                puntajeTotal: resultadoEvaluacion.value.puntajeTotal,
                fechaEvaluacion: new Date().toISOString(),
                detalle: resultadoEvaluacion.value.detalle,
                estado: 'evaluado'
            };
            
            // Llamada a la API para guardar la evaluación
            apiService.guardarEvaluacion(evaluacionFinal)
                .then(response => {
                    // Mover el examen de pendientes a evaluados
                    const index = examenesPendientes.value.findIndex(e => 
                        e.idExamen === examenActual.idExamen && e.idAlumno === examenActual.idAlumno
                    );
                    
                    if (index !== -1) {
                        examenesPendientes.value.splice(index, 1);
                        examenesEvaluados.value.push(evaluacionFinal);
                    }
                    
                    cerrarModal();
                    alert('Evaluación guardada con éxito');
                })
                .catch(error => {
                    console.error('Error al guardar evaluación:', error);
                    alert('Error al guardar la evaluación: ' + error.message);
                });
        }
        
        function verResultadoDetallado(examen) {
            // Cargar los detalles del examen evaluado
            apiService.obtenerEvaluacion(examen.idExamen, examen.idAlumno)
                .then(response => {
                    Object.assign(examenResultado, response.data || examen);
                    modalResultado.value = true;
                })
                .catch(error => {
                    console.error('Error al obtener detalles de evaluación:', error);
                    alert('Error al obtener detalles de la evaluación');
                });
                
            // Para demo, usamos datos de ejemplo
            Object.assign(examenResultado, {
                idExamen: examen.idExamen,
                idAlumno: examen.idAlumno,
                calificacion: examen.calificacion || 16.5,
                puntajeTotal: examen.puntajeTotal || 20,
                fechaEvaluacion: examen.fechaEvaluacion,
                detalle: [
                    {
                        numeroPregunta: 1,
                        tipo: 'marcar',
                        textoPregunta: '¿Cuál es el lenguaje de programación más utilizado para desarrollo web?',
                        respuestaCorrecta: 'JavaScript',
                        respuestaAlumno: 'JavaScript',
                        puntajeTotal: 1,
                        puntajeObtenido: 1,
                        comentario: ''
                    },
                    {
                        numeroPregunta: 2,
                        tipo: 'marcar',
                        textoPregunta: '¿Qué significa HTML?',
                        respuestaCorrecta: 'Hyper Text Markup Language',
                        respuestaAlumno: 'Hyper Text Markup Language',
                        puntajeTotal: 1,
                        puntajeObtenido: 1,
                        comentario: ''
                    },
                    {
                        numeroPregunta: 3,
                        tipo: 'libre',
                        textoPregunta: 'Explique el concepto de programación orientada a objetos.',
                        respuestaAlumno: 'La programación orientada a objetos es un paradigma de programación que utiliza objetos, que son instancias de clases, para estructurar el código. Se basa en conceptos como encapsulamiento, herencia y polimorfismo.',
                        puntajeTotal: 2,
                        puntajeObtenido: 1.5,
                        comentario: 'Respuesta correcta pero falta mencionar la abstracción como uno de los conceptos fundamentales.'
                    },
                    {
                        numeroPregunta: 4,
                        tipo: 'caso',
                        textoPregunta: 'Diseñe una solución utilizando programación orientada a objetos para un sistema de carrito de compras.',
                        respuestaAlumno: `Clases:
1. Producto: Con atributos como id, nombre, precio, descripción.
2. CarritoCompra: Contiene métodos como agregarProducto(), eliminarProducto(), calcularTotal().
3. Usuario: Con datos del cliente.

La clase CarritoCompra tendría una colección de objetos Producto y métodos para manipularlos.`,
                        puntajeTotal: 3,
                        puntajeObtenido: 2,
                        comentario: 'Buena estructura general pero falta implementar detalles sobre la interacción entre clases y manejos de cantidades de productos.'
                    }
                ]
            });
            
            modalResultado.value = true;
        }
        
        function enviarResultado(examen) {
            // Enviar el resultado al alumno
            apiService.enviarResultadoAlumno(examen.idExamen, examen.idAlumno)
                .then(response => {
                    alert('Resultado enviado con éxito al alumno');
                })
                .catch(error => {
                    console.error('Error al enviar resultado:', error);
                    alert('Error al enviar el resultado al alumno');
                });
        }
        
        function enviarResultadoDesdeModal() {
            enviarResultado(examenResultado);
            cerrarModalResultado();
        }
        
        function cerrarModal() {
            modalEvaluacion.value = false;
            evaluando.value = false;
            resultadoEvaluacion.value = null;
            Object.keys(examenActual).forEach(key => delete examenActual[key]);
        }
        
        function cerrarModalResultado() {
            modalResultado.value = false;
            Object.keys(examenResultado).forEach(key => delete examenResultado[key]);
        }
        
        function formatearFecha(fecha) {
            return new Date(fecha).toLocaleString();
        }
        
        // Cargar exámenes de ejemplo para demostración
        const ejemplosPendientes = [
            {
                idExamen: 'EXAM-123456',
                idAlumno: 'ALU-001',
                fechaCarga: '2023-08-15T10:30:00',
                estado: 'pendiente'
            },
            {
                idExamen: 'EXAM-654321',
                idAlumno: 'ALU-002',
                fechaCarga: '2023-08-14T14:45:00',
                estado: 'pendiente'
            }
        ];
        
        const ejemplosEvaluados = [
            {
                idExamen: 'EXAM-111222',
                idAlumno: 'ALU-003',
                calificacion: 18,
                puntajeTotal: 20,
                fechaEvaluacion: '2023-08-13T09:15:00',
                estado: 'evaluado'
            },
            {
                idExamen: 'EXAM-333444',
                idAlumno: 'ALU-004',
                calificacion: 15,
                puntajeTotal: 20,
                fechaEvaluacion: '2023-08-12T11:00:00',
                estado: 'evaluado'
            }
        ];
        
        examenesPendientes.value = ejemplosPendientes;
        examenesEvaluados.value = ejemplosEvaluados;
        
        return {
            filtros,
            examenesPendientes,
            examenesEvaluados,
            modalEvaluacion,
            modalResultado,
            evaluando,
            progreso,
            mensajeEvaluacion,
            examenActual,
            examenResultado,
            resultadoEvaluacion,
            buscarExamenes,
            limpiarFiltros,
            verExamen,
            evaluarExamen,
            guardarEvaluacion,
            verResultadoDetallado,
            enviarResultado,
            enviarResultadoDesdeModal,
            cerrarModal,
            cerrarModalResultado,
            formatearFecha
        };
    }
};

