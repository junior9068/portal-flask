import mysql.connector
import logging
from mysql.connector import IntegrityError
import time

# Configuração para os Logs da aplicação
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        # logging.FileHandler("app.log"),  # salva em arquivo
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
        status = "aguardando"
        valores = (json, acao, status)
        cursor.execute(sql, valores)
        # PEGANDO O ID DO REGISTRO INSERIDO
        registro_id = cursor.lastrowid
        conexao.commit()
        logging.info(f"Registro inserido no banco: {registro_id}")
        saida = registro_id  # Retorna o ID do registro inserido  
    except Exception as erro:
        saida = f"Erro ao cadastrar usuário. Entre em contato com a CGTI"
        logging.error(f"Erro ao cadastrar usuário: {erro}")
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
        return saida


# def lerResultado(id):
#     cursor = None
#     conexao = None
#     saida = ''

#     try:
#         conexao = conexao_banco()
#         cursor = conexao.cursor()
#         sql = "SELECT status FROM registros WHERE id = %s"
#         valores = (id,)  # Tupla com um elemento

#         cursor.execute(sql, valores)
#         resultado = cursor.fetchone()
#         print(resultado)
#         if resultado:
#             saida = resultado  # ou adapte conforme seu uso
#             logging.info(f"Registro encontrado para ID {id}: {resultado}")
#         else:
#             saida = f"Nenhum registro encontrado com ID {id}"
#             logging.warning(saida)

#     except Exception as erro:
#         saida = "Erro ao buscar o registro. Entre em contato com a CGTI."
#         logging.error(f"Erro ao buscar registro: {erro}")

#     finally:
#         if cursor:
#             cursor.close()
#         if conexao:
#             conexao.close()
#         return saida


def lerResultado(id, timeout=10, intervalo=1):
    """
    Fica consultando o status de um registro até que ele seja 'Sucesso' ou 'Erro'.

    Parâmetros:
        id (int): ID do registro.
        timeout (int): Tempo máximo de espera (em segundos).
        intervalo (int): Intervalo entre consultas (em segundos).

    Retorna:
        str: Mensagem baseada no status.
    """
    tempo_inicio = time.time()

    while True:
        cursor = None
        conexao = None
        try:
            conexao = conexao_banco()
            cursor = conexao.cursor()
            sql = "SELECT status FROM registros WHERE id = %s"
            valores = (id,)
            cursor.execute(sql, valores)
            resultado = cursor.fetchone()

            if resultado:
                status = resultado[0]
                logging.info(f"Status atual do ID {id}: {status}")

                if status == "Sucesso":
                    # Lê o campo senha do registro
                    sql = "SELECT senha FROM registros WHERE id = %s"
                    valores = (id,)
                    cursor.execute(sql, valores)
                    resultado = cursor.fetchone()
                    # Retorna uma tupla com o status e a senha
                    return status, resultado[0]
                
                elif status == "Erro":
                    sql = "SELECT erro FROM registros WHERE id = %s"
                    valores = (id,)
                    cursor.execute(sql, valores)
                    resultado = cursor.fetchone()
                    # Retorna uma tupla com o status e o erro
                    return status, resultado[0]

            else:
                return f"Nenhum registro encontrado com ID {id}."

            # Checa se o tempo limite foi atingido
            if time.time() - tempo_inicio > timeout:
                return f"⏳ Tempo limite excedido aguardando conclusão do ID {id}."

            time.sleep(intervalo)

        except Exception as erro:
            logging.error(f"Erro ao consultar status do ID {id}: {erro}")
            return "Erro ao consultar o status. Contate a CGTI."

        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

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


if __name__ == "__main__":
    print(lerResultado(25))
