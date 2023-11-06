# Clientprozess
import socket
import sys

host = "localhost"
port = 8689
if len(sys.argv) > 2:
    port = int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((host, port))
    input_text = sys.argv[1]
    client_socket.send(input_text.encode())
    response = client_socket.recv(1024)
    print(response.decode())