import { ref, reactive, computed, inject, nextTick } from 'vue';
import { Appwrite as AppwriteSDK, config } from '../appwrite-config.js';


const publicUrl = ref('');
const storage = window.AppwriteStorage;
// Usar html2pdf desde el objeto global (ya incluido via CDN en index.html)
const html2pdf = window.html2pdf;
const { databases } = AppwriteSDK; // <-- AÑADE ESTA LÍNEA TAMBIÉN
// Obtener email del usuario autenticado
const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
const currentUserEmail = currentUser.email;


// Función auxiliar para copiar texto al portapapele
window.copiarAlPortapapeles = function(buttonElement)  {
    const targetId = buttonElement.getAttribute('data-target-id');
    const targetParagraph = document.getElementById(targetId);

    if (targetParagraph) {
        const textoACopiar = targetParagraph.textContent || targetParagraph.innerText;
        navigator.clipboard.writeText(textoACopiar).then(() => {
            // Feedback visual (opcional pero útil)
            const originalText = buttonElement.innerHTML;
            buttonElement.innerHTML = '✅'; // Cambia a un check
            setTimeout(() => {
                buttonElement.innerHTML = originalText; // Vuelve al icono original
            }, 1500); // Después de 1.5 segundos
            console.log(`Texto copiado: ${targetId}`);
        }).catch(err => {
            console.error('Error al copiar texto: ', err);
            alert('Error al intentar copiar la respuesta.');
            });
    } else {
        console.error(`Elemento con ID ${targetId} no encontrado.`);
        }
}

// Función global para guardar respuestas desde el modal
window.guardarRespuestasEnBD = async function() {
    try {
        // Obtener datos del componente Vue actual
        const examenData = window.currentExamenData;
        
        if (!examenData) {
            alert('Error: No se encontraron datos del examen');
            return;
        }
        
        const response = await fetch('http://127.0.0.1:5000/api/guardar-respuestas-profesor', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: currentUserEmail,  // ← AGREGAR ESTA LÍNEA email
                examen_id: examenData.id,
                nombre_profesor: examenData.profesor,
                nombre_examen: examenData.nombreExamen,
                tipo_examen: examenData.tipoExamen,
                profesor_id: examenData.profesorId,
                preguntas_marcar: examenData.preguntasMarcar,
                preguntas_libres: examenData.preguntasLibres,
                casos_uso: examenData.casosUso
            })
        });
        
        if (response.ok) {
            alert('Respuestas del profesor guardadas exitosamente');
        } else {
            alert('Error al guardar respuestas');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
};

function recolectarEtiquetasPreguntas() {
    const etiquetas = {};
    const selectores = document.querySelectorAll('.etiqueta-pregunta');
    
    selectores.forEach(selector => {
        const numeroPregunta = selector.getAttribute('data-pregunta');
        const etiquetaSeleccionada = selector.value;
        etiquetas[numeroPregunta] = etiquetaSeleccionada;
    });
    
    console.log("Etiquetas recolectadas:", etiquetas);
    return etiquetas;
}

export const ProfesorComponent = {

    template: `
    <div class="profesor-component-wrapper"> 

        <div class="section" :class="modoEstudiante ? 'modo-estudiante' : 'modo-profesor'">
            <h1>{{ modoEstudiante ? 'Examen Alumno' : 'Panel del Profesor' }}</h1>
            
            <div class="card">  
                 <h2>Completar Datos</h2>
                
                <div class="form-group">
                    <label for="examen-id">ID del Examen</label>
                    <input type="text" id="examen-id" v-model="examen.id" :disabled="examen.bloqueado">
                </div>

                <div class="form-group">
                    <label for="nombre-examen">Nombre del Examen</label>
                    <input type="text" id="nombre-examen" v-model="examen.nombreExamen" :disabled="examen.bloqueado">
                </div>

                <div class="form-group">
                    <label for="tipo-examen">Tipo de Examen</label>
                    <input type="text" id="tipo-examen" v-model="examen.tipoExamen" :disabled="examen.bloqueado">
                </div>
                
                <div class="form-group">
                    <label for="examen-fecha">Fecha</label>
                    <input type="date" id="examen-fecha" v-model="examen.fecha" :disabled="examen.bloqueado">
                </div>
                
                <div class="form-group">
                    <label for="nombre-profesor">Campo para Nombre del Profesor</label>
                    <input type="text" id="nombre-profesor" v-model="examen.profesor" :disabled="examen.bloqueado || modoEstudiante">
                </div>

                <div class="form-group">
                    <label for="id-profesor">ID del Profesor</label>
                    <input type="text" id="id-profesor" v-model="examen.profesorId" :disabled="examen.bloqueado || modoEstudiante">
                </div>

                <div class="form-group">
                <label for="modelo-respuestas">Modelo para Generar Respuestas Automáticas:</label>
                    <select id="modelo-respuestas" v-model="modeloRespuestas" class="form-control">
                        <option value="gemini-1-5-pro">Gemini 1.5 Pro (Por defecto)</option>
                        <option value="gemini-2-5-pro">Gemini 2.5 Pro</option>
                        <option value="gemini-2-0-flash">Gemini 2.0 Flash</option>
                        <option value="claude-sonnet-4">Claude Sonnet 4</option>
                        <option value="gpt-4-1">ChatGPT 4.1</option>
                        <option value="gpt-4o">ChatGPT 4o</option>
                    </select>
                </div>
                            
                <div class="form-group">
                    <label for="nombre-alumno">Campo para Nombre del Alumno</label>
                    <input type="text" id="nombre-alumno" v-model="examen.nombreAlumno" :disabled="!modoEstudiante">
                </div>
                
                <div class="form-group">
                    <label for="id-alumno">Campo para ID del Alumno</label>
                    <input type="text" id="id-alumno" v-model="examen.idAlumno" :disabled="!modoEstudiante">
                </div>
            </div>
            
            <div class="card">
                <h2>Responder de Preguntas</h2>
                    <div class="tab-container">
                    <div class="tab-buttons">
                        <button 
                            class="tab-btn" 
                            :class="{ active: activeTab === 'marcar' }" 
                            @click="activeTab = 'marcar'; console.log('Tab: marcar'); console.log('Preguntas marcar:', examen.preguntasMarcar)"
                        >
                            Preguntas para Marcar
                        </button>
                        <button 
                            class="tab-btn" 
                            :class="{ active: activeTab === 'libres' }" 
                            @click="activeTab = 'libres'; console.log('Tab: libres'); console.log('Preguntas libres:', examen.preguntasLibres)"
                        >
                            Preguntas Libres
                        </button>
                        <button 
                            class="tab-btn" 
                            :class="{ active: activeTab === 'casos' }" 
                            @click="activeTab = 'casos'; console.log('Tab: casos'); console.log('Casos de uso:', examen.casosUso)"
                        >
                            Casos de Uso
                        </button>
                    </div>
                    <div>Pestaña actual: {{ activeTab }}</div>
                    </div>


                    <div class="tab-content">
                        <!-- Preguntas para Marcar -->
                        <div v-if="activeTab === 'marcar'">

                        <div class="form-group" v-if="!modoEstudiante">
                        <label for="prompt-input">Tema para generar pregunta:</label>
                        <input type="text" id="prompt-input" class="form-control" placeholder="Ej: programación, bases de datos, redes...">
                        </div>

                        <div class="form-group" v-if="!modoEstudiante">
                            <label for="modelo-ia">Modelo de IA:</label>
                            <select id="modelo-ia-marcar" class="form-control">
                                <!-- Gemini -->
                                <option value="gemini-2-5-pro">Gemini 2.5 Pro</option>
                                <option value="gemini-2-5-flash">Gemini 2.5 Flash</option>
                                <option value="gemini-2-0-flash">Gemini 2.0 Flash</option>
                                <option value="gemini-1-5-flash">Gemini 1.5 Flash</option>
                                <option value="gemini-1-5-pro">Gemini 1.5 Pro</option>

                                <!-- Nuevos modelos de Together.ai para reemplazar OpenRouter -->
                                <option value="qwen3-235b-thinking">Qwen3 235B Thinking</option>
                                <option value="qwen3-235b-instruct">Qwen3 235B Instruct</option>
                                <option value="qwen3-30b-thinking">Qwen3 30B Thinking</option>
                                <option value="qwen3-30b-instruct">Qwen3 30B Instruct</option>
                                <option value="llama-vision-free">Llama Vision Free</option>
                                <option value="nemotron-ultra">Nemotron Ultra 253B</option>

                                <!-- Modelos originales con model_id -->
                                <option value="deepseek-ai/DeepSeek-R1">DeepSeek R1-0528</option>
                                <option value="meta-llama/Llama-4-Maverick-Instruct">Llama 4 Maverick Instruct</option>
                                <option value="meta-llama/Llama-4-Scout-Instruct">Llama 4 Scout Instruct</option>
                                <option value="Qwen/QwQ-32B-Preview">Qwen QwQ-32B</option>
                                <option value="mistralai/Mistral-Small-Instruct-2501">Mistral Small 25.01</option>
                                <option value="SCB10X/Typhoon-2-70B-Instruct">Typhoon 2 70B Instruct</option>
                                <option value="mistralai/Mixtral-8x7B-Instruct-v0.1">Mixtral-8x7B Instruct</option>
                                <option value="meta-llama/Meta-Llama-3-8B-Instruct">Meta Llama 3 8B Instruct Reference</option>
                                <option value="Qwen/Qwen2.5-Coder-32B-Instruct">Qwen 2.5 Coder 32B Instruct</option>
                                <option value="upstage/SOLAR-10.7B-Instruct-v1.0">Upstage SOLAR Instruct v1</option>
                                <option value="Arcee-AI/Arcee-Maestro">Arcee AI Maestro</option>
                                <option value="NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO">Nous Hermes 2 Mixtral 8X7B</option>
                                <option value="deepseek-ai/DeepSeek-V3">DeepSeek V3</option>
                                <option value="Qwen/Qwen2.5-VL-72B-Instruct">Qwen 2.5 VL 72B</option>
                                <option value="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo">Meta Llama 3.1 405B</option>
                                <option value="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free">Llama 3.3 70B</option>
                                <option value="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo">Meta Llama 3.2 90B Vision</option>

                                <!-- Nuevos modelos potentes agregados -->
                                <option value="deepseek-ai/DeepSeek-R1-Turbo">DeepSeek R1 Turbo</option>
                                <option value="Qwen/Qwen3-Coder-480B-A35B">Qwen3 Coder 480B</option>
                                <option value="Qwen/Qwen3-235B-A22B-Thinking-2507">Qwen3 235B Thinking</option>
                                <option value="Qwen/Qwen3-235B-A22B-Instruct-2507">Qwen3 235B Instruct</option>
                                <option value="Qwen/Qwen3-30B-A3B-Thinking-2507">Qwen3 30B Thinking</option>
                                <option value="Qwen/Qwen3-30B-A3B-Instruct-2507">Qwen3 30B Instruct</option>
                                <option value="LG-AI-Research/exaone-deep-32b">Exaone Deep 32B</option>
                                <option value="moonshotai/Kimi-K2-Instruct">Kimi K2 Instruct</option>
                                <option value="zai-org/GLM-4.5-Air-FP8">GLM 4.5 Air FP8</option>
                                <option value="meta-llama/Llama-Vision-Free">Llama Vision Free</option>
                                <option value="nvidia/llama-3.1-nemotron-ultra-253b-v1">Nemotron Ultra 253B</option>

                                <!-- Toguether: Vision - Multimodal -->
                                <option value="llama-3-2-90b">Meta Llama 3.2 90B</option>

                                <!-- Vision - Multimodal -->
                                <option value="claude-3-7">Claude 3.7 Sonnet</option>
                                <option value="gpt-4-1">ChatGPT 4.1</option>
                            </select>
                            <!-- AGREGA ESTO JUSTO DESPUÉS -->
                            <button 
                            type="button" 
                            class="btn btn-info" 
                            @click="abrirModalRecomendaciones('opcion_multiple', 'modelo-ia-marcar')"
                            style="margin-top: 8px; font-size: 0.9rem;"
                            >
                            💡 ¿Qué modelo usar?
                            </button>
                        </div>

                        <!-- Botón para la IA, parámetro: 'marcar' -->
                            <button class="btn" @click="generarPreguntaIA('marcar')" :disabled="examen.bloqueado" v-if="!modoEstudiante">
                                Generar Pregunta 
                            </button>
                            <div v-for="(pregunta, index) in examen.preguntasMarcar" :key="'marcar-'+index" class="question">
                                <div class="question-header">
                                    <div class="form-group">
                                        <label>Número de Pregunta</label>
                                        <input type="number" v-model="pregunta.numero" :disabled="examen.bloqueado">
                                    </div>
                                    <div class="form-group">
                                        <label>Puntaje</label>
                                        <input type="number" step="0.1" v-model="pregunta.puntaje" :disabled="examen.bloqueado">
                                    </div>
                                </div>
                                
                                <div class="form-group">
                                    <label>Texto de la Pregunta</label>
                                    <textarea v-model="pregunta.texto" rows="3" :disabled="examen.bloqueado"></textarea>
                                </div>
                                
                                <div class="options">
                                    <div v-for="(opcion, i) in pregunta.opciones" :key="i" class="form-group">
                                        <div style="display: flex; gap: 10px;">
                                            <input type="text" v-model="opcion.texto" :disabled="examen.bloqueado" style="flex: 1;">
                                            <!-- Botón X para profesor, Casilla/radio para alumno -->
                                            <button v-if="!modoEstudiante" class="btn btn-danger" @click="eliminarOpcion(pregunta, i)" :disabled="examen.bloqueado">X</button>
                                            <input v-else type="radio" :name="'pregunta-' + pregunta.numero" :value="opcion.valor" v-model="pregunta.respuestaSeleccionada" :disabled="!examen.bloqueado && !modoEstudiante">
                                        </div>
                                    </div>
                                    
                                    <div style="display: flex; gap: 10px; margin-top: 10px;">
                                        <button class="btn" @click="agregarOpcion(pregunta)" :disabled="examen.bloqueado">Agregar Opción</button>
                                        <button class="btn btn-danger" @click="eliminarPreguntaMarcar(index)" v-if="!modoEstudiante" :disabled="examen.bloqueado">Eliminar Pregunta</button>
                                    </div>
                                </div>
                                </div>
                                </div>
                                                    
                        <!-- Preguntas Libres -->
                        <div v-if="activeTab === 'libres'">

                        <div class="form-group" v-if="!modoEstudiante">
                        <label for="prompt-input">Tema para generar pregunta:</label>
                        <input type="text" id="prompt-input" class="form-control" placeholder="Ej: programación, bases de datos, redes...">
                        </div>

                        <div class="form-group" v-if="!modoEstudiante">
                            <label for="modelo-ia">Modelo de IA:</label>
                            <select id="modelo-ia-libres" class="form-control">
                                <!-- Gemini -->
                                <option value="gemini-2-5-pro">Gemini 2.5 Pro</option>
                                <option value="gemini-2-5-flash">Gemini 2.5 Flash</option>
                                <option value="gemini-2-0-flash">Gemini 2.0 Flash</option>
                                <option value="gemini-1-5-flash">Gemini 1.5 Flash</option>
                                <option value="gemini-1-5-pro">Gemini 1.5 Pro</option>

                                <!-- OpenRouter: Texto -->
                                <option value="qwen/qwen3-32b:free">Qwen 3 32B</option>
                                <option value="deepseek/deepseek-chat-v3-0324">DeepSeek Chat V3</option>
                                <option value="google/gemma-3-27b-it:free">Gemma 3 27B</option>
                                <option value="mistralai/mistral-small-3.1-24b-instruct:free">Mistral Small 24B</option>
                                <option value="nvidia/llama-3.1-nemotron-ultra-253b-v1:free">Llama 3.1 Nemotron 253B</option>
                                <option value="meta-llama/llama-3.3-70b-instruct:free">Meta Llama 3.3 70B</option>
                                <option value="meta-llama/llama-3.1-405b:free">Meta Llama 3.1 405B</option>

                                <!-- OpenRouter: Multimodal -->
                                <option value="qwen/qwen2.5-vl-32b-instruct:free">Qwen 2.5 VL 32B - Test</option>
                                <option value="google/gemini-2.0-flash-exp:free">Gemini 2.0 Flash Exp - Test</option>
                                <option value="google/learnlm-1.5-pro-experimental:free">LearnLM 1.5 Pro - Test</option>
                                <option value="meta-llama/llama-3.2-11b-vision-instruct:free">Meta Llama 3.2 11B Vision - Test</option>

                                <!-- Toguether: Texto -->
                                <option value="deepseek-ai/DeepSeek-V3">DeepSeek V3</option>
                                <option value="Qwen/Qwen2.5-VL-72B-Instruct">Qwen 2.5 72B</option>
                                <option value="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo">Meta Llama 3.1 405B</option>
                                <option value="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free">Llama 3.3 70B</option>

                                 <!-- Together: Modelos Agregados -->
                                <option value="deepseek-ai/DeepSeek-R1">DeepSeek R1-0528</option>
                                <option value="meta-llama/Llama-4-Maverick-Instruct">Llama 4 Maverick Instruct</option>
                                <option value="meta-llama/Llama-4-Scout-Instruct">Llama 4 Scout Instruct</option>
                                <option value="Qwen/QwQ-32B-Preview">Qwen QwQ-32B</option>
                                <option value="mistralai/Mistral-Small-Instruct-2501">Mistral Small 25.01</option>
                                <option value="SCB10X/Typhoon-2-70B-Instruct">Typhoon 2 70B Instruct</option>
                                <option value="mistralai/Mixtral-8x7B-Instruct-v0.1">Mixtral-8x7B Instruct</option>
                                <option value="meta-llama/Meta-Llama-3-8B-Instruct">Meta Llama 3 8B Instruct Reference</option>
                                <option value="Qwen/Qwen2.5-Coder-32B-Instruct">Qwen 2.5 Coder 32B Instruct</option>
                                <option value="upstage/SOLAR-10.7B-Instruct-v1.0">Upstage SOLAR Instruct v1</option>
                                <option value="Arcee-AI/Arcee-Maestro">Arcee AI Maestro</option>
                                <option value="NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO">Nous Hermes 2 Mixtral 8X7B</option>

                                <!-- Modelos Gratuitos Agregados -->
                                <option value="LG-AI-Research/exaone-3.5-32b-instruct">EXAONE 3.5 32B Instruct - Test</option>
                                <option value="LG-AI-Research/exaone-deep-32b">EXAONE Deep 32B - Test</option>
                                <option value="meta-llama/Llama-Vision-Free">Meta Llama Vision - Test</option>
                                <option value="deepseek-ai/DeepSeek-R1-Distill-Llama-70B">DeepSeek R1 Distill Llama 70B - Test</option>
                                <option value="Arcee-AI/AFM-4.5B-Preview">AFM-4.5B-Preview - Test</option> 

                                <!-- Toguether: Vision - Multimodal -->
                                <option value="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo">Meta Llama 3.2 90B</option>

                                <!-- Vision - Multimodal -->
                                <option value="claude-sonnet-4">Claude Sonnet 4</option>
                                <option value="gpt-4-1">ChatGPT 4.1</option>
                            </select>
                            <!-- AGREGA ESTO JUSTO DESPUÉS -->
                            <button 
                            type="button" 
                            class="btn btn-info" 
                            @click="abrirModalRecomendaciones('abierta', 'modelo-ia-libres')"
                            style="margin-top: 8px; font-size: 0.9rem;"
                            >
                            💡 ¿Qué modelo usar?
                            </button>
                        </div>

                            <button class="btn" @click="generarPreguntaIA('libres')" :disabled="examen.bloqueado" v-if="!modoEstudiante">Generar Pregunta</button>
                            
                            <div v-for="(pregunta, index) in examen.preguntasLibres" :key="'libre-'+index" class="question">
                                <div class="question-header">
                                    <div class="form-group">
                                        <label>Número de Pregunta</label>
                                        <input type="number" v-model="pregunta.numero" :disabled="examen.bloqueado">
                                    </div>
                                    <div class="form-group">
                                        <label>Puntaje</label>
                                        <input type="number" step="0.1" v-model="pregunta.puntaje" :disabled="examen.bloqueado">
                                    </div>
                                </div>
                                
                                <div class="form-group">
                                    <label>Texto de la Pregunta</label>
                                    <textarea v-model="pregunta.texto" rows="3" :disabled="examen.bloqueado"></textarea>
                                </div>

                                <!-- AGREGAR ESTAS LÍNEAS -->
                                <div v-if="!modoEstudiante" style="margin-top: 10px;">
                                    <button class="btn btn-info" @click="abrirPlayground(pregunta, 'libres')" :disabled="examen.bloqueado" style="margin-right: 10px;">
                                        🎨 Generar Imagen IA
                                    </button>
                                    <button class="btn btn-secondary" @click="subirImagenDirecta(pregunta)" :disabled="examen.bloqueado">
                                        📁 Subir Imagen
                                    </button>
                                    <button class="btn btn-primary" @click="abrirRecursosEducativos(pregunta, 'libres')" 
                                            :disabled="examen.bloqueado" style="margin-left: 10px;">
                                        🎓 Recursos Educativos
                                    </button>                                 
                                </div>

                                <!-- AGREGAR ESTAS LÍNEAS AQUÍ -->
                                <!-- Sección para que el profesor adjunte archivos -->
                                <div v-if="!modoEstudiante" style="margin-top: 10px; padding: 10px; border: 1px dashed #ccc; border-radius: 5px;">
                                    <label style="font-weight: bold;">📎 Archivo adjunto (opcional):</label>
                                    <div style="background: #f0f8ff; padding: 8px; margin: 8px 0; border-left: 4px solid #2196f3; font-size: 0.9em;">
                                        📝 <strong>Importante:</strong> Nombre su archivo como: <code>[ID_Examen]_[ID_Alumno]</code><br>
                                        <strong>Ejemplo:</strong> <code>{{ examen.id || '123456' }}_{{ examen.idAlumno || '789012' }}.pdf</code>
                                    </div>
                                <button 
                                class="btn btn-outline-primary" 
                                @click="abrirSelectorAppwrite(pregunta, 'libres')"
                                :disabled="examen.bloqueado"
                                style="margin: 5px 0;"
                                >
                                📁 Elegir de Repositorio
                                </button>
                                    <div v-if="pregunta.archivoNombre" style="color: green; font-size: 0.9em;">
                                        ✅ {{ pregunta.archivoNombre }}
                                        <button @click="eliminarArchivoAnexo(pregunta)" style="margin-left: 10px; color: red; background: none; border: none; cursor: pointer;">
                                            🗑️
                                        </button>
                                    </div>
                                </div>

                                <!-- Área de respuesta para el alumno, no se bloquea en modo estudiante -->
                                <div v-if="modoEstudiante" class="form-group">
                                    <label>Tu respuesta:</label>
                                    <textarea 
                                        v-model="pregunta.respuestaAlumno" 
                                        rows="3" 
                                        placeholder="Escribe tu respuesta aquí..."
                                        <!--:class="{ 'protected-textarea': modoEstudiante }"-->
                                        <!--:onkeydown="modoEstudiante ? 'return bloquearCopyPaste(event)' : null"-->
                                        <!--:oncontextmenu="modoEstudiante ? 'return bloquearClickDerecho(event)' : null"-->
                                        <!--:onselectstart="modoEstudiante ? 'return bloquearSeleccion(event)' : null"-->
                                        <!--:ondragstart="modoEstudiante ? 'return bloquearArrastrar(event)' : null"-->
                                        :spellcheck="false"
                                        :autocomplete="off"
                                    ></textarea>
                                </div>

                                    <!-- Mostrar botón de descarga si hay documento adjunto y está en modo estudiante -->
                                    <div v-if="modoEstudiante && (pregunta.archivoUrl || pregunta.archivoId || pregunta.archivoNombre)" style="margin-top: 10px; padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;">
                                        <div style="display: flex; align-items: center; gap: 10px;">
                                            <i class="fas fa-file-pdf" style="color: #dc3545; font-size: 18px;"></i>
                                            <span style="font-weight: bold;">{{ pregunta.archivoNombre || 'Archivo adjunto' }}</span>
                                            <button @click="window.open(pregunta.archivoUrl, '_blank')" class="btn btn-primary" style="padding: 5px 10px;">
                                                Ver PDF
                                            </button>
                                        </div>
                                    </div>
                                   
                                <button class="btn btn-danger" @click="eliminarPreguntaLibre(index)" v-if="!modoEstudiante" :disabled="examen.bloqueado">Eliminar Pregunta</button>
                            </div>
                        </div>
                        <!-- Área de respuesta para el profesor en modo plantilla -->
                        
                        <!-- Casos de Uso -->
                        <div v-if="activeTab === 'casos'">
                        <div class="form-group" v-if="!modoEstudiante">
                        <label for="prompt-input">Tema para generar pregunta:</label>
                        <input type="text" id="prompt-input" class="form-control" placeholder="Ej: programación, bases de datos, redes...">
                        </div>

                        <div class="form-group" v-if="!modoEstudiante">
                            <label for="modelo-ia">Modelo de IA:</label>
                            <select id="modelo-ia-casos" class="form-control">
                                <!-- Gemini -->
                                <option value="gemini-2-5-pro">Gemini 2.5 Pro</option>
                                <option value="gemini-2-5-flash">Gemini 2.5 Flash</option>
                                <option value="gemini-2-0-flash">Gemini 2.0 Flash</option>
                                <option value="gemini-1-5-flash">Gemini 1.5 Flash</option>
                                <option value="gemini-1-5-pro">Gemini 1.5 Pro</option>

                                <!-- OpenRouter: Texto -->
                                <option value="qwen/qwen3-32b:free">Qwen 3 32B</option>
                                <option value="deepseek/deepseek-chat-v3-0324">DeepSeek Chat V3</option>
                                <option value="google/gemma-3-27b-it:free">Gemma 3 27B - Test</option>
                                <option value="mistralai/mistral-small-3.1-24b-instruct:free">Mistral Small 24B</option>
                                <option value="nvidia/llama-3.1-nemotron-ultra-253b-v1:free">Llama 3.1 Nemotron 253B</option>
                                <option value="meta-llama/llama-3.3-70b-instruct:free">Meta Llama 3.3 70B</option>
                                <option value="meta-llama/llama-3.1-405b:free">Meta Llama 3.1 405B</option>

                                <!-- OpenRouter: Multimodal -->
                                <option value="qwen/qwen2.5-vl-32b-instruct:free">Qwen 2.5 VL 32B - Test</option>
                                <option value="google/gemini-2.0-flash-exp:free">Gemini 2.0 Flash Exp - Test</option>
                                <option value="google/learnlm-1.5-pro-experimental:free">LearnLM 1.5 Pro - Test</option>
                                <option value="meta-llama/llama-3.2-11b-vision-instruct:free">Meta Llama 3.2 11B Vision - Test</option>

                                <!-- Toguether: Texto -->
                                <option value="deepseek-ai/DeepSeek-V3">DeepSeek V3</option>
                                <option value="Qwen/Qwen2.5-VL-72B-Instruct">Qwen 2.5 72B</option>
                                <option value="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo">Meta Llama 3.1 405B</option>
                                <option value="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free">Llama 3.3 70B</option>

                                <!-- Together: Modelos Agregados -->
                                <option value="deepseek-ai/DeepSeek-R1">DeepSeek R1-0528</option>
                                <option value="meta-llama/Llama-4-Maverick-Instruct">Llama 4 Maverick Instruct</option>
                                <option value="meta-llama/Llama-4-Scout-Instruct">Llama 4 Scout Instruct</option>
                                <option value="Qwen/QwQ-32B-Preview">Qwen QwQ-32B</option>
                                <option value="mistralai/Mistral-Small-Instruct-2501">Mistral Small 25.01</option>
                                <option value="SCB10X/Typhoon-2-70B-Instruct">Typhoon 2 70B Instruct</option>
                                <option value="mistralai/Mixtral-8x7B-Instruct-v0.1">Mixtral-8x7B Instruct</option>
                                <option value="meta-llama/Meta-Llama-3-8B-Instruct">Meta Llama 3 8B Instruct Reference</option>
                                <option value="Qwen/Qwen2.5-Coder-32B-Instruct">Qwen 2.5 Coder 32B Instruct</option>
                                <option value="upstage/SOLAR-10.7B-Instruct-v1.0">Upstage SOLAR Instruct v1</option>
                                <option value="Arcee-AI/Arcee-Maestro">Arcee AI Maestro</option>
                                <option value="NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO">Nous Hermes 2 Mixtral 8X7B</option>

                                <!-- Modelos Gratuitos Agregados -->
                                <option value="LG-AI-Research/exaone-3.5-32b-instruct">EXAONE 3.5 32B Instruct - Test</option>
                                <option value="LG-AI-Research/exaone-deep-32b">EXAONE Deep 32B - Test</option>
                                <option value="meta-llama/Llama-Vision-Free">Meta Llama Vision - Test</option>
                                <option value="deepseek-ai/DeepSeek-R1-Distill-Llama-70B">DeepSeek R1 Distill Llama 70B - Test</option>
                                <option value="Arcee-AI/AFM-4.5B-Preview">AFM-4.5B-Preview - Test</option>

                                <!-- Toguether: Vision - Multimodal -->
                                <option value="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo">Meta Llama 3.2 90B</option>

                                <!-- Vision - Multimodal -->
                                <option value="claude-3-7">Claude 3.7 Sonnet</option>
                                <option value="gpt-4-1">ChatGPT 4.1</option>
                            </select>
                            <!-- AGREGA ESTO JUSTO DESPUÉS -->
                            <button 
                            type="button" 
                            class="btn btn-info" 
                            @click="abrirModalRecomendaciones('caso_uso', 'modelo-ia-casos')"
                            style="margin-top: 8px; font-size: 0.9rem;"
                            >
                            💡 ¿Qué modelo usar?
                            </button>
                        </div>

                            <button class="btn" @click="generarPreguntaIA('casos')" :disabled="examen.bloqueado" v-if="!modoEstudiante">Generar Caso de Uso</button>
                            <div v-for="(caso, index) in examen.casosUso" :key="'caso-'+index" class="question">
                                <div class="question-header">
                                    <div class="form-group">
                                        <label>Número de Caso</label>
                                        <input type="number" v-model="caso.numero" :disabled="examen.bloqueado">
                                    </div>
                                    <div class="form-group">
                                        <label>Puntaje</label>
                                        <input type="number" step="0.1" v-model="caso.puntaje" :disabled="examen.bloqueado">
                                    </div>
                                </div>
                                
                                <div class="form-group">
                                    <label>Descripción del Caso</label>
                                    <textarea v-model="caso.descripcion" rows="3" :disabled="examen.bloqueado"></textarea>
                                </div>
                                
                                <div class="form-group">
                                    <label>Pregunta</label>
                                    <textarea v-model="caso.pregunta" rows="3" :disabled="examen.bloqueado"></textarea>
                                </div>

                                <!-- AGREGAR ESTAS LÍNEAS -->
                                <div v-if="!modoEstudiante" style="margin-top: 10px;">
                                    <button class="btn btn-info" @click="abrirPlayground(caso, 'casos')" :disabled="examen.bloqueado" style="margin-right: 10px;">
                                        🎨 Generar Imagen IA
                                    </button>
                                    <button class="btn btn-secondary" @click="subirImagenDirecta(caso)" :disabled="examen.bloqueado">
                                        📁 Subir Imagen
                                    </button>
                                    <button class="btn btn-primary" @click="abrirRecursosEducativos(caso, 'casos')" 
                                            :disabled="examen.bloqueado" style="margin-left: 10px;">
                                        🎓 Recursos Educativos
                                    </button>

                                </div>

                                <!-- AGREGAR ESTAS LÍNEAS AQUÍ -->
                                <!-- Sección para que el profesor adjunte archivos -->
                                <div v-if="!modoEstudiante" style="margin-top: 10px; padding: 10px; border: 1px dashed #ccc; border-radius: 5px;">
                                    <label style="font-weight: bold;">📎 Archivo adjunto (opcional):</label>
                                    <!-- Indicación de nombrado para el alumno -->
                                        <div style="background: #fff3cd; padding: 8px; margin: 8px 0; border-left: 4px solid #ffc107; font-size: 0.9em;">
                                            📝 <strong>Importante:</strong> Antes de adjuntar, nombre su archivo como: <code>[ID_Examen]_[ID_Alumno]</code><br>
                                            <strong>Ejemplo:</strong> <code>{{ examen.id || '123456' }}_{{ examen.idAlumno || '789012' }}.pdf</code>
                                        </div>
                                <button 
                                class="btn btn-outline-primary" 
                                @click="abrirSelectorAppwrite(caso, 'casos')"
                                :disabled="examen.bloqueado"
                                style="margin: 5px 0;"
                                >
                                📁 Elegir de Repositorio
                                </button>
                                    <div v-if="caso.archivoNombre" style="color: green; font-size: 0.9em;">
                                        ✅ {{ caso.archivoNombre }}
                                        <button @click="eliminarArchivoAnexo(caso)" style="margin-left: 10px; color: red; background: none; border: none;">
                                            🗑️
                                        </button>
                                    </div>
                                </div>
                                <!-- Área de respuesta para el profesor en modo plantilla -->

                                <!-- Área de respuesta para el alumno, no se bloquea en modo estudiante -->
                                <div v-if="modoEstudiante" class="form-group">
                                    <label>Tu respuesta:</label>
                                    <div style="position: relative;">
                                    </div>
                                    <textarea 
                                        v-model="caso.respuestaAlumno" 
                                        rows="3" 
                                        placeholder="Escribe tu respuesta aquí..." 
                                        style="padding-left: 40px;"
                                        <!--:class="{ 'protected-textarea': modoEstudiante }"-->
                                        <!--:onkeydown="modoEstudiante ? 'return bloquearCopyPaste(event)' : null"-->
                                        <!--:oncontextmenu="modoEstudiante ? 'return bloquearClickDerecho(event)' : null"-->
                                        <!--:onselectstart="modoEstudiante ? 'return bloquearSeleccion(event)' : null"-->
                                        <!--:ondragstart="modoEstudiante ? 'return bloquearArrastrar(event)' : null"-->
                                        :spellcheck="false"
                                        :autocomplete="off"
                                    ></textarea>

                                    <!-- Mostrar botón de descarga si hay documento adjunto y está en modo estudiante -->
                                    <div v-if="modoEstudiante && (caso.archivoUrl || caso.archivoId || caso.archivoNombre)" style="margin-top: 10px; padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;">
                                        <div style="display: flex; align-items: center; gap: 10px;">
                                            <i class="fas fa-file-pdf" style="color: #dc3545; font-size: 18px;"></i>
                                            <span style="font-weight: bold;">{{ caso.archivoNombre || 'Archivo adjunto' }}</span>
                                            <button @click="window.open(caso.archivoUrl, '_blank')" class="btn btn-primary" style="padding: 5px 10px;">
                                                Ver PDF
                                            </button>
                                        </div>
                                    </div>
                                                                             
                        <label style="position: absolute; left: 10px; bottom: 10px; cursor: pointer; z-index: 2;">
                            <input 
                                type="file" 
                                @change="(e) => { 
                                    console.log('File input changed, files:', e.target.files); 
                                    handleFileUpload(e, caso); 
                                }" 
                                accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                                style="display: none;"
                                id="file-upload"
                                :disabled="isUploading"
                            >
                            <span style="font-size: 24px;">📎</span>
                        </label>
                    </div>

                    <!-- Barra de progreso para la carga de archivos -->
                    <div v-if="isUploading" class="upload-progress-bar" style="margin-top: 10px;">
                        <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
                        <div class="progress-text">{{ uploadProgress }}%</div>
                    </div>

                    <div v-if="caso.archivoSubido" style="margin-top: 5px; font-size: 14px;">
                        Archivo subido: {{ caso.nombreArchivo }}
                        <button @click="eliminarArchivo(caso)" style="margin-left: 10px; padding: 2px 5px; font-size: 16px; background: none; border: none; color: red; cursor: pointer;" title="Eliminar archivo">🗑️</button>
                        </div>
                       
                    <!-- Área de respuesta para el profesor en modo plantilla -->
                     <button class="btn btn-danger" @click="eliminarCasoUso(index)" v-if="!modoEstudiante" :disabled="examen.bloqueado">
                        Eliminar Caso
                    </button> 
                </div>
            </div>

            <div class="card">
                <h2>Totales y Control</h2>
                
                <div class="totals">
                    <div>
                        <strong>Total de Preguntas:</strong> {{ totalPreguntas }}
                    </div>
                    <div>
                        <strong>Puntaje Total:</strong> {{ puntajeTotal }}
                    </div>
                </div>
                
                <div class="btn-group">
                    <button class="btn" @click="toggleBloqueo" :class="examen.bloqueado ? 'btn-warning' : 'btn-success'" v-if="!modoEstudiante">
                        {{ examen.bloqueado ? 'Desbloquear Edición' : 'Bloquear Edición' }}
                    </button>

                    <button @click="cambiarModo" class="btn" :class="{ 'btn-info': !modoEstudiante, 'btn-warning': modoEstudiante }" v-if="!modoEstudiante">
                    {{ modoEstudiante ? 'Volver a Modo Profesor' : 'Modo Estudiante' }}
                    </button>

                    <button 
                        @click="toggleProteccionCopyPaste" 
                        class="btn"
                        :class="proteccionesActivas ? 'btn-danger' : 'btn-success'"
                        v-if="modoEstudiante"
                    >
                        {{ proteccionesActivas ? '🔒 Copy-Paste: OFF' : '🔓 Copy-Paste: ON' }}
                    </button>

                    <button 
                    class="btn btn-success" 
                    @click="publicarExamenWeb" 
                    v-if="modoEstudiante"
                    :disabled="isPublishing"
                    >
                    {{ isPublishing ? 'Publicando...' : 'Publicar Examen Web' }}
                    </button>

                    <button 
                        @click="cambiarModoDesdePlantilla" 
                        class="btn btn-info"
                    >
                        Modo Profesor
                    </button>

                    <button 
                    class="btn btn-success" 
                    @click="submitPlantilla"
                    v-if="modoPlantillaProfesor && !modoEstudiante"
                    :disabled="isPublishing"
                    >
                    {{ isPublishing ? 'Publicando...' : 'Publicar Plantilla' }}
                    </button>

                    <button class="btn btn-secondary" @click="mostrarBusquedaExamenes">🔍 Buscar Exámenes</button>

                    <button class="btn btn-warning" @click="limpiarCacheExamen" v-if="!modoEstudiante">Limpiar Cache</button>

                </div>
                
                <div v-if="message" :class="'alert ' + messageType">
                    {{ message }}
                </div>
            </div>
            
            <div id="examen-pdf" style="display: none;">
                <div class="examen-container" style="font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; page-break-inside: avoid;">
                    <h1 style="text-align: center;">{{ examen.id }} - Examen</h1>
                    <p><strong>Fecha:</strong> {{ examen.fecha }}</p>
                    <p><strong>Profesor:</strong> {{ examen.profesor || '________________' }}</p>
                    <p><strong>Nombre del Alumno:</strong> {{ modoEstudiante ? examen.nombreAlumno : '________________' }}</p>
                    <p><strong>ID del Alumno:</strong> {{ modoEstudiante ? examen.idAlumno : '________________' }}</p>
                    
                    <div v-if="examen.preguntasMarcar.length > 0">
                        <h2 style="margin-top: 30px; border-bottom: 1px solid #ccc;">Preguntas para Marcar</h2>
                        <div v-for="pregunta in examen.preguntasMarcar" class="pregunta-pdf" style="margin-bottom: 20px;">
                            <p><strong>{{ pregunta.numero }}. ({{ pregunta.puntaje }} pts)</strong> {{ pregunta.texto }}</p>
                            <div v-for="(opcion, i) in pregunta.opciones" class="opcion-pdf" style="margin-left: 20px;">
                                <p>{{ pregunta.respuestaSeleccionada === i ? '●' : '○' }} {{ opcion.texto }}</p>
                            </div>
                        </div>
                    </div>
                    
                    <div v-if="examen.preguntasLibres.length > 0">
                        <h2 style="margin-top: 30px; border-bottom: 1px solid #ccc;">Preguntas Libres</h2>
                        <div v-for="pregunta in examen.preguntasLibres" class="pregunta-pdf" style="margin-bottom: 20px;">
                            <p><strong>{{ pregunta.numero }}. ({{ pregunta.puntaje }} pts)</strong> {{ pregunta.texto }}</p>
                            <div class="respuesta-espacio" style="border: 1px solid #ddd; padding: 10px; min-height: 100px; margin-top: 10px; text-align: justify; white-space: pre-wrap; page-break-inside: avoid;">
                                {{ pregunta.respuestaAlumno || '' }}
                            </div>
                        </div>
                    </div>

                    <!-- Sección de Casos de Uso para el PDF -->
                    <div v-if="examen.casosUso.length > 0">
                        <h2 style="margin-top: 30px; border-bottom: 1px solid #ccc;">Casos de Uso</h2>
                        <div v-for="caso in examen.casosUso" class="pregunta-pdf" style="margin-bottom: 20px;">
                            <p><strong>{{ caso.numero }}. ({{ caso.puntaje }} pts)</strong></p>
                            <p><strong>Descripción:</strong> {{ caso.descripcion }}</p>
                            <p><strong>Pregunta:</strong> {{ caso.pregunta }}</p>
                            <div class="respuesta-espacio" style="border: 1px solid #ddd; padding: 10px; min-height: 100px; margin-top: 10px; text-align: justify; white-space: pre-wrap; page-break-inside: avoid;">
                                {{ caso.respuestaAlumno || '' }}
                            </div>
                            <p v-if="caso.archivoSubido"><strong>Archivo adjunto:</strong> {{ caso.nombreArchivo }}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- MODAL PLAYGROUND GENERACIÓN DE IMÁGENES -->
            <div v-if="mostrarPlayground" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;">
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 30px; border-radius: 10px; max-width: 800px; width: 90%; max-height: 90%; overflow-y: auto;">
                    
                    <h2>🎨 Playground - Generar Imagen IA</h2>
                    
                    <!-- Selector de IA -->
                    <div class="form-group">
                        <label>Modelo de IA para imágenes:</label>
                        <select v-model="playgroundConfig.modelo" class="form-control">
                            <!-- Modelos para generación de HTML/SVG -->
                            <option value="gpt-4-1">ChatGPT 4.1 (OpenAI)</option>
                            <option value="gpt-4o">ChatGPT 4o (OpenAI)</option>
                            <option value="gemini-2-5-pro">Gemini 2.5 Pro (Google)</option>
                            <option value="gemini-2-0-flash">Gemini 2.0 Flash (Google)</option>
                            <option value="claude-sonnet-4">Claude Sonnet 4 (Anthropic)</option>
                            <option value="claude-3-5-sonnet">Claude 3.5 Sonnet (Anthropic)</option>
                            <option value="deepseek-v3">DeepSeek V3</option>
                            <option value="deepseek-chat">DeepSeek Chat</option>

                            <!-- Modelos especializados en generación directa de imágenes -->
                            <option value="flux-1-pro">🎯 Flux.1 Pro - Técnico</option>
                            <option value="kling-ai">🎓 Kling AI - Educativo</option>
                            <option value="ideogram">📊 Ideogram - Texto y Diagramas</option>
                            <option value="dall-e-3">🔧 DALL-E 3 - Confiable</option>
                            <option value="leonardo-ai">🎨 Leonardo AI - Profesional</option>
                        </select>
                    </div>
                    
                    <!-- Campo de texto para prompt -->
                    <div class="form-group">
                        <label>Describe la imagen que necesitas:</label>
                        <textarea v-model="playgroundConfig.prompt" rows="4" class="form-control" 
                                placeholder="Ejemplo: Un triángulo rectángulo con lados de 3cm y 4cm, con medidas marcadas y ángulo recto destacado"></textarea>
                    </div>
                    
                    <!-- Botones de acción -->
                    <div style="text-align: center; margin: 20px 0;">
                        <button class="btn btn-primary" @click="generarImagenIA" :disabled="generandoImagen">
                            {{ generandoImagen ? 'Generando...' : '🎨 Generar Imagen' }}
                        </button>
                    </div>
                    
                    <!-- Preview de imagen generada -->
                    <div v-if="imagenGenerada" style="text-align: center; margin: 20px 0;">
                        <h4>Imagen generada:</h4>
                        <img :src="imagenGenerada" style="max-width: 100%; max-height: 400px; border: 1px solid #ddd; border-radius: 5px;">
                    </div>
                    
                    <!-- Botones finales -->
                    <div style="text-align: center; margin-top: 20px;">
                        <button v-if="imagenGenerada" class="btn btn-success" @click="usarImagenGenerada" style="margin-right: 10px;">
                            ✅ Usar esta Imagen
                        </button>
                        <button v-if="imagenGenerada" class="btn btn-warning" @click="regenerarImagen" style="margin-right: 10px;">
                            🔄 Regenerar
                        </button>
                        <button class="btn btn-secondary" @click="cerrarPlayground">
                            ❌ Cancelar
                        </button>
                    </div>
                    
                </div>
            </div>
        </div> <!-- Cierre de <div class="profesor-component-wrapper"> -->

    <!-- =============================================
     MODAL PARA SELECTOR DE ARCHIVOS APPWRITE
     ============================================= -->

    <!-- REEMPLAZAR EL MODAL COMPLETO POR ESTE -->
    <div id="modalSelectorAppwrite" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 9999; align-items: center; justify-content: center;" onclick="cerrarModalSelector(event)">
    <div style="background-color: rgb(255,255,255); border: 3px solid black; border-radius: 8px; width: 90%; max-width: 800px; max-height: 80vh; display: flex; flex-direction: column; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8); padding: 0;">
        <div style="padding: 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; background: white !important;">
            <h3 style="margin: 0; color: black;">📁 Seleccionar Archivo del Repositorio</h3>
            <button onclick="cerrarModalSelector()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #666;">&times;</button>
        </div>
        
        <div style="padding: 20px; overflow-y: auto; flex-grow: 1; background: white !important; min-height: 200px;">
            <div id="modal-loading" style="display: none; text-align: center;">
                <p>⏳ Cargando archivos...</p>
            </div>
            
            <div id="modal-archivos" style="display: none;">
                <!-- Los archivos se cargarán aquí -->
            </div>
            
            <div id="modal-vacio" style="display: none; text-align: center;">
                <p>📂 No hay archivos disponibles</p>
            </div>
        </div>
        
        <div style="padding: 20px; border-top: 1px solid #eee; display: flex; justify-content: flex-end; gap: 10px; background: white !important;">
            <button onclick="cerrarModalSelector()" style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;">Cancelar</button>
            <button id="btn-confirmar" onclick="confirmarSeleccionArchivo()" disabled style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                ✅ Seleccionar Archivo
            </button>
        </div>
    </div>
</div>
<!-- MODAL DE RECOMENDACIONES INLINE -->
<!-- MODAL DE RECOMENDACIONES COMPLETO -->
<div v-if="modalRecomendaciones.visible" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 20px;" @click="cerrarModalRecomendaciones">
    <div @click.stop style="background: white; border-radius: 15px; max-width: 800px; width: 95%; max-height: 90vh; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 25px 50px rgba(0,0,0,0.25);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <i :class="modalRecomendaciones.tipoPregunta === 'opcion_multiple' ? 'fas fa-list-ul' : modalRecomendaciones.tipoPregunta === 'abierta' ? 'fas fa-edit' : 'fas fa-briefcase'" style="font-size: 2.5rem; opacity: 0.9;"></i>
                <div>
                    <h3 style="margin: 0; font-size: 1.5rem; font-weight: 600;">Modelos Recomendados</h3>
                    <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 0.95rem;">
                        {{ modalRecomendaciones.tipoPregunta === 'opcion_multiple' ? 'Para Preguntas de Opción Múltiple' : 
                           modalRecomendaciones.tipoPregunta === 'abierta' ? 'Para Preguntas de Desarrollo' : 
                           'Para Casos de Uso' }}
                    </p>
                </div>
            </div>
            <button @click="cerrarModalRecomendaciones" style="background: rgba(255,255,255,0.2); border: none; color: white; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">
                ×
            </button>
        </div>

        <!-- Content -->
        <div style="flex: 1; overflow-y: auto; padding: 24px;">
            
            <!-- Loading -->
            <div v-if="modalRecomendaciones.cargando" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; text-align: center;">
                <div style="width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px;"></div>
                <p>Cargando recomendaciones...</p>
            </div>

            <!-- Error -->
            <div v-else-if="modalRecomendaciones.error" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; text-align: center;">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #e74c3c; margin-bottom: 15px;"></i>
                <p>{{ modalRecomendaciones.error }}</p>
                <button @click="cargarRecomendaciones" style="background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; margin-top: 15px;">
                    Reintentar
                </button>
            </div>

            <!-- Recomendaciones -->
            <div v-else-if="modalRecomendaciones.recomendaciones">
                
                <!-- Modelos Recomendados -->
                <div v-if="modalRecomendaciones.recomendaciones.recomendados?.length" style="margin-bottom: 32px;">
                    <h4 style="display: flex; align-items: center; gap: 10px; font-size: 1.2rem; font-weight: 600; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #27ae60; color: #27ae60;">
                        <i class="fas fa-star"></i>
                        Altamente Recomendados
                    </h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 16px;">
                        <div v-for="modelo in modalRecomendaciones.recomendaciones.recomendados" :key="modelo.modelo" 
                             @click="seleccionarModeloDesdeModal(modelo.modelo)"
                             style="border: 2px solid #27ae60; border-radius: 12px; padding: 20px; cursor: pointer; background: linear-gradient(135deg, #ffffff 0%, #f8fff9 100%); transition: all 0.2s ease; position: relative;"
                             @mouseover="($event) => { $event.target.style.transform = 'translateY(-2px)'; $event.target.style.boxShadow = '0 8px 25px rgba(39, 174, 96, 0.2)' }"
                             @mouseleave="($event) => { $event.target.style.transform = 'translateY(0)'; $event.target.style.boxShadow = 'none' }"
                             :style="!modelo.disponible ? 'opacity: 0.6; cursor: not-allowed;' : ''">
                            
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                                <h5 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #2c3e50;">{{ modelo.nombre_display }}</h5>
                                <div style="display: flex; gap: 2px;">
                                    <i v-for="n in 5" :key="n" class="fas fa-star" :style="n <= modelo.puntuacion ? 'color: #f1c40f;' : 'color: #ddd;'" style="font-size: 0.9rem;"></i>
                                </div>
                            </div>
                            
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <span :style="'padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: 500; display: flex; align-items: center; gap: 6px;' + 
                                            (modelo.velocidad === 'rapida' ? 'background: #d4edda; color: #155724;' : 
                                             modelo.velocidad === 'media' ? 'background: #fff3cd; color: #856404;' : 
                                             'background: #f8d7da; color: #721c24;')">
                                    <i class="fas fa-tachometer-alt"></i>
                                    {{ modelo.velocidad === 'rapida' ? 'Rápido' : modelo.velocidad === 'media' ? 'Medio' : 'Lento' }}
                                </span>
                                <span style="font-size: 0.85rem; color: #6c757d;">{{ modelo.tiempo_estimado }}</span>
                            </div>

                            <p style="font-size: 0.9rem; color: #495057; margin: 0 0 10px 0; line-height: 1.4;">{{ modelo.ideal_para }}</p>
                            
                            <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 15px;">
                                <span v-for="fortaleza in modelo.fortalezas.slice(0, 3)" :key="fortaleza" 
                                      style="background: #d4edda; color: #155724; padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 500;">
                                    {{ fortaleza }}
                                </span>
                            </div>

                            <div v-if="modelo.nota" style="background: #e7f3ff; border: 1px solid #b3d9ff; border-radius: 8px; padding: 10px; font-size: 0.85rem; color: #0066cc; display: flex; align-items: flex-start; gap: 8px; margin-top: 12px;">
                                <i class="fas fa-lightbulb" style="margin-top: 2px; flex-shrink: 0;"></i>
                                {{ modelo.nota }}
                            </div>

                            <div v-if="!modelo.disponible" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255,255,255,0.8); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; color: #6c757d; font-weight: 500; border-radius: 12px;">
                                <i class="fas fa-lock" style="font-size: 1.5rem;"></i>
                                <span>No disponible</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Modelos Aceptables -->
                <div v-if="modalRecomendaciones.recomendaciones.aceptables?.length" style="margin-bottom: 32px;">
                    <h4 style="display: flex; align-items: center; gap: 10px; font-size: 1.2rem; font-weight: 600; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #f39c12; color: #f39c12;">
                        <i class="fas fa-check-circle"></i>
                        Alternativas Aceptables
                    </h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;">
                        <div v-for="modelo in modalRecomendaciones.recomendaciones.aceptables" :key="modelo.modelo" 
                             @click="seleccionarModeloDesdeModal(modelo.modelo)"
                             style="border: 2px solid #f39c12; border-radius: 12px; padding: 20px; cursor: pointer; background: linear-gradient(135deg, #ffffff 0%, #fffcf5 100%); transition: all 0.2s ease; position: relative;"
                             @mouseover="(e) => { if(e && e.target) { e.target.style.transform = 'translateY(-2px)'; e.target.style.boxShadow = '0 8px 25px rgba(243, 156, 18, 0.15)'; } }"
                             @mouseleave="(e) => { if(e && e.target) { e.target.style.transform = 'translateY(0)'; e.target.style.boxShadow = 'none'; } }"
                             :style="!modelo.disponible ? 'opacity: 0.6; cursor: not-allowed;' : ''">
                            
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                                <h5 style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #2c3e50;">{{ modelo.nombre_display }}</h5>
                                <div style="display: flex; gap: 2px;">
                                    <i v-for="n in 5" :key="n" class="fas fa-star" :style="n <= modelo.puntuacion ? 'color: #f1c40f;' : 'color: #ddd;'" style="font-size: 0.9rem;"></i>
                                </div>
                            </div>
                            
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <span :style="'padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: 500; display: flex; align-items: center; gap: 6px;' + 
                                            (modelo.velocidad === 'rapida' ? 'background: #d4edda; color: #155724;' : 
                                             modelo.velocidad === 'media' ? 'background: #fff3cd; color: #856404;' : 
                                             'background: #f8d7da; color: #721c24;')">
                                    <i class="fas fa-tachometer-alt"></i>
                                    {{ modelo.velocidad === 'rapida' ? 'Rápido' : modelo.velocidad === 'media' ? 'Medio' : 'Lento' }}
                                </span>
                                <span style="font-size: 0.85rem; color: #6c757d;">{{ modelo.tiempo_estimado }}</span>
                            </div>

                            <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 15px;">
                                <span v-for="fortaleza in modelo.fortalezas.slice(0, 2)" :key="fortaleza" 
                                      style="background: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 500;">
                                    {{ fortaleza }}
                                </span>
                            </div>

                            <div v-if="modelo.limitaciones" style="margin-top: 12px;">
                                <p style="font-size: 0.85rem; color: #856404; margin: 0; display: flex; align-items: flex-start; gap: 8px;">
                                    <i class="fas fa-info-circle" style="margin-top: 2px; flex-shrink: 0;"></i>
                                    {{ modelo.limitaciones.join(', ') }}
                                </p>
                            </div>

                            <div v-if="!modelo.disponible" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255,255,255,0.8); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; color: #6c757d; font-weight: 500; border-radius: 12px;">
                                <i class="fas fa-lock" style="font-size: 1.5rem;"></i>
                                <span>No disponible</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- No Recomendados (colapsible) -->
                <div v-if="modalRecomendaciones.recomendaciones.no_recomendados?.length">
                    <h4 @click="modalRecomendaciones.mostrarNoRecomendados = !modalRecomendaciones.mostrarNoRecomendados" 
                        style="display: flex; align-items: center; gap: 10px; font-size: 1.2rem; font-weight: 600; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #e74c3c; color: #e74c3c; cursor: pointer; transition: all 0.2s ease;">
                        <i class="fas fa-exclamation-triangle"></i>
                        No Recomendados para este tipo
                        <i class="fas fa-chevron-down" :style="modalRecomendaciones.mostrarNoRecomendados ? 'transform: rotate(180deg);' : ''" style="margin-left: auto; transition: transform 0.2s ease;"></i>
                    </h4>
                    
                    <div v-if="modalRecomendaciones.mostrarNoRecomendados" style="background: #fff5f5; border: 1px solid #feb2b2; border-radius: 8px; padding: 16px;">
                        <div v-for="modelo in modalRecomendaciones.recomendaciones.no_recomendados" :key="modelo.modelo" 
                             style="padding: 12px 0; border-bottom: 1px solid #feb2b2;">
                            <div style="font-weight: 600; color: #e53e3e; margin-bottom: 4px;">{{ modelo.modelo }}</div>
                            <div style="font-size: 0.9rem; color: #718096; margin-bottom: 8px;">{{ modelo.razon }}</div>
                            <div v-if="modelo.alternativa" style="font-size: 0.85rem; color: #4a5568;">
                                Usa mejor: 
                                <button @click="seleccionarModeloDesdeModal(modelo.alternativa)" 
                                        style="background: #667eea; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; margin-left: 4px;">
                                    {{ modelo.alternativa }}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div style="background: #f8f9fa; padding: 20px; border-top: 1px solid #e9ecef; display: flex; justify-content: space-between; align-items: center; gap: 20px;">
            <div style="display: flex; gap: 12px;">
                <button @click="usarPrimerRecomendado" style="background: #667eea; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 500; display: flex; align-items: center; gap: 8px; transition: all 0.2s ease;"
                        @mouseover="$event.target.style.background = '#5a6fd8'; $event.target.style.transform = 'translateY(-1px)'"
                        @mouseleave="$event.target.style.background = '#667eea'; $event.target.style.transform = 'translateY(0)'">
                    <i class="fas fa-magic"></i>
                    Usar Recomendado
                </button>
                <button @click="cerrarModalRecomendaciones" style="background: #6c757d; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 500; transition: all 0.2s ease;"
                        @mouseover="$event.target.style.background = '#5a6268'"
                        @mouseleave="event.target.style.background = '#6c757d'">
                    Cerrar sin cambios
                </button>
            </div>
            <div style="display: flex; align-items: center;">
                <label style="display: flex; align-items: center; cursor: pointer; font-size: 0.9rem; color: #6c757d;">
                    <input type="checkbox" v-model="modalRecomendaciones.noMostrarDeNuevo" style="margin-right: 8px;">
                    No mostrar esta ayuda de nuevo
                </label>
            </div>
        </div>
    </div>
</div>


<style>
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
<style>
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* ✅ ESTILOS PHET CON !IMPORTANT */
.modal-recursos-overlay {
    position: fixed !important; 
    top: 0 !important; 
    left: 0 !important; 
    right: 0 !important; 
    bottom: 0 !important;
    background: rgba(0,0,0,0.7) !important; 
    z-index: 9999 !important;
    display: flex !important; 
    align-items: center !important; 
    justify-content: center !important;
}
.modal-recursos-container {
    background: white !important; 
    border-radius: 12px !important; 
    max-width: 800px !important; 
    width: 90% !important;
    max-height: 80vh !important; 
    overflow-y: auto !important; 
    padding: 0 !important;
}
.recursos-header {
    padding: 20px !important; 
    border-bottom: 1px solid #ddd !important;
    display: flex !important; 
    justify-content: space-between !important; 
    align-items: center !important;
}
.recursos-tabs { 
    display: flex !important; 
    border-bottom: 1px solid #ddd !important; 
}
.recursos-tabs button {
    padding: 12px 20px !important; 
    border: none !important; 
    background: #f8f9fa !important;
    cursor: pointer !important; 
    border-bottom: 3px solid transparent !important;
}
.recursos-tabs button.active { 
    background: white !important; 
    border-bottom-color: #007bff !important; 
    color: #007bff !important; 
}
.phet-filtros { 
    padding: 15px 20px !important; 
    border-bottom: 1px solid #eee !important; 
}
.simulaciones-grid {
    display: grid !important; 
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)) !important;
    gap: 15px !important; 
    padding: 20px !important;
}
.simulacion-card {
    border: 2px solid #e9ecef !important; 
    border-radius: 8px !important; 
    padding: 15px !important;
    cursor: pointer !important; 
    transition: all 0.2s !important;
}
.simulacion-card:hover { border-color: #007bff !important; }
.simulacion-card.selected { 
    border-color: #28a745 !important; 
    background: #f8fff9 !important; 
}
.sim-icon { 
    font-size: 2rem !important; 
    text-align: center !important; 
    margin-bottom: 10px !important; 
}
.sim-info h4 { 
    margin: 0 0 8px 0 !important; 
    font-size: 1.1rem !important; 
}
.sim-info p { 
    margin: 0 0 8px 0 !important; 
    color: #666 !important; 
    font-size: 0.9rem !important; 
}
.sim-materia { 
    background: #e9ecef !important; 
    padding: 4px 8px !important; 
    border-radius: 12px !important; 
    font-size: 0.8rem !important; 
    color: #495057 !important; 
}
.phet-acciones { 
    padding: 20px !important; 
    border-top: 1px solid #ddd !important; 
    text-align: center !important; 
}
.recursos-footer { 
    padding: 15px 20px !important; 
    border-top: 1px solid #ddd !important; 
    text-align: right !important; 
}
.close-btn {
    background: none !important; 
    border: none !important; 
    font-size: 24px !important; 
    cursor: pointer !important;
    color: #6c757d !important; 
    width: 30px !important; 
    height: 30px !important;
}
</style>

    `,
    setup() {
        const examen = reactive({
            id: '',
            nombreExamen: '',
            tipoExamen: 'Evaluación', // Valor predeterminado opcional
            fecha: new Date().toISOString().split('T')[0],
            profesor: '',
            profesorId: '',
            nombreAlumno: '',
            idAlumno: '',
            bloqueado: false,
            preguntasMarcar: [],
            preguntasLibres: [],
            casosUso: []
        });

            // Generar ID único si no existe
            if (!examen.id) {
                examen.id = Math.floor(100000 + Math.random() * 900000).toString();
            }

        const activeTab = ref('marcar');
        const message = ref('');
        const messageType = ref('info');
        const modoEstudiante = ref(false);
        const modoPlantillaProfesor = ref(false); // ✅ INICIA DESACTIVADO
        const isPublishing = ref(false);
        const publicUrl = ref('');
        const modeloRespuestas = ref('gemini-1-5-pro');
        // AGREGAR ESTAS NUEVAS VARIABLES AQUÍ
        const mostrarPlayground = ref(false);
        const generandoImagen = ref(false);
        const imagenGenerada = ref(null);
        const preguntaActual = ref(null);
        const tipoActual = ref(null);


        const playgroundConfig = ref({
            modelo: 'deepseek-v3',
            prompt: ''
        });

        const selectorAppwrite = ref({
            cargando: false,
            archivos: [],
            error: null,
            archivoSeleccionado: null,
            preguntaActual: null,
            tipoActual: null,
            mostrarModal: false
        });

        // ======= VARIABLES PARA MODAL DE RECOMENDACIONES =======
        const modalRecomendaciones = ref({
            visible: false,
            tipoPregunta: 'opcion_multiple',
            selectorActual: null,
            cargando: false,
            error: null,
            recomendaciones: null,
            mostrarNoRecomendados: false,
            noMostrarDeNuevo: false
        });

        const totalPreguntas = computed(() => {
            return examen.preguntasMarcar.length + examen.preguntasLibres.length + examen.casosUso.length;
        });

        const puntajeTotal = computed(() => {
            let total = 0;
            examen.preguntasMarcar.forEach(p => total += parseFloat(p.puntaje) || 0);
            examen.preguntasLibres.forEach(p => total += parseFloat(p.puntaje) || 0);
            examen.casosUso.forEach(c => total += parseFloat(c.puntaje) || 0);
            return total.toFixed(1);
        });

        const OPENROUTER_CONFIG = {
            apiKey: 'OPENROUTER_API_KEY',
            baseUrl: 'https://openrouter.ai/api/v1',
            model: 'deepseek/deepseek-chat'
        };

        function agregarPreguntaMarcar() {
            examen.preguntasMarcar.push({
                numero: examen.preguntasMarcar.length + 1,
                texto: '',
                puntaje: 1,
                opciones: [
                    { texto: '' },
                    { texto: '' }
                ],
                respuestaSeleccionada: null
            });
        }

        function eliminarPreguntaMarcar(index) {
            examen.preguntasMarcar.splice(index, 1);
            // Reordenar números
            examen.preguntasMarcar.forEach((p, i) => p.numero = i + 1);
        }

        function agregarOpcion(pregunta) {
            pregunta.opciones.push({ texto: '' });
        }

        function eliminarOpcion(pregunta, index) {
            pregunta.opciones.splice(index, 1);
        }

        function agregarPreguntaLibre() {
            examen.preguntasLibres.push({
                numero: examen.preguntasLibres.length + 1,
                texto: '',
                puntaje: 1,
                respuestaAlumno: '',
                archivoNombre: '', // <-- AÑADIR ESTA LÍNEA
                archivoUrl: ''     // <-- AÑADIR ESTA LÍNEA
            });
        }

        function eliminarPreguntaLibre(index) {
            examen.preguntasLibres.splice(index, 1);
            // Reordenar números
            examen.preguntasLibres.forEach((p, i) => p.numero = i + 1);
        }

        function agregarCasoUso() {
            examen.casosUso.push({
                numero: examen.casosUso.length + 1,
                descripcion: '',
                pregunta: '',
                puntaje: 1,
                respuestaAlumno: '',
                archivoSubido: false,
                nombreArchivo: '',
                urlArchivo: '',
                fileId: '',
                archivo: '',
                archivoUrl: ''     // <-- AÑADIR ESTA LÍNEA
            });
        }

        function eliminarCasoUso(index) {
            examen.casosUso.splice(index, 1);
            // Reordenar números
            examen.casosUso.forEach((c, i) => c.numero = i + 1);
        }

        /*function toggleProteccionCopyPaste() {
            proteccionesActivas = !proteccionesActivas;
            
            const textareas = document.querySelectorAll('textarea[placeholder*="Escribe tu respuesta"]');
            
            if (!proteccionesActivas) {
                // Remover todos los event listeners
                textareas.forEach(textarea => {
                    textarea.removeEventListener('keydown', bloquearCopyPaste);
                    textarea.removeEventListener('contextmenu', bloquearClickDerecho);
                    textarea.removeEventListener('selectstart', bloquearSeleccion);
                    textarea.removeEventListener('dragstart', bloquearArrastrar);
                    textarea.classList.remove('protected-textarea');
                });
            } else {
                // Aplicar protecciones
                aplicarProteccionDinamica();
            }
        }*/

        async function subirArchivoAnexo(event, item, tipo) {
            const file = event.target.files[0];
            if (!file) return;
            
            try {
                message.value = 'Subiendo archivo adjunto...';
                messageType.value = 'info';
                
                const formData = new FormData();
                formData.append('email', currentUserEmail);  // ← AGREGAR ESTA LÍNEA email
                formData.append('file', file);
                formData.append('tipo', tipo);
                formData.append('numero', item.numero);
                
                const response = await fetch('http://127.0.0.1:5000/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('Error al subir archivo');
                }
                
                const result = await response.json();
                
                // Actualizar el item con la info del archivo
                item.archivoNombre = file.name;
                item.archivoUrl = result.url;
                
                message.value = 'Archivo adjunto subido correctamente';
                messageType.value = 'success';
                
            } catch (error) {
                message.value = 'Error al subir archivo adjunto: ' + error.message;
                messageType.value = 'error';
                console.error('Error:', error);
            }
            
            setTimeout(() => { message.value = ''; }, 3000);
        }
        
        function eliminarArchivoAnexo(item) {
            item.archivoNombre = '';
            item.archivoUrl = '';
            message.value = 'Archivo adjunto eliminado';
            messageType.value = 'info';
            setTimeout(() => { message.value = ''; }, 2000);
        }

        // FUNCIONES DEL PLAYGROUND
        function abrirPlayground(item, tipo) {
            preguntaActual.value = item;     // CORRECTO: usar .value
            tipoActual.value = tipo;         // CORRECTO: usar .value
            mostrarPlayground.value = true;
            playgroundConfig.value.prompt = '';
            imagenGenerada.value = null;
        }

        function cerrarPlayground() {
            mostrarPlayground.value = false;
            preguntaActual.value = null;     // AGREGAR .value
            tipoActual.value = null;         // AGREGAR .value
            imagenGenerada.value = null;
            generandoImagen.value = false;
        }

        function abrirRecursosEducativos(item, tipo) {
            window.open('http://165.227.186.166:8080', '_blank');
        }

        // =============================================
        // NUEVOS MÉTODOS PARA SELECTOR APPWRITE
        // =============================================

        /**
         * Abrir selector de archivos Appwrite
         */

        function abrirSelectorAppwrite(item, tipo) {
            try {
                // Guardar referencia de la pregunta/caso actual
                selectorAppwrite.value.preguntaActual = item;
                selectorAppwrite.value.tipoActual = tipo;
                selectorAppwrite.value.archivoSeleccionado = null;
                selectorAppwrite.value.error = null;
                selectorAppwrite.value.cargando = true;

                window.itemActualModal = item;

                mostrarModalSelector(); // ← CAMBIAR A ESTO
        
                // Cargar archivos del bucket
                cargarArchivosAppwrite();
        
            } catch (error) {
                console.error('Error abriendo selector:', error);
                selectorAppwrite.value.error = 'Error al abrir el selector de archivos';
            }
        }

        // AGREGAR FUNCIÓN
        function cerrarSelectorAppwrite() {
            selectorAppwrite.value.mostrarModal = false;
        }

        /**
        * Cargar archivos del bucket Appwrite
        */
        async function cargarArchivosAppwrite() {
            try {
                console.log("[DEBUG] Iniciando carga de archivos");
                selectorAppwrite.value.cargando = true;
                selectorAppwrite.value.error = null;
        
                const response = await fetch('http://127.0.0.1:5000/api/listar-archivos-bucket', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email: currentUserEmail })  // ← AGREGAR ESTA LÍNEA email
                });

                console.log("[DEBUG] Response status:", response.status);
                console.log("[DEBUG] Response ok:", response.ok);
        
                const data = await response.json();
                console.log("[DEBUG] Data recibida:", data);

        
                if (data.success) {
                    console.log("[DEBUG] Asignando archivos:", data.archivos.length);
                    selectorAppwrite.value.archivos = data.archivos;

                    // AGREGAR: Mostrar archivos en el modal
                    mostrarArchivosEnModal(data.archivos);
                } else {
                    throw new Error(data.error || 'Error cargando archivos');
                }
        
            } catch (error) {
                console.error('Error cargando archivos:', error);
                selectorAppwrite.value.error = 'Error al cargar los archivos del repositorio';
                selectorAppwrite.value.archivos = [];
                mostrarErrorEnModal();
            } finally {
                selectorAppwrite.value.cargando = false;
            }
        }

        /**
        * Cargar el modal
        */

        function cargarArchivosModal() {
            document.getElementById('modal-loading').style.display = 'block';
            document.getElementById('modal-archivos').style.display = 'none';
            document.getElementById('modal-vacio').style.display = 'none';
            
            // Usar la función existente
            cargarArchivosAppwrite();
        }

        // AGREGAR nueva función
        function mostrarArchivosEnModal(archivos) {
            document.getElementById('modal-loading').style.display = 'none';
            
            if (archivos.length > 0) {
                const modalArchivos = document.getElementById('modal-archivos');
                modalArchivos.innerHTML = '';
                
                archivos.forEach(archivo => {
                    const archivoDiv = document.createElement('div');
                    archivoDiv.className = 'archivo-card';
                    archivoDiv.onclick = () => window.seleccionarArchivoModal(archivo);
                    
                    archivoDiv.innerHTML = `
                        <div class="archivo-info">
                            <div class="archivo-icono">
                                ${archivo.mimeType.includes('pdf') ? '📄' : 
                                archivo.mimeType.includes('image') ? '🖼️' : 
                                archivo.mimeType.includes('word') ? '📝' : '📎'}
                            </div>
                            <div class="archivo-detalles">
                                <p class="archivo-nombre">${archivo.name}</p>
                                <p class="archivo-tamaño">${formatearTamaño(archivo.sizeOriginal)}</p>
                                <p class="archivo-fecha">${formatearFecha(archivo.$createdAt)}</p>
                            </div>
                        </div>
                    `;
                    
                    modalArchivos.appendChild(archivoDiv);
                });
                
                modalArchivos.style.display = 'block';
                document.getElementById('modal-vacio').style.display = 'none';
            } else {
                document.getElementById('modal-vacio').style.display = 'block';
                document.getElementById('modal-archivos').style.display = 'none';
            }
        }

        // AGREGAR nueva función
        function mostrarErrorEnModal() {
            document.getElementById('modal-loading').style.display = 'none';
            document.getElementById('modal-vacio').style.display = 'block';
            document.getElementById('modal-archivos').style.display = 'none';
        }
        
        // AGREGAR nueva función
        let archivoSeleccionadoModal = null;
        
        function seleccionarArchivoModal(archivo) {
            // Quitar selección anterior
            document.querySelectorAll('.archivo-card').forEach(card => {
                card.classList.remove('selected');
            });
            
            // Agregar selección actual
            event.currentTarget.classList.add('selected');
            archivoSeleccionadoModal = archivo;
            
            // Habilitar botón confirmar
            document.getElementById('btn-confirmar').disabled = false;
        }

        // AGREGAR nueva función
        function confirmarSeleccionArchivo() {
            if (!archivoSeleccionadoModal) {
                alert('Por favor selecciona un archivo');
                return;
            }
        
            const item = selectorAppwrite.value.preguntaActual;
            
            // Guardar información del archivo
            item.archivoId = archivoSeleccionadoModal.$id;
            //item.archivoNombre = archivoSeleccionadoModal.name; ----------CAMBIO DE NOMBRE ARCHIVO
            item.archivoUrl = generarUrlDescarga(archivoSeleccionadoModal.$id);
            item.archivoTamaño = archivoSeleccionadoModal.sizeOriginal;
            item.archivoTipo = archivoSeleccionadoModal.mimeType;

            //=========INICIA CAMBIO MODIFICAR NOMBRE ARCHIVO=======
            // Obtener extensión del archivo original
            const extension = archivoSeleccionadoModal.name.split('.').pop();
            // Generar nombre automático: ID_Examen + Tipo + Número
            const tipoPrefix = selectorAppwrite.value.tipoActual === 'libres' ? 'P' : 'C';
            item.archivoNombre = `${examen.id}_${tipoPrefix}${item.numero}.${extension}`;
            //=========FIN CAMBIO====================================
        
            // Cerrar modal
            cerrarModalSelector();
            
            console.log('Archivo adjuntado correctamente');
        }

        /**
        * Seleccionar un archivo
        */
        function seleccionarArchivo(archivo) {
            selectorAppwrite.value.archivoSeleccionado = archivo.$id;
        }

        /**
        * Confirmar selección de archivo
        */
        async function confirmarSeleccion() {
            try {
                if (!selectorAppwrite.value.archivoSeleccionado) {
                    alert('Por favor selecciona un archivo');
                    return;
                }
        
                // Encontrar el archivo seleccionado
                const archivoSeleccionado = selectorAppwrite.value.archivos.find(
                    archivo => archivo.$id === selectorAppwrite.value.archivoSeleccionado
                );
        
                if (!archivoSeleccionado) {
                    throw new Error('Archivo no encontrado');
                }
        
                // Asignar archivo a la pregunta/caso
                const item = selectorAppwrite.value.preguntaActual;
        
                // Guardar información del archivo en el item
                item.archivoId = archivoSeleccionado.$id;
                item.archivoNombre = archivoSeleccionado.name;
                item.archivoUrl = generarUrlDescarga(archivoSeleccionado.$id);
                console.log("URL generada:", item.archivoUrl); // ← AGREGAR ESTA LÍNEA
                item.archivoTamaño = archivoSeleccionado.sizeOriginal;
                item.archivoTipo = archivoSeleccionado.mimeType;
        
                // Cerrar modal
                selectorAppwrite.value.mostrarModal = false;  // CAMBIAR ESTO
               
        
                // Mostrar confirmación
                mostrarNotificacion('Archivo adjuntado correctamente', 'success');
        
            } catch (error) {
                console.error('Error confirmando selección:', error);
                alert('Error al seleccionar el archivo: ' + error.message);
            }
        }

        /**
        * Generar URL de descarga para Appwrite
        */
        function generarUrlDescarga(fileId) {
            const projectId = '67e565df001722171560'; // ID real del proyecto
            const bucketId = '67e579bd0018f15c73c3'; // ID real del bucket
            return `https://fra.cloud.appwrite.io/v1/storage/buckets/${bucketId}/files/${fileId}/view?project=${projectId}`;
        }

        /**
        * Formatear tamaño de archivo
        */
        function formatearTamaño(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        /**
        * Formatear fecha
        */
        function formatearFecha(fechaISO) {
            const fecha = new Date(fechaISO);
            return fecha.toLocaleDateString('es-ES') + ' ' + fecha.toLocaleTimeString('es-ES', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        /**
        * Mostrar notificación
        */
        function mostrarNotificacion(mensaje, tipo = 'info') {
            // Implementar según tu sistema de notificaciones
            // Ejemplo con toast o alert básico:
            console.log(`[${tipo.toUpperCase()}] ${mensaje}`);
            
            // Si usas Bootstrap toast:
            // mostrarToast(mensaje, tipo);
            
            // Si usas SweetAlert:
            // Swal.fire(mensaje, '', tipo);
        }

        async function generarImagenIA() {
            if (!playgroundConfig.value.prompt.trim()) {
                message.value = 'Por favor describe la imagen que necesitas';
                messageType.value = 'error';
                return;
            }
            
            try {
                generandoImagen.value = true;
                
                const response = await fetch('http://127.0.0.1:5000/api/generar-imagen', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        email: currentUserEmail,  // ← AGREGAR ESTA LÍNEA email
                        prompt: playgroundConfig.value.prompt,
                        modelo: playgroundConfig.value.modelo
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Error al generar imagen');
                }
                
                const data = await response.json();
                imagenGenerada.value = data.imagen_url;
                
            } catch (error) {
                message.value = 'Error al generar imagen: ' + error.message;
                messageType.value = 'error';
            } finally {
                generandoImagen.value = false;
            }
        }

        function regenerarImagen() {
            imagenGenerada.value = null;
            generarImagenIA();
        }

        function usarImagenGenerada() {
            if (preguntaActual && imagenGenerada.value) {
                preguntaActual.archivoUrl = imagenGenerada.value;
                preguntaActual.archivoNombre = `imagen_${tipoActual}_${preguntaActual.numero}.png`;
                
                message.value = 'Imagen adjuntada exitosamente';
                messageType.value = 'success';
                
                cerrarPlayground();
            }
        }

        function subirImagenDirecta(item) {
            // Crear input file dinámico
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.jpg,.jpeg,.png,.gif,.pdf';
            input.onchange = (e) => subirArchivoAnexo(e, item, item.numero ? 'casos' : 'libres');
            input.click();
        }

        function toggleBloqueo() {
            examen.bloqueado = !examen.bloqueado;
            message.value = examen.bloqueado ? 'Examen bloqueado para edición' : 'Examen desbloqueado para edición';
            messageType.value = 'success';
            setTimeout(() => { message.value = ''; }, 3000);
        }

        function activarModoPlantilla() {
            modoPlantillaProfesor.value = true;
            modoEstudiante.value = false;
          }
        
          function cambiarModoDesdePlantilla() {
            modoPlantillaProfesor.value = true;  // ✅ Activa modo plantilla
            modoEstudiante.value = false;        // ✅ Desactiva modo estudiante por si acaso
        }
          

        function cambiarModo() {
            modoEstudiante.value = !modoEstudiante.value;

            // --- INICIO: Bloque añadido ---
            if (modoEstudiante.value) {
            // Si ACABAMOS de entrar en Modo Estudiante,
            // llamamos a la función que limpia las respuestas del alumno.
            console.log("Cambiando a Modo Estudiante, reiniciando respuestas del alumno...");
            inicializarRespuestas();
            }
                        // --- FIN: Bloque añadido --
            // 🔥 Añade esta línea para emitir el evento global:
            window.dispatchEvent(new CustomEvent('modo-estudiante-cambiado', {
                detail: { modoEstudiante: modoEstudiante.value }
            }));
            message.value = modoEstudiante.value ? 'Modo Estudiante activado' : 'Modo Profesor activado';
            messageType.value = 'info';
            setTimeout(() => { message.value = ''; }, 3000);
        }

        function inicializarRespuestas() {
            examen.preguntasMarcar.forEach(p => p.respuestaSeleccionada = null);
            examen.preguntasLibres.forEach(p => p.respuestaAlumno = '');
            examen.casosUso.forEach(c => c.respuestaAlumno = '');
        }


        async function generarPreguntaIA(tipo) {

            console.log('INICIO FUNCION - TIPO:', tipo);
            console.log('currentUserEmail:', currentUserEmail);

            // Verificar créditos antes de generar
            const creditos = await obtenerCreditos();
            if (!creditos || creditos.saldo_actual < 100) { // Ajustar límite según necesidad
                message.value = 'Créditos insuficientes para generar examen';
                messageType.value = 'error';
                return;
            }

            // Si no existe el campo, usamos un valor predeterminado
            const promptValue = document.getElementById('prompt-input') ? 
            document.getElementById('prompt-input').value : 'programación';

            // DEBUG - agregar estas 3 líneas aquí:
            console.log('Elemento prompt:', document.getElementById('prompt-input'));
            console.log('Valor capturado:', document.getElementById('prompt-input').value);
            console.log('promptValue final:', promptValue);

            // Obtener el modelo de IA seleccionado del dropdown
            const modeloSeleccionado = document.getElementById(`modelo-ia-${tipo}`).value;
            // --- FIN MODIFICACIÓN ---


            // Mapeo de tipos de pregunta para la API
            const tiposPregunta = {
                'marcar': 'opcion_multiple',
                'libres': 'abierta',
                'casos': 'caso_uso'
            };
            message.value = 'Generando pregunta con IA...';
            messageType.value = 'info';
            
            try {

                console.log('DATOS ENVIADOS:', {
                    email: currentUserEmail,
                    prompt: promptValue,
                    tipo_pregunta: tiposPregunta[tipo],
                    num_opcion_multiple: tipo === 'marcar' ? 10 : 0,
                    num_abiertas: tipo === 'libres' ? 5 : 0,
                    num_casos_uso: tipo === 'casos' ? 5 : 0,
                    modelo_ia: modeloSeleccionado
                });

                const response = await fetch('http://127.0.0.1:5000/api/generar-examen', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
            body: JSON.stringify({
                email: currentUserEmail,  // ← AGREGAR ESTA LÍNEA email
                prompt: promptValue, // Tema - puede ser dinámico en el futuro
                tipo_pregunta: tiposPregunta[tipo], // Convertir al formato esperado por la API
                num_opcion_multiple: tipo === 'marcar' ? 10 : 0,
                num_abiertas: tipo === 'libres' ? 5 : 0,
                num_casos_uso: tipo === 'casos' ? 5 : 0,
                modelo_ia: modeloSeleccionado // <--- LÍNEA AÑADIDA
            })
        });

                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                    
                }
                // Si la generación fue exitosa, descontar créditos
                await descontarCreditos(modeloSeleccionado, 1); // 1 estudiante por defecto
                    
                // Actualizar display de créditos
                await actualizarMostrarCreditos();

                const data = await response.json();
                console.log("Respuesta completa:", data);
                console.log("Respuesta completa del servidor:", data);
                console.log("Propiedades disponibles:", Object.keys(data));
                
                // Asignar el ID del examen si está disponible
                if (data.examenId) {
                    console.log("ID de examen recibido:", data.examenId);
                    examen.id = data.examenId;
                    console.log("ID asignado al examen:", examen.id);
                } else {
                    console.warn("No se recibió examenId en la respuesta");
                }
                
                if (tipo === 'marcar') {
                    // Extraer las opciones si están disponibles en la respuesta
                    if (data.examen_estructurado?.preguntas) {
                        data.examen_estructurado.preguntas.forEach((preguntaData, idx) => {
                            // Extraer opciones para esta pregunta
                            let opciones = [];
                            if (preguntaData.opciones){
                                opciones = preguntaData.opciones.map((opcion, index) => {
                            return {
                                texto: opcion,
                                valor: ['A', 'B', 'C', 'D', 'E'][index]
                            };
                        });
                    } else {
                        // Opciones por defecto si no se encuentran
                        opciones = [
                            { texto: 'Opción A', valor: 'A' },
                            { texto: 'Opción B', valor: 'B' },
                            { texto: 'Opción C', valor: 'C' },
                            { texto: 'Opción D', valor: 'D' },
                            { texto: 'Opción E', valor: 'E' }
                        ];
                    }
                    
                    const nuevaPregunta = {
                        numero: examen.preguntasMarcar.length + 1,
                        texto: preguntaData.texto || `Pregunta ${idx+1} generada por IA`,
                        puntaje: 1,
                        opciones: opciones,
                        respuestaSeleccionada: null
                    };
                    examen.preguntasMarcar.push(nuevaPregunta);
                });  
            }  
                    
                } else if (tipo === 'libres') {
                   // Modificar para procesar todas las preguntas abiertas, no solo la primera
                    if (data.examen_estructurado?.preguntas) {
                        data.examen_estructurado.preguntas.forEach((preguntaData) => {
                    
                    // Crear la nueva pregunta
                    const nuevaPregunta = {
                        numero: examen.preguntasLibres.length + 1,
                        texto: preguntaData.texto || 'Pregunta libre generada por IA',
                        puntaje: 1,
                        respuestaAlumno: ''
                    };
                    // Agregar la pregunta al array
                    examen.preguntasLibres.push(nuevaPregunta);
                    // Para depuración
                    console.log("Pregunta libre añadida:", nuevaPregunta);
                });
                    console.log("Total preguntas libres:", examen.preguntasLibres.length);
                }
                    
                    } else if (tipo === 'casos') {
                        // Modificar para procesar todos los casos de uso, no solo el primero
                        if (data.examen_estructurado?.preguntas) {
                            data.examen_estructurado.preguntas.forEach((casoData) => {
                                const nuevoCaso = {
                                    numero: examen.casosUso.length + 1,
                                    descripcion: casoData.texto || 'Caso de uso generado por IA',
                                    pregunta: casoData.requisitos?.[0] || 'Desarrolle una solución para el caso descrito anteriormente',
                                    puntaje: 1,
                                    respuestaAlumno: '',
                                    archivoSubido: false
                                };
                                examen.casosUso.push(nuevoCaso);
                                // Para depuración
                                console.log("Caso de uso añadido:", nuevoCaso);
                            });
                            console.log("Total casos de uso:", examen.casosUso.length);
                        }
                    }

                    message.value = 'Pregunta generada exitosamente';
                messageType.value = 'success';

            } catch (error) {
                message.value = 'Error al generar pregunta con IA: ' + error.message;
                messageType.value = 'error';
                console.error('Error generando pregunta IA:', error);
            }
            setTimeout(() => { message.value = ''; }, 3000);
        }

        // Código para manejar la carga y eliminación de archivos
        const uploadProgress = ref(0);
        const isUploading = ref(false);

        async function handleFileUpload(event, caso) {
            const file = event.target.files[0];
            if (!file) return;

            try {
                // Inicializar estado de carga
                message.value = 'Subiendo archivo...';
                messageType.value = 'info';
                isUploading.value = true;
                uploadProgress.value = 0;
                
                const formData = new FormData();
                formData.append('file', file);
                formData.append('examenId', examen.id);
                formData.append('casoNumero', caso.numero);
                // ► Añadir estos campos
                formData.append('nombreAlumno', examen.nombreAlumno);
                formData.append('idAlumno', examen.idAlumno);

                // Crear XMLHttpRequest para monitorear el progreso
                const xhr = new XMLHttpRequest();
                
                // Configurar la promesa para la respuesta
                const uploadPromise = new Promise((resolve, reject) => {
                    xhr.open('POST', 'http://127.0.0.1:5000/api/upload');
                    
                    // Evento para monitorear el progreso
                    xhr.upload.addEventListener('progress', (event) => {
                        if (event.lengthComputable) {
                            // Calcular y actualizar el progreso (0-100)
                            const percentComplete = Math.round((event.loaded / event.total) * 100);
                            uploadProgress.value = percentComplete;
                        }
                    });

                    // Configurar manejadores de eventos
                    xhr.onload = () => {
                        if (xhr.status >= 200 && xhr.status < 300) {
                            try {
                                const result = JSON.parse(xhr.responseText);
                                resolve(result);
                            } catch (e) {
                                reject(new Error('Error al procesar la respuesta del servidor'));
                            }
                        } else {
                            try {
                                const errorData = JSON.parse(xhr.responseText);
                                reject(new Error(errorData.error || 'Error en la carga'));
                            } catch (e) {
                                reject(new Error(`Error en la carga: ${xhr.status}`));
                            }
                        }
                    };
                    
                    xhr.onerror = () => {
                        reject(new Error('Error de red al subir el archivo'));
                    };
                    
                    xhr.onabort = () => {
                        reject(new Error('Carga cancelada'));
                    };
                });
                
                // Enviar los datos
                xhr.send(formData);
                
                // Esperar la respuesta
                const result = await uploadPromise;
                
                // Actualizar el estado del caso
                caso.nombreArchivo = file.name;
                caso.archivoSubido = true;
                caso.fileId = result.fileId;
                message.value = 'Archivo subido exitosamente';
                messageType.value = 'success';
            } catch (error) {
                message.value = 'Error al subir archivo: ' + error.message;
                messageType.value = 'error';
                console.error('Error subiendo archivo:', error);
            } finally {
                // Restablecer estado de carga
                setTimeout(() => { 
                    isUploading.value = false;
                    message.value = '';
                }, 3000);
            }
        }

        async function verificarTipoCuenta() {
            try {
                const response = await fetch(`http://127.0.0.1:5002/api/verificar-tipo-cuenta/${currentUserEmail}`);
                const tipoCuenta = await response.json();
                return tipoCuenta;
            } catch (error) {
                console.error('Error verificando tipo cuenta:', error);
                return { tipo_cuenta: 'individual' };
            }
        }

        // Función para obtener créditos del usuario
        async function obtenerCreditos() {
            try {
                const response = await fetch(`http://127.0.0.1:5002/api/saldo/${currentUserEmail}`);
                const creditos = await response.json();
                return creditos;
            } catch (error) {
                console.error('Error obteniendo créditos:', error);
                return null;
            }
        }

        // Función para mostrar créditos en la UI
        async function actualizarMostrarCreditos() {
            const creditos = await obtenerCreditos();
            if (creditos) {
                const creditosElement = document.getElementById('saldo-creditos');
                if (creditosElement) {
                    creditosElement.textContent = `${creditos.saldo_actual} créditos`;
                     
                    // Cambiar color según nivel de créditos
                    if (creditos.saldo_actual < 1000) {
                        creditosElement.style.color = '#f44336'; // Rojo
                        mostrarAlertaCreditosBajos(creditos.saldo_actual);
                    } else if (creditos.saldo_actual < 3000) {
                        creditosElement.style.color = '#ff9800'; // Naranja
                    } else {
                        creditosElement.style.color = '#4CAF50'; // Verde
                    }
                }
            }
        }
        actualizarMostrarCreditos();

        function mostrarAlertaCreditosBajos(saldoActual) {
            // Evitar múltiples alertas
            if (document.getElementById('alerta-creditos')) return;
            
            const alerta = document.createElement('div');
            alerta.id = 'alerta-creditos';
            alerta.style.cssText = `
                position: fixed; top: 20px; right: 20px; z-index: 1000;
                background: #f44336; color: white; padding: 15px; border-radius: 5px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3); max-width: 300px;
            `;
            alerta.innerHTML = `
                <strong>⚠️ Créditos bajos</strong><br>
                Solo tienes ${saldoActual} créditos restantes.<br>
                <button onclick="this.parentElement.remove()" style="margin-top:10px; background:white; color:#f44336; border:none; padding:5px 10px; border-radius:3px;">Cerrar</button>
            `;
            
            document.body.appendChild(alerta);
            
            // Auto-remover después de 10 segundos
            setTimeout(() => {
                if (alerta.parentElement) alerta.remove();
            }, 10000);
        }

        async function eliminarArchivo(caso) {
            try {
                if (caso.fileId) {
                    message.value = 'Eliminando archivo...';
                    messageType.value = 'info';
                    
                    const response = await fetch('http://127.0.0.1:5000/api/delete-file', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            email: currentUserEmail,  // ← AGREGAR ESTA LÍNEA email
                            fileId: caso.fileId
                        })
                    });

                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.error || 'Error al eliminar archivo');
                    }
                }
                
                caso.nombreArchivo = '';
                caso.archivoSubido = false;
                caso.urlArchivo = '';
                caso.fileId = '';
                
                message.value = 'Archivo eliminado exitosamente';
                messageType.value = 'success';
            } catch (error) {
                message.value = 'Error al eliminar archivo: ' + error.message;
                messageType.value = 'error';
                console.error('Error eliminando archivo:', error);
            }
            setTimeout(() => { message.value = ''; }, 3000);
        }

        async function descontarCreditos(modelo, numEstudiantes = 1) {

            // Verificar tipo de cuenta primero
            const tipoCuenta = await verificarTipoCuenta();
            
            // Si es usuario de empresa, usar email del admin para descuento
            const emailDescuento = tipoCuenta.es_usuario_empresa ? 
                tipoCuenta.empresa_admin : currentUserEmail;

            try {
                const response = await fetch('http://127.0.0.1:5002/api/evaluar-examen', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: currentUserEmail,
                        examen_id: `examen_${Date.now()}`,
                        modelos_seleccionados: [modelo],
                        num_estudiantes: numEstudiantes
                    })
                });
                
                if (!response.ok) {
                    console.error('Error descontando créditos');
                }
            } catch (error) {
                console.error('Error en descuento:', error);
            }
        }

        async function subirArchivoPregunta(event, item) {
            const file = event.target.files[0];
            if (!file) return;
          
            const formData = new FormData();
            formData.append('email', currentUserEmail);  // ← AGREGAR ESTA LÍNEA email
            formData.append('file', file);
            formData.append('examenId', examen.id);
            formData.append('tipo', activeTab.value);
            formData.append('numero', item.numero);
          
            try {
              const response = await fetch('http://127.0.0.1:5000/api/upload-recursos', {
                method: 'POST',
                body: formData
              });
              const result = await response.json();
              item.archivoNombre = file.name;
              item.archivoUrl = result.url;
              message.value = 'Archivo subido exitosamente';
              messageType.value = 'success';
            } catch (err) {
              message.value = 'Error al subir archivo';
              messageType.value = 'error';
              console.error(err);
            }
          }
          

        function guardarPDF() {
            // Mostrar mensaje de generación en proceso
            message.value = 'Generando PDF...';
            messageType.value = 'info';
            
            // Esperar a que el DOM se actualice
            nextTick(() => {
                // Obtener el elemento que contiene el contenido del examen
                const element = document.getElementById('examen-pdf');
                
                // Asegurar que los datos del examen estén actualizados en el elemento PDF
                // Esto es importante para reflejar las respuestas más recientes de los alumnos
                const preguntasMarcarEl = element.querySelectorAll('.pregunta-pdf');
                examen.preguntasMarcar.forEach((pregunta, idx) => {
                    if (preguntasMarcarEl[idx]) {
                        // Actualizar las opciones seleccionadas
                        const opcionesEl = preguntasMarcarEl[idx].querySelectorAll('.opcion-pdf p');
                        pregunta.opciones.forEach((opcion, i) => {
                            if (opcionesEl[i]) {
                                opcionesEl[i].textContent = 
                                    (pregunta.respuestaSeleccionada === i ? '●' : '○') + ' ' + opcion.texto;
                            }
                        });
                    }
                });
                
                // Asegurar que las respuestas abiertas estén actualizadas
                const respuestasLibresEl = element.querySelectorAll('.respuesta-espacio');
                examen.preguntasLibres.forEach((pregunta, idx) => {
                    if (respuestasLibresEl[idx]) {
                        respuestasLibresEl[idx].textContent = pregunta.respuestaAlumno || '';
                    }
                });
                
                // Crear un clon fuera de la página para no afectar el diseño actual
                const clone = element.cloneNode(true);
                clone.style.position = 'absolute';
                clone.style.left = '-9999px';
                clone.style.top = '0';
                clone.style.display = 'block'; // Hacer visible el clon para generación
                document.body.appendChild(clone);
                
                // Configuración del PDF
                const options = {
                    margin: [10, 10, 10, 10],
                    filename: `Examen_${examen.id || 'nuevo'}.pdf`,
                    image: { type: 'jpeg', quality: 0.98 },
                    html2canvas: { scale: 2, useCORS: true },
                    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
                };
                
                // Generar el PDF desde el clon
                html2pdf()
                    .from(clone)
                    .set(options)
                    .save()
                    .then(() => {
                        // Eliminar el clon cuando termine
                        document.body.removeChild(clone);
                        message.value = 'PDF generado exitosamente';
                        messageType.value = 'success';
                        setTimeout(() => { message.value = ''; }, 3000);
                    })
                    .catch(error => {
                        console.error('Error generando PDF:', error);
                        document.body.removeChild(clone);
                        message.value = 'Error al generar PDF';
                        messageType.value = 'error';
                        setTimeout(() => { message.value = ''; }, 3000);
                    });
                                    
                }); 
            }


            function crearVistaPrevia() {
                // Crear una nueva ventana
                const vistaPreviaWindow = window.open('', 'Vista Previa Examen', 'width=800,height=600');
                
                // Obtener datos del examen
                const examenActual = {
                  id: examen.id,
                  fecha: examen.fecha,
                  profesor: examen.profesor,
                  nombreAlumno: examen.nombreAlumno,
                  idAlumno: examen.idAlumno,
                  preguntasMarcar: examen.preguntasMarcar,
                  preguntasLibres: examen.preguntasLibres,
                  casosUso: examen.casosUso
                };
                
                // Comenzar a construir el HTML
                let contenidoHTML = `
                  <!DOCTYPE html>
                  <html>
                  <head>
                    <title>Vista Previa - Examen ${examenActual.id}</title>
                    <style>
                      body { font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
                      h1 { text-align: center; }
                      h2 { margin-top: 30px; border-bottom: 1px solid #ccc; }
                      .pregunta { margin-bottom: 20px; }
                      .opcion { margin-left: 20px; }
                      .respuesta { border: 1px solid #ddd; padding: 10px; min-height: auto; margin-top: 10px; 
                                  text-align: justify; white-space: pre-wrap; background-color: #f9f9f9; }
                      .info-archivo { font-style: italic; color: #666; }
                      @media print { 
                        body { font-size: 12px; }
                        .no-print { display: none; }
                        .page-break { page-break-before: always; }
                      }
                    </style>
                  </head>
                  <body>
                    <div class="no-print" style="text-align: center; margin-bottom: 20px;">
                      <button onclick="window.print()">Imprimir Examen</button>
                    </div>
                    
                    <h1>${examenActual.id} - Examen</h1>
                    <p><strong>Fecha:</strong> ${examenActual.fecha}</p>
                    <p><strong>Profesor:</strong> ${examenActual.profesor || '________________'}</p>
                    <p><strong>Nombre del Alumno:</strong> ${examenActual.nombreAlumno || '________________'}</p>
                    <p><strong>ID del Alumno:</strong> ${examenActual.idAlumno || '________________'}</p>
                `;
                
                // Añadir preguntas para marcar
                if (examenActual.preguntasMarcar && examenActual.preguntasMarcar.length > 0) {
                  contenidoHTML += `<h2>Preguntas para Marcar</h2>`;
                  
                  examenActual.preguntasMarcar.forEach(pregunta => {
                    contenidoHTML += `
                      <div class="pregunta">
                        <p><strong>${pregunta.numero}. (${pregunta.puntaje} pts)</strong> ${pregunta.texto}</p>
                    `;
                    
                    // Añadir opciones
                    if (pregunta.opciones) {
                      pregunta.opciones.forEach((opcion, i) => {
                        const marcado = pregunta.respuestaSeleccionada === i ? '●' : '○';
                        contenidoHTML += `
                          <div class="opcion">
                            <p>${marcado} ${opcion.texto}</p>
                          </div>
                        `;
                      });
                    }
                    
                    contenidoHTML += `</div>`;
                  });
                }
                
                // Añadir preguntas libres
                if (examenActual.preguntasLibres && examenActual.preguntasLibres.length > 0) {
                  contenidoHTML += `<h2>Preguntas Libres</h2>`;
                  
                  examenActual.preguntasLibres.forEach(pregunta => {
                    contenidoHTML += `
                      <div class="pregunta">
                        <p><strong>${pregunta.numero}. (${pregunta.puntaje} pts)</strong> ${pregunta.texto}</p>
                        <div class="respuesta">
                          ${pregunta.respuestaAlumno || ''}
                        </div>
                      </div>
                    `;
                  });
                }
                
                // Añadir casos de uso
                if (examenActual.casosUso && examenActual.casosUso.length > 0) {
                  contenidoHTML += `<h2>Casos de Uso</h2>`;
                  
                  examenActual.casosUso.forEach(caso => {
                    contenidoHTML += `
                      <div class="pregunta">
                        <p><strong>${caso.numero}. (${caso.puntaje} pts)</strong></p>
                        <p><strong>Descripción:</strong> ${caso.descripcion}</p>
                        <p><strong>Pregunta:</strong> ${caso.pregunta}</p>
                        <div class="respuesta">
                          ${caso.respuestaAlumno || ''}
                        </div>
                    `;
                    
                    // Añadir información del archivo si existe
                    if (caso.archivoSubido) {
                      contenidoHTML += `
                        <p class="info-archivo">
                          <strong>Archivo adjunto:</strong> ${caso.nombreArchivo}
                        </p>
                      `;
                    }
                    
                    contenidoHTML += `</div>`;
                  });
                }
                
                // Cerrar el HTML
                contenidoHTML += `
                    </body>
                  </html>
                `;
                
                // Escribir en la nueva ventana
                vistaPreviaWindow.document.write(contenidoHTML);
                vistaPreviaWindow.document.close();
              }
                 
        
        function limpiarCacheExamen() {
            // Solicitar confirmación antes de limpiar
            if (!confirm('Esta acción eliminará todos los datos del examen actual. ¿Desea continuar?')) {
                return;
            }
            
            // Reiniciar todas las propiedades del examen
            examen.id = '';
            examen.fecha = new Date().toISOString().split('T')[0];
            examen.profesor = '';
            examen.nombreAlumno = '';
            examen.idAlumno = '';
            examen.bloqueado = false;
            examen.publicado = false;
            examen.preguntasMarcar = [];
            examen.preguntasLibres = [];
            examen.casosUso = [];
            
            // Volver a la primera pestaña
            activeTab.value = 'marcar';
            
            // Mostrar mensaje de confirmación
            message.value = 'Examen limpiado correctamente';
            messageType.value = 'success';
            setTimeout(() => { message.value = ''; }, 3000);
            
            // También limpiar localStorage si estás guardando el examen allí
            localStorage.removeItem('examenData');
        }

        function publicarPlantillaWeb() {
            const baseUrl = "http://127.0.0.1:5000";  // o tu dominio si lo has desplegado
            const idExamen = examen.id || "sin_id";
            const url = `${baseUrl}/plantilla/${idExamen}`;
            window.open(url, "_blank");
        }
        

        function verPlantillaLocal() {
            const baseUrl = "http://127.0.0.1:5000";  // mismo que arriba
            const idExamen = examen.id || "sin_id";
            const url = `${baseUrl}/plantilla/${idExamen}`;
            window.open(url, "_blank");
        }

        function abrirPublicUrl() {
            if (publicUrl.value) {
              window.open(publicUrl.value, "_blank");
            } else {
              console.warn("🔴 publicUrl no está definido o aún no se ha generado.");
              alert("La URL aún no está disponible. Asegúrate de haber publicado la plantilla.");
            }
          }          
        
        
          async function submitPlantilla() {
            console.log("🔥 submitPlantilla EJECUTÁNDOSE!!!");

            let result; // Declarar result fuera del bloque try

            try {
                isPublishing.value = true; // Usar la misma constante para indicar carga
                message.value = 'Guardando plantilla de respuestas...';
                messageType.value = 'info';

                // Verificar que las respuestas del profesor están presentes
                console.log('Verificando respuestas del profesor:');
                console.log('Marcar:', examen.preguntasMarcar.map(p => p.respuestaSeleccionada));
                console.log('Libres:', examen.preguntasLibres.map(p => p.respuestaAlumno));
                console.log('Casos:', examen.casosUso.map(c => c.respuestaAlumno));

               
                // URL para desarrollo local
                const apiUrl = 'http://127.0.0.1:5000/api/publishPlantilla';

                // Las respuestas ya están en el modelo reactivo, no necesitamos capturar del DOM
                console.log('✅ Usando respuestas del modelo reactivo');
                
                // Usar la variable examen en lugar de plantilla
                const datosPara = {
                    plantilla_data:  {
                        email: currentUserEmail,  // ← AGREGAR ESTA LÍNEA email
                        examen_id: examen.id,
                        nombre_examen: examen.nombreExamen,
                        tipo_examen: examen.tipoExamen,
                        fecha: new Date().toISOString(),  // ✅ Agregado
                        nombre_profesor: examen.profesor || "Profesor",
                        profesor_id: examen.profesorId,
                        preguntas_marcar: examen.preguntasMarcar,
                        preguntas_libres: examen.preguntasLibres,
                        casos_uso: examen.casosUso
                    },
                    config: {
                        publicAccess: true,
                        expiration: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
                    }
                };
                
                console.log("Datos a enviar:", JSON.stringify(datosPara));

                // ACTUALIZA las respuestas antes de enviar al backend (¡COPIA Y PEGA esto!)

                console.log('DEBUG preguntasMarcar:', JSON.parse(JSON.stringify(examen.preguntasMarcar)));
                console.log('DEBUG preguntasLibres:', JSON.parse(JSON.stringify(examen.preguntasLibres)));
                console.log('DEBUG casosUso:', JSON.parse(JSON.stringify(examen.casosUso)));

                console.log('DEBUG preguntasMarcar:', examen.preguntasMarcar);
                console.log('DEBUG preguntasLibres:', examen.preguntasLibres);
                console.log('DEBUG casosUso:', examen.casosUso);


                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },

                    
                    // En profesor.js, línea donde se construye el body de la solicitud:
                    
                    body: JSON.stringify(datosPara)

                });

                console.log("Respuesta del servidor:", response);

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Error al guardar plantilla');
                }
                
                try {
                    // Intenta convertir la respuesta a JSON
                    result = await response.json();
                    console.log("Resultado:", result);
                } catch (e) {
                    // Captura el error si la conversión falla
                    console.error("Error al procesar respuesta JSON:", e);
                    result = null; // O manejar de otra forma
                }
                
                // Verificar si result tiene un valor antes de usarlo
                if (result && result.url) {
                    publicUrl.value = result.url;
                } else {
                    // Usar URL alternativa si result.url no existe o hubo error al parsear
                    publicUrl.value = `http://127.0.0.1:5000/plantilla/${examen.id}`;
                    // Opcional: Mostrar un mensaje indicando que se usó la URL alternativa
                    console.warn("No se pudo obtener la URL de la respuesta, usando URL alternativa.");
                }
                
                // Abrir la URL en una nueva ventana
                window.open(publicUrl.value, "_blank");
        
                message.value = `Plantilla guardada! URL: ${publicUrl.value}`;
                messageType.value = 'success';
                
                // Copiar URL al portapapeles
                navigator.clipboard.writeText(publicUrl.value);


                 // --- INICIO: GENERAR RESPUESTAS DEL PROFESOR PRIMERO ---
                 try {
                    console.log("🔄 Obteniendo respuestas modelo actualizadas...");
                    const respuestasResponse = await fetch('http://127.0.0.1:5000/api/generar-respuestas', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', },
                        body: JSON.stringify({ 
                            email: currentUserEmail,  // ← AGREGAR ESTA LÍNEA email
                            examenData: examen,
                            modelo_ia: modeloRespuestas.value 
                        }) // Enviar estado actual (puede no ser necesario si el server usa el ID)
                    });
                    if (!respuestasResponse.ok) throw new Error('Fallo al obtener respuestas modelo');

                    const resultRespuestas = await respuestasResponse.json();
                    const examenActualizado = resultRespuestas.examen_con_respuestas;

                    // Actualiza el objeto 'examen' local con las respuestas recibidas
                    if (examenActualizado) {
                        // Actualizar Marcar (asume que el server devuelve respuestaCorrectaIndex)
                        if (examenActualizado.preguntasMarcar) {
                           examen.preguntasMarcar.forEach((pLocal, i) => {
                              if (examenActualizado.preguntasMarcar[i]?.respuestaCorrectaIndex !== undefined) {
                                 pLocal.respuestaCorrectaIndex = examenActualizado.preguntasMarcar[i].respuestaCorrectaIndex;
                              }
                           });
                        }
                        // Actualizar Libres (asume que el server devuelve respuestaProfesor)
                         if (examenActualizado.preguntasLibres) {
                           examen.preguntasLibres.forEach((pLocal, i) => {
                              if (examenActualizado.preguntasLibres[i]?.respuestaProfesor !== undefined) {
                                 pLocal.respuestaProfesor = examenActualizado.preguntasLibres[i].respuestaProfesor;
                              }
                           });
                        }
                         // Actualizar Casos (asume que el server devuelve respuestaProfesor)
                        if (examenActualizado.casosUso) {
                           examen.casosUso.forEach((cLocal, i) => {
                              if (examenActualizado.casosUso[i]?.respuestaProfesor !== undefined) {
                                 cLocal.respuestaProfesor = examenActualizado.casosUso[i].respuestaProfesor;
                              }
                           });
                        }
                         console.log("✅ Objeto 'examen' local actualizado con respuestas modelo.");
                    }
                } catch (errorFetchRespuestas) {
                    console.error("Error al obtener/actualizar respuestas modelo en finally:", errorFetchRespuestas);
                    // Decide si mostrar el modal igual o no
                }
                // --- FIN: GENERAR RESPUESTAS DEL PROFESOR ---

                
            } catch (error) {
                console.error("Error completo:", error);
                message.value = `Error al guardar plantilla: ${error.message}`;
                messageType.value = 'error';
            } finally {
                isPublishing.value = false; // Restaurar estado al finalizar
                setTimeout(() => { message.value = ''; }, 5000);
                mostrarPlantillaRespuestas();

                

                // Verificar que esta línea existe:
                console.log("Datos de las respuestas (en finally):", result);
                console.log("Llamando a mostrarPlantillaRespuestas desde submitPlantilla");
            
            }
        }

        function mostrarPlantillaRespuestas() {
            // Hacer datos disponibles globalmente
            window.currentExamenData = examen;
            console.log("Función mostrarPlantillaRespuestas ejecutada");
            
            // Obtener referencias a los elementos del modal
            const modal = document.getElementById('modalPlantillaRespuestas');
            console.log("Modal element:", modal);
            const modalBody = document.getElementById('modalPlantillaBody');
            const modalError = document.getElementById('modalPlantillaError');
            
            if (!modal || !modalBody || !modalError) {
                console.error("Error: Elementos del modal no encontrados en el DOM");
                alert("Error interno: No se pudo inicializar la vista de plantilla.");
                return;
            }
            
            // Mostrar el modal con un mensaje de carga
            modalBody.innerHTML = '<p>Cargando plantilla de respuestas...</p>';
            modalError.textContent = '';
            modal.style.display = 'flex';
            
            // Crear contenido HTML básico para el modal
            let contenidoHTML = `
                <h1>Plantilla de Respuestas: ${examen.nombreExamen || 'Examen sin nombre'}</h1>
                <p><strong>ID del Examen:</strong> ${examen.id || 'N/A'}</p>
                <p><strong>Profesor:</strong> ${examen.profesor || 'No especificado'}</p>
                <p><strong>Fecha:</strong> ${new Date().toLocaleDateString()}</p>
            `;
            
            // Añadir secciones para cada tipo de pregunta
            if (examen.preguntasMarcar && examen.preguntasMarcar.length > 0) {
                contenidoHTML += `<h2>Preguntas para Marcar</h2>`;
                examen.preguntasMarcar.forEach(pregunta => {
                    if (!pregunta) return;
                    contenidoHTML += `
                        <div class="pregunta">
                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                                <p class="numero" style="margin: 0;">${pregunta.numero || '?'}. (${pregunta.puntaje || 0} pts) ${pregunta.texto || 'Pregunta sin texto'}</p>
                                <select class="etiqueta-pregunta" data-pregunta="${pregunta.numero}" data-tipo="marcar">
                                    <option value="marcar" selected>code:marcar</option>
                                    <option value="libres">code:libres</option>
                                    <option value="casos">code:casos</option>
                                </select>
                            </div>
                            <div class="opciones">
                    `;
                    
                    if (pregunta.opciones && pregunta.opciones.length > 0) {
                        pregunta.opciones.forEach((opcion, index) => {
                            if (!opcion) return;
                            const esCorrecta = pregunta.respuestaCorrectaIndex === index; // ASUME que existe 'respuestaCorrectaIndex'
                            const letraOpcion = String.fromCharCode(65 + index); // A, B, C, etc.
                            contenidoHTML += `
                                <div class="opcion ${esCorrecta ? 'respuesta-correcta' : ''}">
                                    ${letraOpcion}) ${opcion.texto || 'Opción sin texto'}
                                    ${esCorrecta ? ' <strong>(CORRECTA)</strong>' : ''}
                                </div>
                            `;
                        });
                    } else {
                        contenidoHTML += `<p><i>(Sin opciones definidas)</i></p>`;
                    }
                    
                    contenidoHTML += `</div></div>`;
                });
            }
            
            if (examen.preguntasLibres && examen.preguntasLibres.length > 0) {
                contenidoHTML += `<h2>Preguntas Libres</h2>`;
                examen.preguntasLibres.forEach(pregunta => {
                    if (!pregunta) return;
                    contenidoHTML += `
                        <div class="pregunta">
                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                                <p class="numero" style="margin: 0;">${pregunta.numero || '?'}. (${pregunta.puntaje || 0} pts) ${pregunta.texto || 'Pregunta sin texto'}</p>
                                <select class="etiqueta-pregunta" data-pregunta="${pregunta.numero}" data-tipo="libres">
                                    <option value="marcar">code:marcar</option>
                                    <option value="libres" selected>code:libres</option>
                                    <option value="casos">code:casos</option>
                                </select>
                            </div>
                            <div class="modelo-respuesta">
                                <strong>Respuesta modelo:</strong>
                                <div style="position: relative;">
                                <p id="respuesta-libre-${pregunta.numero}" style="text-align: justify; white-space: pre-wrap; padding-right: 30px;">${pregunta.respuestaProfesor || 'No hay respuesta modelo disponible.'}</p>
                                    <button
                                        type="button"
                                        title="Copiar respuesta"
                                        class="copy-btn"
                                        data-target-id="respuesta-libre-${pregunta.numero}"
                                        style="position: absolute; top: 0; right: 0; cursor: pointer; background: none; border: none; font-size: 1.2em; padding: 5px;"
                                        onclick="copiarAlPortapapeles(this)"
                                    >📋</button>
                                </div>
                            </div>
                        </div>
                    `;
                });
            }
            
            if (examen.casosUso && examen.casosUso.length > 0) {
                contenidoHTML += `<h2>Casos de Uso</h2>`;
                examen.casosUso.forEach(caso => {
                    if (!caso) return;
                    contenidoHTML += `
                        <div class="pregunta">
                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                                <p class="numero" style="margin: 0;">${caso.numero || '?'}. (${caso.puntaje || 0} pts)</p>
                                <select class="etiqueta-pregunta" data-pregunta="${caso.numero}" data-tipo="casos">
                                    <option value="marcar">code:marcar</option>
                                    <option value="libres">code:libres</option>
                                    <option value="casos" selected>code:casos</option>
                                </select>
                            </div>
                            <p><strong>Descripción:</strong> ${caso.descripcion || 'Sin descripción'}</p>
                            <div class="modelo-respuesta">
                                <strong>Respuesta modelo:</strong>
                                <div style="position: relative;">
                                <p id="respuesta-caso-${caso.numero}" style="text-align: justify; white-space: pre-wrap; padding-right: 30px;">${caso.respuestaProfesor || 'No hay respuesta modelo disponible.'}</p>
                                    <button
                                        type="button"
                                        title="Copiar respuesta"
                                        class="copy-btn"
                                        data-target-id="respuesta-caso-${caso.numero}"
                                        style="position: absolute; top: 0; right: 0; cursor: pointer; background: none; border: none; font-size: 1.2em; padding: 5px;"
                                        onclick="copiarAlPortapapeles(this)"
                                    >📋</button>
                                </div>
                            </div>
                        </div>
                    `;
                });
            }
            
            // Agregar botón para guardar en BD
            contenidoHTML += `
            <div style="text-align: center; margin-top: 20px;">
                <button onclick="guardarRespuestasEnBD()" class="btn btn-success">Guardar Respuestas en BD</button>
            </div>
            `;
            // Mostrar el contenido en el modal
            modalBody.innerHTML = contenidoHTML;
        }


// **** INICIO: REEMPLAZA LA FUNCIÓN publicarExamenWeb CON ESTO ****
async function publicarExamenWeb() {
    console.log("🔥 publicarExamenWeb INICIANDO"); // ← AGREGAR SOLO ESTA LÍNEA
    const logger = console; // <--- AÑADE ESTA LÍNEA
    logger.info("Ejecutando publicarExamenWeb..."); // Log de inicio
    // --- Validación Inicial (Igual que antes) ---
    if (!examen.id) {
        message.value = 'Error: Se requiere un ID de examen para publicar.';
        messageType.value = 'error';
        setTimeout(() => { message.value = ''; }, 3000);
        return;
    }
     if (!examen.bloqueado) {
         message.value = 'Error: Bloquee la edición del examen antes de publicar.';
         messageType.value = 'error';
         setTimeout(() => { message.value = ''; }, 3000);
         return;
     }
    // --- Fin Validación ---

    isPublishing.value = true; // Indicador de carga
    message.value = 'Guardando examen persistente y generando enlace...'; // Mensaje inicial
    messageType.value = 'info';

    let studentUrl = ''; // Variable para guardar la URL del alumno
    let flaskApiSuccess = false; // Bandera para saber si la llamada a Flask tuvo éxito

    // --- 1. LLAMADA A LA API FLASK (para guardar examen en Appwrite vía Backend) ---
    try {
        logger.info("Llamando a /api/publish en Flask...");
        const apiUrl = 'http://127.0.0.1:5000/api/publish';
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', },
            body: JSON.stringify({
                email: currentUserEmail,  // ← AGREGAR ESTA LÍNEA email
                examenData: examen, // Enviar datos completos
                puntajeTotal: puntajeTotal.value, // ← AGREGAR ESTA LÍNEA
                config: {} // Enviar config vacío o lo que necesite tu backend
            })
        });

        // Intenta leer la respuesta como texto PRIMERO para depuración, sin consumir el body para JSON (Incorrecto, sí lo consume)
        const responseText = await response.text();
        logger.debug(`Respuesta de Flask (${response.status}): ${responseText}`); // Log respuesta cruda
        // ... luego usa responseText para parsear si es necesario ...

        if (!response.ok) {
            let errorMsg = `Error del servidor Flask (${response.status})`;
            try {
                const responseCopy = response.clone(); // Crear una copia antes de leerla
                const errorData = await responseCopy.json();
                errorMsg = errorData.error || errorMsg;
            } catch (e) { /* Ignorar error de parseo JSON si no es JSON */ }
            throw new Error(errorMsg); // Lanza error para ir al catch principal
        }

        const result = JSON.parse(responseText); // <<<--- CORRECCIÓN AQUÍ
        logger.info("Respuesta exitosa de Flask:", result);

        if (!result.url || !result.success) {
            throw new Error("La respuesta de Flask no contiene la URL esperada o indica fallo.");
        }

        studentUrl = result.url; // <<<--- CAPTURA LA URL DEL FRONTEND devuelta por Flask
        flaskApiSuccess = true;
        message.value = 'Examen guardado persistente. Guardando enlace en lista...'; // Actualizar mensaje

    } catch (error) {
        logger.error("Error en la llamada a /api/publish:", error);
        message.value = `Error al guardar examen persistente: ${error.message}. No se guardará el enlace.`;
        messageType.value = 'error';
        // NO continuar si falla el guardado principal del examen
        isPublishing.value = false;
        setTimeout(() => { message.value = ''; }, 6000);
        return; // Detener ejecución aquí
    }
    // --- Fin Llamada a API Flask ---


    // --- 2. (Opcional pero recomendado) GUARDAR ENLACE EN APPWRITE (Colección examenes_publicados) ---
    // --- Fin Llamada a API Flask ---

    // --- Mensaje final (después de que Flask guardó todo) ---
    if (flaskApiSuccess && studentUrl) {
        message.value = `¡Examen publicado! Enlace de Alumno copiado: ${studentUrl}`;
        messageType.value = 'success';
        navigator.clipboard.writeText(studentUrl); // Copiar URL del ALUMNO
    } else {
        // Este 'else' probablemente ya no sea necesario si el catch anterior detiene la ejecución
        // pero lo dejamos por seguridad. El mensaje de error ya se mostró en el catch.
        logger.error("No se pudo obtener la URL del alumno después de la llamada a Flask.");
        // message.value ya tiene el mensaje de error del catch
        // messageType.value ya es 'error'
    }
    // --- Fin Mensaje Final ---

    // --- Limpieza Final ---
    isPublishing.value = false;
    setTimeout(() => { message.value = ''; }, 7000); // Más tiempo para leer el mensaje

}

//====================== INICIO FUNCION ANTI COPY PAGE ========================================================

// Variable global para controlar protecciones
/*let proteccionesActivas = true;

// Toggle para habilitar/deshabilitar protecciones
function toggleProtecciones() {
    proteccionesActivas = !proteccionesActivas;
    
    const textareas = document.querySelectorAll('textarea[placeholder*="Escribe tu respuesta"]');
    
    if (proteccionesActivas) {
        // Activar protecciones
        textareas.forEach(textarea => {
            textarea.addEventListener('keydown', bloquearCopyPaste);
            textarea.addEventListener('contextmenu', bloquearClickDerecho);
            textarea.addEventListener('selectstart', bloquearSeleccion);
            textarea.addEventListener('dragstart', bloquearArrastrar);
            textarea.classList.add('protected-textarea');
        });
        document.getElementById('toggle-proteccion').textContent = '🔒 Protecciones: ON';
        document.getElementById('toggle-proteccion').style.background = '#dc3545';
    } else {
        // Desactivar protecciones
        textareas.forEach(textarea => {
            textarea.removeEventListener('keydown', bloquearCopyPaste);
            textarea.removeEventListener('contextmenu', bloquearClickDerecho);
            textarea.removeEventListener('selectstart', bloquearSeleccion);
            textarea.removeEventListener('dragstart', bloquearArrastrar);
            textarea.classList.remove('protected-textarea');
        });
        document.getElementById('toggle-proteccion').textContent = '🔓 Protecciones: OFF';
        document.getElementById('toggle-proteccion').style.background = '#28a745';
    }
}

// FUNCIONES DE PROTECCIÓN ANTI-COPY-PASTE
function aplicarProteccionDinamica() {
    if (!modoEstudiante.value || !proteccionesActivas) return; // Agregar esta condición
    
    // Buscar todos los textarea de respuestas
    const textareas = document.querySelectorAll('textarea[placeholder*="Escribe tu respuesta"]');
    
    textareas.forEach(textarea => {
        // Agregar eventos de protección
        textarea.addEventListener('keydown', bloquearCopyPaste);
        textarea.addEventListener('contextmenu', bloquearClickDerecho);
        textarea.addEventListener('selectstart', bloquearSeleccion);
        textarea.addEventListener('dragstart', bloquearArrastrar);
        textarea.classList.add('protected-textarea');
        textarea.spellcheck = false;
        textarea.autocomplete = 'off';
    });
}

function bloquearCopyPaste(event) {
    if (!proteccionesActivas) return true; // Permitir si está desactivado
    if (event.ctrlKey && (event.key === 'c' || event.key === 'v' || event.key === 'x' || event.key === 'a')) {
        event.preventDefault();
        mostrarAdvertenciaCopyPaste();
        return false;
    }
    if (event.key === 'F12' || (event.ctrlKey && event.shiftKey && event.key === 'I')) {
        event.preventDefault();
        return false;
    }
    return true;
}

function bloquearClickDerecho(event) {
    if (!proteccionesActivas) return true; // Permitir si está desactivado
    event.preventDefault();
    mostrarAdvertenciaCopyPaste(); 
    return false;
}

function bloquearSeleccion(event) {
    if (!proteccionesActivas) return true;
    event.preventDefault();
    return false;
}

function bloquearArrastrar(event) {
    if (!proteccionesActivas) return true;
    event.preventDefault();
    return false;
}

function mostrarAdvertenciaCopyPaste() {
    // Mostrar advertencia temporal
    const advertencia = document.createElement('div');
    advertencia.innerHTML = '⚠️ Copy-paste no permitido durante el examen';
    advertencia.style.cssText = `
        position: fixed; top: 20px; right: 20px; 
        background: #ff4444; color: white; 
        padding: 10px 20px; border-radius: 5px; 
        z-index: 9999; font-weight: bold;
        animation: fadeInOut 3s ease-in-out;
    `;
    
    document.body.appendChild(advertencia);
    setTimeout(() => document.body.removeChild(advertencia), 3000);
}

function mostrarArchivo(input) {
    const inputName = input.name;
    const preguntaId = inputName.replace('archivo-', '');
    const infoDiv = document.getElementById('archivo-info-' + preguntaId);
    const nombreSpan = document.getElementById('nombre-archivo-' + preguntaId);
    
    if (input.files && input.files[0]) {
        const archivo = input.files[0];
        nombreSpan.innerHTML = '📎 <strong>' + archivo.name + '</strong>';
        infoDiv.style.display = 'block';
    }
}


function eliminarArchivoFormulario(preguntaId) {
    const input = document.querySelector('input[name="archivo-' + preguntaId + '"]');
    const infoDiv = document.getElementById('archivo-info-' + preguntaId);
    
    if (input) {
        input.value = '';
        infoDiv.style.display = 'none';
    }
}

// CSS para la animación de advertencia
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes fadeInOut {
        0% { opacity: 0; transform: translateY(-10px); }
        20% { opacity: 1; transform: translateY(0); }
        80% { opacity: 1; transform: translateY(0); }
        100% { opacity: 0; transform: translateY(-10px); }
    }
    .protected-textarea {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
        -webkit-touch-callout: none !important;
        -webkit-tap-highlight-color: transparent !important;
    }
    .protected-textarea::selection {
        background: transparent !important;
    }
    .protected-textarea::-moz-selection {
        background: transparent !important;
    }
`;
document.head.appendChild(styleSheet); */

//====================== FIN FUNCION ANTI COPY PAGE ========================================================


// Agregar al final del archivo
function mostrarModalSelector() {
    console.log("mostrarModalSelector llamada");
    const modal = document.getElementById('modalSelectorAppwrite');
    console.log("Modal encontrado:", modal);
    document.getElementById('modalSelectorAppwrite').style.display = 'flex';
    console.log("Display después del cambio:", document.getElementById('modalSelectorAppwrite').style.display);
    console.log("Computed style:", window.getComputedStyle(modal).display);
    
    // AGREGAR ESTAS LÍNEAS:
    document.getElementById('btn-confirmar').disabled = true;
    document.getElementById('btn-confirmar').style.background = '#ccc';
    window.archivoSeleccionadoModal = null;
    
    cargarArchivosModal();
 }

function cerrarModalSelector(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById('modalSelectorAppwrite').style.display = 'none';
}


// ===================================
// UPSTASH VECTOR INTEGRATION
// Agregar al final de profesor.js
// ===================================

// FUNCIÓN: MOSTRAR BÚSQUEDA
// FUNCIÓN: BÚSQUEDA SIMPLE DE EXÁMENES
async function buscarExamenes(termino) {
    try {
        console.log('🔍 Buscando exámenes:', termino);
        
        const response = await fetch('http://127.0.0.1:5000/api/buscar-examenes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: currentUserEmail,
                termino: termino
            })
        });
        
        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }
        
        const result = await response.json();
        return result;
        
    } catch (error) {
        console.error('❌ Error en búsqueda:', error);
        return { success: false, error: error.message };
    }
}

// FUNCIÓN: MOSTRAR BÚSQUEDA
async function mostrarBusquedaExamenes() {
    const termino = prompt('🔍 Buscar exámenes por nombre:');
    
    if (termino && termino.trim()) {
        const resultado = await buscarExamenes(termino.trim());
        
        if (resultado.success && resultado.resultados.length > 0) {
            console.log('📊 Exámenes encontrados:', resultado.resultados);
            let lista = 'Exámenes encontrados:\n\n';
            resultado.resultados.forEach((examen, index) => {
                lista += `${index + 1}. ${examen.nombre} - ${examen.profesor}\n`;
            });
            
            const seleccion = prompt(lista + '\nEscribe el número:');
            if (seleccion) {
                const indice = parseInt(seleccion) - 1;
                if (resultado.resultados[indice]) {
                    window.cargarExamenSeleccionado(resultado.resultados[indice].id);
                }
            }
        } else {
            alert('❌ No se encontraron exámenes.');
        }
    }
}

// ======= FUNCIONES PARA MODAL DE RECOMENDACIONES =======

const cargarRecomendaciones = async () => {
    modalRecomendaciones.value.cargando = true;
    modalRecomendaciones.value.error = null;
    
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/recomendaciones-modelos/${modalRecomendaciones.value.tipoPregunta}`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            modalRecomendaciones.value.recomendaciones = data.recomendaciones;
            modalRecomendaciones.value.mostrarNoRecomendados = false;
        } else {
            throw new Error(data.error || 'Error desconocido');
        }
    } catch (error) {
        console.error('Error cargando recomendaciones:', error);
        modalRecomendaciones.value.error = 'No se pudieron cargar las recomendaciones. Verifica tu conexión.';
    } finally {
        modalRecomendaciones.value.cargando = false;
    }
};

// Usar el primer modelo recomendado automáticamente
const usarPrimerRecomendado = () => {
    if (modalRecomendaciones.value.recomendaciones?.recomendados?.length > 0) {
        const primerRecomendado = modalRecomendaciones.value.recomendaciones.recomendados[0];
        if (primerRecomendado.disponible) {
            seleccionarModeloDesdeModal(primerRecomendado.modelo);
        } else {
            // Buscar el primer modelo disponible
            const modeloDisponible = modalRecomendaciones.value.recomendaciones.recomendados.find(m => m.disponible);
            if (modeloDisponible) {
                seleccionarModeloDesdeModal(modeloDisponible.modelo);
            } else {
                alert('No hay modelos recomendados disponibles');
            }
        }
    }
};

const abrirModalRecomendaciones = (tipoPregunta, selectorId) => {
    modalRecomendaciones.value.tipoPregunta = tipoPregunta;
    modalRecomendaciones.value.selectorActual = selectorId;
    modalRecomendaciones.value.visible = true;
    modalRecomendaciones.value.error = null;
    modalRecomendaciones.value.recomendaciones = null;
    modalRecomendaciones.value.mostrarNoRecomendados = false;
    modalRecomendaciones.value.noMostrarDeNuevo = false;
    
    // Cargar recomendaciones automáticamente
    cargarRecomendaciones();
};

const cerrarModalRecomendaciones = () => {
    if (modalRecomendaciones.value.noMostrarDeNuevo) {
        localStorage.setItem('ocultarAyudaModelos', 'true');
    }
    modalRecomendaciones.value.visible = false;
    modalRecomendaciones.value.selectorActual = null;
    modalRecomendaciones.value.error = null;
    modalRecomendaciones.value.recomendaciones = null;
};

const seleccionarModeloDesdeModal = (modeloSeleccionado) => {
    const selector = document.getElementById(modalRecomendaciones.value.selectorActual);
    if (selector) {
        selector.value = modeloSeleccionado;
        // Disparar evento change para que Vue detecte el cambio
        selector.dispatchEvent(new Event('change'));
    }
    cerrarModalRecomendaciones();
};


// ======= FIN FUNCIONES MODAL =======

// Escuchar evento de carga de examen
window.addEventListener('cargar-examen', (event) => {
    Object.assign(examen, event.detail.examenData);
});

// Detectar y cargar examen desde cargar.html
const examenParaCargar = localStorage.getItem('examenParaCargar');
if (examenParaCargar) {
    localStorage.removeItem('examenParaCargar');
    
    // Cargar examen por ID
    //fetch(`http://127.0.0.1:5000/api/examen/${examenParaCargar}`)
    fetch(`http://127.0.0.1:5000/api/examen/${examenParaCargar}?email=${currentUserEmail}`)
        .then(response => response.json())
        .then(data => {
            if (data.examenDataJson) {
                const examenData = JSON.parse(data.examenDataJson);
                Object.assign(examen, {
                    id: examenData.id,
                    nombreExamen: examenData.nombreExamen,
                    tipoExamen: examenData.tipoExamen,
                    fecha: examenData.fecha,
                    profesor: examenData.profesor,
                    profesorId: examenData.profesorId,
                    preguntasMarcar: examenData.preguntasMarcar || [],
                    preguntasLibres: examenData.preguntasLibres || [],
                    casosUso: examenData.casosUso || [],
                    bloqueado: true
                });
                modoEstudiante.value = true;
                message.value = 'Examen cargado correctamente';
                messageType.value = 'success';
            }
        })
        .catch(error => {
            console.error('Error cargando examen:', error);
            message.value = 'Error al cargar el examen';
            messageType.value = 'error';
        });
}

// **** FIN: REEMPLAZO ****

        return {
            examen,
            activeTab,
            message,
            messageType,
            modoEstudiante,
            totalPreguntas,
            puntajeTotal,
            uploadProgress,
            isUploading,
            isPublishing,
            publicUrl,
            modoPlantillaProfesor,
            guardarRespuestasEnBD,
            mostrarPlayground,
            generandoImagen,
            imagenGenerada,
            preguntaActual,
            tipoActual,
            playgroundConfig,
            selectorAppwrite,
            modalRecomendaciones,
            modeloRespuestas,
            agregarPreguntaMarcar,
            eliminarPreguntaMarcar,
            agregarOpcion,
            eliminarOpcion,
            agregarPreguntaLibre,
            eliminarPreguntaLibre,
            agregarCasoUso,
            eliminarCasoUso,
            subirArchivoAnexo,
            eliminarArchivoAnexo,
            abrirPlayground,
            cerrarPlayground,
            generarImagenIA,
            regenerarImagen,
            usarImagenGenerada,
            subirImagenDirecta,
            toggleBloqueo,
            cambiarModo,
            inicializarRespuestas,
            generarPreguntaIA,
            handleFileUpload,
            eliminarArchivo,
            limpiarCacheExamen,
            crearVistaPrevia,
            guardarPDF,
            publicarExamenWeb,
            activarModoPlantilla,
            publicarPlantillaWeb,
            cambiarModoDesdePlantilla,
            submitPlantilla,
            mostrarPlantillaRespuestas,
            recolectarEtiquetasPreguntas,
            subirArchivoPregunta,
            verPlantillaLocal,
            mostrarNotificacion,
            formatearFecha,
            formatearTamaño,
            generarUrlDescarga,
            confirmarSeleccion,
            seleccionarArchivo,
            cargarArchivosAppwrite,
            abrirSelectorAppwrite,
            cerrarSelectorAppwrite,
            mostrarModalSelector,
            cerrarModalSelector,
            cargarArchivosModal,
            mostrarArchivosEnModal,
            mostrarErrorEnModal,
            seleccionarArchivoModal,
            mostrarBusquedaExamenes,
            buscarExamenes,
            /*bloquearCopyPaste,
            bloquearClickDerecho,
            bloquearSeleccion,
            bloquearArrastrar,
            mostrarAdvertenciaCopyPaste,
            aplicarProteccionDinamica,
            mostrarArchivo,
            eliminarArchivoFormulario,*/
            abrirModalRecomendaciones,
            cerrarModalRecomendaciones,
            seleccionarModeloDesdeModal,
            cargarRecomendaciones,
            usarPrimerRecomendado,
            abrirRecursosEducativos,
            confirmarSeleccionArchivo,
            obtenerCreditos,              
            actualizarMostrarCreditos,
            verificarTipoCuenta,
            mostrarAlertaCreditosBajos,
            /*toggleProtecciones,
            toggleProteccionCopyPaste*/
        };
    }
}

window.cargarExamenSeleccionado = async function(examenId) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/examen/${examenId}?email=${currentUserEmail}`);
        const data = await response.json();
        
        if (data.examenDataJson) {
            const examenData = JSON.parse(data.examenDataJson);
            
            // USAR EL EVENTO PERSONALIZADO PARA COMUNICAR CON VUE
            window.dispatchEvent(new CustomEvent('cargar-examen', {
                detail: { examenData: examenData }
            }));
            
            alert('✅ Examen cargado correctamente');
            window.close(); // Cerrar popup
        }
    } catch (error) {
        alert('❌ Error al cargar examen');
    }
}

// Agregar al final del archivo, fuera de Vue
window.cerrarModalSelector = function(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById('modalSelectorAppwrite').style.display = 'none';
    
    // Limpiar selección
    window.archivoSeleccionadoModal = null;
    if (document.getElementById('btn-confirmar')) {
        document.getElementById('btn-confirmar').disabled = true;
    }
 }
 
 window.seleccionarArchivoModal = function(archivo) {
    console.log("Archivo seleccionado:", archivo.name);
    
    // Quitar selección anterior
    document.querySelectorAll('.archivo-card').forEach(card => {
        card.classList.remove('selected');
        card.style.backgroundColor = '';
        card.style.border = '';
    });
    
    // Agregar selección actual
    event.currentTarget.classList.add('selected');
    event.currentTarget.style.backgroundColor = '#e3f2fd';
    event.currentTarget.style.border = '2px solid #2196f3';
    
    window.archivoSeleccionadoModal = archivo;
    
    // Habilitar y cambiar color del botón
    const btnConfirmar = document.getElementById('btn-confirmar');
    btnConfirmar.disabled = false;
    btnConfirmar.style.background = '#28a745';
}
 
 window.confirmarSeleccionArchivo = function() {
    if (!window.archivoSeleccionadoModal) {
        alert('Por favor selecciona un archivo');
        return;
    }
 
    // Usar la instancia de Vue para acceder a selectorAppwrite
    const item = window.itemActualModal;
    
    if (!item) {
        alert('Error: No se encontró el item');
        return;
    }
    
    // Guardar información del archivo
    item.archivoId = window.archivoSeleccionadoModal.$id;
    item.archivoNombre = window.archivoSeleccionadoModal.name;
    item.archivoUrl = `https://cloud.appwrite.io/v1/storage/buckets/APPWRITE_BUCKET_DOCUMENTO_ANEXO_EXAMEN/files/${window.archivoSeleccionadoModal.$id}/view?project=67e565df001722171560`;
    item.archivoTamaño = window.archivoSeleccionadoModal.sizeOriginal;
    item.archivoTipo = window.archivoSeleccionadoModal.mimeType;

    // AGREGAR ESTE DEBUG:
    console.log("Archivo adjuntado a item:", item);
    console.log("archivoNombre:", item.archivoNombre);
    console.log("archivoUrl:", item.archivoUrl);
 
    // Cerrar modal
    window.cerrarModalSelector();
    
    console.log('Archivo adjuntado correctamente');
 }

 
