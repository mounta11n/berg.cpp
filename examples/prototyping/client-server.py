# Serverprozess
import socket
import struct
import numpy as np
import os
import sys
import threading

N_EMBD = 384

def embeddings_from_local_server(s, sock):
    sock.sendall(s.encode())
    data = sock.recv(N_EMBD*4)
    floats = struct.unpack('f' * N_EMBD, data)
    return floats

def handle_client(client_socket):
    request = client_socket.recv(1024)
    input_text = request.decode()
    closest_texts, closest_similarities = query(input_text)
    response = ""
    for i, text in enumerate(closest_texts):
        response += f"{i+1}. {text.strip()} (similarity score: {closest_similarities[i]:.4f})\n"
    client_socket.send(response.encode())
    client_socket.close()

host = "localhost"
port = 8986
if len(sys.argv) > 2:
    port = int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((host, port))
    server_socket.listen(5)

    txt_file = "sample_client_texts.txt"
    with open(os.path.join(os.path.dirname(__file__), txt_file), 'r') as f:
        texts = f.readlines()

    embedded_texts = [embeddings_from_local_server(text, socket) for text in texts]

    def query(text, k=3):
        embedded_text = embeddings_from_local_server(text, sock)
        similarities = [np.dot(embedded_text, embedded_text_i) / (np.linalg.norm(embedded_text) * np.linalg.norm(embedded_text_i)) for embedded_text_i in embedded_texts]
        sorted_indices = np.argsort(similarities)[::-1]
        closest_texts = [texts[i] for i in sorted_indices[:k]]
        closest_similarities = [similarities[i] for i in sorted_indices[:k]]
        return closest_texts, closest_similarities

    while True:
        client_sock, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_sock,))
        client_thread.start()