from flask import Flask, request
from markupsafe import escape
from flask import render_template
from funcoes import funcoes
import logging
from funcoes.banco import inserir_usuario, deletar_usuario


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/manutencao")
def manutencao():
    return render_template("manutencao.html")


@app.route("/manutencao1")
def manutencao1():
    return render_template("manutencao.html")


@app.route("/manutencao2")
def manutencao2():
    return render_template("manutencao.html")


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
    cpf_usuario = request.form['cpfUsuario']
    app.logger.info(f"Chamou a rota executa_desativa_usuario")
    app.logger.info(f"CPF do usuário: {cpf_usuario}")
    saida = deletar_usuario(cpf=cpf_usuario)
    return render_template("desativa_usuario.html", nome_usuario=saida)


@app.route("/executa_cria_usuario", methods=['POST'])
def executa_cria_usuario():
    nome_usuario = request.form['nomeUsuario']
    cpf_usuario = request.form['cpfUsuario']
    data_nascimento_usuario = request.form['dataNascimentoUsuario']
    saida = inserir_usuario(nome=nome_usuario, cpf=cpf_usuario, dataNascimento=data_nascimento_usuario)
    # app.logger.info(f"Usuário: {nome_usuario}")
    # app.logger.info(f"CPF: {cpf_usuario}")
    # execucao_comando = funcoes.exemplo_chamada_bash()
    return render_template("cria_usuario.html", variavel_execucao_comando=saida)


if __name__ == "__main__":
    app.run(debug=True)
