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
    #IMPORTANTE: RESOLVI ESSA QUESTÃO APENAS NO SELECT DO HTML. TENHO QUE APAGAR O CÓDIGO EXCEDENTE CASO NÃO SEJA UTILIZADO
    dicionarioDepartamentos = {
        "ASCOM": "Ana Paula Lopes Guedes Teixeira",
        "ASINT": "Bruna Pamplona de Queiroz",
        "ASTEC": "Ricardo Medeiros de Castro",
        "AUDIT": "Márcia da Rosa Pereira",
        "CCJ": "Bruna Maria Palhano Medeiros",
        "CEACO": "Tomas de Siervi Barcellos",
        "CECAN": "Fernando Daniel Franke",
        "CEMAC": "Gerson Carvalho Bênia",
        "CEP": "Antônio Marcos Guerreiro Salmeirão",
        "CGAA 1": "Alden Caribé de Sousa",
        "CGAA 10": "Emmanuel Ali Novaes Faria",
        "CGAA 11": "Yedda Beatriz Gomes de Almeida Dysman da Cruz Seixas",
        "CGAA 2": "Letícia Ribeiro Versiani",
        "CGAA 3": "Juliana  Marcelino da Silva",
        "CGAA 4": "Igor Carvalho Rocha",
        "CGAA 5": "Rodrigo Monteiro Ferreira",
        "CGAA 6": "Leonardo Sodre de Aragão Vasconcelos Peixoto",
        "CGAA 7": "Andrea Lucia Freire do Nascimento",
        "CGAA 8": "Carolina Saito da Costa",
        "CGAA 9": "Rubem Accioly Pires",
        "CGESP": "Karine Lustosa Panerai",
        "CGOFL": "Sarah Gamaliel Alves Silva",
        "CGP": "Victor Kaled Sousa do Espirito Santo",
        "CGTI": "Vinicius Eloy dos Reis",
        "COL": "Antônio Clóvis Melhor Galvão dos Santos",
        "COA 1": "Danielle Kineipp de Souza",
        "COA 10": "Joice Arantes Luciano",
        "COA 11": "Marcus Vinicius Silveira de Sá",
        "COA 2": "Marcelo Pacheco Bastos",
        "COA 3": "Beatriz Pierri",
        "COA 4": "Márcio Magalhães Teixeira",
        "COA 5": "Amanda Bispo Menezes",
        "COA 6": "Leandro dos Reis Lucheses",
        "COA 7": "Victor Lubambo Peixoto Accioly",
        "COA 8": "Leila Cristina Ferraresi Girardi",
        "COA 9-I": "Luís Cláudio Lima Pinheiro",
        "COA 9-II": "Guilherme D'Alessandro Silva",
        "CORREG": "Roxeli Lalla Rosa",
        "DAP": "Bruna Cardoso dos Santos",
        "DEE": "Lílian Santos Marques Severino",
        "DIAP": "Jeruza Huckembeck Pardo",
        "DICOR": "Beatriz Leal dos Reis",
        "DIPLAN": "André Botelho Vilaron",
        "GAB 1": "Bruno Polonio Renzetti",
        "GAB 2": "Diogo Thomson de Andrade",
        "GAB 2b": "Paulo Henrique de Oliveira",
        "GAB 3": "Gustavo Augusto Freitas de Lima",
        "GAB 3a": "Bertrand Wanderer",
        "GAB 4": "Victor Oliveira Fernandes",
        "GAB 4a": "Fabiana Pereira Veloso",
        "GAB 5": "Camila Cabral Pires Alves",
        "GAB 5a": "Vitor Jardim Machado Barbosa",
        "GAB 6": "José Levi Mello do Amaral Júnior",
        "GAB 6a": "Ludmila dos Santos Boldo Maluf",
        "GAB-PRES": "Maria Luiza Bittar Khouri",
        "GAB-SG": "Rebeca de Queiroga Falcao",
        "GAB1b": "Carlos Jacques Vieira Gomes",
        "PFE": "André Luís Macagnan Freire",
        "PRESIDÊNCIA": "Alexandre Cordeiro Macedo",
        "PROT": "Juliana Oliveira Marques Moraes",
        "SAGEP": "Gabrielle Drago Thorpe",
        "SAGPRO": "Marilucy Silva Lima",
        "SEACA": "Ana Luiza Maria Guimarães Coelho",
        "SEAAP": "Thayane da Conceição Oliveira Silva",
        "SEAPE": "Taynara Alessandra Dantas da Silva",
        "SEAPRO": "Tauana Almeida Siqueira",
        "SEAUD": "Bruna Casarotto Lima Sucha",
        "SECOM": "Carmen Lia Remedi Fros",
        "SECOP": "Otávio Augusto de Oliveira Cruz Filho",
        "SEDADOS": "Ana Paula Pessoa Mello",
        "SEEAC": "Nicole Chama dos Santos",
        "SEGOV": "Alessandro Lustosa Seixas Pinheiro",
        "SEMAP": "Liliane Pereira Castro",
        "SERCJ": "Humberto Cunha dos Santos",
        "SEREP": "Fabio Henrique Sgueri",
        "SESIC": "Thiago Lazaro de Souza Nogueira",
        "SESIN": "Thiago Nogueira de Oliveira",
        "SESIS": "Felipe Alberto Moreira Dias",
        "SETED": "Silvia Regina Borges",
        "SG": "Gabriel Mamede de Carvalho",
        "SGA 1": "Felipe Neiva Mundim",
        "SGA 2": "Felipe Leitão Valadares Roquete",
        "SIDOC": "Camila Dias dos Santos",
        "VIGILANTE": "Marcos Alexandre Ribeiro Azevedo de Souza"
    }
    #Separa o departamento da chefia vindos do formulário. Utilizaremos a chefia para capturar o departamento correto.
    #A motivação é a seguinte: no formulário HTML existem um departamento com dois chefes diferentes (setor dividido que tem o mesmo nome). O Back-end do Marcello tem nomes diferentes para estes departamentos divididos:
    # EX: GAB 3 e GAB 3a. Temos que escrever no banco o departamento correto, conforme o dicionario acima. 
    departamentoComChefia = departamentoComChefia.split("-")
    departamento = departamentoComChefia[0].strip()
    chefia = departamentoComChefia[1].strip()
    # Cria variáveis que serão enviadas para o banco
    # departamentoBanco = ''
    # chefiaBanco = ''
    #Varre o dicionario procurando pelo nome da chefia
    # for chave, valor in dicionarioDepartamentos.items():
    #     if valor == chefia:
    #         departamentoBanco = chave
    #         chefiaBanco = valor
    # return departamentoBanco, chefiaBanco
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