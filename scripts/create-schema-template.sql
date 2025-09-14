-- Verificar transacciones históricas

CREATE SCHEMA IF NOT EXISTS financial_pipeline;

CREATE TABLE IF NOT EXISTS financial_pipeline.historical_transactions (
    id SERIAL PRIMARY KEY,
    app VARCHAR(255),
    id_ordenante VARCHAR(255),
    valor NUMERIC(10, 2),
    producto VARCHAR(255),
    cuenta_ordenante VARCHAR(255),
    cuenta_beneficiario VARCHAR(255),
    detalle TEXT,
    timestamp TIMESTAMP,
    batch_date DATE
);

SELECT COUNT(*) FROM historical_transactions;

SELECT * FROM historical_transactions

DELETE FROM historical_transactions;
