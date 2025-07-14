import subprocess
import logging
import smtplib
from email.message import EmailMessage


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


def enviar_email(senha, destinatario, assunto, remetente, servidor_smtp='smtp.cade.gov.br', porta=25):
    corpo = f"Prezado(a) {destinatario},\n\nSegue sua senha {senha}\n\nEste é um e-mail de teste.\n\nAtenciosamente,\nEquipe CGTI"
    try:
        # Cria a mensagem
        msg = EmailMessage()
        msg['Subject'] = assunto
        msg['From'] = remetente
        msg['To'] = destinatario
        msg.set_content(corpo)

        # Conexão com o SMTP (sem login)
        with smtplib.SMTP(servidor_smtp, porta) as smtp:
            smtp.send_message(msg)
            logging.info(f"E-mail enviado para {destinatario}")
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
    print(enviar_email("Essa_é_sua_senha@123456", "edilson.cade@cade.gov.br", "Teste de Envio de E-mail", "naoresponda@cade.gov.br"))