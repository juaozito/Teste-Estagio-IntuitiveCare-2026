-- Cria o banco de dados
CREATE DATABASE IF NOT EXISTS intuitivecare;
USE intuitivecare;

-- Remove tabelas se já existirem (para resetar o teste)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS despesas_consolidadas;
DROP TABLE IF EXISTS operadoras;
SET FOREIGN_KEY_CHECKS = 1;

-- Tabela de Operadoras (Dados Cadastrais)
CREATE TABLE operadoras (
    RegistroANS VARCHAR(20) PRIMARY KEY,
    CNPJ VARCHAR(20),
    RazaoSocial VARCHAR(255),
    Modalidade VARCHAR(100),
    UF CHAR(2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabela de Despesas (Dados Financeiros)
CREATE TABLE despesas_consolidadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    registro_ans VARCHAR(20),
    trimestre INT,
    ano INT,
    valor_despesa DECIMAL(18,2),
    CONSTRAINT fk_operadora FOREIGN KEY (registro_ans) REFERENCES operadoras(RegistroANS)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;