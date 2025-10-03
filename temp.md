# Criar nova taleba no banco:

```
CRIAR OS ARQUIVOS DE LOG 

TO DO:
 
Perguntar para o Thiago sobre o e-mail ser requisito obrigatorio ou não
VERIFICAR E TRATAR O ERRO NA DN DA DESATIVAÇÃO DO USUÁRIO NO AMBIENTE DE DESENVOLVIMENTO;
LIMITAR OS CAMPOS DO FORMULÁRIO DE CRIAÇÃO DO USUÁRIO;
AJUSTAR EMAIL FAKE PARA SUBSTITUIR AS CHAMADAS DO OIDC PARA PEGAR QUEM ESTÁ LOGADO NO AMBIENTE DE DESENVOVIMENTO;
CRIAÇÃO DE FUNÇÃO PARA ENVIAR E-MAIL NO ATO DA DESATIVAÇÃO DA CONTA;
CRIAÇÃO DE TELA PARA ATIVAÇÃO DE USUÁRIO;
ADICIONAR APLICAÇÃO NA ESTEIRA CI/CD;

Ambiente de teste: Já fiz o ad.py. Assim que finalizar todos, tenho que configurar o config.py, importar nos modulos que usam variavel de ambiente, setar as variaveis no servidor de producao e testar.


if os.getenv("FLASK_ENV") == "desenvolvimento":
    BASE_DN = "dc=ad,dc=local"
    NOVA_OU = 'OU=Usuarios,OU=NoSync--M365,DC=ad,DC=local'
else:
    BASE_DN = 'DC=cade,DC=gov,DC=br'
    NOVA_OU = 'OU=Usuarios,OU=NoSync--M365,DC=cade,DC=gov,DC=br'


=====================


Enviar codigo git
Botão de logout
Enviar email quando desativar conta - DEBUGAR O ERRO QUANDO ATIVA A FUNÇÃO DE ENVIO DE EMAIL.
Formato data formulario 

```