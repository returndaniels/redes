from socket import *
import sqlite3
import sys
import urllib.parse
from pasword import verify_password
from livereload import Server
import uuid

sessions = {}


def verify_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def send_page_response(connectionSocket, response_header, filename):
    try:
        with open(filename, "rb") as file:
            outputdata = file.read()
    except IOError:
        response_header = "HTTP/1.1 404 Not Found\r\n\r\n"
        send_page_response(connectionSocket, response_header, "./static/404.html")

    connectionSocket.send(response_header.encode())
    connectionSocket.send(outputdata)
    connectionSocket.send(b"\r\n")


def handle_request(connectionSocket):
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
    elif request_method == "POST" and "/logoff" in message:
        for session_id, user in sessions.items():
            if user == username:
                del sessions[session_id]
                break

        response_header = "HTTP/1.1 302 Found\r\nLocation: /login\r\n\r\n"
        connectionSocket.send(response_header.encode())
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
