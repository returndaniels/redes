from socket import *
import sqlite3
import sys
import urllib.parse
from pasword import verify_password
from livereload import Server
import uuid

sessions = {}


def verify_user(username):
    """
    Verifica se um usuário com o nome de usuário fornecido existe no banco de dados.

    Args:
        username (str): O nome de usuário a ser verificado.

    Returns:
        tuple or None: Uma tupla contendo as informações do usuário se encontrado,
        ou None se o usuário não existir no banco de dados.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def send_page_response(connectionSocket, response_header, filename):
    """
    Envia uma resposta HTTP para o cliente, incluindo um cabeçalho e o conteúdo de um arquivo.

    Args:
        connectionSocket (socket): O socket de conexão com o cliente.
        response_header (str): O cabeçalho da resposta HTTP.
        filename (str): O nome do arquivo a ser enviado como conteúdo da resposta.

    Returns:
        None
    """
    try:
        with open(filename, "rb") as file:
            outputdata = file.read()
    except IOError:
        response_header = "HTTP/1.1 404 Not Found\r\n\r\n"
        send_page_response(connectionSocket, response_header, "./static/404.html")

    connectionSocket.send(response_header.encode())
    connectionSocket.send(outputdata)
    connectionSocket.send(b"\r\n")


def handle_login(connectionSocket, message):
    """
    Lida com a solicitação de login do cliente, verifica as credenciais e cria uma sessão se válido.

    Args:
        connectionSocket (socket): O socket de conexão com o cliente.
        message (str): A mensagem HTTP recebida do cliente.

    Returns:
        None
    """
    _, data = message.split("\r\n\r\n")
    data = urllib.parse.parse_qs(data)
    username = data["username"][0]
    password = data["password"][0]

    user = verify_user(username)
    if user:
        _, _, user_password, salt = user

    if user and verify_password(password, user_password, salt):
        session_id = str(uuid.uuid4())

        sessions[session_id] = username

        response_header = "HTTP/1.1 302 Found\r\nLocation: /home\r\nSet-Cookie: session_id={}\r\n\r\n".format(
            session_id
        )
        connectionSocket.send(response_header.encode())
    else:
        response_header = "HTTP/1.1 401 Unauthorized\r\n\r\n"
        send_page_response(
            connectionSocket, response_header, "./static/unauthorized.html"
        )


def handle_logoff(connectionSocket, username):
    """
    Lida com a solicitação de logoff do cliente e encerra a sessão do usuário.

    Args:
        connectionSocket (socket): O socket de conexão com o cliente.
        username (str): O nome de usuário da sessão a ser encerrada.

    Returns:
        None
    """
    for session_id, user in sessions.items():
        if user == username:
            del sessions[session_id]
            break

    response_header = "HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n"
    connectionSocket.send(response_header.encode())


def get_dns_ip():
    """
    Obtém o endereço IP de DNS do servidor.

    Returns:
        str: O endereço IP de DNS do servidor.
    """
    try:
        host_name = gethostname()
        dns_ip = gethostbyname(host_name)
        return dns_ip
    except socket.error:
        return "Endereço IP de DNS não encontrado"


def handle_request(connectionSocket):
    """
    Lida com a solicitação HTTP recebida do cliente, roteia para as funções apropriadas e envia a resposta.

    Args:
        connectionSocket (socket): O socket de conexão com o cliente.

    Returns:
        None
    """
    request_method = None
    is_logged = False
    message = connectionSocket.recv(1024).decode()
    headers = message.split("\r\n")

    for header in headers:
        if header.startswith("Cookie:"):
            cookies = header.split(" ")
            for cookie in cookies:
                if "session_id" in cookie:
                    session_id = cookie.split("=")[1]
                    if session_id in sessions:
                        username = sessions[session_id]
                        is_logged = True
                        break

    if len(message.split()) >= 5:
        request_method, _, _, _, _ = message.split()[:5]

    if request_method == "POST" and "/login" in message:
        handle_login(connectionSocket, message)
    elif request_method == "POST" and "/logoff" in message:
        handle_logoff(connectionSocket, username)
    elif request_method == "GET" and "/get-dns" in message:
        dns_ip = get_dns_ip()
        response_header = "HTTP/1.1 200 OK\r\n\r\n"
        connectionSocket.send(response_header.encode())
        connectionSocket.send(dns_ip.encode())
    elif len(message.split()) > 0:
        filename = message.split()[1]
        filename = "/index.html" if filename == "/" else filename

        if is_logged and (filename == "/home" or "/login" in filename):
            filename = "/success.html"
        elif not (is_logged) and (filename == "/home" or "/login" in filename):
            filename = "/login.html"

        response_header = "HTTP/1.1 200 OK\r\n\r\n"
        send_page_response(
            connectionSocket, response_header, f"./static/{filename[1:]}"
        )

    connectionSocket.close()


def main():
    """
    Função principal que configura o servidor e inicia o loop de escuta por conexões.

    Returns:
        None
    """
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverPort = 3000
    serverSocket.bind(("", serverPort))
    serverSocket.listen(1)

    print("Ready to serve...")

    server = Server()

    server.watch(filepath="./static", func=handle_request)

    try:
        while True:
            connectionSocket, addr = serverSocket.accept()
            handle_request(connectionSocket)

    except KeyboardInterrupt:
        pass

    serverSocket.close()
    sys.exit()


if __name__ == "__main__":
    main()
