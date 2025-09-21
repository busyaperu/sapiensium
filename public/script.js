// script.js - Convertido a Appwrite Auth
import { databases, account, config } from './appwrite-config.js';
import { Query, Client, Databases, Account } from "https://cdn.jsdelivr.net/npm/appwrite@13.0.1/+esm";


document.addEventListener('DOMContentLoaded', () => {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const forms = document.querySelectorAll('.form');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    
    // Controla el cambio entre pestañas
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            console.log('Tab clicked:', button.textContent);
            tabButtons.forEach(btn => btn.classList.remove('active'));
            forms.forEach(form => form.classList.remove('active'));
            
            button.classList.add('active');
            const formName = button.getAttribute('data-form');
            const targetForm = document.getElementById(`${formName}-form`);
            if (targetForm) {
                targetForm.classList.add('active');
            } else {
                console.error(`Form with ID "${formName}-form" not found`);
            }
        });
    });

    // Función para registrar un usuario usando Appwrite Auth + Database
    async function registerUser(email, password, userData) {
        try {
            // 1. Crear usuario en Appwrite Auth
            const user = await account.create(
                'unique()', // ID único automático
                email,
                password,
                userData.nombre // Nombre del usuario
            );
            
            console.log('Usuario creado en Auth:', user);

            // 2. CREAR SESIÓN TEMPORAL INMEDIATAMENTE 
            await account.createEmailSession(email, password);
            
            // 3. Guardar documento con usuario autenticado en Appwrite Database
            const userDocument = await databases.createDocument(
                config.databaseId,
                config.collectionDatosProfesores,
                'unique()',
                {
                    userId: user.$id,
                    email: email,
                    nombre: userData.nombre,
                    documento_id: userData.documento,
                    telefono: userData.telefono, 
                    institucion: userData.institucion,
                    curso: userData.curso
                }
            );
            
            console.log('Datos guardados en DB:', userDocument);
            return { user, userDocument };
            
        } catch (error) {
            console.error("Error en el registro:", error);
            throw error;
        }
    }

    // Función para obtener datos del usuario desde la base de datos
    async function getUserData(userId) {
        try {
            const response = await databases.listDocuments(
                config.databaseId,
                config.collectionUsuarios,
                [
                    `userId=${userId}`
                ]
            );
            
            if (response.documents.length > 0) {
                return response.documents[0];
            }
            return null;
        } catch (error) {
            console.error("Error obteniendo datos del usuario:", error);
            return null;
        }
    }

    // Manejador del formulario de registro
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;

        // *** AGREGAR VALIDACIÓN AQUÍ ***
        if (email.endsWith('@sapiensium.com')) {
            alert('Los usuarios de Sapiensium deben registrarse a través del portal administrativo.');
            return;
        }
        const userData = {
            documento: document.getElementById('documento').value,
            nombre: document.getElementById('nombre').value,
            telefono: document.getElementById('telefono').value,
            institucion: document.getElementById('institucion').value,
            curso: document.getElementById('curso').value
        };
        
        try {
            const result = await registerUser(email, password, userData);
            
            // *** CREAR SESIÓN TEMPORAL PARA EL USUARIO RECIÉN CREADO ***
            await account.createEmailSession(email, password);

            const role = 'cliente_externo'; // Todos los registros públicos son clientes externos

            console.log('=== DEBUG VARIABLES ===');
            console.log('config completo:', config);
            console.log('databaseId:', config.databaseId);
            console.log('collectionUserRoles:', config.collectionUserRoles);
            console.log('role a guardar:', role);
            console.log('user_id:', result.user.$id);
            
            await databases.createDocument(
                config.databaseId,
                config.collectionUserRoles,
                'unique()',
                {
                    user_id: result.user.$id,
                    role: role
                }
            );
            
            // Cerrar sesión después de crear el rol
            await account.deleteSession('current');

            alert('Profesor registrado correctamente. Ahora puedes iniciar sesión.');
            signupForm.reset();
            tabButtons[0].click();
            
        } catch (error) {
            if (error.message.includes('user with the same id, email, or phone already exists')) {
                alert('Error: Ya existe un usuario con ese email. Por favor usa otro email o inicia sesión.');
            } else {
                alert(`Error en el registro: ${error.message}`);
            }
        }
    });

    // Manejador del formulario de login
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        // *** AGREGAR VALIDACIÓN AQUÍ ***
        if (email.endsWith('@sapiensium.com')) {
            alert('Los usuarios de Sapiensium deben acceder a través del portal administrativo.');
            return;
        }

        try {
            // Cerrar cualquier sesión existente primero
            try {
                await account.deleteSession('current');
                console.log('Sesión previa cerrada');
            } catch (error) {
                // Si no hay sesión previa, continuar
                console.log('No había sesión previa');
            }
            
            // Crear nueva sesión
            await account.createEmailSession(email, password);
        
            // Verificar saldo de créditos (solo para usuarios externos)
            if (!email.endsWith('@sapiensium.com')) {
                const hasCredits = await verificarSaldoCreditos(email);
                
                if (!hasCredits) {
                    alert('No tienes créditos suficientes. Necesitas comprar un plan para ingresar.');
                    window.location.replace("public/carrito.html?required=true");
                    return;
                }
            }
            
            // *** NUEVO: Obtener el rol del usuario ***
            const currentUser = await account.get();
            
            // Buscar el rol en la colección user_roles
            const roleQuery = await databases.listDocuments(
                config.databaseId,
                config.collectionUserRoles,
                [Query.equal('user_id', currentUser.$id)]
            );
            
            const userRole = roleQuery.documents.length > 0 ? roleQuery.documents[0].role : 'cliente_externo';
            
            // Guardar datos con el rol incluido
            localStorage.setItem('currentUser', JSON.stringify({
                email: email,
                nombre: 'Profesor',
                role: userRole,
                userId: currentUser.$id
            }));
            localStorage.setItem('isAuthenticated', 'true');
            
            // Redirigir inmediatamente
            window.location.replace("index.html");
            
        } catch (error) {
            if (error.message.includes('Invalid credentials')) {
                alert('Error: Email o contraseña incorrectos. Verifica tus datos.');
            } else {
                alert(`Error en el login: ${error.message}`);
            }
        }
    });

    async function verificarSaldoCreditos(email) {
        try {
            console.log('Email buscado:', email);
            
            const creditosClient = new Client()
                .setEndpoint(config.endpoint)
                .setProject("68b9b7dd98304d1d2268");
                
            const creditosDatabases = new Databases(creditosClient);
            
            console.log('Consultando créditos sin autenticación...');
            
            const response = await creditosDatabases.listDocuments(
                "68b9b80f1fae24f27525",
                config.collectionUsuariosCreditos,
                [`equal("email", "${email}")`]
            );
            
            console.log('Documentos encontrados:', response.documents.length);
            
            if (response.documents.length === 0) {
                console.log('Usuario no encontrado en la base de datos');
                return false;
            }
            
            const usuario = response.documents[0];
            console.log('Usuario encontrado:', usuario);
            
            const saldoDisponible = usuario.saldo_actual || 0;
            console.log('Saldo disponible:', saldoDisponible);
            console.log('Verificación >= 10:', saldoDisponible >= 10);
            
            return saldoDisponible >= 10;
            
        } catch (error) {
            console.error('Error verificando créditos:', error);
            return false;
        }
    }

    // Función para cerrar sesión
    async function logout() {
        try {
            await account.deleteSession('current');
            localStorage.removeItem('currentUser');
            localStorage.removeItem('isAuthenticated');
            console.log('Sesión cerrada');
            location.reload();
        } catch (error) {
            console.log('Error cerrando sesión:', error);
            localStorage.removeItem('currentUser');
            localStorage.removeItem('isAuthenticated');
            location.reload();
        }
    }

    // Hacer la función global para poder usarla desde la consola
    window.logout = logout;
    
});

