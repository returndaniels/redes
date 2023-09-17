import sqlite3


def seed_database():
    # Conecte-se ao banco de dados (ele será criado se não existir)
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Crie uma tabela para armazenar informações de usuário (ela será criada se não existir)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """
    )

    # Inserir dados de amostra (usuários e senhas)
    sample_users = [
        {
            "username": "usuario1",
            "password": b"$2b$12$eiBKBr0097HxRun4Env1eO93Kb/U/pRR7N0Ygk6eRUv/P4iFoOUMa",
            "salt": b"$2b$12$eiBKBr0097HxRun4Env1eO",
        },
        {
            "username": "usuario2",
            "password": b"$2b$12$eiBKBr0097HxRun4Env1eO93Kb/U/pRR7N0Ygk6eRUv/P4iFoOUMa",
            "salt": b"$2b$12$eiBKBr0097HxRun4Env1eO",
        },
        {
            "username": "usuario3",
            "password": b"$2b$12$eiBKBr0097HxRun4Env1eO93Kb/U/pRR7N0Ygk6eRUv/P4iFoOUMa",
            "salt": b"$2b$12$eiBKBr0097HxRun4Env1eO",
        },
    ]

    for user_data in sample_users:
        cursor.execute(
            "INSERT INTO users (username, password,salt) VALUES (?, ?, ?)",
            (user_data["username"], user_data["password"], user_data["salt"]),
        )

    conn.commit()
    conn.close()


# Chame a função para popular o banco de dados com dados de amostra e criar a tabela
seed_database()
