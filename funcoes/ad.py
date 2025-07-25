import re
import ldap3
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import logging
from flask import jsonify
import string
import random
# --- CONFIGURAÇÕES DO AD ---
SERVIDOR_AD = "ldaps://SRVPADDNS02.cade.gov.br"
USUARIO_AD = "srvportalad@cade.gov.br"
SENHA_AD = "s2G2x2xgKc54."
BASE_DN = 'DC=cade,DC=gov,DC=br'
NOVA_OU = 'OU=Usuarios,OU=NoSync--M365,DC=cade,DC=gov,DC=br'

def testar_conexao_ad():
    try:
        server = Server(SERVIDOR_AD, get_info=ALL)
        conn = Connection(server, user=USUARIO_AD, password=SENHA_AD, auto_bind=True)
        if conn.bound:
            print("[OK] Conexão com AD estabelecida com sucesso.")
            conn.unbind()
        else:
            print("[ERRO] Falha na conexão com AD.")
    except Exception as e:
        print(f"[ERRO] Exceção ao conectar no AD: {e}")


def conectar_ad():
    server = Server(SERVIDOR_AD, get_info=ALL)
    conn = Connection(server, user=USUARIO_AD, password=SENHA_AD, auto_bind=True)
    return conn


def buscar_nome(cpf):
    conn = conectar_ad()
    filtro = f"(employeeNumber={cpf})"
    #conn.search(BASE_DN, filtro, attributes=["distinguishedName"])
    conn.search(BASE_DN, filtro, attributes=["mail", "distinguishedName"])

    # return conn.entries[0]
    if conn.entries:
        dn = conn.entries[0].distinguishedName.value
        nome = dn.split(',')[0].split('=')[1]
        email = conn.entries[0].mail.value
        # retorna uma tupla com nome e email (o Flask deve estar em execução para funcionar)
        return jsonify({"nome": nome, "email": email})
    logging.error(f"Usuário com CPF {cpf} não encontrado.")
    return jsonify({"nome": "Não encontrado", "email": "Não encontrado"})


def buscar_usuario_por_cpf(conn, cpf):
    filtro = f"(employeeNumber={cpf})"
    conn.search(BASE_DN, filtro, attributes=["distinguishedName"])

    if conn.entries:
        return conn.entries[0].distinguishedName.value
        print("Entrei no IF")
    return None


def nome_login(nome_completo):
    partes = nome_completo.strip().split()
    if len(partes) < 2:
        return None, None
    nome = partes[0].lower()
    sobrenome1 = partes[-1].lower()
    login1 = f"{nome}.{sobrenome1}"
    login2 = f"{nome}.{partes[1].lower()}" if len(partes) >= 3 else None
    return login1, login2


def buscar_login(nome_completo):
    conn_ad = conectar_ad()
    # Gera login
    login1, login2 = nome_login(nome_completo)
    login_final = None

    for login in [login1, login2]:
        if not login:
            continue
        filtro_login = f"(sAMAccountName={login})"
        conn_ad.search(BASE_DN, filtro_login, attributes=["distinguishedName"])
        if not conn_ad.entries:
            login_final = login
            return login_final
    logging.error(f"Todos os logins {login1} e {login2} já existem no AD.")
    return "Todos os logins que tentamos criar já existem no AD."


def gerar_senha(segura=True):
    if not segura:
        return "Senha@123"  # Fallback (evite usar em produção)

    while True:
        senha = ''.join(random.choices(
            string.ascii_letters + string.digits + "!@#$%&*?",
            k=10
        ))
        # Garante pelo menos uma minúscula, uma maiúscula, um dígito e um especial
        if (any(c.islower() for c in senha) and
            any(c.isupper() for c in senha) and
            any(c.isdigit() for c in senha) and
            any(c in "!@#$%&*?" for c in senha)):
            return senha

def busca_manager(chefia):
    conn_ad = conectar_ad()
    manager_dn = None
    conn_ad.search(BASE_DN, f"(displayName={chefia})", attributes=["distinguishedName"])
    if len(conn_ad.entries) == 1:
        manager_dn = conn_ad.entries[0]["distinguishedName"].value
        return manager_dn
    logging.error(f"Erro ao buscar manager: {chefia} não encontrado ou múltiplos resultados.")
    return None


def cria_usuario_ad(nomeUsuarioCapitalizado,cpfUsuario,dataNascimentoUsuario,emailPessoal,telefoneComercial,
        matriculaSiape,
        empresa,
        localizacao,
        cargo,
        departamento,
        chefia
    ):
    conn_ad = conectar_ad()
    saida = ""
    # Monta DN do novo usuário
    if cargo == 'Servidor':
        ou_destino = "OU=Servidores,OU=Usuarios,OU=CADE"
    else:
        ou_destino = "OU=Colaboradores,OU=Usuarios,OU=CADE"

    dn_usuario = f"CN={nomeUsuarioCapitalizado},{ou_destino},{BASE_DN}"
    login_final = buscar_login(nomeUsuarioCapitalizado)

    atributos = {
    "objectClass": ["top", "person", "organizationalPerson", "user"],
    "cn": nomeUsuarioCapitalizado,
    "displayName": nomeUsuarioCapitalizado,
    "sAMAccountName": login_final,
    #"userPrincipalName": login_final,
    "userPrincipalName": f"{login_final}@cade.gov.br",
    #"mail": email,
    "title": cargo,
    "department": departamento,
    "telephoneNumber": telefoneComercial,
    "company": empresa,
    "extensionAttribute1": dataNascimentoUsuario,
    #"homePhone": data_nascimento,
    "employeeNumber": cpfUsuario,
    }
    senha_gerada = gerar_senha()
    logging.info(f"Gerou a senha: {senha_gerada}")       
    # Verifica se a chefia existe. Caso não exista ou seja inválida, não adiciona o atributo manager
    manager_dn = busca_manager(chefia)
    if manager_dn:
        atributos["manager"] = manager_dn
    logging.info(f"Verificou o manager : {manager_dn}")  

    if conn_ad.add(dn_usuario, attributes=atributos):
        logging.info(f"[SUCESSO] Conta criada: {login_final}")
        # Gera a senha segura
        #print(f"  - Senha gerada {senha_gerada}")
        try:
            # Define a senha
            conn_ad.extend.microsoft.modify_password(dn_usuario, senha_gerada)

            # Ativa o usuário e força troca de senha
            conn_ad.modify(dn_usuario, {
                "userAccountControl": [(ldap3.MODIFY_REPLACE, [544])],
                "pwdLastSet": [(ldap3.MODIFY_REPLACE, [0])]
            })

            saida = (f"Conta criada, senha aplicada e troca exigida no primeiro logon. E-mail enviado com a senha criada.")
        except Exception as e:
            logging.error(f"[EXCEÇÃO] Falha ao definir senha ou ativar conta: {e}")
            saida = f"Erro ao criar usuário. Entre em contato com a CGTI"
            return saida
    else:
        logging.error("Caiu no Else")
        saida = f"Erro: Falha ao criar {nome_login}: {conn_ad.result}"
        return saida
    return "Não executou nada"


def extrair_cn(dn):
    match = re.search(r"CN=([^,]+)", dn)
    return match.group(1) if match else None


def desativar_usuario(conn, dn):
    return conn.modify(dn, {
        "userAccountControl": [(MODIFY_REPLACE, [514])]
    })

def mover_usuario(conn, dn, nova_ou):
    cn = extrair_cn(dn)
    if not cn:
        raise ValueError(f"Não foi possível extrair CN de: {dn}")
    return conn.modify_dn(dn, f"CN={cn}", new_superior=nova_ou)


def modificaUsuario(cpfUsuario):
    cpf_input = cpfUsuario.strip()
    # Remove caracteres não numéricos do CPF
    cpf = re.sub(r'\D', '', cpf_input)

    if not re.fullmatch(r'\d{11}', cpf):
        print(f"[ERRO] CPF inválido: {cpf_input}")
        return

    try:
        conn = conectar_ad()
        dn_usuario = buscar_usuario_por_cpf(conn, cpf)
        #Variável para armazenar o nome do usuário
        # nome = extrair_cn(dn_usuario)

        if not dn_usuario:
            logging.error(f"Usuário com CPF {cpf} não encontrado.")
            return f"Usuário com CPF {cpf} não encontrado."
        
        #Verifica se a conta já está desativada
        conn.search(dn_usuario, '(objectClass=person)', attributes=['userAccountControl'])
        if conn.entries:
            uac = int(conn.entries[0]['userAccountControl'].value)
            if uac & 2:
                return f"Usuário já está desativado."
        # return f"Usuário encontrado: {nome}"
        if not desativar_usuario(conn, dn_usuario):
            logging.error(f"Falha ao desativar a conta: {conn.result['description']}")
            return f"Falha ao desativar a conta."
        if not mover_usuario(conn, dn_usuario, NOVA_OU):
            logging.error(f"Falha ao mover o usuário de OU: {conn.result['description']}")
            return f"Falha ao desativar a conta."
        return f"Usuário desativado com sucesso!"
    except Exception as e:
        logging.error(f"[EXCEÇÃO] {e}")
        return f"Falha ao desativar a conta."
    finally:
        if 'conn' in locals() and conn.bound:
            conn.unbind()
            logging.info("Conexão AD encerrada.")


# --- Executar o script diretamente ---
if __name__ == "__main__":
    # Se quiser só testar a conexão, descomente a linha abaixo:
    # testar_conexao_ad()
    #conn = conectar_ad()
    # cria_usuario_ad(nomeUsuarioCapitalizado="Suvaco Pires de Melo",cpfUsuario="11111111111",
    #                 dataNascimentoUsuario="1988-06-16",emailPessoal="suvaco@gmail.com",telefoneComercial="6199999999",
    #     matriculaSiape="123456",
    #     empresa="LENATEC",
    #     localizacao="Remoto",
    #     cargo="Terceiro",
    #     departamento="SESIN",
    #     chefia="Thiago Nogueira de Oliveira"
    # )  # Exemplo de CPF
    # #print(busca_manager("Thiago Nogueira de Oliveiraddd"))
    pass
