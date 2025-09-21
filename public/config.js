// Configuración del sistema
export const config = {
    // Ajustes de la aplicación
    appName: "Sistema de Registro",
    
    // Validación de formularios
    validation: {
        minPasswordLength: 6,
        carnetFormat: /^\d{8}$/ // Formato ejemplo: 8 dígitos
    },
    
    // URLs para API (en caso de implementar backend)
    apiEndpoints: {
        login: "/api/login",
        signup: "/api/signup"
    },

    pagosAppwrite: {
        endpoint: 'https://appwrite.sapiensium.com/v1',
        projectId: '68b9b7dd98304d1d2268',
        apiKey: 'a4b1fb952131d67d62683abf9b6a5605518cf13fcf0b683df3ea67dc694f487e582c9d723fbc655ade93005fee8822868b6cc74cb940882d8acee2c549fb1907217d92783c5e4200f65fb2f290eb92557ae65ca79e767ba73ee43b6e907c63dd4a5ba1a4a61401b9d9d48837b2039be2da1844468a35d8784c09301d3b50c016', // La API Key que creaste
        databaseId: '68b9b80f1fae24f27525', 
        collectionTransacciones: 'transacciones'
    },

    // Lógica de créditos según tu plan
    creditsSystem: {
        dollarsPerMonth: 20,          // $20 por mes (suscripción)
        creditsPerMonth: 3030,        // 3,030 créditos por mes
        isSubscription: true,         // Modelo de suscripción mensual
        minCreditsToAccess: 10        // Créditos mínimos para acceder
}
};





