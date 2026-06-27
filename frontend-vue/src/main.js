import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Importa tus estilos globales (donde tienes configurado Tailwind)
import './assets/main.css' 

const app = createApp(App)

// Pinia permite gestionar el estado global (ej: datos de sesión, carrito, estado de caja)
app.use(createPinia())

// Vue Router para la navegación entre vistas
app.use(router)

app.mount('#app')