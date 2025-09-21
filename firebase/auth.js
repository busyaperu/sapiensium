import { auth } from "./firebase-config";
import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "firebase/auth";

// Función para registrar usuario (Signup)
export async function signup(email, password) {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    console.log("Usuario registrado:", userCredential.user);
    return userCredential.user;
  } catch (error) {
    console.error("Error en el registro:", error.message);
    throw error;
  }
}

// Función para iniciar sesión (Login)
export async function login(email, password) {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    console.log("Usuario autenticado:", userCredential.user);
    return userCredential.user;
  } catch (error) {
    console.error("Error en el login:", error.message);
    throw error;
  }
}

// Función para cerrar sesión (Logout)
export async function logout() {
  try {
    await signOut(auth);
    console.log("Sesión cerrada correctamente");
  } catch (error) {
    console.error("Error al cerrar sesión:", error.message);
  }
}
