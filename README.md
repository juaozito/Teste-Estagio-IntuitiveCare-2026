# 🩺 Sistema de Gestão de Operadoras ANS - Teste Estagiário v2.0

Este projeto é uma solução completa para o desafio técnico da **Intuitive Care**. O sistema automatiza o ciclo completo de dados da ANS: extração do portal, tratamento de

inconsistências, integração de bases (Join), armazenamento relacional e visualização através de um dashboard interativo.

---

## 📂 Estrutura do Projeto

* **`scripts/`**: Pipeline de dados (ETL) desenvolvida em Python e Pandas.
  
* **`backend/`**: API REST desenvolvida com **FastAPI**, configurada para servir também os arquivos estáticos do frontend.
  
* **`frontend/`**: Interface Single Page Application (SPA) com **Vue.js 3 via CDN**.
  
* **`sql/`**: Scripts de estrutura (`schema.sql`) e consultas analíticas de negócio (`analise.sql`).

---

## 🛠️ Instruções de Execução

### 1. Pré-requisitos

* **Python 3.10+** (Testado e compatível com Python 3.14).
  
* **MySQL Server 8.0**.
  
* **Navegador Web** (Chrome, Firefox ou Edge).

### 2. Configuração do Banco de Dados

1.  No seu MySQL, crie o schema: `CREATE DATABASE intuitivecare;`.
   
2.  Execute o arquivo `sql/schema.sql` para criar as tabelas e relações necessárias.

### ⚙️ 3. Pipeline de Dados (ETL)

Para processar os dados e realizar o cruzamento das bases (Join), execute os scripts na pasta `scripts/` seguindo esta ordem exata:

1.  `python scripts/etapa1_requisicao.py` - Download dos arquivos ZIP brutos da ANS.
   
2.  `python scripts/etapa1_processamento.py` - Extração e limpeza inicial dos CSVs.
   
3.  `python scripts/etapa2_cadastral.py` - Normalização dos dados cadastrais das operadoras.
   
4.  `python scripts/etapa2_join.py` - **Integração:** Cruza as despesas financeiras com o cadastro via `RegistroANS`.
   
5.  `python scripts/etapa2_agregacao.py` - Consolidação de dados para performance do Dashboard.
    
6.  `python scripts/etapa3_banco_dados.py` - Executa a carga final dos dados tratados no MySQL.

### 🚀 4. Interface e API (Execução Unificada)

Para facilitar a avaliação, o Backend foi configurado para servir o Frontend simultaneamente:

1.  Acesse a pasta `backend`.
   
2.  Instale as dependências: `pip install -r ../requirements.txt`.
   
3.  Configure o arquivo `.env` com suas credenciais do MySQL.
   
4.  Rode o comando: `python main.py`.
   
5.  Abra o navegador em: **`http://localhost:8000`** (O sistema carregará o Dashboard automaticamente).

---

## 🧠 Trade-offs Técnicos e Justificativas (Requisitos PDF v2.0)

Abaixo estão as decisões fundamentadas tomadas durante o desenvolvimento:

### **1. Processamento de Dados (ETL)**

* **Processamento Incremental:** Decidi utilizar `stream=True` no download e processamento. **Justificativa:** Os arquivos da ANS são volumosos. O processamento em memória de uma vez (Opção B) poderia estourar a RAM. A abordagem incremental garante estabilidade.
  
* **Inconsistências de CNPJ:** Implementada a estratégia de correção via `.zfill(14)`. **Justificativa:** Garante que o ID da operadora não seja corrompido pela leitura automática do Pandas/Excel que remove zeros à esquerda.

### **2. Banco de Dados (SQL)**

* **Normalização:** Escolhida a **Opção B (Tabelas Separadas)**. **Justificativa:** Como os dados cadastrais são estáveis e as despesas são trimestrais, a separação evita redundância e facilita queries analíticas complexas.
  
* **Tipos de Dados:** Uso de `DECIMAL(18,2)` para valores monetários. **Justificativa:** Diferente do `FLOAT`, o `DECIMAL` evita erros de arredondamento em cálculos financeiros.

### **3. Backend (FastAPI)**

* **Framework:** Escolhida a **Opção B (FastAPI)**. **Justificativa:** Pela natureza assíncrona, oferece melhor performance para múltiplas requisições simultâneas e gera documentação Swagger automática.
  
* **Paginação:** Escolhida a **Opção A (Offset-based)**. **Justificativa:** Ideal para dados históricos e estáveis da ANS, permitindo que o usuário pule para páginas específicas rapidamente.
  
* **Estatísticas:** Escolhida a **Opção A (Queries Diretas)**. **Justificativa:** Garante consistência absoluta. Com índices bem aplicados no SQL, o cálculo em tempo real é eficiente e elimina riscos de cache desatualizado.

### **4. Frontend (Vue.js)**

* **Arquitetura:** Frontend servido como arquivo estático. **Justificativa:** Aplicação do princípio **KISS**. Elimina a necessidade de o avaliador configurar ambiente Node.js, tornando a execução do teste imediata.
  
* **Estratégia de Busca:** Escolhida a **Opção A (Busca no Servidor)**. **Justificativa:** Performance de UX. Filtrar milhares de registros no cliente pesaria o navegador; o filtro via SQL é escalável.
  
* **Gerenciamento de Estado:** Escolhida a **Opção C (Composables - Vue 3)**. **Justificativa:** Permite compartilhar reatividade entre componentes de forma modular e leve, sem a sobrecarga de uma biblioteca como Pinia/Vuex.

---

## 📊 Análises Adicionais

O arquivo `sql/analise.sql` contém as queries que respondem aos desafios de negócio, como o Top 5 operadoras com maior crescimento e a distribuição de despesas por UF.



---
**Candidato:** João Lucas Rebouças de Souza

**E-mail:** reboucasjoao85@gmail.com

**Linkedin:** www.linkedin.com/in/joaolucasreb
