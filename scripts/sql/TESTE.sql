SELECT 
    (SELECT COUNT(*) FROM operadoras) as total_operadoras,
    (SELECT COUNT(*) FROM despesas_consolidadas) as total_despesas;