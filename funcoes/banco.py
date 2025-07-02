import mysql.connector
import logging
from mysql.connector import IntegrityError
# Configuração para os Logs da aplicação
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # salva em arquivo
        logging.StreamHandler()         # mostra no terminal
    ]
)
# Conectar ao banco
def conexao_banco():
    try:
        return mysql.connector.connect(
        host="localhost",
        user="user_banco",           # usuário
        password="Usuariobanco@2025",  # senha do usuário
        database="portal"       # nome do banco
        )
    except Exception as erro:
        logging.error(f"Erro no Banco de Dados: {erro}")

# cursor = conexao.cursor()

def inserir_usuario(json, acao):
    cursor = ''
    saida = ''
    try:
        conexao=conexao_banco()
        cursor = conexao.cursor()
        sql = "INSERT INTO registros (dados_json, acao, status) VALUES (%s, %s, %s)"
        valores = (json, acao, 0)
        cursor.execute(sql, valores)
        conexao.commit()
        logging.info(f"JSON: {json}")
        logging.info(f"Ação: {acao}")
        logging.info(f"Status: 0")
        # cursor.close()
        # conexao.close()
        saida = "Usuário cadastrado com sucesso!"
    except IntegrityError as erro:
        if erro.errno == 1062:
            saida = "CPF já cadastrado. Verifique os dados e tente novamente."
        else:
            saida = "Erro de integridade ao cadastrar usuário. Contate a CGTI."
        logging.error(f"Erro de integridade: {erro}")    
    except Exception as erro:
        saida = f"Erro ao cadastrar usuário. Entre em contato com a CGTI"
        logging.error(f"Erro ao cadastrar usuário: {erro}")
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
        return saida

def deletar_usuario(cpf):
    cursor = ''
    saida = ''
    try:
        conexao=conexao_banco()
        cursor = conexao.cursor()
        sql =  "DELETE FROM usuarios WHERE cpf = %s"
        valores = (cpf,)
        cursor.execute(sql, valores)
        conexao.commit()
        # Verifica se foi encontrado CPF no Banco (o MySql simplesmente não gera erro quando não encontra o CPF no banco para deletar)
        if cursor.rowcount == 0:
            saida = "Nenhum usuário encontrado com esse CPF."
        else:
            saida = "Usuário deletado com sucesso!"
    except Exception as erro:
        saida = f"Erro ao deletar usuário. Entre em contato com a CGTI"
        logging.error(f"Erro ao deletar usuário: {erro}")
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
        return saida


# # Inserir dados
# nome = "Edilson"
# cpf = "02982448530jkj"

# sql = "INSERT INTO usuarios (nome, cpf) VALUES (%s, %s)"
# valores = (nome, cpf)

# cursor.execute(sql, valores)
# conexao.commit()

# print("Usuário cadastrado com sucesso!")

# Listar todos os usuários
# cursor.execute("SELECT * FROM usuarios")
# usuarios = cursor.fetchall()

# print("Usuários cadastrados:")
# for u in usuarios:
#     print(u)

# Fechar conexão

