🩺 Sistema de Gestão de Operadoras ANS - Teste Estagiário v2.0
Este projeto é uma solução completa para o desafio técnico da Intuitive Care. O sistema automatiza o ciclo completo de dados da ANS: extração do portal, tratamento de inconsistências, integração de bases (Join), armazenamento relacional e visualização através de um dashboard interativo.

📂 Estrutura do Projeto
scripts/: Pipeline de dados (ETL) desenvolvida em Python e Pandas.

backend/: API REST desenvolvida com FastAPI, configurada para servir também os arquivos estáticos do frontend.

frontend/: Interface Single Page Application (SPA) com Vue.js 3 via CDN.

sql/: Scripts de estrutura (schema.sql) e consultas analíticas de negócio (analise.sql).

🛠️ Pré-requisitos
1. Programas Necessários
Python 3.10+ (Testado e compatível com Python 3.14).

MySQL Server 8.0.

Navegador Web (Chrome, OperaGX, Firefox ou Edge).

⚙️ 2. Pipeline de Dados (ETL) e Transformação
O pipeline foi desenhado para ser resiliente a variações de formatos e garantir a integridade referencial entre os dados financeiros e cadastrais. Execute os scripts na pasta scripts/ seguindo esta ordem exata:

python scripts/etapa1_requisicao.py

Integração com API Pública: Acessa a API de Dados Abertos da ANS, identifica os últimos 3 trimestres disponíveis e realiza o download dos arquivos de Demonstrações Contábeis.

python scripts/etapa1_processamento.py

Processamento de Arquivos: Extrai os arquivos ZIP, identifica dados de despesas com eventos/sinistros e normaliza diferentes formatos (CSV, TXT, XLSX).

Trade-off técnico (Processamento): Foi escolhido o processamento incremental.

Justificativa: Devido ao grande volume de dados, evita o estouro de memória RAM e garante a escalabilidade.

python scripts/etapa2_cadastral.py

Enriquecimento e Validação: Baixa os dados cadastrais das operadoras ativas e implementa validações de CNPJ, valores numéricos e campos obrigatórios.

Tratamento de Inconsistências: CNPJs duplicados ou com razões sociais diferentes foram corrigidos ou marcados para garantir a unicidade.

python scripts/etapa2_join.py

Integração de Bases: Realiza o join entre os dados de despesas e o cadastro usando o CNPJ como chave.

Trade-off técnico (Join): Realizado em memória utilizando a biblioteca Pandas antes da persistência.

Justificativa: Simplifica o tratamento de registros sem correspondência e permite a normalização antes da inserção no banco.

python scripts/etapa2_agregacao.py

Agregação com Múltiplas Estratégias: Agrupa os dados por operadora e UF, calculando total, média por trimestre e desvio padrão.

Trade-off técnico (Ordenação): Ordenação baseada no valor total decrescente.

python scripts/etapa3_banco_dados.py

Persistência e Análise: Estrutura as tabelas e importa o conteúdo dos arquivos CSV normalizados para o MySQL 8.0.

Trade-off técnico (Normalização): Adotada a Opção B (Tabelas normalizadas separadas).

🧠 Trade-offs Técnicos e Justificativas (Requisitos PDF v2.0)
Abaixo estão as decisões fundamentadas tomadas durante o desenvolvimento:

1. Processamento de Dados (ETL)
Processamento Incremental: Utilização de stream=True. Justificativa: Os arquivos da ANS são volumosos; a abordagem incremental garante estabilidade contra estouro de RAM.

Inconsistências de CNPJ: Correção via .zfill(14). Justificativa: Impede que a leitura automática do Pandas remova zeros à esquerda, corrompendo o ID.

2. Banco de Dados (SQL)
Normalização (Opção B): Tabelas Separadas. Justificativa: Cadastro estável e despesas trimestrais; a separação evita redundância e facilita queries analíticas.

Tipos de Dados: Uso de DECIMAL(18,2). Justificativa: Evita erros de arredondamento comuns em tipos FLOAT em cálculos financeiros.

3. Backend (FastAPI)
Framework: FastAPI. Justificativa: Alta performance assíncrona e geração automática de documentação Swagger.

Paginação: Offset-based. Justificativa: Ideal para dados históricos, permitindo pular para páginas específicas rapidamente.

4. Frontend (Vue.js)
Arquitetura: Servido como arquivo estático (KISS). Justificativa: Elimina a necessidade de ambiente Node.js para o avaliador, tornando a execução imediata.

Busca no Servidor: Processamento via SQL para garantir performance e escalabilidade ao lidar com milhares de registros.

🗄️ 3. Configuração do Banco de Dados
No seu MySQL, vá em File -> Open SQL Script e adicione o arquivo sql/schema.sql para criar as tabelas.

Execute o script de carga gerado após a execução dos scripts de ETL.

Execute o arquivo sql/analise.sql para validar as métricas de negócio.

🚀 4. Interface e API (Execução Unificada)
Acesse a pasta backend.

Instale as dependências: pip install -r ../requirements.txt.

Configure o arquivo .env com suas credenciais do MySQL.

Rode o comando: python main.py.

Abra o navegador em: http://localhost:8000

📊 Análises Adicionais
O arquivo sql/analise.sql contém as queries que respondem aos desafios de negócio, como o Top 5 operadoras com maior crescimento e a distribuição de despesas por UF.

Candidato: João Lucas Rebouças de Souza E-mail: reboucasjoao85@gmail.com Linkedin: www.linkedin.com/in/joaolucasreb
