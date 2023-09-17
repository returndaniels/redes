from socket import *
import sqlite3
import sys
import urllib.parse
from pasword import verify_password


def verify_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username))
    user = cursor.fetchone()
    conn.close()
    return user


def send_page_response(response_header, filename):
    f = open(filename)
    outputdata = f.read()
    f.close()

    connectionSocket.send(response_header.encode())

    for i in range(0, len(outputdata)):
        connectionSocket.send(outputdata[i].encode())
    connectionSocket.send("\r\n".encode())


serverSocket = socket(AF_INET, SOCK_STREAM)
serverPort = 3000
serverSocket.bind(("", serverPort))
serverSocket.listen(1)

while True:
    print("Ready to serve...")
    connectionSocket, addr = serverSocket.accept()
    try:
        message = connectionSocket.recv(1024).decode()
        request_method, _, _, _, _ = message.split()[:5]

        if request_method == "POST" and "/login" in message:
            _, data = message.split("\r\n\r\n")
            data = urllib.parse.parse_qs(data)
            username = data["username"][0]
            password = data["password"][0]

            print(data)
            user = verify_user(username)
            print(4242, user)

            if user:
                response_header = "HTTP/1.1 200 OK\r\n\r\n"
                send_page_response(response_header, "./static/success.html")
            else:
                response_header = "HTTP/1.1 401 Unauthorized\r\n\r\n"
                send_page_response(response_header, "./static/unauthorized.html")
        else:
            filename = message.split()[1]

            try:
                response_header = "HTTP/1.1 200 OK\r\n\r\n"
                send_page_response(response_header, f"./static/{filename[1:]}")

            except IOError:
                response_header = "HTTP/1.1 404 Not Found\r\n\r\n"
                send_page_response(response_header, "./static/404.html")

        connectionSocket.close()

    except Exception as e:
        print("Error:", e)
        connectionSocket.close()

serverSocket.close()
sys.exit()
