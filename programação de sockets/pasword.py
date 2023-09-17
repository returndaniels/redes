import bcrypt


# Função para criar um hash de senha
def create_hash_verify_password(password):
    # Gere um "sal" aleatório
    salt = bcrypt.gensalt()

    # Crie o hash da senha usando o sal
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)

    return password_hash, salt


# Função para verificar a senha
def verify_password(password, stored_password_hash, salt):
    # Verifique se a senha fornecida corresponde ao hash usando o mesmo "sal"
    new_hash = bcrypt.hashpw(password.encode("utf-8"), salt)
    return new_hash == stored_password_hash
