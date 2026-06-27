import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // <-- ¡Esto es vital!
// Busca esta línea y cámbiala por la ruta correcta:
import './assets/main.css'
const app = createApp(App)

app.use(router) // <-- ¡Esta línea es la que hace que App.vue entienda a las rutas!
app.mount('#app')