import bcrypt


# Função para criar um hash de senha
def create_hash_verify_password(password):
    # Gere um "sal" aleatório
    sal = bcrypt.gensalt()

    # Crie o hash da senha usando o sal
    password_hash = bcrypt.hashpw(password.encode("utf-8"), sal)

    return password_hash


# Função para verificar a senha
def verify_password(password, password_hash):
    # Verifique se a senha fornecida corresponde ao hash
    return bcrypt.checkpw(password.encode("utf-8"), password_hash)
