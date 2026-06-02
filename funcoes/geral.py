import subprocess
import logging
import smtplib
from email.message import EmailMessage
import os, requests, json
from io import BytesIO
import matplotlib.pyplot as plt
from flask import Response
from funcoes.banco import consulta_geral
from dateutil.relativedelta import relativedelta
from datetime import date
from pathlib import Path
import csv
import json


if os.getenv('FLASK_ENV') == 'desenvolvimento':
    usuarioEmail=os.getenv('USUARIO_EMAIL')
    senhaEmail=os.getenv('SENHA_EMAIL')
    servidor_smtp=os.getenv('SERVIDOR_SMTP')
    porta=int(os.getenv('PORTA_SMTP'))
else:
    servidor_smtp='smtp.cade.gov.br'
    porta=25

#Diretório do arquivo JSON para consulta de caixas de email
BASE_DIR_CAIXAS = Path(__file__).resolve().parent.parent  # volta para a raiz do projeto


def capitalizaNome(nome):
    """
    Função para capitalizar o nome do usuário.
    Exemplo: 'joão da silva' -> 'João Da Silva'
    """
    if not nome:
        return ''
    partes = nome.split(" ")
    nome_capitalizado = ' '.join(part.capitalize() for part in partes)
    return nome_capitalizado

# Função descontinuada, agora o front-end envia um dicionário com setor e nome do chefe.
# def buscaDepartamento(departamentoComChefia):
#     #Separa o departamento da chefia vindos do formulário.
#     departamentoComChefia = departamentoComChefia.split("-")
#     departamento = departamentoComChefia[0].strip()
#     chefia = departamentoComChefia[1].strip()
#     return departamento, chefia


def enviar_email_criacao(senha, destinatario, login, servidor_smtp=servidor_smtp, porta=porta):
    # Extrai nome do e-mail (antes do @) para exibição
    # login = destinatario.split('@')[0]
    nome = login.replace('.', ' ').title()  # ex: "edilson.junior" → "Edilson Junior"

    # Corpo HTML do e-mail
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; border: 1px solid #7AA230; padding: 20px;">
        <p>Prezado(a) <strong>{nome}</strong>,</p>
        <p>Bem vindo ao CADE! Seguem abaixo os seus dados de acesso à rede corporativa:</p>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
            <tr>
                <td><strong>Login</strong></td>
                <td>{login}</td>
            </tr>
            <tr>
                <td><strong>Senha</strong></td>
                <td>{senha}</td>
            </tr>
            <tr>
                <td><strong>E-mail</strong></td>
                <td>{login}@cade.gov.br</td>
            </tr>
        </table>
        <br>
        <p><strong>ATENÇÃO:</strong> sua caixa de e-mail poderá demorar até <strong>24 horas</strong> para ser disponibilizada.</p>
        <p>A alteração da senha deve ser realizada no primeiro login.</p>
        <p>Em caso de dúvidas, favor entrar em contato com a CGTI</p>
        <br>
        <p style="font-size: 12px;">
        CADE - Conselho Administrativo de Defesa Econômica<br>
        </p>
    </body>
    </html>
    """

    try:
        msg = EmailMessage()
        msg['Subject'] = "CADE - Criação de conta de acesso"
        msg['From'] = "naoresponda@cade.gov.br"
        msg['To'] = destinatario

        # Corpo alternativo (texto puro) + HTML
        msg.set_content(f"Prezado(a) {nome},\n\nSeu acesso à rede foi criado. Caso não visualize o conteúdo HTML, contate o suporte.")
        msg.add_alternative(html, subtype='html')

        # Envio
        with smtplib.SMTP(servidor_smtp, porta) as smtp:
            if os.getenv('FLASK_ENV') == 'desenvolvimento':
                smtp.starttls()
                smtp.login(usuarioEmail, senhaEmail)
            smtp.send_message(msg)
            return True

    except Exception as e:
        logging.error(f"Erro ao enviar e-mail: {e}")
        return False


def enviar_email_desativacao(destinatario, login, servidor_smtp=servidor_smtp, porta=porta):
    # Extrai nome do e-mail (antes do @) para exibição
    # login = destinatario.split('@')[0]
    nome = login.replace('.', ' ').title()  # ex: "edilson.junior" → "Edilson Junior"

    # Corpo HTML do e-mail
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; border: 1px solid #7AA230; padding: 20px;">
        <p>Prezado(a) <strong>{nome}</strong>,</p>
        <p>Informamos que sua conta de usuário da rede CADE foi desativada.</p>
        <p>Coordenação Geral de Tecnologia da Informação - CGTI</p>
        <br>
        <p style="font-size: 12px;">
        CADE - Conselho Administrativo de Defesa Econômica<br>
        </p>
    </body>
    </html>
    """

    try:
        msg = EmailMessage()
        msg['Subject'] = "CADE - Desativação de conta de acesso"
        msg['From'] = "naoresponda@cade.gov.br"
        msg['To'] = destinatario
        # Corpo alternativo (texto puro) + HTML
        msg.set_content(f"Prezado(a) {nome},\n\nSua conta foi desativada. Caso não visualize o conteúdo HTML, contate o suporte.")
        msg.add_alternative(html, subtype='html')

        # Envio
        with smtplib.SMTP(servidor_smtp, porta) as smtp:
            # descomentar a linha abaixo para ver detalhes do envio e validar se está direcionando corretamente para o BBC (cópia oculta)
            # smtp.set_debuglevel(1)
            if os.getenv('FLASK_ENV') == 'desenvolvimento':
                smtp.starttls()
                smtp.login(usuarioEmail, senhaEmail)
            smtp.send_message(msg)
            return True

    except Exception as e:
        logging.error(f"Erro ao enviar e-mail: {e}")
        return False
    

def enviar_email_desativacao_gestao(destinatario, login, servidor_smtp=servidor_smtp, porta=porta):
    # Extrai nome do e-mail (antes do @) para exibição
    # login = destinatario.split('@')[0]
    nome = login.replace('.', ' ').title()  # ex: "edilson.junior" → "Edilson Junior"

    # Corpo HTML do e-mail
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; border: 1px solid #7AA230; padding: 20px;">
        <p>Prezados(as),</p>
        <p>Informamos que a conta <strong>{login}</strong> foi desativada.</p>
        <p>Coordenação Geral de Tecnologia da Informação - CGTI</p>
        <br>
        <p style="font-size: 12px;">
        CADE - Conselho Administrativo de Defesa Econômica<br>
        </p>
    </body>
    </html>
    """

    try:
        msg = EmailMessage()
        msg['Subject'] = "CADE - Desativação de conta de acesso"
        msg['From'] = "naoresponda@cade.gov.br"
        msg['To'] = destinatario
        # # Cópia oculta (BCC) — direto na linha
        # msg['Bcc'] = "usuariosdesativados@cade.gov.br"
        # Corpo alternativo (texto puro) + HTML
        msg.set_content(f"Prezado(a) {nome},\n\nSua conta foi desativada. Caso não visualize o conteúdo HTML, contate o suporte.")
        msg.add_alternative(html, subtype='html')

        # Envio
        with smtplib.SMTP(servidor_smtp, porta) as smtp:
            # descomentar a linha abaixo para ver detalhes do envio e validar se está direcionando corretamente para o BBC (cópia oculta)
            # smtp.set_debuglevel(1)
            if os.getenv('FLASK_ENV') == 'desenvolvimento':
                smtp.starttls()
                smtp.login(usuarioEmail, senhaEmail)
            smtp.send_message(msg)
            return True

    except Exception as e:
        logging.error(f"Erro ao enviar e-mail: {e}")
        return False

def exemplo_chamada_bash():
    saida = ''
    try:
        comando = subprocess.run(["pwsh", "/home/edilson/projetos/portal-flask/teste.ps1"], capture_output=True, text=True)
        if comando.stderr:
            txt = ['Houve um erro. Entre em contato com a CGTI']
            saida = f"{txt}"
            logging.error(comando.stderr)
        else:
            saida = comando.stdout.splitlines()
    except Exception as e:
        txt_erro = ['Houve um erro na execução do comando. Entre em contato com a CGTI']
        saida = f"{txt_erro}"  # a variavel "e" irá para o log
        logging.error(e)
    return saida

def enviar_mensagem_teams(mensagem):
    webhook_url = "https://oncade.webhook.office.com/webhookb2/26f03ec9-ba58-48d0-bf15-714ea93cfafd@0f45bbf5-e0b2-4611-869d-02cbccbc164c/IncomingWebhook/c8612753ebb64840abbaee36d133d873/ef2ef433-cef6-480d-b4e4-f97cb7dcb37b/V2ve1ILeaGngHECO_BYlk3NYIu8byR5RPQHyP16BezbPc1"
    message_content = mensagem

    headers = {"Content-Type": "application/json"}
    payload = {"text": message_content}

    try:
        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for bad status codes
        logging.info("Mensagem enviada com sucesso para o Teams.")
    except requests.exceptions.RequestException as e:
            logging.error("Erro ao enviar mensagem para o Teams: {e}")


# Estrutura simples com chave e valor em JSON
def chefes_departamento_1(json_data):
    try:
        lista_chefes = []
        #Chave é o departamento e valor é o chefe do departamento
        for chave, valor in json_data.items():
            lista_chefes.append(f"{chave} - {valor}")
        return lista_chefes
    except Exception as e:
        logging.error(f"Erro ao extrair chefes de departamento: {e}")
        return "Erro ao buscar chefes de departamento."


#Estrutura de uma lista de dicionários em JSON
def chefes_departamento_2(json_data):
    try:
        lista_chefes = []
        for item in json_data:
            lista_chefes.append(f"{item.get('departamento')} - {item.get('chefe_departamento')}")
        return lista_chefes
    except Exception as e:
        logging.error(f"Erro ao extrair chefes de departamento: {e}")
        return "Erro ao buscar chefes de departamento."

# Função para gerar os últimos 12 meses no formato "MM/AA"
def ultimos_12_meses():
    try:
        meses = []
        data = date.today()

        for i in range(12):
            mes_formatado = data.strftime("%m/%y")  # Ex: "11/25"
            meses.append(mes_formatado)
            data -= relativedelta(months=1)

        return list(reversed(meses))  # do mais antigo para o mais novo
    except Exception as e:
        logging.error(f"Erro ao gerar últimos 12 meses: {e}")
        return []


def mostra_grafico(acao):
    try:
        meses=ultimos_12_meses() # Gera os últimos 12 meses no formato "MM/AA". Ex: ['01/25', '02/25', '03/25', ... , '1225']

        # categorias = ['01/25', '02/25', '03/25', '04/25', '05/25', '06/25', '07/25', '08/25', '09/25', '10/25', '11/25']
        # valores = [9, 14, 10, 7, 6, 5, 4, 15, consulta_geral(9, 2025, acao), consulta_geral(10, 2025, acao), consulta_geral(11, 2025, acao)]
        categorias = meses
        valores = [] # o loop abaixo irá preencher essa lista. EX: [consulta_geral(01, 2025, acao), ... , consulta_geral(12, 2025, acao)]
        for mes_ano in categorias:
            mes, ano = mes_ano.split('/')   # separa "11/25"
            ano = int("20" + ano)           # transforma "25" em 2025
            mes = int(mes)
            valores.append(consulta_geral(mes, ano, acao))
        logging.info(f"Valores para o gráfico de {acao}: {valores}")
        # 3. Gera o gráfico
        # fig, ax = plt.subplots()
        fig, ax = plt.subplots(figsize=(16, 7))
        barras = ax.bar(categorias, valores, color=["#0A7DC9"])

        # Adiciona os valores no topo de cada barra
        for barra in barras:
            altura = barra.get_height()
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                altura,
                str(altura),
                ha='center',
                va='bottom',
                fontsize=10
            )
        # Altera o título do gráfico conforme a ação
        if acao == 'criar_usuario':
            frase = 'Criação de usuários nos últimos 12 meses'
        elif acao == 'desativar_usuario':
            frase = 'Desativação de usuários nos últimos 12 meses'
        elif acao == 'ativar_usuario':
            frase = 'Ativação de usuários nos últimos 12 meses'
        plt.xlabel('Mês/Ano')
        plt.ylabel('Quantidade de usuários')
        plt.title(frase)

        # 4. Cria um "arquivo" na memória
        img = BytesIO()

        # 5. Salva o gráfico DENTRO desse "arquivo"
        fig.savefig(img, format='png', bbox_inches='tight')

        # 6. Fecha o gráfico no Matplotlib para não vazar memória
        plt.close(fig)

        # 7. Volta ponteiro para o início
        img.seek(0)

        # 8. Retorna os bytes como imagem PNG
        return Response(img.getvalue() , mimetype='image/png')
    except Exception as e:
        logging.error(f"Erro ao gerar gráfico: {e}")
        return None

# Busca caixas de e-mail associadas a um usuário consultando o arquivo JSON por_usuario_grupo.json
def busca_caixa_email(usuario):
    try:
        usuario = usuario.split('@')[0]  # Remove o domínio do e-mail, se presente. Ex: "
        caminho_arquivo = BASE_DIR_CAIXAS / "data" / "permissoes_caixas.json"
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
        dicionario = {}
        lista_de_caixas = []
        if usuario in dados.keys():
            for caixa in dados.get(usuario).get("caixas").items():
                print(caixa)
                dicionario_caixa = {}
                dicionario_caixa["email"] = caixa[0] # caixa[0] é a caixa de email, ex: cgti@cade.gov.br"
                dicionario_caixa["nome"] = caixa[1].get("caixa") # caixa[1].get("caixa") é o nome da caixa, ex: "Caixa CGTI"
                dicionario_caixa["permissoes"] = caixa[1].get("permissoes") # caixa[1].get("permissoes") é a lista de permissões, ex: ["Leitura", "Full Access"]
                # print(caixa[0]) # caixa[0] é a caixa de email, ex: cgti@cade.gov.br"
                # print(caixa[1].get("caixa")) # caixa[1].get("caixa") é o nome da caixa, ex: "Caixa CGTI"
                # print(caixa[1].get("permissoes")) # caixa[1].get("permissoes") é a lista de permissões, ex: ["Leitura", "Full Access"]
                lista_de_caixas.append(dicionario_caixa)
            # Para debugar a estrutura do dicionário que estamos montando, podemos imprimir a variável "dicionario" aqui antes 
            # de convertê-la para JSON. A ideia é que a estrutura final seja algo como:
            # temp = {
            # "caixas": [
            #     {
            #     "nome": "Caixa Financeiro",
            #     "email": "financeiro@empresa.gov.br",
            #     "permissao": "Leitura"
            #     },
            #     {
            #     "nome": "Caixa RH",
            #     "email": "rh@empresa.gov.br",
            #     "permissao": "Full Access"
            #     }
            # ]
            # }
            dicionario["caixas"] = lista_de_caixas
            # dicionario1 = {"caixas": ["Caixa1", "Caixa2", "Caixa3"]} # Exemplo de dicionário para teste
            # print(dicionario)
            #TENHO QUE TRATAR O CASO DE TER UM "-" QUANDO NÃO TEM NENHUMA CAIXA ATRIBUIDA AU USUARIO MESMO ELE ESTANDO NO JSON, POIS O CSV ORIGINAL VEM COM UM "-" NESSA SITUAÇÃO. ENTÃO O SISTEMA DEVE RETORNAR UMA MENSAGEM DE "Usuário encontrado, mas sem caixas de e-mail atribuídas." OU ALGO DO TIPO, PARA O FRONT-END EXIBIR ESSA INFORMAÇÃO PARA O USUÁRIO FINAL.
            return json.dumps(dicionario) # Retorna o dicionário convertido em JSON para o front-end
            # return f"Usuário {usuario} tem permissão na(s) seguinte(s) caixa(s) de e-mail: {(dados.get(usuario).get('mailboxes'))}"
        else:
            #deve retornar um JSON para o front-end (onde o valor da chave deve ser uma lista), mesmo que o usuário não seja encontrado, para evitar erros de parsing no JavaScript
            return json.dumps({"caixas": ["Usuário não encontrado ou caixas de e-mail não atribuídas."]})
            #return "Usuário não encontrado."
    except Exception as erro:
        logging.error(f"Erro ao buscar caixa de e-mail: {erro}")
        return f"Erro ao buscar caixa de e-mail: {erro}"


def busca_compartilhamentos(grupos):
    grupos = ["G_CECADE"] # aqui deve ser a variável que vem da função busca_grupos(), ex: "G_2022_ICN_Merger_Workshop"
    try:
        caminho_arquivo = BASE_DIR_CAIXAS / "data" / "Relatorio_Grupos_Permissoes_DFS.json"
        with open(caminho_arquivo, 'r', encoding='utf-8-sig') as arquivo:
            dados = json.load(arquivo)
        compartilhamento = []
        for item in dados:
            if item.get("Grupo") in grupos:
                compartilhamento.append({
                    "compartilhamento": item.get("Pasta"),
                    "grupo": item.get("Grupo"),
                    "permissao": item.get("Permissao")
                })
        if compartilhamento:
            return {"compartilhamentos": compartilhamento}
        else:
            logging.warning(f"Nenhum compartilhamento encontrado para os grupos: {grupos}")
            return {"compartilhamentos": [{"compartilhamento": "Nao encontrado", "grupo": "Não encontrado", "permissao": "Não encontrado"}]}
    except Exception as erro:
        logging.error(f"Erro ao buscar compartilhamento: {erro}")
        return {"compartilhamentos": [{"compartilhamento": "Erro", "grupo": "Erro", "permissao": "Erro"}]}


#CONTINUAR: DEVEMOS CRIAR UMA FUNÇÃO PARA GERAR O ARQUIVO JSON A PARTIR DO CSV, POIS O ARQUIVO CSV FORNECIDO PELA CGTI ESTÁ COM ASPAS DUPLICADAS E QUEBRADO, O QUE CAUSA ERROS DE PARSING. 
# ESSA FUNÇÃO DEVE SER RODADA APENAS 1 VEZ PARA GERAR O JSON LIMPO, E DEPOIS O SISTEMA DEVE CONSULTAR APENAS O JSON GERADO.
def converte_csv_em_json():

    arquivo_csv = BASE_DIR_CAIXAS / "data" / "Permissoes_Caixas_Email_Completo(in).csv"
    arquivo_json = BASE_DIR_CAIXAS / "data" / "permissoes_caixas.json"

    usuarios = {}

    with open(arquivo_csv, "r", encoding="utf-8-sig") as f:

        conteudo = f.read()

    # Corrige export quebrado
    conteudo = conteudo.replace('""', '"')

    # Remove aspas do começo/fim do arquivo
    if conteudo.startswith('"'):
        conteudo = conteudo[1:]

    if conteudo.endswith('"'):
        conteudo = conteudo[:-1]

    linhas = conteudo.splitlines()

    # remove aspas extras linha a linha
    linhas_corrigidas = []

    for linha in linhas:

        linha = linha.strip()

        if linha.startswith('"'):
            linha = linha[1:]

        if linha.endswith('"'):
            linha = linha[:-1]

        linhas_corrigidas.append(linha)

    reader = csv.DictReader(linhas_corrigidas, delimiter=",")

    print(reader.fieldnames)

    for row in reader:

        row = {k.strip(): v.strip() for k, v in row.items()}

        login = row["Login"]

        if login not in usuarios:
            usuarios[login] = {
                "nome": row["NomeUsuario"],
                "email": row["EmailUsuario"],
                "caixas": {}
            }

        email_caixa = row["EmailDaCaixa"]

        if email_caixa not in usuarios[login]["caixas"]:
            usuarios[login]["caixas"][email_caixa] = {
                "caixa": row["CaixaComAcesso"],
                "permissoes": []
            }

        permissao = row["Permissao"]

        if permissao not in usuarios[login]["caixas"][email_caixa]["permissoes"]:
            usuarios[login]["caixas"][email_caixa]["permissoes"].append(permissao)

    with open(arquivo_json, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=4)

    print(f"JSON gerado: {arquivo_json}")



if __name__ == "__main__":
    print(busca_compartilhamentos())
    # print(busca_caixa_email("ediran.almeida"))


    # print(enviar_email("Senha@123456", "thiago.nogueiira@gmail.com"))
    # json_data = [
    #     {"departamento": "Recursos Humanos", "chefe_departamento": "Ana Silva"},
    #     {"departamento": "Tecnologia da Informação", "chefe_departamento": "Bruno Souza"},
    #     {"departamento": "Financeiro", "chefe_departamento": "Carlos Lima"},
    #     {"departamento": "Marketing", "chefe_departamento": "Ana Silva"},
    # ]
    # json_data = {
    #     "Recursos Humanos": "Ana Silva",
    #     "Tecnologia da Informação": "Bruno Souza",
    #     "Financeiro": "Carlos Lima",
    #     "Marketing": "Ana Silva"
    # }
    # print(chefes_departamento_1(json_data))
    # mostra_grafico('criar_usuario')