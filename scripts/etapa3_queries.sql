-- ETAPA 3: QUERIES ANALÍTICAS (CONFORME REQUISITO 3.4 DO PDF)

-- Query 1: Top 5 operadoras com maior crescimento percentual (1T vs 3T)
WITH trimestres AS (
    SELECT razao_social, 
           SUM(CASE WHEN trimestre LIKE '%1T%' THEN valor_despesa ELSE 0 END) as v1,
           SUM(CASE WHEN trimestre LIKE '%3T%' THEN valor_despesa ELSE 0 END) as v3
    FROM despesas_consolidadas
    GROUP BY razao_social
)
SELECT razao_social, 
       ((v3 - v1) / NULLIF(v1, 0)) * 100 as crescimento_pct
FROM trimestres
WHERE v1 > 0 AND v3 > 0
ORDER BY crescimento_pct DESC
LIMIT 5;

-- Query 2: Distribuição por UF (Top 5) + Média por operadora na UF
SELECT uf, 
       SUM(valor_despesa) as total_despesa,
       AVG(valor_despesa) as media_por_operadora
FROM despesas_consolidadas
GROUP BY uf
ORDER BY total_despesa DESC
LIMIT 5;

-- Query 3: Operadoras acima da média geral em pelo menos 2 trimestres
SELECT razao_social
FROM (
    SELECT razao_social, trimestre, SUM(valor_despesa) as valor,
           (SELECT AVG(valor_despesa) FROM despesas_consolidadas) as media_geral
    FROM despesas_consolidadas
    GROUP BY razao_social, trimestre
) t
WHERE valor > media_geral
GROUP BY razao_social
HAVING COUNT(DISTINCT trimestre) >= 2;