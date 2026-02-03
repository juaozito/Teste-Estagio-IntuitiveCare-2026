<template>
  <div id="app">
    <header class="header">
      <h1>Sistema de Gestão ANS</h1>
    </header>

    <main class="container">
      <router-view />
    </main>

    <footer class="footer">
      <p>Teste Técnico - Analista de Dados / Desenvolvedor</p>
    </footer>
  </div>
</template>

<style>
/* Estilos globais para o projeto */
#app {
  font-family: Arial, sans-serif;
  color: #2c3e50;
}

.header {
  background-color: #42b983;
  color: white;
  padding: 1rem;
  text-align: center;
  margin-bottom: 2rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer {
  text-align: center;
  margin-top: 3rem;
  padding: 2rem;
  font-size: 0.8rem;
  color: #7f8c8d;
}
</style>