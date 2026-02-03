<template>
  <div class="dashboard">
    <h1>Painel de Operadoras ANS</h1>
    
    <div class="chart-container">
      <GraficoDespesas />
    </div>

    <div class="table-container">
      <TabelaOperadoras />
    </div>
  </div>
</template>

<script setup>
import GraficoDespesas from '../components/GraficoDespesas.vue';
import TabelaOperadoras from '../components/TabelaOperadoras.vue';
</script>

<style scoped>
.dashboard { padding: 20px; }
.chart-container { margin-bottom: 40px; background: #f9f9f9; padding: 20px; border-radius: 8px; }
</style>