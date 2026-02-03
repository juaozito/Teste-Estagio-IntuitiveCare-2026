import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css' // Opcional, se quiser carregar seu CSS

const app = createApp(App)

app.use(router) // Conecta o roteador
app.mount('#app')