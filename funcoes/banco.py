import mysql.connector
import logging
from mysql.connector import IntegrityError
import time, os

USUARIO_BANCO = os.getenv('USUARIO_BANCO')
SENHA_BANCO = os.getenv('SENHA_BANCO')
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
        user=USUARIO_BANCO,           # usuário
        password=SENHA_BANCO,  # senha do usuário
        database="portal"       # nome do banco
        )
    except Exception as erro:
        logging.error(f"Erro no Banco de Dados: {erro}")

# cursor = conexao.cursor()

def registrar_log(usuario_sistema, usuario_ad, acao, observacoes=None):
    conexao = None
    cursor = None
    try:
        conexao = conexao_banco()
        cursor = conexao.cursor()
        sql = """
            INSERT INTO log_ad (usuario_sistema, usuario_ad, acao, observacoes)
            VALUES (%s, %s, %s, %s)
        """
        valores = (usuario_sistema, usuario_ad, acao, observacoes)
        cursor.execute(sql, valores)
        conexao.commit()
        log_id = cursor.lastrowid
        logging.info(f"Log inserido: {usuario_sistema} -> {usuario_ad} ({acao})")
        return log_id
    except Exception as erro:
        logging.error(f"Erro ao inserir log de registro no banco: {erro}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


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

def consulta_geral(mes, ano, acao):
    cursor = ''
    saida = ''
    try:
        conexao=conexao_banco()
        cursor = conexao.cursor(buffered=True)
        sql = """select COUNT(*) from log_ad where MONTH(data_acao) = %s and YEAR(data_acao) = %s and acao= %s;"""
        cursor.execute(sql, (mes, ano, acao))
        resultado = cursor.fetchall()
        quantidade = resultado[0][0]
        saida = quantidade
    except Exception as erro:
        saida = 0
        logging.error(f"Erro ao realizar a consulta no banco: {erro}")
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
        return saida

if __name__ == "__main__":
    print(consulta_geral(11, 2025, 'consultar_usuario'))
    # print(registrar_log(
    #             usuario_sistema="edilson.junior@cade.gov.br",
    #             usuario_ad="teste.fulano",
    #             acao="criar_usuario",
    #             observacoes=f"Usuário teste.fulano criado com sucesso."
    #         ))
