import os
# Carrega as variáveis de acordo com o ambiente: Producao ou Desenvolvimento
# Para o ambiente de Desenvolvimento, crie um arquivo .env na raiz do projeto

LDAP_URL = os.getenv("LDAP_URL")
LDAP_USER = os.getenv("LDAP_USER")
LDAP_PASSWORD = os.getenv("LDAP_PASSWORD")
FLASK_ENV = os.getenv("FLASK_ENV")
SERVIDOR_AD = os.getenv("SERVIDOR_AD")
USUARIO_AD = os.getenv("USUARIO_AD")
SENHA_AD = os.getenv("SENHA_AD")
BASE_DN = os.getenv("BASE_DN")
NOVA_OU = os.getenv("NOVA_OU")
