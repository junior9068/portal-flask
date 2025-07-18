# #Para rodar com o Gunicorn

# import logging
# import sys

# def configurar_logs():
#     gunicorn_logger = logging.getLogger('gunicorn.error')
#     root_logger = logging.getLogger()

#     if gunicorn_logger.handlers:
#         # Se estiver rodando com Gunicorn, herda os handlers
#         root_logger.handlers = gunicorn_logger.handlers
#         root_logger.setLevel(gunicorn_logger.level)
#     else:
#         # Executando localmente (flask run, python app.py, etc.)
#         logging.basicConfig(
#             level=logging.INFO,
#             format='%(asctime)s [%(levelname)s] %(message)s',
#             handlers=[
#                 logging.StreamHandler(sys.stdout)
#             ]
#         )

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