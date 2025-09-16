
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Insere alguns dados de exemplo (a senha 'password123' é um hash bcrypt)
INSERT INTO users (name, password)
VALUES 
    ('joao', '$2b$12$KACSrr/u4PANsgfeS3lh1.X3F4xcnEqnAKv0PfrgGwkEjexHPceh6'),
    ('maria', '$2b$12$KACSrr/u4PANsgfeS3lh1.X3F4xcnEqnAKv0PfrgGwkEjexHPceh6');