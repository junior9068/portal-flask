import subprocess
import logging
import smtplib
from email.message import EmailMessage
import os

if os.getenv('FLASK_ENV') == 'desenvolvimento':
    usuarioEmail=os.getenv('USUARIO_EMAIL')
    senhaEmail=os.getenv('SENHA_EMAIL')
    servidor_smtp=os.getenv('SERVIDOR_SMTP')
    porta=int(os.getenv('PORTA_SMTP'))
else:
    servidor_smtp='smtp.cade.gov.br'
    porta=25


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


def buscaDepartamento(departamentoComChefia):
    #Separa o departamento da chefia vindos do formulário.
    departamentoComChefia = departamentoComChefia.split("-")
    departamento = departamentoComChefia[0].strip()
    chefia = departamentoComChefia[1].strip()
    return departamento, chefia


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

if __name__ == "__main__":
    # print(enviar_email("Senha@123456", "thiago.nogueiira@gmail.com"))
    enviar_email_desativacao("edilsonjuniorti@gmail.com", "edilson.junior")