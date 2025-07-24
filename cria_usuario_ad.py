#import MySQLdb
import mysql.connector
import json
import ssl
import re
import ldap3
import random
import string
from mysql.connector import Error
#ifrom MySQLdb import Error
#from ldap3 import Tls
from ldap3 import Server, Connection, ALL, Tls
# --- CONFIGURAÇÕES ---

#server_address = "ldap://10.1.6.37"
server_address = "ldaps://SRVPADDNS02.cade.gov.br"
usuario_ad = "srvportalad@cade.gov.br"
#usuario_ad = "cade\srvportalad"
senha_ad = "s2G2x2xgKc54."
base_dn = "DC=cade,DC=gov,DC=br"
#ou_destino = "OU=Usuarios,OU=TI"  # Altere conforme sua estrutura do AD
ou_destino = "OU=Usuarios,OU=CADE"  # Altere conforme sua estrutura do AD


# --- CONECTA AO AD ---
tls_config = Tls(validate=ssl.CERT_REQUIRED)
server = Server(server_address, port=636, use_ssl=True, get_info=ALL, tls=tls_config)
#server = ldap3.Server(server_address, port=636, use_ssl=True, tls=tls_configuration)
#server = ldap3.Server(server_address)
try:
    conn_ad = ldap3.Connection(server, user=usuario_ad, password=senha_ad, authentication='SIMPLE', auto_bind=True)
except ldap3.core.exceptions.LDAPBindError as e:
    print(f"[ERRO] Falha no bind: {e}")
    exit(1)

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
# --- FUNÇÃO PARA GERAR LOGIN ---
def gerar_login(nome_completo):
    partes = nome_completo.strip().split()
    if len(partes) < 2:
        return None, None
    nome = partes[0].lower()
    sobrenome1 = partes[-1].lower()
    login1 = f"{nome}.{sobrenome1}x"
    login2 = f"{nome}.{partes[1].lower()}" if len(partes) >= 3 else None
    return login1, login2

# --- CONEXÃO COM MYSQL ---
try:
    conexao = mysql.connector.connect(
        host='10.1.7.72',
        user='usr_integracao',
        password='Integracao@portal25',
        database='portal'
    )

    if conexao.is_connected():
        print("Conectado ao banco de dados.")
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT id,dados_json FROM registros WHERE acao = 'cadastrar_usuario' and status not in ('Erro','Sucesso')")
        registros = cursor.fetchall()

        for registro in registros:
            try:
                dados = json.loads(registro["dados_json"])
                nome = dados.get("nome", "").strip()
                cpf = str(dados.get("cpf", "") or "").strip().replace(".", "").replace("-", "")
                #email = dados.get("email", "").strip()
                cargo = dados.get("cargo", "").strip()
                departamento = dados.get("departamento", "").strip()
                telefone = dados.get("telefoneComercial", "").strip()
                empresa = dados.get("empresa", "").strip()
                data_nascimento = dados.get("dataNascimento", "").strip()
                chefia = dados.get("chefia", "").strip()

                # Verifica se CPF tem ao menos um número
                if not re.search(r"\d", cpf):
                    print(f"[IGNORADO] CPF inválido: {cpf}")
                    continue

                # Verifica se já existe alguém com este CPF no AD
                filtro_cpf = f"(employeeNumber={cpf})"
                conn_ad.search(base_dn, filtro_cpf, attributes=["distinguishedName"])
                if conn_ad.entries:
                    print(f"[DUPLICADO] CPF {cpf} já existe no AD.")
                    cursor.execute("UPDATE registros SET erro = %s, status = %s WHERE id = %s",("CPF ja cadastrado", "Erro", int(registro["id"])))
                    conexao.commit()
                    continue

                # Gera login
                login1, login2 = gerar_login(nome)
                login_final = None

                for login in [login1, login2]:
                    if not login:
                        continue
                    filtro_login = f"(sAMAccountName={login})"
                    conn_ad.search(base_dn, filtro_login, attributes=["distinguishedName"])
                    if not conn_ad.entries:
                        login_final = login
                        break

                if not login_final:
                    print(f"[ERRO] Login já existe")
                    cursor.execute("UPDATE registros SET erro = %s, status = %s WHERE id = %s",("Usuario ja existe", "Erro", registro["id"]))
                    conexao.commit()
                    continue

                # Resolve chefia se possível
                manager_dn = None
                if chefia:
                    conn_ad.search(base_dn, f"(displayName={chefia})", attributes=["distinguishedName"])
                    if len(conn_ad.entries) == 1:
                        manager_dn = conn_ad.entries[0]["distinguishedName"].value
                        print(f"  - Chefia encontrada: {manager_dn}")

                # Monta DN do novo usuário
                if cargo in ['servidor']:
                    ou_destino = "OU=Servidores,OU=Usuarios,OU=CADE"
                else:
                    ou_destino = "OU=Colaboradores,OU=Usuarios,OU=CADE"

                dn_usuario = f"CN={nome},{ou_destino},{base_dn}"

                atributos = {
                    "objectClass": ["top", "person", "organizationalPerson", "user"],
                    "cn": nome,
                    "displayName": nome,
                    "sAMAccountName": login_final,
                    #"userPrincipalName": login_final,
                    "userPrincipalName": f"{login_final}@cade.gov.br",
                    #"mail": email,
                    "title": cargo,
                    "department": departamento,
                    "telephoneNumber": telefone,
                    "company": empresa,
                    "extensionAttribute1": data_nascimento,
                    #"homePhone": data_nascimento,
                    "employeeNumber": cpf
                }

                if manager_dn and manager_dn is not None:
                    atributos["manager"] = manager_dn
                senha_gerada = gerar_senha()
                print(f"[CRIANDO] {nome} |dn {dn_usuario} | login: {login_final} | CPF: {cpf} | {data_nascimento}")
                if conn_ad.add(dn_usuario, attributes=atributos):
                    print(f"[SUCESSO] Conta criada: {login_final}")
                    # Gera a senha segura
                    senha_gerada = gerar_senha()
                    #print(f"  - Senha gerada {senha_gerada}")
                    try:
                        # Define a senha
                        conn_ad.extend.microsoft.modify_password(dn_usuario, senha_gerada)

                        # Ativa o usuário e força troca de senha
                        conn_ad.modify(dn_usuario, {
                            "userAccountControl": [(ldap3.MODIFY_REPLACE, [544])],
                            "pwdLastSet": [(ldap3.MODIFY_REPLACE, [0])]
                        })

                        print(f"[SUCESSO] Senha aplicada, conta ativada e troca exigida no primeiro logon.")
                        # Atualiza o banco com a senha e status
                        cursor.execute("UPDATE registros SET senha = %s, status = %s WHERE id = %s",(senha_gerada, "Sucesso", registro["id"]))
                        conexao.commit()
                    except Exception as e:
                        print(f"[ERRO] Ao definir senha/ativar: {e}")
                        cursor.execute("UPDATE registros SET senha = %s, status = %s WHERE id = %s",(senha_gerada, conn_ad, registro["id"]))
                        conexao.commit()
                else:
#                    print(f"[ERRO] Falha ao criar {nome}: {conn_ad.result['description']}")
                    print(f"[ERRO] Falha ao criar {nome}: {conn_ad.result}")
                    cursor.execute("UPDATE registros SET status = %s WHERE id = %s",(f"Falha: {conn_ad}", registro["id"]))
                    conexao.commit()

            except json.JSONDecodeError:
                print(f"[ERRO] JSON malformado: {registro['dados_json']}")
            except Exception as e:
                print(f"[EXCEÇÃO] {e}")

except Error as e:
    print(f"[ERRO MYSQL] {e}")

finally:
    if 'conexao' in locals() and conexao.is_connected():
        cursor.close()
        conexao.close()
        print("Conexão MySQL encerrada.")

    if conn_ad.bound:
        conn_ad.unbind()
        print("Conexão AD encerrada.")

if __name__ == "__main__":
    print(gerar_login("Edilson Cardoso de Souza Junior"))