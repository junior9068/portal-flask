import subprocess
import logging

logger = logging.getLogger('flask.app')

def exemplo_chamada_bash():
    saida = ''
    try:
        a = aff
        comando = subprocess.run(["pwsh", "/home/edilson/projetos/portal-flask/teste.ps1"], capture_output=True, text=True)
        if comando.stderr:
            txt = ['Houve um erro. Entre em contato com a CGTI']
            saida = f"{txt}"
            logger.error(comando.stderr)
        else:
            saida = comando.stdout.splitlines()
    except Exception as e:
        txt_erro = ['Houve um erro na execução do comando. Entre em contato com a CGTI']
        saida = f"{txt_erro}"  # a variavel "e" irá para o log
        logger.error(e)
    return saida

if __name__ == "__main__":
    print(exemplo_chamada_bash())