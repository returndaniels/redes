from socket import *
import sqlite3
import sys
import urllib.parse
from pasword import verify_password
from livereload import Server


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
        outputdata = b"File not found"

    connectionSocket.send(response_header.encode())
    connectionSocket.send(outputdata)
    connectionSocket.send(b"\r\n")


def handle_request(connectionSocket):
    message = connectionSocket.recv(1024).decode()
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
            response_header = "HTTP/1.1 200 OK\r\n\r\n"
            send_page_response(
                connectionSocket, response_header, "./static/success.html"
            )
        else:
            response_header = "HTTP/1.1 401 Unauthorized\r\n\r\n"
            send_page_response(
                connectionSocket, response_header, "./static/unauthorized.html"
            )
    else:
        filename = message.split()[1]

        try:
            response_header = "HTTP/1.1 200 OK\r\n\r\n"
            send_page_response(
                connectionSocket, response_header, f"./static/{filename[1:]}"
            )

        except IOError:
            response_header = "HTTP/1.1 404 Not Found\r\n\r\n"
            send_page_response(connectionSocket, response_header, "./static/404.html")

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
