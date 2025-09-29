import re
import ldap3
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, ALL_ATTRIBUTES, MODIFY_ADD
import logging
from flask import jsonify
import string
import random, os
from funcoes.funcoes import enviar_email_criacao, enviar_email_desativacao
from funcoes.banco import registrar_log
# --- CONFIGURAÇÕES DO AD ---
# Senha e usuario do AD estão definidos como variável de ambiente

USUARIO_AD = os.environ.get("USUARIO_AD")
SENHA_AD = os.environ.get("SENHA_AD")
if os.getenv("FLASK_ENV") == "desenvolvimento":
    BASE_DN = "dc=ad,dc=local"
    NOVA_OU = 'OU=Usuarios,OU=NoSync--M365,DC=ad,DC=local'
    SERVIDOR_AD = os.environ.get("SERVIDOR_AD")
else:
    SERVIDOR_AD = "ldaps://SRVPADDNS02.cade.gov.br"
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
    conn = Connection(server, user=USUARIO_AD, password=SENHA_AD, auto_bind=True, raise_exceptions=True)
    return conn


def consultar_usuario(identificador, usuarioLogado):
    # Verifica se o identificador é um email ou CPF
    if "@" in identificador:
        email = identificador.strip()
        filtro = f"(mail={email})"
    else:
        cpf = identificador.strip()
        filtro = f"(employeeNumber={cpf})"
    try:
        conn = conectar_ad()
        #filtro = f"(employeeNumber={cpf})"
        # email = "edilson.junio@cade.gov.br"
        # filtro = f"(mail={email})"
        #conn.search(BASE_DN, filtro, attributes=["distinguishedName"])
        conn.search(BASE_DN, filtro, attributes=["mail", "distinguishedName","cn", "title", "department", "company", "extensionAttribute1", "employeeID", "manager", "employeeNumber", "otherMailbox", "telephoneNumber"])

        # return conn.entries[0]
        if conn.entries:
            # dn = conn.entries[0].distinguishedName.value
            # nome = dn.split(',')[0].split('=')[1]
            nome = conn.entries[0].cn.value
            email = conn.entries[0].mail.value
            departamento = conn.entries[0].department.value
            cargo = conn.entries[0].title.value
            empresa = conn.entries[0].company.value
            data_nascimento = conn.entries[0].extensionAttribute1.value
            siape = conn.entries[0].employeeID.value
            chefia = conn.entries[0].manager.value.split(',')[0].replace('CN=', '') if conn.entries[0].manager.value else "-"
            cpf = conn.entries[0].employeeNumber.value
            email_pessoal = conn.entries[0].otherMailbox.value
            telefone_comercial = conn.entries[0].telephoneNumber.value
            login = email.split('@')[0] if email else "-"
            logging.info(f"Email: {email}")
            # print(f"Nome: {nome}, Email: {email}, Departamento: {departamento}, Cargo: {cargo}, Empresa: {empresa}, Data de Nascimento: {data_nascimento}, SIAPE: {siape}, Chefia: {chefia}, CPF: {cpf}")
            # retorna uma tupla com nome e email (o Flask deve estar em execução para funcionar)
            logging.info(f"Usuário encontrado: {nome}, Email: {email}")
            registrar_log(
                usuario_sistema=usuarioLogado.get('email'),
                usuario_ad=login,
                acao="consultar_usuario",
                observacoes=f"Usuário consultado!"
            )
            return {
                "nome": nome, 
                "email": email, 
                "departamento": departamento,
                "cargo": cargo, 
                "empresa": empresa, 
                "data_de_nascimento": data_nascimento,
                "siape": siape, 
                "chefia": chefia, 
                "cpf": cpf,
                "email_pessoal": email_pessoal,
                "telefone_comercial": telefone_comercial   
            }
        logging.warning(f"Usuário não encontrado.")
        return None
        # return jsonify({"nome": "Não encontrado", "email": "Não encontrado"})
    except Exception as e:
        logging.error(f"Erro ao consultar usuário: {e}")
        return None


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

def convete_data(data):
    if not data:
        return None
    try:
        partes = data.split('-')
        if len(partes) == 3:
            return f"{partes[2]}/{partes[1]}/{partes[0]}"
        else:
            logging.error(f"Formato de data inválido: {data}")
            return None
    except Exception as e:
        logging.error(f"Erro ao converter data: {e}")
        return None


def adicionar_usuario_a_grupo(dn_usuario, dn_grupo, conexao_ad):
    saida = ''
    try:
        # Adicionar o usuário ao grupo
        conexao_ad.modify(
            dn_grupo,
            {
                'member': [(MODIFY_ADD, [dn_usuario])]
            }
        )
        if conexao_ad.result['result'] == 0:
            logging.info(f"Usuário adicionado ao grupo {dn_grupo}")
            saida =  "Sucesso"
        else:
            logging.error("Erro:", conexao_ad.result)
            saida =  "Erro"
    except Exception as e:
        logging.error("Erro ao adicionar usuário ao grupo:", e)
        saida =  "Erro"
    return saida


def cria_usuario_ad(nomeUsuarioCapitalizado,cpfUsuario,dataNascimentoUsuario,emailPessoal,telefoneComercial,
        matriculaSiape,
        empresa,
        localizacao,
        cargo,
        departamento,
        chefia,
        usuarioLogado
    ):
    conn_ad = conectar_ad()
    saida = ""
    dataConvertida = convete_data(dataNascimentoUsuario)
    # Cria a lista de grupos padrão
    lista_grupos = [f"cn=FW_PADRAO,ou=Grupos,ou=CADE,{BASE_DN}"]
    # Monta DN do novo usuário e completa a lista de grupos conforme o cargo
    if cargo == 'Servidor':
        ou_destino = "OU=Servidores,OU=Usuarios,OU=CADE"
        lista_grupos.append(f"cn=GoFluent,ou=Grupos,ou=CADE,{BASE_DN}")
        lista_grupos.append(f"cn=GS_LICENCA_M365_E3,ou=m365,ou=Grupos,ou=CADE,{BASE_DN}")
    else:
        ou_destino = "OU=Colaboradores,OU=Usuarios,OU=CADE"
        lista_grupos.append(f"cn=GS_LICENCA_M365_E1,ou=m365,ou=Grupos,ou=CADE,{BASE_DN}")

    dn_usuario = f"CN={nomeUsuarioCapitalizado},{ou_destino},{BASE_DN}"
    login_final = buscar_login(nomeUsuarioCapitalizado)
    # Separa o nome e sobrenome
    nomes = nomeUsuarioCapitalizado.split()
    nomes.pop(0)
    sobrenome = " ".join(nomes)

    atributos = {
    "objectClass": ["top", "person", "organizationalPerson", "user"],
    "cn": nomeUsuarioCapitalizado,
    "displayName": nomeUsuarioCapitalizado,
    "sAMAccountName": login_final,
    "userPrincipalName": f"{login_final}@cade.gov.br",
    "title": cargo,
    "department": departamento,
    "telephoneNumber": telefoneComercial,
    "company": empresa,
    "extensionAttribute1": dataConvertida,
    "employeeNumber": cpfUsuario,
    "mail": f"{login_final}@cade.gov.br",
    "physicalDeliveryOfficeName": localizacao,
    "givenName": nomeUsuarioCapitalizado.split()[0],
    "sn": sobrenome,
    "otherMailbox": emailPessoal
    }
    # Adiciona o atributo de matricula SIAPE
    if matriculaSiape != "":
        atributos["employeeID"] = matriculaSiape
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
            # Adiciona o usuário aos grupos
            for grupo in lista_grupos:
                adicionar_usuario_a_grupo(dn_usuario, grupo, conn_ad)
            envio_email = enviar_email_criacao(senha_gerada, emailPessoal, login_final)
            if envio_email:
                logging.info(f"[SUCESSO] E-mail enviado para {emailPessoal}")
            else:
                saida = f"Usuário {nomeUsuarioCapitalizado} criado, mas tivemos uma falha ao enviar e-mail para {emailPessoal}."
                logging.error(f"[ERRO] Falha ao enviar e-mail para {emailPessoal}")

            logging.info(f"[SUCESSO] Senha definida e conta ativada)")
            registrar_log(
                usuario_sistema=usuarioLogado.get('email'),
                usuario_ad=login_final,
                acao="criar_usuario",
                observacoes=f"Usuário criado!"
            )
            # Retorna uma mensagem de sucesso
            saida = f"A conta {login_final}@cade.gov.br foi criada com sucesso. As informações de acesso à rede do CADE foram enviadas para o email {emailPessoal}."
            return saida
        except Exception as e:
            logging.error(f"[EXCEÇÃO] Falha ao definir senha ou ativar conta: {e}")
            saida = f"Erro ao criar usuário. Entre em contato com a CGTI"
            return saida
    else:
        logging.error("Caiu no Else")
        saida = f"Erro: Falha ao criar {nome_login}: {conn_ad.result}"
        return saida


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


def modificaUsuario(cpfUsuario, usuarioLogado):
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
        conn.search(dn_usuario, '(objectClass=person)', attributes=['userAccountControl', 'sAMAccountName', 'otherMailbox'])
        if conn.entries:
            login_usuario_ad = conn.entries[0]['sAMAccountName'].value
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
        # Envia o e-mail de desativação
        # email_usuario = conn.entries[0]['otherMailbox'].value
        # enviar_email_desativacao(email_usuario, login_usuario_ad)
        # if envio_email:
        #     logging.info(f"[SUCESSO] E-mail de desativação enviado para {email_usuario}")
        # else:
        #     logging.error(f"[ERRO] Falha ao enviar e-mail de desativação para {email_usuario}")
        registrar_log(
            usuario_sistema=usuarioLogado.get('email'),
            usuario_ad=login_usuario_ad,
            acao="desativar_usuario",
            observacoes=f"Usuário desativado!"
        )
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
    testar_conexao_ad()
    #conn = conectar_ad()
    # print(cria_usuario_ad(nomeUsuarioCapitalizado="Pedro de Lara Cancum",
    #     cpfUsuario="704.466.230-75",
    #     dataNascimentoUsuario="1980-01-01",
    #     emailPessoal="pedro@gmail.com",
    #     telefoneComercial="61999999999",
    #     matriculaSiape="1234567",
    #     empresa="CADE",
    #     localizacao="Remoto",
    #     cargo="Servidor",
    #     departamento="SESIN",
    #     chefia="Thiago Nogueira de Oliveira"
    # ))
    #print(consultar_usuario("03869833130", "edilson.junior@cade.gov.br"))
    # print(os.environ.get("SENHA_AD"))
    # conn = conectar_ad()
    # dn_usuario = buscar_usuario_por_cpf(conn,"02982448530")
    # conn.search(dn_usuario,'(objectClass=person)',attributes=ALL_ATTRIBUTES)
    # print(conn.entries[0])
