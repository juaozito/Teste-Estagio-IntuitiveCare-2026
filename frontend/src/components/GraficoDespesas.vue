<template>
  <div style="max-height: 400px;">
    <Bar v-if="chartData" :data="chartData" :options="options" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
import api from '../services/api';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const chartData = ref(null);
const options = { responsive: true, maintainAspectRatio: false };

onMounted(async () => {
  const { data } = await api.get('/estatisticas/por-uf');
  chartData.value = {
    labels: data.map(i => i.UF),
    datasets: [{
      label: 'Total de Despesas por UF',
      backgroundColor: '#42b983',
      data: data.map(i => i.total)
    }]
  };
});
</script>