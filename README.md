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

## 🛠️ Pré-requisitos

### 1. Programas Necessários.

* **Python 3.10+** (Testado e compatível com Python 3.14).
  
* **MySQL Server 8.0**.
  
* **Navegador Web** (Chrome, OperaGX, Firefox ou Edge).

### ⚙️ 2. Pipeline de Dados (ETL) e Transformação

O pipeline foi desenhado para ser resiliente a variações de formatos e garantir a integridade referencial entre os dados financeiros e cadastrais. Execute os scripts na pasta scripts/ seguindo esta ordem exata:


python scripts/etapa1_requisicao.py - Integração com API Pública: Acessa a API de Dados Abertos da ANS, identifica os últimos 3 trimestres disponíveis e realiza o download dos arquivos de Demonstrações Contábeis.


python scripts/etapa1_processamento.py - Processamento de Arquivos: Extrai os arquivos ZIP, identifica dados de despesas com eventos/sinistros e normaliza diferentes formatos (CSV, TXT, XLSX).


Trade-off técnico (Processamento): Foi escolhido o processamento incremental.


Justificativa: Devido ao grande volume de dados das demonstrações contábeis da ANS, o processamento incremental evita o estouro de memória RAM e garante a escalabilidade do sistema.


python scripts/etapa2_cadastral.py - Enriquecimento e Validação: Baixa os dados cadastrais das operadoras ativas e implementa validações de CNPJ, valores numéricos e campos obrigatórios.


Tratamento de Inconsistências: CNPJs duplicados ou com razões sociais diferentes foram corrigidos ou marcados para garantir a unicidade no banco de dados.


python scripts/etapa2_join.py - Integração de Bases: Realiza o join entre os dados consolidados de despesas e o cadastro das operadoras usando o CNPJ como chave.


Trade-off técnico (Join): Optou-se por realizar o join em memória utilizando a biblioteca Pandas antes da persistência.


Justificativa: Esta abordagem simplifica o tratamento de registros sem correspondência no cadastro e permite a normalização dos dados antes da inserção no banco de dados relacional.


python scripts/etapa2_agregacao.py - Agregação com Múltiplas Estratégias: Agrupa os dados por operadora e UF, calculando o total, média por trimestre e desvio padrão das despesas.


Trade-off técnico (Ordenação): Utilizada ordenação baseada no valor total decrescente diretamente na query ou processamento final.


python scripts/etapa3_banco_dados.py - Persistência e Análise: Executa as queries DDL para estruturar as tabelas e importa o conteúdo dos arquivos CSV normalizados para o MySQL 8.0.


Trade-off técnico (Normalização): Foi adotada a Opção B (Tabelas normalizadas separadas).


Justificativa: Melhora a integridade dos dados e a performance em queries analíticas complexas, considerando a frequência de atualizações trimestrais.

### 3. Configuração do Banco de Dados
   
1.  No seu MySQL, vá em File (no topo do MySQL), clique em "Open SQL Script" e adicione o arquivo `sql/schema.sql`(Localizado em Teste-Estagio-IntuitiveCare-2026\scripts\sql) para criar as tabelas e relações necessárias.
   
2.  Adicone o 'carga_dados.sql' gerado logo após você executar os scripts
   
3.  Execute a 'analise.aql' para mostrar a respostas das queries.

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
