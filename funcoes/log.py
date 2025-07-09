import logging
import sys

# Criação de configuração de logs
# Configura o nível de log, formato e onde os logs serão enviados
# Basta chamar a função configurar_logs() no início do app.py. Se for preciso, pode-se usar este log em outros arquivos também. Basta importar a função logging.
def configurar_logs():
    logging.basicConfig(
        level=logging.INFO,  # Ou DEBUG, se quiser mais detalhes
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)  # Todos os logs vão para stdout
        ]
    )