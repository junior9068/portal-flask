from flask import Flask, request, render_template
import os
import logging



app = Flask(__name__)  # Inicializa a aplicação


# Tela inicial
@app.route("/")  # Cria uma rota
def index():
    return render_template("index.html")

logging.basicConfig(level=logging.DEBUG)  # Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
