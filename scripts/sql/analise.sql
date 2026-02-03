USE intuitivecare;

-- ---------------------------------------------------------------------------------------------------------
-- QUERY 1: AS 5 OPERADORAS COM MAIOR CRESCIMENTO (LIMITADO A ESCALA DE 100%)
-- ---------------------------------------------------------------------------------------------------------

WITH Trimestres AS (
    SELECT 
        registro_ans,
        SUM(CASE WHEN trimestre = 1 THEN valor_despesa ELSE 0 END) as v1,
        SUM(CASE WHEN trimestre = 3 THEN valor_despesa ELSE 0 END) as v3
    FROM despesas_consolidadas
    GROUP BY registro_ans
)
SELECT 
    o.RazaoSocial AS 'Operadora',
    CONCAT('R$ ', FORMAT(t.v1, 2, 'de_BR')) AS 'Despesa Q1',
    CONCAT('R$ ', FORMAT(t.v3, 2, 'de_BR')) AS 'Despesa Q3',
    -- Cálculo: (Valor Final - Valor Inicial) / Valor Final para escala de 0 a 100% do total
    -- Ou simplesmente mantendo o cálculo anterior mas formatando para não explodir a visualização
    CONCAT(
        ROUND(
            LEAST(((t.v3 - t.v1) / NULLIF(t.v3, 0)) * 100, 100), 
        2), 
    '%') AS 'Crescimento (%)'
FROM Trimestres t
JOIN operadoras o ON t.registro_ans = o.RegistroANS
WHERE t.v1 > 0 AND t.v3 > t.v1
ORDER BY (t.v3 - t.v1) DESC
LIMIT 5;

-- ---------------------------------------------------------------------------------------------------------
-- QUERY 2: DISTRIBUIÇÃO DE DESPESAS POR UF (TOP 5)
-- ---------------------------------------------------------------------------------------------------------

SELECT 
    o.UF,
    CONCAT('R$ ', FORMAT(SUM(d.valor_despesa), 2, 'de_BR')) AS 'Despesa Total UF',
    CONCAT('R$ ', FORMAT(AVG(d.valor_despesa), 2, 'de_BR')) AS 'Média por Operadora na UF'
FROM despesas_consolidadas d
JOIN operadoras o ON d.registro_ans = o.RegistroANS
GROUP BY o.UF
ORDER BY SUM(d.valor_despesa) DESC
LIMIT 5;

-- ---------------------------------------------------------------------------------------------------------
-- QUERY 3: QTD OPERADORAS ACIMA DA MÉDIA EM PELO MENOS 2 TRIMESTRES
-- ---------------------------------------------------------------------------------------------------------

SELECT COUNT(*) AS 'Qtd Operadoras Acima da Média'
FROM (
    SELECT registro_ans
    FROM despesas_consolidadas
    WHERE valor_despesa > (SELECT AVG(valor_despesa) FROM despesas_consolidadas)
      AND trimestre IN (1, 2, 3)
    GROUP BY registro_ans, ano
    HAVING COUNT(DISTINCT trimestre) >= 2
) AS subquery_analise;