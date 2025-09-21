// appwrite-config.js
// Configuración y utilidades para Appwrite usando módulos ES en el navegador.
// Provee una exportación nombrada "Appwrite" y el objeto "config" para evitar errores de importación.
import { Client, Databases, ID, Storage, Account } from "https://cdn.jsdelivr.net/npm/appwrite@13.0.1/+esm";



//Parámetros de conexión a Appwrite.
export const config = {
  endpoint: "https://appwrite.sapiensium.com/v1",
  projectId: "68b8bd1c726aac025c40",
  databaseId: "67e566170025284a0b1a",
  bucketId: "67e579bd0018f15c73c3",
  collectionDatosAlumno: "67f5ca28002e23e4d290",
  collectionExamenesCompletos: "67f82fac00345dbf7b06",
  collectionDatosProfesores: "683f7e1f0014a6d2cffb",
  collectionUserRoles: "68bd9bb28b61dc775483",
  collectionUsuariosCreditos: "68c19ba15c0d1a8461b3",
  creditosProjectId: "68b9b7dd98304d1d2268",
  creditosDatabaseId: "68b9b80f1fae24f27525"
  };

/**
 * Cliente principal de Appwrite y utilidades asociadas.
 */
const client = new Client()
  .setEndpoint(config.endpoint)
  .setProject(config.projectId);

const databases = new Databases(client);
const account = new Account(client);  // ← AGREGAR ESTA LÍNEA

/**
 * Objeto SDK agrupado que se expone como "Appwrite".
 * Incluye las clases Client, Databases, ID y las instancias listas para usar.
 */
export const Appwrite = {
  Client,
  Databases,
  ID,
  client,
  databases,
  account,  // ← AGREGAR
  Storage
};

/**
 * Inicializa Appwrite y devuelve las referencias necesarias.
 * Esta función puede ser llamada desde tu código para obtener rápidamente
 * las instancias y saber si el SDK está listo.
 */
export function initializeAppwrite() {
  return {
    client,
    databases,
    config,
    ready: true,
    sdk: Appwrite
  };
}

// Exportación por defecto de un objeto de conveniencia
export default {
  initializeAppwrite,
  client,
  databases,
  config,
  Appwrite
};

// Exportaciones individuales
export { databases, account };


