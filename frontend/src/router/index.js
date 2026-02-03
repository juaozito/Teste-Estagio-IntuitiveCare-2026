import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import DetalheOperadora from '../views/DetalheOperadora.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/operadora/:cnpj', // O ":cnpj" é um parâmetro dinâmico
    name: 'DetalheOperadora',
    component: DetalheOperadora,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router