# 🩺 Sistema de Gestão de Operadoras ANS - Teste Estagiário v2.0

Este projeto é uma solução completa para o desafio técnico da **Intuitive Care**. O sistema automatiza o ciclo completo de dados da ANS: extração do portal, tratamento de inconsistências, integração de bases (**Join**), armazenamento relacional e visualização através de um dashboard interativo.

---

## 📂 Estrutura do Projeto

* **`scripts/`**: Pipeline de dados (ETL) desenvolvida em Python e Pandas.
  
* **`backend/`**: API REST desenvolvida com **FastAPI**, configurada para servir também os arquivos estáticos do frontend.
  
* **`frontend/`**: Interface Single Page Application (SPA) com **Vue.js 3 via CDN**.
  
* **`sql/`**: Scripts de estrutura (`schema.sql`) e consultas analíticas de negócio (`analise.sql`).

---

## 🛠️ Pré-requisitos

### **1. Programas Necessários**

* **Python 3.10+** (Testado e compatível com Python 3.14).
  
* **MySQL Server 8.0**.
  
* **Navegador Web** (Chrome, OperaGX, Firefox ou Edge).
  
* **Ativar Ambiente Virtual (Caso não esteja ativado)**: `python -m venv venv` -> `.\venv\Scripts\activate`
  
* **Instale as dependências (Dentro do Projeto, no Terminal do VSCode, e certifique-se de que o ambiente virtual está ativo):** `pip install -r ../requirements.txt`.

---

## ⚙️ 2. Pipeline de Dados (ETL) e Transformação



O pipeline foi desenhado para ser resiliente a variações de formatos e garantir a integridade referencial entre os dados financeiros e cadastrais. **Execute os scripts na pasta `scripts/` seguindo esta ordem exata:**

1.  `python scripts/etapa1_requisicao.py`
   
    * **Integração com API Pública**: Acessa a API de Dados Abertos da ANS e realiza o download das Demonstrações Contábeis.

   
2.  `python scripts/etapa1_processamento.py`
   
    * **Processamento de Arquivos**: Extrai ZIPs e normaliza diferentes formatos (CSV, TXT, XLSX).
    * **Trade-off técnico**: Escolhido o **processamento incremental**.
    * **Justificativa**: Evita estouro de RAM ao lidar com arquivos de centenas de MBs.

   
3.  `python scripts/etapa2_cadastral.py`
   
    * **Enriquecimento e Validação**: Baixa os dados das operadoras ativas e valida CNPJs.

      
4.  `python scripts/etapa2_join.py`
   
    * **Integração de Bases**: Realiza o *join* entre despesas e cadastro usando o CNPJ.
    * **Trade-off técnico**: Join realizado em memória com **Pandas**.

      
5.  `python scripts/etapa2_agregacao.py`
    
    * **Agregação**: Calcula total, média trimestral e desvio padrão por operadora/UF.

   
6.  `python scripts/etapa3_banco_dados.py`
    
    * **Persistência**: Estrutura as tabelas e importa o conteúdo para o MySQL 8.0.

---

## 🧠 Trade-offs Técnicos e Justificativas (Requisitos PDF v2.0)

### **1. Processamento de Dados (ETL)**

* **Processamento Incremental**: Utilização de `stream=True`. **Justificativa**: Estabilidade contra falhas de memória em arquivos volumosos.
  
* **Inconsistências de CNPJ**: Tratamento via `.zfill(14)`. **Justificativa**: Impede que o Pandas corrompa a chave de identificação ao remover zeros à esquerda.

### **2. Banco de Dados (SQL)**

* **Normalização (Opção B)**: Uso de tabelas separadas. **Justificativa**: Evita redundância e facilita queries complexas.
  
* **Tipos de Dados**: Uso de `DECIMAL(18,2)`. **Justificativa**: Precisão absoluta para cálculos financeiros.

---

## 🗄️ 3. Configuração do Banco de Dados

1.  No **MySQL Workbench**, acesse `File` -> `Open SQL Script` e execute o arquivo `sql/schema.sql`.
   
2.  O script de carga é gerado automaticamente após a execução da **Etapa 6** do Pipeline, adicione-o (mesmo processo anterior) e execute-o.
   
3.  Utilize o arquivo `sql/analise.sql` para validar as métricas de negócio requisitadas.

---

## 🚀 4. Interface e API (Execução Unificada)

1.  Acesse a pasta do backend: `cd backend`.
   
3.  Instale as dependências: `pip install -r ../requirements.txt`.
   
5.  Configure o arquivo `.env` com suas credenciais do MySQL.
6.  Rode o servidor: `python main.py`.
7.  Abra o navegador em: **http://localhost:8000**

---

**Candidato:** João Lucas Rebouças de Souza
**E-mail:** reboucasjoao85@gmail.com
**Linkedin:** https://www.linkedin.com/in/joaolucasreb
EOF
