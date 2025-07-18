from flask import Flask, request, jsonify, redirect, url_for
from flask_session import Session
from flask import render_template
from funcoes.log import configurar_logs
import logging
from funcoes.banco import inserir_usuario, deletar_usuario, lerResultado
from funcoes.funcoes import capitalizaNome, buscaDepartamento, exemplo_chamada_bash
from funcoes.ad import modificaUsuario
import json, time
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_oidc import OpenIDConnect

# Importar módulo SAML
# from saml_auth import create_saml_auth, login_required

configurar_logs()

app = Flask(__name__)

# Flask-Session config
app.config['SESSION_TYPE'] = 'filesystem'  # ou 'redis', 'mongodb', 'sqlalchemy' se quiser
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = '/opt/portal-flask/.flask_session/'  # pasta onde sessões serão salvas

# Inicializa Flask-Session
Session(app)

app.config.update({
    'SECRET_KEY': 'minha-chave-secreta',
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_RESOURCE_SERVER_ONLY': False,
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False  # True em produção com HTTPS
})

oidc = OpenIDConnect(app)
logging.info(f"OIDC: {oidc}")
# Resolve encaminhamento do pacote
#app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Configurar chave secreta para sessões (IMPORTANTE: mude para uma chave segura em produção)
app.config['SECRET_KEY'] = 'sua-chave-secreta-mude-em-producao'

# Inicializar autenticação SAML
# saml_auth = create_saml_auth(app, saml_path='saml')

# Disponibilizar saml_auth globalmente para o decorator standalone
# app.saml_auth = saml_auth

@app.route("/")
@oidc.require_login
def home():
    #após implementar o OIDC
    user = oidc.user_getinfo(['email', 'name'])
    logging.info(f"Usuário autenticado: {user}")
    # return jsonify(user)
    return render_template("home.html")

@app.route('/logout')
def logout():
    oidc.logout()  # limpa a sessão local

    tenant_id = "0f45bbf5-e0b2-4611-869d-02cbccbc164c"
    post_logout_redirect_uri = url_for('index', _external=True)

    azure_logout_url = (
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/logout"
        f"?post_logout_redirect_uri={post_logout_redirect_uri}"
    )

    return redirect(azure_logout_url)

# @app.route('/logout')
# def logout():
#     oidc.logout()
#     return redirect(url_for('index'))

#pegar os dados da sessão do usuário autenticado
# @app.route('/perfil')
# @oidc.require_login
# def perfil():
#     user_info = oidc.user_getinfo(['sub', 'email', 'name'])
#     return jsonify(user_info)

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
#@login_required
def cria_usuario():
    logging.info(f"Chamou a rota cria_usuario")
    return render_template("formulario_ajax_simples.html")
    # return render_template("cria_usuario.html")

@app.route("/desativa_usuario")
#@login_required
def desativa_usuario():
    logging.info(f"Chamou a rota desativa_usuario")
    return render_template("desativa_usuario.html")

@app.route("/executa_desativa_usuario", methods=['POST'])
#@login_required
def executa_desativa_usuario():
    cpf_usuario = request.form['cpfUsuario']
    logging.info(f"Chamou a rota executa_desativa_usuario")
    logging.info(f"CPF do usuário: {cpf_usuario}")
    saida = modificaUsuario(cpf_usuario)
    return render_template("desativa_usuario.html", nome_usuario=saida)

@app.route("/executa_cria_usuario", methods=['POST'])
#@login_required
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

    idRegistro = inserir_usuario(json=dadosJson, acao='cadastrar_usuario')
    saida = lerResultado(idRegistro)
    if saida[0] == "Sucesso":
        #COLOCAR AQUI A FUNÇÃO DE ENVIO DE EMAIL
        saida = f"Usuário {nomeUsuarioCapitalizado} cadastrado com sucesso. Segue a senha: {saida[1]}"
    elif saida[0] == "Erro":
        saida = f"Ocorreu um erro ao cadastrar o usuário {nomeUsuarioCapitalizado}. Erro: {saida[1]}"
    else:
        logging.error(f"Erro na criação do usuário: {saida}")
        saida = f"Erro desconhecido. Entre em contato com a CGTI."


    # time.sleep(3)
    return str(saida)

@app.route("/consulta_nome", methods=['POST'])
def consulta_nome():
    cpfUsuario = request.form['cpfUsuario']
    saida = modificaUsuario(cpfUsuario)
    return saida



# ===== ROTAS ADICIONAIS PARA SAML =====

# @app.route("/login")
# def login():
#     """Página de login - redireciona para SAML"""
#     return render_template("login_saml.html")

# @app.route("/dashboard")
# @login_required
# def dashboard():
#     """Dashboard para usuários autenticados"""
#     user_data = saml_auth.get_user_data()
#     return render_template("dashboard_saml.html", user=user_data)

# @app.route("/profile")
# @login_required
# def profile():
#     """Perfil do usuário autenticado"""
#     user_data = saml_auth.get_user_data()
#     return render_template("profile_saml.html", user=user_data)

# @app.route("/test-saml")
# def test_saml():
#     """Página para testar configurações SAML"""
#     settings_info = saml_auth.check_saml_settings()
#     return render_template("test_saml.html", settings=settings_info)

# ===== EXEMPLO DE COMO PROTEGER ROTAS EXISTENTES =====
# 
# Para proteger uma rota existente, basta adicionar o decorator @login_required:
#
# @app.route("/cria_usuario")
# @login_required  # <- Adicione esta linha
# def cria_usuario():
#     logging.info(f"Chamou a rota cria_usuario")
#     return render_template("formulario_ajax_simples.html")
#
# @app.route("/desativa_usuario")
# @login_required  # <- Adicione esta linha
# def desativa_usuario():
#     logging.info(f"Chamou a rota desativa_usuario")
#     return render_template("desativa_usuario.html")

# ===== EXEMPLO DE PROTEÇÃO POR GRUPO =====
#
# Para proteger uma rota por grupo específico:
#
# @app.route("/admin")
# @saml_auth.require_group("Administradores")
# def admin():
#     return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

