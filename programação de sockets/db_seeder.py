import sqlite3

def seed_database():
    # Conecte-se ao banco de dados (ele será criado se não existir)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Crie uma tabela para armazenar informações de usuário (ela será criada se não existir)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Inserir dados de amostra (usuários e senhas)
    sample_users = [
        ("usuario1", "b'$2b$12$yHSjlfiSI8JCzYCRDwWMsud4IepNRFsAFb89SoDLA28.VJCFJVooi'"),
        ("usuario2", "b'$2b$12$1X93n8ig8vCgVtvi2ps16ugawTn3DBXupRSjkeY1ND2C22luxPa6a'"),
        ("usuario3", "b'$2b$12$fXE6xiUT8JVpMXxyZDoCleUgLRJ2EuJKX0qS8.YRZwZXiwOfnDNVy'"),
        # Adicione mais usuários conforme necessário
    ]

    for user_data in sample_users:
        username, password = user_data
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

    conn.commit()
    conn.close()

# Chame a função para popular o banco de dados com dados de amostra e criar a tabela
seed_database()
