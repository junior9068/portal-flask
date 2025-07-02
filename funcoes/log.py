import logging

def teste1():
# Configuração para os Logs da aplicação
    return logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            # logging.FileHandler("app.log"),  # salva em arquivo
            logging.StreamHandler()         # mostra no terminal
        ]
    )