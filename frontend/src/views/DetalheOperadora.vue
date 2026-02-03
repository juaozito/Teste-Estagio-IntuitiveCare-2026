<template>
  <div class="detalhe-container">
    <router-link to="/" class="btn-voltar">← Voltar para a Listagem</router-link>

    <div v-if="loading" class="status">Carregando dados da operadora...</div>

    <div v-else-if="erro" class="status erro">{{ erro }}</div>

    <div v-else>
      <section class="card-info">
        <h2>{{ operadora.RazaoSocial }}</h2>
        <p><strong>CNPJ:</strong> {{ operadora.CNPJ }}</p>
        <p><strong>Registro ANS:</strong> {{ operadora.RegistroANS }}</p>
        <p><strong>Modalidade:</strong> {{ operadora.Modalidade }}</p>
        <p><strong>UF:</strong> {{ operadora.UF }}</p>
      </section>

      <section class="historico">
        <h3>Histórico de Despesas</h3>
        <table v-if="despesas.length > 0">
          <thead>
            <tr>
              <th>Ano</th>
              <th>Trimestre</th>
              <th>Valor da Despesa</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in despesas" :key="index">
              <td>{{ item.ano }}</td>
              <td>{{ item.trimestre }}º Trimestre</td>
              <td>{{ formatarMoeda(item.valor_despesa) }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else>Nenhuma despesa registrada para esta operadora.</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../services/api';

const route = useRoute();
const cnpj = route.params.cnpj;

const operadora = ref(null);
const despesas = ref([]);
const loading = ref(true);
const erro = ref(null);

const formatarMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
};

const buscarDados = async () => {
  loading.value = true;
  try {
    // 1. Busca detalhes cadastrais
    const resOp = await api.get(`/operadoras/${cnpj}`);
    operadora.value = resOp.data;

    // 2. Busca histórico de despesas
    const resDesp = await api.get(`/operadoras/${cnpj}/despesas`);
    despesas.value = resDesp.data;
  } catch (e) {
    erro.value = "Não foi possível carregar os detalhes desta operadora.";
    console.error(e);
  } finally {
    loading.value = false;
  }
};

onMounted(buscarDados);
</script>

<style scoped>
.detalhe-container { padding: 20px; max-width: 900px; margin: 0 auto; }
.btn-voltar { display: inline-block; margin-bottom: 20px; color: #42b983; text-decoration: none; font-weight: bold; }
.card-info { background: #f4f4f4; padding: 20px; border-radius: 8px; margin-bottom: 30px; border-left: 5px solid #42b983; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; }
th, td { padding: 12px; border-bottom: 1px solid #ddd; text-align: left; }
th { background-color: #eee; }
.erro { color: red; font-weight: bold; }
</style>