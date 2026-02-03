🩺 Relatório de Desenvolvimento - TESTE DE ENTRADA PARA ESTAGIÁRIOS v2.0

Este projeto apresenta uma solução completa para o desafio técnico da Intuitive Care, cobrindo o ciclo de vida de um engenheiro de dados e desenvolvedor full-stack: Extração (Web Scraping), Transformação (Pandas), Carga (SQL), Backend (FastAPI) e Frontend (Vue.js).

📂 Estrutura do Repositório

backend/: API em FastAPI e lógica de conexão com o banco.

frontend/: Interface em Vue.js 3 para visualização dos dados.

scripts/: Pipeline de ETL (Etapas 1, 2 e 3 do teste).

sql/: Scripts de criação de tabelas (schema.sql) e consultas analíticas (analise.sql).

🛠️ Como Instalar e Rodar

1. Banco de Dados (MySQL 8.0)
   
Crie o banco de dados intuitivecare no seu MySQL.

Execute o arquivo schema.sql para criar as tabelas operadoras e despesas_consolidadas.

Execute as queries de analise.sql para validar os requisitos de lógica SQL.

2. Backend (API Python)
   
Aceda à pasta backend.

Instale as dependências: pip install -r requirements.txt.

Configuração de Ambiente: Renomeie o arquivo .env.example para .env e insira as suas credenciais do MySQL.

Inicie o servidor: python main.py.

A API estará disponível em: http://localhost:8000

3. Frontend (Dashboard Vue.js)

Aceda à pasta frontend.

Instale os pacotes: npm install.

Inicie a aplicação: npm run dev.

Abra o navegador em: http://localhost:5173.

🧠 Trade-offs Técnicos e Justificativas

Conforme solicitado no PDF do teste, aqui estão as decisões fundamentadas:

Backend

Framework (Opção B - FastAPI): Escolhido pela alta performance e documentação Swagger automática. É ideal para uma aplicação que precisa de validação rigorosa de dados (Pydantic).

Paginação (Opção A - Offset-based): Implementada via LIMIT/OFFSET. Como a base de dados da ANS é estática (atualização trimestral), esta estratégia oferece a melhor experiência de navegação para o usuário final.

Estatísticas (Opção A - Queries Diretas): As estatísticas de despesas por UF são calculadas em tempo real. Justifica-se pela consistência absoluta dos dados, eliminando riscos de cache desatualizado.

Frontend

Busca/Filtro (Opção A - Busca no Servidor): A filtragem por Razão Social ou CNPJ é feita via API. Justificativa: Carregar milhares de linhas da ANS no navegador prejudicaria a performance (UX). A busca no banco de dados é escalável.

Tratamento de Erros e Loading: O sistema utiliza estados de loading para cada chamada de API e mensagens de erro específicas. Justificativa: Evita que o utilizador pense que a aplicação travou durante o processamento de grandes volumes de dados.

📊 Pipeline de Dados (ETL)

O processo de ingestão de dados foi automatizado nos scripts da pasta scripts/:

Extração: O etapa1_requisicao.py usa stream=True para baixar os ZIPs pesados da ANS em pedaços (chunks), protegendo a memória RAM.

Limpeza: Os dados foram normalizados (remoção de acentos e caracteres especiais) para garantir compatibilidade com o encoding do MySQL.

Integridade: Tratamento de CNPJs com zfill(14) para evitar que o Excel ou o Pandas removam os zeros à esquerda.

📁 Documentação Adicional

A coleção do Postman (Postman_Collection.json) está incluída na raiz para teste imediato de todas as rotas da API.

Candidato: João Lucas Rebouças de Souza Teste: Estagiário de Desenvolvimento/Dados - Intuitive Care.
