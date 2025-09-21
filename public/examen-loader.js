// Exponer las funciones de Vue globalmente
window.vueExports = {
    ref: Vue.ref,
    reactive: Vue.reactive,
    onMounted: Vue.onMounted,
    inject: Vue.inject
};