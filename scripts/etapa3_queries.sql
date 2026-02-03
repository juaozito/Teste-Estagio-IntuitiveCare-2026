/* TAREFA 3.2 - JUSTIFICATIVAS TÉCNICAS (CONFORME PDF)
1. NORMALIZAÇÃO: Escolhida a Opção B (Tabelas separadas).
   Justificativa: Considerando o volume de dados (3 trimestres), a normalização 
   evita redundância e otimiza a performance de buscas cadastrais.
2. TIPOS DE DADOS: 
   - Moeda: DECIMAL(18,2) para precisão absoluta.
   - Datas: INT (Ano/Trimestre) para simplificar a lógica de períodos da ANS.
*/

-- DDL: MySQL 8.0 / PostgreSQL
CREATE TABLE IF NOT EXISTS operadoras (
    RegistroANS VARCHAR(20) PRIMARY KEY,
    CNPJ VARCHAR(20),
    RazaoSocial VARCHAR(255),
    Modalidade VARCHAR(100),
    UF CHAR(2)
);

CREATE TABLE IF NOT EXISTS despesas_consolidadas (
    id INT AUTO_INCREMENT PRIMARY KEY, -- No Postgres use SERIAL
    registro_ans VARCHAR(20),
    trimestre INT,
    ano INT,
    valor_despesa DECIMAL(18,2),
    FOREIGN KEY (registro_ans) REFERENCES operadoras(RegistroANS)
);

-- QUERY 1: Crescimento Percentual (Tratando dados faltantes com INNER JOIN)
WITH p1 AS (SELECT registro_ans, valor_despesa FROM despesas_consolidadas WHERE trimestre = 1),
     p3 AS (SELECT registro_ans, valor_despesa FROM despesas_consolidadas WHERE trimestre = 3)
SELECT o.RazaoSocial, ((p3.valor_despesa - p1.valor_despesa) / p1.valor_despesa) * 100 as crescimento
FROM p1 JOIN p3 ON p1.registro_ans = p3.registro_ans JOIN operadoras o ON o.RegistroANS = p1.registro_ans
ORDER BY crescimento DESC LIMIT 5;

-- QUERY 2: UF e Médias
SELECT o.UF, SUM(d.valor_despesa) as total, AVG(d.valor_despesa) as media
FROM despesas_consolidadas d JOIN operadoras o ON d.registro_ans = o.RegistroANS
GROUP BY o.UF ORDER BY total DESC LIMIT 5;

-- QUERY 3: Acima da média em 2 trimestres (Abordagem: Subquery com Having)
SELECT COUNT(*) FROM (
    SELECT registro_ans FROM despesas_consolidadas
    WHERE valor_despesa > (SELECT AVG(valor_despesa) FROM despesas_consolidadas)
    GROUP BY registro_ans HAVING COUNT(DISTINCT trimestre) >= 2
) as elite;