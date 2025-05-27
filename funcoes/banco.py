import mysql.connector

# Conectar ao banco
conexao = mysql.connector.connect(
    host="localhost",
    user="user_banco",           # usuário
    password="Usuariobanco@2025",  # senha do usuário
    database="portal"       # nome do banco
)

cursor = conexao.cursor()

# Inserir dados
nome = "Edilson"
cpf = "02982448530jkj"

sql = "INSERT INTO usuarios (nome, cpf) VALUES (%s, %s)"
valores = (nome, cpf)

cursor.execute(sql, valores)
conexao.commit()

print("Usuário cadastrado com sucesso!")

# Listar todos os usuários
cursor.execute("SELECT * FROM usuarios")
usuarios = cursor.fetchall()

print("Usuários cadastrados:")
for u in usuarios:
    print(u)

# Fechar conexão
cursor.close()
conexao.close()
