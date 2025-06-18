from flask import Flask, request
from markupsafe import escape
from flask import render_template
from funcoes import funcoes
import logging
from funcoes.banco import inserir_usuario


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/cria_usuario")
def cria_usuario():
    app.logger.info(f"Chamou a rota cria_usuario")
    return render_template("cria_usuario.html")


@app.route("/desativa_usuario")
def desativa_usuario():
    app.logger.info(f"Chamou a rota desativa_usuario")
    return render_template("desativa_usuario.html")


@app.route("/executa_desativa_usuario", methods=['POST'])
def executa_desativa_usuario():
    nome_usuario = request.form['nomeUsuario']
    app.logger.info(f"Chamou a rota executa_desativa_usuario")
    app.logger.info(f"Nome do usuário: {nome_usuario}")
    return render_template("desativa_usuario.html", nome_usuario=nome_usuario)


@app.route("/executa_cria_usuario", methods=['POST'])
def executa_cria_usuario():
    nome_usuario = request.form['nomeUsuario']
    cpf_usuario = request.form['cpfUsuario']
    saida = inserir_usuario(nome=nome_usuario, cpf=cpf_usuario)
    # app.logger.info(f"Usuário: {nome_usuario}")
    # app.logger.info(f"CPF: {cpf_usuario}")
    # execucao_comando = funcoes.exemplo_chamada_bash()
    return render_template("cria_usuario.html", variavel_execucao_comando=saida)


if __name__ == "__main__":
    app.run(debug=True)
