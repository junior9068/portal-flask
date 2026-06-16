import csv
import json
import logging
from datetime import datetime
from pathlib import Path

# Configuração de Logs (Importante para o Crontab)
LOG_FILE = Path(__file__).parent / "converte_csv.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Caminho absoluto ambiente de teste/produção
# BASE_DIR_CAIXAS = Path("/home/edilson/projetos/portal-flask")

# Ccaminho para o ponto de montagem do NFS de produção
BASE_DIR_CAIXAS = Path("/mnt/nfs-portal")

def buscar_csv_mais_recente(diretorio: Path) -> Path:
    """Busca o arquivo mais recente que combine com o padrão estabelecido."""
    padrao = "Permissoes_Caixas_Email_Completo*.csv"
    arquivos = list(diretorio.glob(padrao))
    
    if not arquivos:
        return None
    
    # Ordena pela data de modificação (mtime) do mais recente para o mais antigo
    arquivos.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return arquivos[0]

def converte_csv_em_json():
    # Ambiente de teste
    # pasta_data = BASE_DIR_CAIXAS / "data"
    # Ambiente de produção
    pasta_data = BASE_DIR_CAIXAS
    
    # 1. Busca dinâmica utilizando o seu padrão com asterisco
    arquivo_csv = buscar_csv_mais_recente(pasta_data)
    
    if not arquivo_csv:
        logging.error(f"Nenhum arquivo CSV correspondente a 'Permissoes_Caixas_Email_Completo*.csv' foi encontrado em: {pasta_data}")
        return

    logging.info(f"Arquivo CSV selecionado: {arquivo_csv.name}")

    # 2. Nome do arquivo JSON de saída com a data atual
    data_atual = datetime.now().strftime("%Y-%m-%d")
    arquivo_json = pasta_data / f"permissoes_caixas_{data_atual}.json"

    usuarios = {}

    try:
        # --- SEU CÓDIGO ORIGINAL COMEÇA AQUI (Usando a variável arquivo_csv dinâmica) ---
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

        logging.info(f"Campos detectados: {reader.fieldnames}")

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

        # --- SEU CÓDIGO ORIGINAL TERMINA AQUI (Usando a variável arquivo_json dinâmica) ---

        with open(arquivo_json, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, ensure_ascii=False, indent=4)

        logging.info(f"JSON gerado com sucesso: {arquivo_json.name}")

    except Exception as e:
        logging.exception(f"Ocorreu um erro durante a conversão: {e}")

if __name__ == "__main__":
    converte_csv_em_json()