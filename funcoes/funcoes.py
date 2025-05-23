import subprocess

def exemplo_chamada_bash():
    saida = ''
    try:
        comando = subprocess.run(["pwsh", "/home/edilson/projetos/portal-flask/teste.ps1"], capture_output=True, text=True)
        if comando.stderr:
            txt = ['Houve um erro. Entre em contato com a CGTI']
            saida = f"{txt} \n {comando.stderr}" # a variavel comando.stderr irá para o log
        else:
            saida = comando.stdout.splitlines()
    except Exception as e:
        txt_erro = ['Houve um erro na execução do comando. Entre em contato com a CGTI']
        saida = f"{txt_erro} \n {e}"  # a variavel "e" irá para o log
    return saida

if __name__ == "__main__":
    print(exemplo_chamada_bash())