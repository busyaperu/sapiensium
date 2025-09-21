// Componente Vue: ModalRecomendacionesModelos.vue
// Ubicación sugerida: src/components/ModalRecomendacionesModelos.vue

<template>
  <div v-if="visible" class="modal-overlay" @click="cerrarModal">
    <div class="modal-container" @click.stop>
      <!-- Header del modal -->
      <div class="modal-header">
        <div class="header-content">
          <div class="tipo-pregunta-info">
            <i :class="iconoTipoPregunta" class="tipo-icon"></i>
            <div>
              <h3>Modelos Recomendados</h3>
              <p class="tipo-subtitle">{{ tituloTipoPregunta }}</p>
            </div>
          </div>
          <button @click="cerrarModal" class="btn-cerrar">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="cargando" class="loading-container">
        <div class="spinner"></div>
        <p>Cargando recomendaciones...</p>
      </div>

      <!-- Error state -->
      <div v-else-if="error" class="error-container">
        <i class="fas fa-exclamation-triangle"></i>
        <p>{{ error }}</p>
        <button @click="cargarRecomendaciones" class="btn-reintentar">
          Reintentar
        </button>
      </div>

      <!-- Content -->
      <div v-else class="modal-content">
        <!-- Modelos Recomendados -->
        <div class="seccion-modelos">
          <h4 class="seccion-titulo recomendado">
            <i class="fas fa-star"></i>
            Altamente Recomendados
          </h4>
          <div class="modelos-grid">
            <div 
              v-for="modelo in recomendaciones.recomendados" 
              :key="modelo.modelo"
              class="modelo-card recomendado"
              :class="{ 'no-disponible': !modelo.disponible }"
              @click="seleccionarModelo(modelo.modelo)"
            >
              <div class="modelo-header">
                <h5>{{ modelo.nombre_display }}</h5>
                <div class="puntuacion">
                  <i 
                    v-for="n in 5" 
                    :key="n"
                    class="fas fa-star"
                    :class="{ 'estrella-activa': n <= modelo.puntuacion }"
                  ></i>
                </div>
              </div>
              
              <div class="modelo-details">
                <div class="velocidad-badge" :class="modelo.velocidad">
                  <i class="fas fa-tachometer-alt"></i>
                  {{ velocidadTexto(modelo.velocidad) }}
                </div>
                <p class="tiempo-estimado">{{ modelo.tiempo_estimado }}</p>
              </div>

              <div class="fortalezas">
                <p class="ideal-para">{{ modelo.ideal_para }}</p>
                <div class="tags">
                  <span 
                    v-for="fortaleza in modelo.fortalezas.slice(0, 3)" 
                    :key="fortaleza"
                    class="tag"
                  >
                    {{ fortaleza }}
                  </span>
                </div>
              </div>

              <div v-if="modelo.nota" class="nota">
                <i class="fas fa-lightbulb"></i>
                {{ modelo.nota }}
              </div>

              <div v-if="!modelo.disponible" class="no-disponible-overlay">
                <i class="fas fa-lock"></i>
                <span>No disponible</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Modelos Aceptables -->
        <div v-if="recomendaciones.aceptables?.length" class="seccion-modelos">
          <h4 class="seccion-titulo aceptable">
            <i class="fas fa-check-circle"></i>
            Alternativas Aceptables
          </h4>
          <div class="modelos-grid alternativas">
            <div 
              v-for="modelo in recomendaciones.aceptables" 
              :key="modelo.modelo"
              class="modelo-card aceptable"
              :class="{ 'no-disponible': !modelo.disponible }"
              @click="seleccionarModelo(modelo.modelo)"
            >
              <div class="modelo-header">
                <h5>{{ modelo.nombre_display }}</h5>
                <div class="puntuacion">
                  <i 
                    v-for="n in 5" 
                    :key="n"
                    class="fas fa-star"
                    :class="{ 'estrella-activa': n <= modelo.puntuacion }"
                  ></i>
                </div>
              </div>
              
              <div class="modelo-details">
                <div class="velocidad-badge" :class="modelo.velocidad">
                  <i class="fas fa-tachometer-alt"></i>
                  {{ velocidadTexto(modelo.velocidad) }}
                </div>
                <p class="tiempo-estimado">{{ modelo.tiempo_estimado }}</p>
              </div>

              <div class="fortalezas">
                <div class="tags">
                  <span 
                    v-for="fortaleza in modelo.fortalezas.slice(0, 2)" 
                    :key="fortaleza"
                    class="tag"
                  >
                    {{ fortaleza }}
                  </span>
                </div>
              </div>

              <div v-if="modelo.limitaciones" class="limitaciones">
                <p class="limitaciones-text">
                  <i class="fas fa-info-circle"></i>
                  {{ modelo.limitaciones.join(', ') }}
                </p>
              </div>

              <div v-if="!modelo.disponible" class="no-disponible-overlay">
                <i class="fas fa-lock"></i>
                <span>No disponible</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Modelos No Recomendados (colapsible) -->
        <div v-if="recomendaciones.no_recomendados?.length" class="seccion-modelos">
          <h4 
            class="seccion-titulo no-recomendado clickable"
            @click="mostrarNoRecomendados = !mostrarNoRecomendados"
          >
            <i class="fas fa-exclamation-triangle"></i>
            No Recomendados para este tipo
            <i class="fas fa-chevron-down" :class="{ 'rotated': mostrarNoRecomendados }"></i>
          </h4>
          
          <div v-if="mostrarNoRecomendados" class="no-recomendados-list">
            <div 
              v-for="modelo in recomendaciones.no_recomendados" 
              :key="modelo.modelo"
              class="no-recomendado-item"
            >
              <div class="modelo-nombre">{{ modelo.modelo }}</div>
              <div class="razon">{{ modelo.razon }}</div>
              <div v-if="modelo.alternativa" class="alternativa">
                Usa mejor: 
                <button 
                  @click="seleccionarModelo(modelo.alternativa)"
                  class="btn-alternativa"
                >
                  {{ modelo.alternativa }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer con acciones -->
      <div class="modal-footer">
        <div class="acciones">
          <button @click="usarRecomendado" class="btn-principal">
            <i class="fas fa-magic"></i>
            Usar Recomendado
          </button>
          <button @click="cerrarModal" class="btn-secundario">
            Cerrar sin cambios
          </button>
        </div>
        <div class="configuracion">
          <label class="checkbox-container">
            <input 
              type="checkbox" 
              v-model="noMostrarDeNuevo"
            >
            <span class="checkmark"></span>
            No mostrar esta ayuda de nuevo
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModalRecomendacionesModelos',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    tipoPregunta: {
      type: String,
      required: true,
      validator: value => ['opcion_multiple', 'abierta', 'caso_uso'].includes(value)
    },
    modeloActual: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      recomendaciones: {
        recomendados: [],
        aceptables: [],
        no_recomendados: []
      },
      cargando: false,
      error: null,
      mostrarNoRecomendados: false,
      noMostrarDeNuevo: false
    }
  },
  computed: {
    iconoTipoPregunta() {
      const iconos = {
        'opcion_multiple': 'fas fa-list-ul',
        'abierta': 'fas fa-edit',
        'caso_uso': 'fas fa-briefcase'
      }
      return iconos[this.tipoPregunta] || 'fas fa-question'
    },
    tituloTipoPregunta() {
      const titulos = {
        'opcion_multiple': 'Para Preguntas de Opción Múltiple',
        'abierta': 'Para Preguntas de Desarrollo',
        'caso_uso': 'Para Casos de Uso'
      }
      return titulos[this.tipoPregunta] || 'Selección de Modelo'
    }
  },
  watch: {
    visible(newValue) {
      if (newValue) {
        this.cargarRecomendaciones()
      }
    },
    tipoPregunta() {
      if (this.visible) {
        this.cargarRecomendaciones()
      }
    }
  },
  methods: {
    async cargarRecomendaciones() {
      this.cargando = true
      this.error = null
      
      try {
        const response = await fetch(`/api/recomendaciones-modelos/${this.tipoPregunta}`)
        
        if (!response.ok) {
          throw new Error(`Error HTTP: ${response.status}`)
        }
        
        const data = await response.json()
        
        if (data.success) {
          this.recomendaciones = data.recomendaciones
        } else {
          throw new Error(data.error || 'Error desconocido')
        }
      } catch (error) {
        console.error('Error cargando recomendaciones:', error)
        this.error = 'No se pudieron cargar las recomendaciones. Verifica tu conexión.'
      } finally {
        this.cargando = false
      }
    },
    seleccionarModelo(modelo) {
      this.$emit('modelo-seleccionado', modelo)
      this.cerrarModal()
    },
    usarRecomendado() {
      if (this.recomendaciones.recomendados?.length > 0) {
        const primerRecomendado = this.recomendaciones.recomendados[0]
        if (primerRecomendado.disponible) {
          this.seleccionarModelo(primerRecomendado.modelo)
        }
      }
    },
    cerrarModal() {
      if (this.noMostrarDeNuevo) {
        localStorage.setItem('ocultarAyudaModelos', 'true')
      }
      this.$emit('cerrar')
    },
    velocidadTexto(velocidad) {
      const textos = {
        'rapida': 'Rápido',
        'media': 'Medio',
        'lenta': 'Lento'
      }
      return textos[velocidad] || velocidad
    }
  }
}
</script>


<style scoped>
/* === MODAL OVERLAY === */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
  backdrop-filter: blur(2px);
}

/* === MODAL CONTAINER === */
.modal-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* === MODAL HEADER === */
.modal-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 24px;
  position: relative;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tipo-pregunta-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.tipo-icon {
  font-size: 2.5rem;
  opacity: 0.9;
}

.tipo-pregunta-info h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.tipo-subtitle {
  margin: 4px 0 0 0;
  opacity: 0.9;
  font-size: 0.95rem;
}

.btn-cerrar {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-cerrar:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* === LOADING & ERROR STATES === */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container i {
  font-size: 3rem;
  color: #e74c3c;
  margin-bottom: 15px;
}

.btn-reintentar {
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 15px;
  transition: background 0.2s ease;
}

.btn-reintentar:hover {
  background: #5a6fd8;
}

/* === MODAL CONTENT === */
.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* === SECCIONES DE MODELOS === */
.seccion-modelos {
  margin-bottom: 32px;
}

.seccion-titulo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid;
}

.seccion-titulo.recomendado {
  color: #27ae60;
  border-color: #27ae60;
}

.seccion-titulo.aceptable {
  color: #f39c12;
  border-color: #f39c12;
}

.seccion-titulo.no-recomendado {
  color: #e74c3c;
  border-color: #e74c3c;
  cursor: pointer;
  transition: all 0.2s ease;
}

.seccion-titulo.clickable:hover {
  opacity: 0.8;
}

.seccion-titulo .fa-chevron-down {
  margin-left: auto;
  transition: transform 0.2s ease;
}

.seccion-titulo .fa-chevron-down.rotated {
  transform: rotate(180deg);
}

/* === GRID DE MODELOS === */
.modelos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.modelos-grid.alternativas {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

/* === CARDS DE MODELOS === */
.modelo-card {
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
  position: relative;
  overflow: hidden;
}

.modelo-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.modelo-card.recomendado {
  border-color: #27ae60;
  background: linear-gradient(135deg, #ffffff 0%, #f8fff9 100%);
}

.modelo-card.recomendado:hover {
  border-color: #219a52;
  box-shadow: 0 8px 25px rgba(39, 174, 96, 0.2);
}

.modelo-card.aceptable {
  border-color: #f39c12;
  background: linear-gradient(135deg, #ffffff 0%, #fffcf5 100%);
}

.modelo-card.aceptable:hover {
  border-color: #e67e22;
  box-shadow: 0 8px 25px rgba(243, 156, 18, 0.15);
}

.modelo-card.no-disponible {
  opacity: 0.6;
  cursor: not-allowed;
}

.modelo-card.no-disponible:hover {
  transform: none;
}

/* === HEADER DEL MODELO === */
.modelo-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.modelo-header h5 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}

.puntuacion {
  display: flex;
  gap: 2px;
}

.puntuacion .fa-star {
  color: #ddd;
  font-size: 0.9rem;
}

.puntuacion .fa-star.estrella-activa {
  color: #f1c40f;
}

/* === DETALLES DEL MODELO === */
.modelo-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.velocidad-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.velocidad-badge.rapida {
  background: #d4edda;
  color: #155724;
}

.velocidad-badge.media {
  background: #fff3cd;
  color: #856404;
}

.velocidad-badge.lenta {
  background: #f8d7da;
  color: #721c24;
}

.tiempo-estimado {
  font-size: 0.85rem;
  color: #6c757d;
  margin: 0;
}

/* === FORTALEZAS Y TAGS === */
.fortalezas {
  margin-bottom: 15px;
}

.ideal-para {
  font-size: 0.9rem;
  color: #495057;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  background: #e9ecef;
  color: #495057;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.modelo-card.recomendado .tag {
  background: #d4edda;
  color: #155724;
}

.modelo-card.aceptable .tag {
  background: #fff3cd;
  color: #856404;
}

/* === NOTA Y LIMITACIONES === */
.nota {
  background: #e7f3ff;
  border: 1px solid #b3d9ff;
  border-radius: 8px;
  padding: 10px;
  font-size: 0.85rem;
  color: #0066cc;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 12px;
}

.nota i {
  margin-top: 2px;
  flex-shrink: 0;
}

.limitaciones {
  margin-top: 12px;
}

.limitaciones-text {
  font-size: 0.85rem;
  color: #856404;
  margin: 0;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.limitaciones-text i {
  margin-top: 2px;
  flex-shrink: 0;
}

/* === NO DISPONIBLE OVERLAY === */
.no-disponible-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #6c757d;
  font-weight: 500;
}

.no-disponible-overlay i {
  font-size: 1.5rem;
}

/* === NO RECOMENDADOS === */
.no-recomendados-list {
  background: #fff5f5;
  border: 1px solid #feb2b2;
  border-radius: 8px;
  padding: 16px;
}

.no-recomendado-item {
  padding: 12px 0;
  border-bottom: 1px solid #feb2b2;
}

.no-recomendado-item:last-child {
  border-bottom: none;
}

.modelo-nombre {
  font-weight: 600;
  color: #e53e3e;
  margin-bottom: 4px;
}

.razon {
  font-size: 0.9rem;
  color: #718096;
  margin-bottom: 8px;
}

.alternativa {
  font-size: 0.85rem;
  color: #4a5568;
}

.btn-alternativa {
  background: #667eea;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  margin-left: 4px;
}

.btn-alternativa:hover {
  background: #5a6fd8;
}

/* === MODAL FOOTER === */
.modal-footer {
  background: #f8f9fa;
  padding: 20px 24px;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.acciones {
  display: flex;
  gap: 12px;
}

.btn-principal {
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-principal:hover {
  background: #5a6fd8;
  transform: translateY(-1px);
}

.btn-secundario {
  background: #6c757d;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-secundario:hover {
  background: #5a6268;
}

/* === CONFIGURACIÓN === */
.configuracion {
  display: flex;
  align-items: center;
}

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.9rem;
  color: #6c757d;
}

.checkbox-container input[type="checkbox"] {
  margin-right: 8px;
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .modal-container {
    margin: 10px;
    max-height: calc(100vh - 20px);
  }
  
  .modelos-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .acciones {
    flex-direction: column;
  }
  
  .configuracion {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .modal-overlay {
    padding: 10px;
  }
  
  .modal-header {
    padding: 16px;
  }
  
  .tipo-pregunta-info {
    gap: 10px;
  }
  
  .tipo-icon {
    font-size: 2rem;
  }
  
  .modal-content {
    padding: 16px;
  }
  
  .modelo-card {
    padding: 16px;
  }
}
</style>