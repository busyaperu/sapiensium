export const config = {
    apiUrl: 'http://localhost:5000/api',
    iaApiKey: 'your-together-ai-api-key', // Esta clave sería reemplazada en un entorno real
    dbConfig: {
        host: 'db.example.neon.tech',
        database: 'examenes',
        user: 'usuario_db',
        password: 'contraseña_segura'
    },
    pdfOptions: {
        margin: 10,
        format: 'a4',
        orientation: 'portrait'
    },
    toolsLinks: [
        { name: 'GitHub', url: 'https://github.com/' },
        { name: 'Stack Overflow', url: 'https://stackoverflow.com/' },
        { name: 'W3Schools', url: 'https://www.w3schools.com/' },
        { name: 'MDN Web Docs', url: 'https://developer.mozilla.org/' },
        { name: 'CodePen', url: 'https://codepen.io/' }
    ],

    // MANTENER ESTA SECCIÓN (para autenticación):
    appwrite: {
        endpoint: 'https://cloud.appwrite.io/v1',
        projectId: '6880167c001039506b2d',
        databaseId: '6880183a00216863c2e9',
        collectionUsuarios: '683f7e1f0014a6d2cffb',
        bucketId: '6880173a0002818c5236'
    },

    // AGREGAR ESTA SECCIÓN (para pagos):
    pagosAppwrite: {
        endpoint: 'https://nyc.cloud.appwrite.io/v1',
        projectId: '6880167c001039506b2d',
        apiKey: 'standard_eb59104cb6f4424521c24b749d7b56a1fc2712b6c4c9a733368f8c108bab692072f50f52294540f072075e80de3eefbbcb5d9c8193fab22ef9b29b760ccf840af55ee658003662bc414e8350d9d1b28cf908db37e9dda2bfbf83239287df27be703d64a665b31a00b2e4fbcefc429950959324e0f7572281575c593fb06b091b',
        databaseId: '6880183a00216863c2e9',
        collectionTransacciones: '68801888002a6917bc47',
        collectionTemp: '68815536002647eb06a1', 
        bucketId: '6880173a0002818c5236'
    }
};

