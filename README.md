# portal-flask

## Arquivo .env (para rodar localmente)

FLASK_ENV=development
MYSQL_DATABASE=portal
MYSQL_ROOT_PASSWORD=[senha do root do banco]
MYSQL_USER=[usuario do banco]
MYSQL_PASSWORD=[senha do usuario de banco]

Na primeira criação do ambiente, deve criar a seguiinte tabela no banco:

```
CREATE TABLE log_ad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_sistema VARCHAR(100) NOT NULL,
    usuario_ad VARCHAR(100) NOT NULL,
    acao VARCHAR(50) NOT NULL,
    data_acao DATETIME DEFAULT CURRENT_TIMESTAMP,
    observacoes TEXT
);

```

## Configuração do OIDC

Crie um arquivo chamado `client_secrets.json` com o conteúdo baseado em `client_secrets.example.json`.

Esse arquivo **NÃO deve ser versionado** (já está no `.gitignore`).