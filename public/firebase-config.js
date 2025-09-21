// firebase-config.js
// Configuración de Firebase
const firebaseConfig = {
  apiKey: "AIzaSyA3xBEqByp6HHo1rM1hwhtDB4Q0zth-dJ0",
  authDomain: "examen-online-c34c0.firebaseapp.com",
  projectId: "examen-online-c34c0",
  messagingSenderId: "16388106290",
  appId: "1:16388106290:web:1f97dd0f39a85a1a9fb42b",
  measurementId: "G-7X1FX9M2SC"
};

// Inicializar Firebase
const app = firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();
const FieldValue = firebase.firestore.FieldValue;

// Exportar servicios
export { auth, db, FieldValue };
