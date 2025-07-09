import logging
import sys

def configurar_logs():
    logging.basicConfig(
        level=logging.INFO,  # Ou DEBUG, se quiser mais detalhes
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)  # Todos os logs vão para stdout
        ]
    )