# Usar imagem oficial do Python
FROM python:3.10-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema (se precisar de psycopg2, ldap, etc, pode acrescentar aqui)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar os arquivos do projeto
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código
COPY . .

# Variável de ambiente para evitar buffering nos logs
ENV PYTHONUNBUFFERED=1

# Porta exposta (Gunicorn vai rodar aqui dentro do container)
EXPOSE 5050

# Comando para iniciar o Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "app:app"]