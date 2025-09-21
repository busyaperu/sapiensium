// Verificación simple sin efectos secundarios
if (!localStorage.getItem('currentUser') && !window.location.href.includes('loging.html')) {
    window.location.replace("loging.html");
}