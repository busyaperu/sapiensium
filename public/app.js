import { createApp } from 'vue';
import { ProfesorComponent } from './components/profesor.js';
import { ExamenComponent } from './components/examen.js';
import { EvaluacionComponent } from './components/evaluacion.js';
import { config } from './config.js';
import { ApiService } from './services/api-service.js';
import { reactive } from 'vue';


// Verificar autenticación de forma estricta al cargar la aplicación
if (!localStorage.getItem('currentUser') || localStorage.getItem('currentUser') === 'null') {
    window.location.href = "loging.html";
    // Detener la ejecución del resto del script
    throw new Error("Redirigiendo a login");
}

// Verificar autenticación antes de montar la aplicación
const currentUser = localStorage.getItem('currentUser');
if (!currentUser || currentUser === 'null') {
    // Si no hay usuario autenticado, redirigir a login
    window.location.href = "loging.html";
    // Detener la ejecución del resto del script
    throw new Error("Redirigiendo a login");
}

// Crea un estado global reactivo
const globalState = reactive({
    isModoEstudiante: false
});

const app = createApp({
    data() {
        return {
            currentSection: 'profesor',
            currentComponent: ProfesorComponent,
            user: currentUser ? JSON.parse(currentUser) : null,
            globalState ,// Exponer el estado global
            lastSection: 'profesor' // ✅ Añadir esto al original
        };
    },

    // Añade este bloque de mounted
    mounted() {
        console.log('Usuario al montar:', this.user);
        console.log('Role del usuario:', this.user ? this.user.role : 'no user');
    // Escuchar el evento personalizado para cambio de modo estudiante
    window.addEventListener('modo-estudiante-cambiado', (event) => {
        this.globalState.isModoEstudiante = event.detail.modoEstudiante;
        });
    },
    
    methods: {
        navigateTo(section) {
            this.lastSection = this.currentSection;
            this.currentSection = section;
            switch(section) {
                case 'profesor':
                    this.currentComponent = ProfesorComponent;
                    break;
                case 'examen':
                    this.currentComponent = ExamenComponent;
                    break;
                case 'evaluacion':
                    this.currentComponent = EvaluacionComponent;
                    break;
            }
        },
        
        async cerrarSesion() {
            if (confirm('¿Estás seguro que deseas cerrar sesión?')) {
                try {
                    const { account } = await import('./appwrite-config.js');
                    await account.deleteSession('current');
                } catch (error) {
                    console.log('Error cerrando sesión:', error);
                }
                
                // Obtener tipo de usuario antes de limpiar localStorage
                const userData = JSON.parse(localStorage.getItem('currentUser') || '{}');
                const isAdmin = ['admin', 'validador', 'supervisor', 'operador'].includes(userData.role);
                
                localStorage.removeItem('currentUser');
                localStorage.removeItem('isAuthenticated');
                localStorage.removeItem('tempCredentials');
                
                // Redirigir según tipo de usuario
                if (isAdmin) {
                    window.location.replace('admin-auth.html');
                } else {
                    window.location.replace('loging.html');
                }
            }
        }
    },
    provide() {
        return {
            apiService: new ApiService(config.apiUrl)
        }
    }
});


app.mount('#app');

