from flask import Flask, request
from flask import render_template
from funcoes.log import configurar_logs
import logging
from funcoes.banco import inserir_usuario, deletar_usuario
from funcoes.funcoes import capitalizaNome, buscaDepartamento
import json, time

configurar_logs()

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
    logging.info(f"Chamou a rota cria_usuario")
    return render_template("formulario_ajax_simples.html")
    # return render_template("cria_usuario.html")


@app.route("/desativa_usuario")
def desativa_usuario():
    logging.info(f"Chamou a rota desativa_usuario")
    return render_template("desativa_usuario.html")


@app.route("/executa_desativa_usuario", methods=['POST'])
def executa_desativa_usuario():
    cpf_usuario = request.form['cpfUsuario']
    logging.info(f"Chamou a rota executa_desativa_usuario")
    logging.info(f"CPF do usuário: {cpf_usuario}")
    saida = deletar_usuario(cpf=cpf_usuario)
    return render_template("desativa_usuario.html", nome_usuario=saida)


@app.route("/executa_cria_usuario", methods=['POST'])
def executa_cria_usuario():
    # Cria um dicionário para armazenar os dados do usuário
    nomeUsuario = request.form['nomeUsuario']
    nomeUsuarioCapitalizado = capitalizaNome(nomeUsuario)
    cpfUsuario = request.form['cpfUsuario']
    dataNascimentoUsuario = request.form['dataNascimentoUsuario']
    emailPessoal = request.form['emailPessoal']
    telefoneComercial = request.form['telefoneComercial']
    departamentoHtml = request.form['departamento']
    matriculaSiape = request.form['matriculaSiape']
    empresa = request.form['empresa']
    localizacao = request.form['localizacao']
    cargo = request.form['cargo']
    departamento, chefia = buscaDepartamento(departamentoHtml)
    dicionarioUsuario = {'nome': nomeUsuarioCapitalizado, 'cpf': cpfUsuario, 'dataNascimento': dataNascimentoUsuario, 'email': emailPessoal, 'empresa': empresa, 'localizacao': localizacao, 'cargo': cargo,
                         'telefoneComercial': telefoneComercial, 'departamento': departamento, 'chefia': chefia, 'matriculaSiape': matriculaSiape,}
    dadosJson = json.dumps(dicionarioUsuario)
    logging.info(dicionarioUsuario)
    #Gera arquivo JSON caso necessário
    # time.sleep(5)
    saida = inserir_usuario(json=dadosJson, acao='cadastrar_usuario')
    # logging.info(f"Usuário: {nome_usuario}")
    # logging.info(f"CPF: {cpf_usuario}")
    # execucao_comando = funcoes.exemplo_chamada_bash()

    # return render_template("cria_usuario.html", variavel_execucao_comando=saida)
    #Para o ajax
    # variavel_execucao_comando=saida
    time.sleep(3)
    return str(saida)
    # return render_template('formulario_com_loading.html', variavel_execucao_comando=saida)


if __name__ == "__main__":
    app.run(debug=True)
