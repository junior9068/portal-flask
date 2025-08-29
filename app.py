from flask import Flask, request, jsonify, redirect, url_for, send_file
from flask_session import Session
from flask import render_template
from funcoes.log import configurar_logs
import logging, os
from funcoes.banco import inserir_usuario, deletar_usuario, lerResultado
from funcoes.funcoes import capitalizaNome, buscaDepartamento, exemplo_chamada_bash
from funcoes.ad import modificaUsuario, consultar_usuario, cria_usuario_ad, buscar_login, gerar_senha
import json, time
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_oidc import OpenIDConnect
import requests
from flask import Response, session

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
    'OIDC_SCOPES': ['openid', 'email', 'profile', 'User.Read'],
    'OIDC_ID_TOKEN_COOKIE_SECURE': False  # True em produção com HTTPS
})

oidc = OpenIDConnect(app)

# Resolve encaminhamento do pacote
#app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Configurar chave secreta para sessões (IMPORTANTE: mude para uma chave segura em produção)
app.config['SECRET_KEY'] = 'sua-chave-secreta-mude-em-producao'

@app.route("/")
def raiz():
    return redirect(url_for("home"))

# @app.route("/index")
# def index():
#     return render_template("index.html")

@app.route("/home")
@oidc.require_login
def home():
    #após implementar o OIDC
    user = oidc.user_getinfo(['email', 'name'])
    # Salva o access_token na sessão manualmente
    token = oidc.get_access_token()
    session['access_token'] = token
    nome = user.get('name')
    nomes = nome.split(" ")
    nomeLista = [nomes[0], nomes[1]]
    nomeExibicao = " ".join(nomeLista)
    logging.info(f"TESTE PARA PEGAR EMAIL DO USUÁRIO: {oidc.user_getinfo(['email']).get('email')}")
    # return jsonify(user)
    return render_template("home.html", nome=nomeExibicao)

# NÃO FUNCIONOU. TEMOS QUE CORRIGIR
@app.route('/logout')
def logout():
    session.clear()  # Limpa a sessão local

    # Impede o Flask-OIDC de redirecionar automaticamente
    oidc.logout(redirect_to=None)

    tenant_id = "0f45bbf5-e0b2-4611-869d-02cbccbc164c"
    post_logout_redirect_uri = url_for('index', _external=True)

    logout_url = (
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/logout"
        f"?post_logout_redirect_uri={post_logout_redirect_uri}"
    )

    return redirect(logout_url)


@app.route('/user/photo')
def user_photo():
    token = session.get('access_token')  # seu token armazenado na sessão
    if not token:
        return "Unauthorized", 401

    headers = {'Authorization': f'Bearer {token}'}
    graph_url = "https://graph.microsoft.com/v1.0/me/photo/$value"
    r = requests.get(graph_url, headers=headers)

    if r.status_code == 200:
        logging.info(f"Foto do usuário obtida com sucesso. {Response(r.content, content_type=r.headers['Content-Type'])}")
        return Response(r.content, content_type=r.headers['Content-Type'])
    else:
        logging.error(f"Erro ao obter foto do usuário: {r.status_code} - {r.text}")
        # Caminho da imagem padrão dentro da pasta static
        default_image_path = os.path.join(app.root_path, 'static', 'images', 'default_user.png')
        return send_file(default_image_path, mimetype='image/png')


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
@oidc.require_login
def cria_usuario():
    logging.info(f"Chamou a rota cria_usuario")
    return render_template("cria_usuario.html")
    # return render_template("cria_usuario.html")

@app.route("/desativa_usuario")
@oidc.require_login
def desativa_usuario():
    logging.info(f"Chamou a rota desativa_usuario")
    return render_template("desativa_usuario.html")

@app.route("/consulta_usuario")
@oidc.require_login
def consulta_usuario():
    logging.info(f"Chamou a rota consulta_usuario")
    return render_template("consulta_usuario.html")


@app.route("/executa_desativa_usuario", methods=['POST'])
@oidc.require_login
def executa_desativa_usuario():
    cpf_usuario = request.form['cpfUsuario']
    logging.info(f"Chamou a rota executa_desativa_usuario")
    logging.info(f"CPF do usuário: {cpf_usuario}")
    usuarioLogado = oidc.user_getinfo(['email'])
    saida = modificaUsuario(cpf_usuario, usuarioLogado)
    #return render_template("desativa_usuario.html", nome_usuario=saida)
    return saida

@app.route("/executa_cria_usuario", methods=['POST'])
@oidc.require_login
def executa_cria_usuario():
    saida = ""
    # Cria um dicionário para armazenar os dados do usuário
    nomeUsuario = request.form['nomeUsuario']
    nomeUsuarioCapitalizado = capitalizaNome(nomeUsuario)
    departamentoHtml = request.form['departamento']
    departamento, chefia = buscaDepartamento(departamentoHtml)
    usuarioLogado = oidc.user_getinfo(['email'])
    try:
        saida = cria_usuario_ad(
            nomeUsuarioCapitalizado,
            cpfUsuario = request.form['cpfUsuario'],
            dataNascimentoUsuario = request.form['dataNascimentoUsuario'],
            emailPessoal = request.form['emailPessoal'],
            telefoneComercial = request.form['telefoneComercial'],
            matriculaSiape = request.form['matriculaSiape'],
            empresa = request.form['empresa'],
            localizacao = request.form['localizacao'],
            cargo = request.form['cargo'],
            departamento = departamento,
            chefia = chefia,
            usuarioLogado = usuarioLogado
        )
    except Exception as e:
        logging.error(f"Erro ao criar usuário: {e}")
        saida = jsonify({"status": "Erro", "mensagem": str(e)})
    return saida

    # dicionarioUsuario = {'nome': nomeUsuarioCapitalizado, 'cpf': cpfUsuario, 'dataNascimento': dataNascimentoUsuario, 'email': emailPessoal, 'empresa': empresa, 'localizacao': localizacao, 'cargo': cargo,
    #                      'telefoneComercial': telefoneComercial, 'departamento': departamento, 'chefia': chefia, 'matriculaSiape': matriculaSiape,}
    # dadosJson = json.dumps(dicionarioUsuario)
    # logging.info(dicionarioUsuario)

    # idRegistro = inserir_usuario(json=dadosJson, acao='cadastrar_usuario')
    # saida = lerResultado(idRegistro)


    # if saida[0] == "Sucesso":
    #     #COLOCAR AQUI A FUNÇÃO DE ENVIO DE EMAIL
    #     saida = f"Usuário {nomeUsuarioCapitalizado} cadastrado com sucesso. Segue a senha: {saida[1]}"
    # elif saida[0] == "Erro":
    #     saida = f"Ocorreu um erro ao cadastrar o usuário {nomeUsuarioCapitalizado}. Erro: {saida[1]}"
    # else:
    #     logging.error(f"Erro na criação do usuário: {saida}")
    #     saida = f"Erro desconhecido. Entre em contato com a CGTI."


    # time.sleep(3)
    # return str(saida)

@app.route("/consulta_nome", methods=['POST'])
def consulta_dados_usuario():
    #user = oidc.user_getinfo(['email', 'name'])
    usuarioLogado = oidc.user_getinfo(['email'])
    #logging.info(f"Usuário autenticado: {user}")
    #Função utilizada nas páginas de consulta do usuário e desativação do usuário
    identificadorPesquisa = ""
    if 'identificador' in request.form:
        identificadorPesquisa = request.form['identificador']
    else:
        identificadorPesquisa = request.form['cpf']
    saida = consultar_usuario(identificadorPesquisa, usuarioLogado)
    if saida is None:
        return jsonify({
            "nome": "Não encontrado", 
            "email": "Não encontrado",
            "departamento": "Não encontrado",
            "cargo": "Não encontrado", 
            "empresa": "Não encontrado", 
            "data_de_nascimento": "Não encontrado",
            "siape": "Não encontrado",
            "chefia": "Não encontrado", 
            "cpf": "Não encontrado",
            "email_pessoal": "Não encontrado",
            "telefone_comercial": "Não encontrado"
            })
    else:
        return jsonify(saida)
    #saida = modificaUsuario(cpfUsuario)
    # return saida


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

