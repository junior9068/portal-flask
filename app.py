from flask import Flask, request
from markupsafe import escape
from flask import render_template
from funcoes import funcoes
import logging


app = Flask(__name__)

# Configuração para os Logs da aplicação
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # salva em arquivo
        logging.StreamHandler()         # mostra no terminal
    ]
)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/cria_usuario")
def cria_usuario():
    app.logger.info(f"Chamou a rota cria_usuario")
    return render_template("cria_usuario.html")


@app.route("/executa_cria_usuario", methods=['POST'])
def executa_cria_usuario():
    nome_usuario = request.form['nomeUsuario']
    cpf_usuario = request.form['cpfUsuario']
    app.logger.info(f"Usuário: {nome_usuario}")
    app.logger.info(f"CPF: {cpf_usuario}")
    execucao_comando = funcoes.exemplo_chamada_bash()
    return render_template("cria_usuario.html", variavel_execucao_comando=execucao_comando)



if __name__ == "__main__":
    app.run(debug=True)
