#import socket module
from socket import *
import sys # In order to terminate the program

serverSocket = socket(AF_INET, SOCK_STREAM)
# Prepare a sever socket
serverPort = 3000  # You can choose any available port
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

while True:
  # Establish the connection
  print('Ready to serve...')
  connectionSocket, addr = serverSocket.accept()  # Accept incoming connection
  try:
    message = connectionSocket.recv(1024).decode()  # Receive request message from the client
    filename = message.split()[1]
    f = open(filename[1:])
    outputdata = f.read()
    f.close()

    # Send one HTTP header line into socket
    response_header = "HTTP/1.1 200 OK\r\n\r\n"
    connectionSocket.send(response_header.encode())

    # Send the content of the requested file to the client
    for i in range(0, len(outputdata)):
      connectionSocket.send(outputdata[i].encode())
    connectionSocket.send("\r\n".encode())

    connectionSocket.close()
  except IOError:
    # Send response message for file not found
    error_response = "HTTP/1.1 404 Not Found\r\n\r\n"
    connectionSocket.send(error_response.encode())

    # Close client socket
    connectionSocket.close()
serverSocket.close()
sys.exit()  # Terminate the program after sending the corresponding data
