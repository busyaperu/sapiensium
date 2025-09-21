import { doc, setDoc } from "firebase/firestore";
import { db } from "./firebase-config.js";

export class ApiService {
    constructor(apiUrl) {
        this.apiUrl = apiUrl || 'http://localhost:5000/api';
    }
    
    async publicarExamen(examenData) {
        try {
            console.log("Intentando publicar examen con ID:", examenData.id);
            console.log("Datos a guardar:", {
                exam_id: examenData.id,
                name: examenData.profesor || 'No disponible',
                profesor_id: examenData.profesorId || 'No disponible',
                empty_exam: window.location.origin + '/examen-vista.html?id=' + examenData.id
            });
            
            await setDoc(doc(db, "examen_generado", examenData.id), {
                exam_id: examenData.id,
                name: examenData.profesor || 'No disponible',
                profesor_id: examenData.profesorId || 'No disponible',
                empty_exam: window.location.origin + '/examen-vista.html?id=' + examenData.id
            });
            
            console.log("Examen publicado exitosamente en Firestore");
            return { success: true, message: 'Examen publicado con éxito' };
        } catch (error) {
            console.error("Error al publicar:", error);
            console.error("Detalles del error:", error.code, error.message);
            throw error;
        }
    }
    
    async guardarExamenPDF(examenData) {
        console.log('Guardando examen en PDF:', examenData);
        
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    message: 'PDF guardado con éxito',
                    data: { id: examenData.id }
                });
            }, 1000);
        });
    }
    
    async registrarAlumno(alumnoData) {
        console.log('Registrando alumno:', alumnoData);
        
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    message: 'Alumno registrado con éxito',
                    data: { ...alumnoData, id: 'A' + Date.now() }
                });
            }, 1000);
        });
    }
    
    async obtenerExamenesDisponibles(filtros) {
        console.log('Obteniendo exámenes disponibles con filtros:', filtros);
        
        // Datos de ejemplo para simular respuesta de la API
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    data: [
                        {
                            id: 'EXAM-123456',
                            fecha: '2023-08-15',
                            profesor: 'Dr. Juan Pérez',
                            titulo: 'Examen Parcial de Programación I'
                        },
                        {
                            id: 'EXAM-654321',
                            fecha: '2023-08-20',
                            profesor: 'Dra. María López',
                            titulo: 'Examen Final de Desarrollo Web'
                        }
                    ]
                });
            }, 800);
        });
    }
    
    async obtenerExamen(examenId) {
        console.log('Obteniendo detalles del examen:', examenId);
        
        // Datos de ejemplo para simular respuesta de la API
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    data: {
                        id: examenId,
                        fecha: '2023-08-15',
                        profesor: 'Dr. Juan Pérez',
                        titulo: 'Examen Parcial de Programación I',
                        preguntasMarcar: [
                            {
                                numero: 1,
                                texto: '¿Cuál es el lenguaje de programación más utilizado para desarrollo web?',
                                puntaje: 1,
                                opciones: [
                                    { texto: 'Java' },
                                    { texto: 'Python' },
                                    { texto: 'JavaScript' },
                                    { texto: 'C++' }
                                ]
                            },
                            {
                                numero: 2,
                                texto: '¿Qué significa HTML?',
                                puntaje: 1,
                                opciones: [
                                    { texto: 'Hyper Text Markup Language' },
                                    { texto: 'High Tech Modern Language' },
                                    { texto: 'Home Tool Markup Language' },
                                    { texto: 'Hyperlinks and Text Markup Language' }
                                ]
                            }
                        ],
                        preguntasLibres: [
                            {
                                numero: 3,
                                texto: 'Explique el concepto de programación orientada a objetos.',
                                puntaje: 2
                            }
                        ],
                        casosUso: [
                            {
                                numero: 4,
                                descripcion: 'Una tienda en línea necesita implementar un sistema de carrito de compras que permita a los usuarios agregar productos, eliminarlos y calcular el total.',
                                pregunta: 'Diseñe una solución utilizando programación orientada a objetos. Identifique las clases, métodos y atributos necesarios.',
                                puntaje: 3
                            }
                        ]
                    }
                });
            }, 800);
        });
    }
    
    async guardarRespuestasExamen(datosRespuestas) {
        console.log('Guardando respuestas de examen:', datosRespuestas);
        
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    message: 'Respuestas guardadas con éxito',
                    data: { id: datosRespuestas.examenId }
                });
            }, 1000);
        });
    }
    
    async cargarExamenResuelto(formData) {
        console.log('Cargando examen resuelto:', formData);
        
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    message: 'Examen cargado con éxito',
                    data: {
                        id: formData.get('idExamen'),
                        alumnoId: formData.get('idAlumno'),
                        fechaCarga: new Date().toISOString()
                    }
                });
            }, 1500);
        });
    }
    
    async obtenerPDFExamen(examenId, alumnoId) {
        console.log('Obteniendo PDF del examen:', examenId, 'alumno:', alumnoId);
        
        // En una implementación real, esto devolvería un blob de datos PDF
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    data: new Blob(['PDF content would be here'], { type: 'application/pdf' })
                });
            }, 800);
        });
    }
    
    async eliminarExamenResuelto(examenId, alumnoId) {
        console.log('Eliminando examen resuelto:', examenId, 'alumno:', alumnoId);
        
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    message: 'Examen eliminado con éxito'
                });
            }, 800);
        });
    }
    
    async buscarExamenes(filtros) {
        console.log('Buscando exámenes con filtros:', filtros);
        
        // Datos de ejemplo para simular respuesta de la API
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    data: [
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
                        },
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
                    ]
                });
            }, 800);
        });
    }
    
    async evaluarExamen(examenId, alumnoId) {
        console.log('Evaluando examen:', examenId, 'alumno:', alumnoId);
        
        // Esta función en realidad sería una llamada al API de IA para evaluación
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    message: 'Evaluación completada con éxito',
                    data: {
                        calificacionFinal: 16.5,
                        puntajeTotal: 20,
                        detalle: [
                            // Detalles de evaluación...
                        ]
                    }
                });
            }, 5000); // Simulamos que toma tiempo evaluar
        });
    }
    
    async guardarEvaluacion(evaluacionData) {
        console.log('Guardando evaluación:', evaluacionData);
        
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    message: 'Evaluación guardada con éxito',
                    data: { id: evaluacionData.idExamen }
                });
            }, 1000);
        });
    }
    
    async obtenerEvaluacion(examenId, alumnoId) {
        console.log('Obteniendo evaluación:', examenId, 'alumno:', alumnoId);
        
        // Datos de ejemplo para simular respuesta de la API
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    data: {
                        idExamen: examenId,
                        idAlumno: alumnoId,
                        calificacion: 16.5,
                        puntajeTotal: 20,
                        fechaEvaluacion: '2023-08-13T09:15:00',
                        detalle: [
                            // Detalles de evaluación...
                        ]
                    }
                });
            }, 800);
        });
    }
    
    async enviarResultadoAlumno(examenId, alumnoId) {
        console.log('Enviando resultado a alumno:', examenId, 'alumno:', alumnoId);
        
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    message: 'Resultado enviado con éxito al alumno'
                });
            }, 1200);
        });
    }
}

