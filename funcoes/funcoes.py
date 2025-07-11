import subprocess
import logging


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
    dep, chefia = departamento("GAB 4-Victor Oliveira Fernandes")
    print(dep)
    print(chefia)