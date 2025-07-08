# Criar nova taleba no banco:

```
CRIAR OS ARQUIVOS DE LOG 
trabalhar no select do banco com tela assincrona
VALIDAR FORMULÁRIO DE CRIAÇÃO DE USUÁRIO (resta apenas limitar a matricula)

TO DO:
 
1 - Preparar front-end para receber os dados da resposta da criação / desativação do usuário

2 - Praparar o front-end com o nome dos departamentos juntamente com o nome da chefia. EX: CGTI - Vinicius Eloy dos Reis;
 
3 - Enviar para o back-end o departamento e chefia separadamente;
Criar função com o dicionario com os departamentos e chefes;
Pegar o que vem do formulário dar um split pelo "-" e varrer o dicionario pelo nome do chefe;
Adicionar as informações no dicionario que vai para o banco.
Falar para o Marcelo que vaou devolver os dados pra ele do jeito que está e ele trata no backend

    "PRES": "Alexandre Cordeiro Macedo",
    "PRESIDÊNCIA": "Alexandre Cordeiro Macedo",
    "DAP": "Bruna Cardoso dos Santos",
    "CGESP": "Karine Lustosa Panerai",
    "SAGEP": "Gabrielle Drago Torpe",
    "SEAPE": "Taynara Alessandra Dantas da Silva",
    "SETED": "Silvia Regina Borges",
    "CGTI": "Vinicius Eloy dos Reis",
    "SESIN": "Thiago Nogueira de Oliveira",
    "CGAA 1": "Alden Caribé de Sousa",
    "SEGOV": "Alessandro Lustosa Seixas Pinheiro",
    "SG": "Gabriel Mamede de Carvalho",
    "COA 5": "Amanda Bispo Menezes",
    "GAB 1": "Bruno Polonio Renzetti",
    "GAB 1a": "Bruno Polonio Renzetti",
    "GAB 2": "Diogo Thomson de Andrade",
    "GAB 2b": "Paulo Henrique de Oliveira",
    "GAB 3a": "Bertrand Wanderer",
    "GAB 3": "Gustavo Augusto Freitas de Lima",
    "GAB 4": "Victor Oliveira Fernandes",
    "GAB 4a": "Fabiana Pereira Veloso",
    "GAB 4b": "Victor Oliveira Fernandes",
    "GAB 5": "Camila Cabral Pires Alves",
    "GAB 5a": "Vitor Jardim Machado Barbosa",
    "GAB 6": "José Levi Mello do Amaral Júnior",
    "GAB 6a": "Ludmila dos Santos Boldo Maluf",
    "SEACA": "Ana Luiza Maria Guimarães Coelho",
    "ASCOM": "Ana Paula Lopes Guedes Teixeira",
    "SEDADOS": "Ana Paula Pessoa Mello",
    "DIPLAN": "André Botelho Vilaron",
    "PFE": "André Luís Macagnan Freire",
    "CGAA 7": "Andrea Lucia Freire do Nascimento",
    "COL": "Antônio Clóvis Melhor Galvão dos Santos",
    "DICOR": "Beatriz Leal dos Reis",
    "COA 3": "Beatriz Pierri",
    "SEAUD": "Bruna Casarotto Lima Sucha",
    "CCJ": "Bruna Maria Palhano Medeiros",
    "ASINT": "Bruna Pamplona de Queiroz",
    "SIDOC": "Camila Dias dos Santos",
    "GAB1b": "Carlos Jacques Vieira Gomes",
    "SECOM": "Carmen Lia Remedi Fros",
    "CGAA 11": "Yedda Beatriz Gomes de Almeida Dysman da Cruz Seixas",
    "CGAA 8": "Carolina Saito da Costa",
    "COA 1": "Danielle Kineipp de Souza",
    "CGAA 3": "Juliana  Marcelino da Silva",
    "CGAA 10": "Emmanuel Ali Novaes Faria",
    "COF": "Fabiana Frigo Souza",
    "SEREP": "Fabio Henrique Sgueri",
    "SESIS": "Felipe Alberto Moreira Dias",
    "SGA 2": "Felipe Leitão Valadares Roquete",
    "SGA 1": "Felipe Neiva Mundim",
    "CECAN": "Fernando Daniel Franke",
    "SEMMA": "Gabriel Oliveira de Alarcão",
    "SAGEP": "Gabrielle Drago Thorpe",
    "CEMAC": "Gerson Carvalho Bênia",
    "COA 9-II": "Guilherme D'Alessandro Silva",
    "SERCJ": "Humberto Cunha dos Santos",
    "CGAA 4": "Igor Carvalho Rocha",
    "DIAP": "Jeruza Huckembeck Pardo",
    "COA 10": "Joice Arantes Luciano",
    "PROT": "Juliana Oliveira Marques Moraes",
    "CGESP": "Karine Lustosa Panerai",
    "CGP": "Victor Kaled Sousa do Espirito Santo",
    "COA 6": "Leandro dos Reis Lucheses",
    "COA 8": "Leila Cristina Ferraresi Girardi",
    "CGAA 2": "Letícia Ribeiro Versiani",
    "DEE": "Lílian Santos Marques Severino",
    "SEMAP": "Liliane Pereira Castro",
    "COA 9-I": "Luís Cláudio Lima Pinheiro",
    "COA 2": "Marcelo Pacheco Bastos",
    "AUDIT": "Márcia da Rosa Pereira",
    "COA 4": "Márcio Magalhães Teixeira",
    "COA 11": "Marcus Vinicius Silveira de Sá",
    "GAB-PRES": "Maria Luiza Bittar Khouri",
    "SAGPRO": "Marilucy Silva Lima",
    "SEEAC": "Nicole Chama dos Santos",
    "SECOP": "Otávio Augusto de Oliveira Cruz Filho",
    "CGAA 6": "Leonardo Sodre de Aragão Vasconcelos Peixoto",
    "GAB-SG": "Rebeca de Queiroga Falcao",
    "ASTEC": "Ricardo Medeiros de Castro",
    "CGAA 5": "Rodrigo Monteiro Ferreira",
    "CORREG": "Roxeli Lalla Rosa",
    "CGAA 9": "Rubem Accioly Pires",
    "CGOFL": "Sarah Gamaliel Alves Silva",
    "SETED": "Silvia Regina Borges",
    "SEAPRO": "Tauana Almeida Siqueira",
    "SEAPE": "Taynara Alessandra Dantas da Silva",
    "SEAAP": "Thayane da Conceição Oliveira Silva",
    "SESIC": "Thiago Lazaro de Souza Nogueira",
    "CEACO": "Tomas de Siervi Barcellos",
    "COA 7": "Victor Lubambo Peixoto Accioly"
    "CEP": "Antônio Marcos Guerreiro Salmeirão"
    "VIGILANTE": "Marcos Alexandre Ribeiro Azevedo de Souza"

```