import re
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import logging

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


def buscar_usuario_por_cpf(conn, cpf):
    filtro = f"(employeeNumber={cpf})"
    conn.search(BASE_DN, filtro, attributes=["distinguishedName"])

    if conn.entries:
        return conn.entries[0].distinguishedName.value
        print("Entrei no IF")
    return None


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
        nome = extrair_cn(dn_usuario)

        if not dn_usuario:
            logging.error(f"Usuário com CPF {cpf} não encontrado.")
            return f"Usuário com CPF {cpf} não encontrado."
        
        # Verifica se a conta já está desativada
        conn.search(dn_usuario, '(objectClass=person)', attributes=['userAccountControl'])
        if conn.entries:
            uac = int(conn.entries[0]['userAccountControl'].value)
            if uac & 2:
                return f"Usuário já está desativado."
        return f"Usuário encontrado: {nome}"
        # if not desativar_usuario(conn, dn_usuario):
        #     logging.error(f"Falha ao desativar a conta: {conn.result['description']}")
        #     return f"Falha ao desativar a conta."
        # if not mover_usuario(conn, dn_usuario, NOVA_OU):
        #     logging.error(f"Falha ao mover o usuário de OU: {conn.result['description']}")
        #     return f"Falha ao desativar a conta."
        # return f"Usuário desativado com sucesso!"
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
    modificaUsuario("11111111111")
