from flask import Flask, request
from markupsafe import escape
from flask import render_template
from funcoes import funcoes
import logging
from funcoes.banco import inserir_usuario, deletar_usuario
import json

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
    # Cria um dicionário para armazenar os dados do usuário
    nomeUsuario = request.form['nomeUsuario']
    cpfUsuario = request.form['cpfUsuario']
    dataNascimentoUsuario = request.form['dataNascimentoUsuario']
    telefoneComercial = request.form['telefoneComercial']
    departamento = request.form['departamento']
    matriculaSiape = request.form['matriculaSiape']
    empresa = request.form['empresa']
    localizacao = request.form['localizacao']
    cargo = request.form['cargo']
    dicionarioUsuario = {'nome': nomeUsuario, 'cpf': cpfUsuario, 'dataNascimento': dataNascimentoUsuario, 'empresa': empresa, 'localizacao': localizacao, 'cargo': cargo,
                         'telefoneComercial': telefoneComercial, 'departamento': departamento, 'matriculaSiape': matriculaSiape,}
    dadosJson = json.dumps(dicionarioUsuario)

    app.logger.info(dicionarioUsuario)
    #Gera arquivo JSON caso necessário
    criaArquivoJson(dicionarioUsuario)
    saida = inserir_usuario(json=dadosJson, acao='cadastrar_usuario')
    # app.logger.info(f"Usuário: {nome_usuario}")
    # app.logger.info(f"CPF: {cpf_usuario}")
    # execucao_comando = funcoes.exemplo_chamada_bash()
    return render_template("cria_usuario.html", variavel_execucao_comando=saida)

#Função criada para uma possível necessidade de gerar um arquivo json.
def criaArquivoJson(dadosJson):
    # Dicionário Python (estrutura de dados que vamos salvar como JSON)
    dados = dadosJson
    try:
        # Criar e salvar em um arquivo JSON
        with open("dados.json", "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)
        saida = "Arquivo JSON criado" 
    except:
        saida = 'Erro na geração do arquivo JSON'
        app.logger.error(saida)
    finally:
        return saida

if __name__ == "__main__":
    app.run(debug=True)
