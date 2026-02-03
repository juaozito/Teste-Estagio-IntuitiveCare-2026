<template>
  <div>
    <div class="filters">
      <input v-model="busca" @input="buscarDados" placeholder="Filtrar por nome ou CNPJ..." />
    </div>

    <table v-if="!loading">
      <thead>
        <tr>
          <th>Registro ANS</th>
          <th>Razão Social</th>
          <th>CNPJ</th>
          <th>UF</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="op in operadoras" :key="op.RegistroANS">
          <td>{{ op.RegistroANS }}</td>
          <td>{{ op.RazaoSocial }}</td>
          <td>{{ op.CNPJ }}</td>
          <td>{{ op.UF }}</td>
          <td>
            <router-link :to="'/operadora/' + op.CNPJ">Ver Histórico</router-link>
          </td>
        </tr>
      </tbody>
    </table>
    
    <div v-else>Carregando...</div>

    <div class="pagination">
      <button :disabled="page === 1" @click="mudarPagina(-1)">Anterior</button>
      <span>Página {{ page }}</span>
      <button :disabled="operadoras.length < limit" @click="mudarPagina(1)">Próxima</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const operadoras = ref([]);
const loading = ref(true);
const page = ref(1);
const limit = 10;
const busca = ref('');

const carregar = async () => {
  loading.value = true;
  try {
    const { data } = await api.get('/operadoras', { 
      params: { page: page.value, limit: limit, q: busca.value } 
    });
    operadoras.value = data.data;
  } finally {
    loading.value = false;
  }
};

const mudarPagina = (dir) => {
  page.value += dir;
  carregar();
};

const buscarDados = () => {
  page.value = 1; // Reinicia a página ao buscar
  carregar();
};

onMounted(carregar);
</script>