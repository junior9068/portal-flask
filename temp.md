# Criar nova taleba no banco:

```
Criar a nova tabela no banco:

CREATE TABLE registros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dados_json JSON NOT NULL,
    acao VARCHAR(15),
    status INT
);

```