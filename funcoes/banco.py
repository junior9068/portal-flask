import mysql.connector
import logging

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
    return mysql.connector.connect(
    host="localhost",
    user="user_banco",           # usuário
    password="Usuariobanco@2025",  # senha do usuário
    database="portal"       # nome do banco
    )

# cursor = conexao.cursor()

def inserir_usuario(nome, cpf, dataNascimento):
    try:
        conexao=conexao_banco()
        cursor = conexao.cursor()
        sql = "INSERT INTO usuarios (nome, cpf, data_nascimento) VALUES (%s, %s, %s)"
        valores = (nome, cpf, dataNascimento)
        cursor.execute(sql, valores)
        conexao.commit()
        logging.info(f"Usuário: {nome}")
        logging.info(f"CPF: {cpf}")
        logging.info(f"Data de Nascimento: {dataNascimento}")
        cursor.close()
        conexao.close()
        saida = "Usuário cadastrado com sucesso!"
    except mysql.connector.Error as err:
        saida = f"Erro ao cadastrar usuário. Entrer em contato com a CGTI"
        logging.error(f"Erro ao cadastrar usuário: {err}")
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

