from socket import *
import sys


def send_page_response(response_header, filename):
    f = open(filename)
    outputdata = f.read()
    f.close()

    # Send one HTTP header line into socket
    connectionSocket.send(response_header.encode())

    # Send the content of the requested file to the client
    for i in range(0, len(outputdata)):
        connectionSocket.send(outputdata[i].encode())
    connectionSocket.send("\r\n".encode())


serverSocket = socket(AF_INET, SOCK_STREAM)
# Prepare a sever socket
serverPort = 3000
serverSocket.bind(("", serverPort))
serverSocket.listen(1)

while True:
    # Establish the connection
    print("Ready to serve...")
    connectionSocket, addr = serverSocket.accept()
    try:
        message = connectionSocket.recv(1024).decode()
        filename = message.split()[1]

        # Check if the requested file exists
        try:
            response_header = "HTTP/1.1 200 OK\r\n\r\n"
            send_page_response(response_header, filename[1:])

        except IOError:
            # Send a 404 Not Found response
            response_header = "HTTP/1.1 404 Not Found\r\n\r\n"
            send_page_response(response_header, "404.html")

        connectionSocket.close()

    except Exception as e:
        print("Error:", e)
        connectionSocket.close()

serverSocket.close()
sys.exit()
