// firebase-config.js
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore, FieldValue } from "firebase/firestore";
import { getStorage } from "firebase/storage";

const firebaseConfig = {
  apiKey: "AIzaSyA3xBEqByp6HHo1rM1hwhtDB4Q0zth-dJ0",
  authDomain: "examen-online-c34c0.firebaseapp.com",
  projectId: "examen-online-c34c0",
  storageBucket: "examen-online-c34c0.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef1234567890abcdef"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const storage = getStorage(app);

export { auth, db, storage, FieldValue };
