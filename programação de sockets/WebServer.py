import socket
from socket import *
import sqlite3
import sys
import re
import subprocess
import platform
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


def is_valid_ipv4_address(ip):
    """
    Verifica se a string fornecida é um endereço IPv4 válido.

    Args:
        ip (str): A string a ser verificada.

    Returns:
        bool: True se a string for um endereço IPv4 válido; caso contrário, False.
    """
    ipv4_pattern = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
    return bool(ipv4_pattern.match(ip))


def get_unix_dns_ips():
    """
    Recupera os endereços IP do servidor DNS em um sistema baseado em Unix do arquivo "/etc/resolv.conf".

    Returns:
        list: Uma lista de endereços IP de servidores DNS IPv4 válidos encontrados no arquivo.
    """
    dns_ips = []

    with open("/etc/resolv.conf") as fp:
        for line in fp:
            columns = line.split()
            if len(columns) >= 2 and columns[0] == "nameserver":
                ip = columns[1]
                if is_valid_ipv4_address(ip):
                    dns_ips.append(ip)

    return dns_ips


def get_windows_dns_ips():
    """
    Recupera os endereços IP do servidor DNS em um sistema Windows usando o comando “ipconfig”.

    Returns:
        list: Uma lista de endereços IP de servidores DNS IPv4 válidos encontrados na saída "ipconfig".
    """
    try:
        output = subprocess.check_output(["ipconfig", "/all"], universal_newlines=True)
    except subprocess.CalledProcessError:
        return []

    ipconfig_all_list = output.split("\n")

    dns_ips = []
    found_dns_servers = False

    for line in ipconfig_all_list:
        if "DNS Servers" in line or "Servidores DNS" in line:
            found_dns_servers = True
        elif found_dns_servers:
            ips = re.findall(r"[0-9.:a-fA-F%]+", line)
            for ip in ips:
                if is_valid_ipv4_address(ip):
                    dns_ips.append(ip)
                else:
                    found_dns_servers = False
    return dns_ips


def get_dns_ips():
    """
    Obtém o endereço IP de DNS do servidor.

    Returns:
        str: O endereço IP de DNS do servidor.
    """
    dns_ips = []

    if platform.system() == "Windows":
        dns_ips = get_windows_dns_ips()
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        dns_ips = get_unix_dns_ips()
    else:
        print("Plataforma não suportada: {0}".format(platform.system()))
    return dns_ips


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
        dns_ips = get_dns_ips()
        dns_info = "<br/>".join(dns_ips)
        response_header = "HTTP/1.1 200 OK\r\n\r\n"
        connectionSocket.send(response_header.encode())
        connectionSocket.send(dns_info.encode())
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
