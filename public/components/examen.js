import { ref, reactive, onMounted, inject } from 'vue';

export const ExamenComponent = {
    template: `
        <div class="section">
            <h1>🎓 Dashboard del Estudiante</h1>
            
            <!-- Loading State -->
            <div v-if="isLoading" class="card">
                <div class="loading-state">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>Cargando información...</p>
                </div>
            </div>
            
            <!-- Error de Autenticación -->
            <div v-else-if="!alumno.id_alumno" class="card error-card">
                <div class="error-content">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h2>Acceso No Autorizado</h2>
                    <p>No hay alumno autenticado. Por favor, inicia sesión primero.</p>
                    <button class="btn btn-primary" @click="irALogin">
                        <i class="fas fa-sign-in-alt"></i> Ir a Login
                    </button>
                </div>
            </div>
            
            <!-- Dashboard Principal -->
            <div v-else class="dashboard-container">
                
                <!-- Datos del Alumno -->
                <div class="card alumno-card">
                    <h2><i class="fas fa-user"></i> Datos del Alumno</h2>
                    <div class="info-grid">
                        <div class="info-item">
                            <label>Nombre:</label>
                            <span>{{ alumno.nombre_alumno }}</span>
                        </div>
                        <div class="info-item">
                            <label>ID Alumno:</label>
                            <span>{{ alumno.id_alumno }}</span>
                        </div>
                        <div class="info-item">
                            <label>Email:</label>
                            <span>{{ alumno.email }}</span>
                        </div>
                        <div class="info-item">
                            <label>Curso:</label>
                            <span>{{ alumno.curso }}</span>
                        </div>
                        <div class="info-item">
                            <label>Profesor:</label>
                            <span>{{ alumno.nombre_profesor }}</span>
                        </div>
                        <div class="info-item">
                            <label>Institución:</label>
                            <span>{{ alumno.institucion }}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Datos del Examen -->
                <div v-if="examenDisponible" class="card examen-card">
                    <h2><i class="fas fa-clipboard-list"></i> Examen Disponible</h2>
                    <div class="info-grid">
                        <div class="info-item">
                            <label>Nombre del Examen:</label>
                            <span>{{ examenDisponible.nombre_examen }}</span>
                        </div>
                        <div class="info-item">
                            <label>ID del Examen:</label>
                            <span>{{ examenDisponible.id_examen }}</span>
                        </div>
                        <div class="info-item">
                            <label>Curso:</label>
                            <span>{{ examenDisponible.curso }}</span>
                        </div>
                        <div class="info-item">
                            <label>Fecha Límite:</label>
                            <span>{{ formatearFecha(examenDisponible.fecha_limite) }}</span>
                        </div>
                        <div class="info-item" :class="{ 'urgente': examenDisponible.tiempo_restante < 60 }">
                            <label>Tiempo Restante:</label>
                            <span>{{ formatearTiempoRestante(examenDisponible.tiempo_restante) }}</span>
                        </div>
                        <div class="info-item">
                            <label>Institución:</label>
                            <span>{{ examenDisponible.institucion }}</span>
                        </div>
                    </div>
                    
                    <!-- Botón para Iniciar Examen -->
                    <div class="accion-examen">
                        <button 
                            class="btn btn-success btn-large" 
                            @click="iniciarExamen"
                            :disabled="examenDisponible.tiempo_restante <= 0"
                        >
                            <i class="fas fa-play"></i> 
                            {{ examenDisponible.tiempo_restante <= 0 ? 'Examen Expirado' : 'Iniciar Examen' }}
                        </button>
                        
                        <p class="examen-info">
                            <i class="fas fa-info-circle"></i>
                            Al hacer clic se abrirá el examen en una nueva ventana
                        </p>
                    </div>
                </div>
                
                <!-- No hay Examen Disponible -->
                <div v-else-if="!buscarError" class="card no-examen-card">
                    <div class="no-examen-content">
                        <i class="fas fa-calendar-times"></i>
                        <h2>No hay examen disponible</h2>
                        <p>Tu profesor aún no ha publicado un examen para tu curso.</p>
                        <button class="btn btn-secondary" @click="buscarExamen">
                            <i class="fas fa-sync"></i> Verificar Nuevamente
                        </button>
                    </div>
                </div>
                
                <!-- Error al Buscar Examen -->
                <div v-else class="card error-card">
                    <div class="error-content">
                        <i class="fas fa-exclamation-circle"></i>
                        <h2>Error al cargar examen</h2>
                        <p>{{ buscarError }}</p>
                        <button class="btn btn-secondary" @click="buscarExamen">
                            <i class="fas fa-retry"></i> Intentar Nuevamente
                        </button>
                    </div>
                </div>
                
                <!-- Acciones Adicionales -->
                <div class="card acciones-card">
                    <h2><i class="fas fa-cogs"></i> Acciones</h2>
                    <div class="btn-group">
                        <button class="btn btn-info" @click="buscarExamen">
                            <i class="fas fa-sync"></i> Actualizar Información
                        </button>
                        <button class="btn btn-secondary" @click="cerrarSesion">
                            <i class="fas fa-sign-out-alt"></i> Cerrar Sesión
                        </button>
                    </div>
                </div>
                
                <!-- Mensajes del Sistema -->
                <div v-if="message" :class="'alert alert-' + messageType" class="system-message">
                    <i :class="getMessageIcon()"></i>
                    {{ message }}
                </div>
            </div>
        </div>
    `,
    
    setup() {
        // Estado reactivo
        const isLoading = ref(true);
        const alumno = reactive({});
        const examenDisponible = ref(null);
        const buscarError = ref('');
        const message = ref('');
        const messageType = ref('info');
        
        // Función para cargar datos del alumno desde localStorage
        function cargarDatosAlumno() {
            try {
                const alumnoData = localStorage.getItem('currentAlumno');
                if (alumnoData) {
                    const datos = JSON.parse(alumnoData);
                    Object.assign(alumno, datos);
                    console.log('Datos del alumno cargados:', alumno);
                    return true;
                } else {
                    console.warn('No se encontraron datos del alumno en localStorage');
                    return false;
                }
            } catch (error) {
                console.error('Error al cargar datos del alumno:', error);
                return false;
            }
        }
        
        // Función para buscar examen disponible
        async function buscarExamen() {
            if (!alumno.curso || !alumno.nombre_profesor || !alumno.institucion) {
                buscarError.value = 'Faltan datos del alumno para buscar el examen';
                return;
            }
            
            isLoading.value = true;
            buscarError.value = '';
            examenDisponible.value = null;
            
            try {
                const params = new URLSearchParams({
                    curso: alumno.curso,
                    nombre_profesor: alumno.nombre_profesor,
                    institucion: alumno.institucion,
                    email: alumno.email || ''
                });
                
                const response = await fetch(`/api/examenes-disponibles?${params}`);
                const data = await response.json();
                
                if (response.ok && data.success) {
                    examenDisponible.value = data.examen;
                    console.log('Examen encontrado:', data.examen);

                // Detectar si es Test CHAEA
                if (data.examen.nombre_examen === 'Test CHAEA' || data.examen.tipo === 'chaea') {
                    // Cargar Test CHAEA en lugar de examen normal
                    cargarTestCHAEA();
                    return;
                }
    
                } else {
                    // Error controlado del servidor
                    buscarError.value = data.message || data.error || 'No se encontró examen disponible';
                    
                    if (response.status === 404) {
                        // No hay examen - no es realmente un error
                        buscarError.value = '';
                    } else if (response.status === 410) {
                        // Examen expirado
                        buscarError.value = 'El examen ha expirado';
                    }
                }
            } catch (error) {
                console.error('Error al buscar examen:', error);
                buscarError.value = 'Error de conexión al buscar el examen';
            } finally {
                isLoading.value = false;
            }
        }
        
        // Función para iniciar el examen
        function iniciarExamen() {
            if (!examenDisponible.value || !examenDisponible.value.url_examen) {
                mostrarMensaje('Error: No se pudo obtener la URL del examen', 'error');
                return;
            }
            
            if (examenDisponible.value.tiempo_restante <= 0) {
                mostrarMensaje('El examen ha expirado', 'warning');
                return;
            }
            
            const confirmar = confirm(
                `¿Estás seguro de que quieres iniciar el examen "${examenDisponible.value.nombre_examen}"?\n\n` +
                `Tiempo restante: ${formatearTiempoRestante(examenDisponible.value.tiempo_restante)}`
            );
            
            if (confirmar) {
                // Abrir examen en nueva ventana
                const ventanaExamen = window.open(
                    examenDisponible.value.url_examen, 
                    '_blank',
                    'width=1200,height=800,scrollbars=yes,resizable=yes'
                );
                
                if (ventanaExamen) {
                    mostrarMensaje('Examen abierto en nueva ventana', 'success');
                } else {
                    mostrarMensaje('Error: No se pudo abrir el examen. Verifica que no estén bloqueadas las ventanas emergentes.', 'error');
                }
            }
        }
        
        // Función para cerrar sesión
        function cerrarSesion() {
            if (confirm('¿Seguro que quieres cerrar sesión?')) {
                localStorage.removeItem('currentAlumno');
                // Navegar de vuelta al login
                window.location.href = 'alumno.html';
            }
        }
        
        // Función para ir al login
        function irALogin() {
            window.location.href = 'alumno.html';
        }
        
        // Funciones auxiliares para formateo
        function formatearFecha(fechaISO) {
            try {
                const fecha = new Date(fechaISO);
                return fecha.toLocaleString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch (error) {
                return fechaISO;
            }
        }
        
        function formatearTiempoRestante(minutos) {
            if (minutos <= 0) return 'Expirado';
            
            if (minutos < 60) {
                return `${minutos} minuto${minutos !== 1 ? 's' : ''}`;
            } else {
                const horas = Math.floor(minutos / 60);
                const mins = minutos % 60;
                return `${horas}h ${mins}m`;
            }
        }
        
        function mostrarMensaje(texto, tipo = 'info') {
            message.value = texto;
            messageType.value = tipo;
            
            // Auto-limpiar mensaje después de 5 segundos
            setTimeout(() => {
                message.value = '';
            }, 5000);
        }
        
        function getMessageIcon() {
            switch (messageType.value) {
                case 'success': return 'fas fa-check-circle';
                case 'error': return 'fas fa-exclamation-circle';
                case 'warning': return 'fas fa-exclamation-triangle';
                default: return 'fas fa-info-circle';
            }
        }
        
        // Ciclo de vida del componente
        onMounted(async () => {
            console.log('Dashboard del estudiante montado');
            
            // Cargar datos del alumno
            const datosAlumnoCargados = cargarDatosAlumno();
            
            if (datosAlumnoCargados) {
                // Si hay datos del alumno, buscar examen
                await buscarExamen();
            } else {
                // Si no hay datos del alumno, terminar carga
                isLoading.value = false;
            }
        });

        function cargarTestCHAEA() {
            // Configurar datos para CHAEA usando currentAlumno
            const userData = {
                userId: alumno.id_alumno,
                courseId: alumno.email,
                userName: alumno.nombre_alumno
            };
            
            // Mostrar interfaz de Test CHAEA
            // (aquí iría la lógica del cuestionario CHAEA)
        }
        
        // Retornar datos y funciones para el template
        return {
            isLoading,
            alumno,
            examenDisponible,
            buscarError,
            message,
            messageType,
            buscarExamen,
            iniciarExamen,
            cerrarSesion,
            irALogin,
            formatearFecha,
            formatearTiempoRestante,
            getMessageIcon
        };
    }
};