import socket
import struct
import numpy as np
import os
import sys

N_EMBD = 384

def embeddings_from_local_server(s, sock):
    sock.sendall(s.encode())
    data = sock.recv(N_EMBD*4)
    floats = struct.unpack('f' * N_EMBD, data)
    return floats

host = "localhost"
port = 8689
if len(sys.argv) > 2:
    port = int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((host, port))
    N_EMBD = struct.unpack('i', sock.recv(4))[0]

    txt_file = "sample_client_texts.txt"
    with open(os.path.join(os.path.dirname(__file__), txt_file), 'r') as f:
        texts = f.readlines()

    embedded_texts = [embeddings_from_local_server(text, sock) for text in texts]

    def query(text, k=3):
        embedded_text = embeddings_from_local_server(text, sock)
        similarities = [np.dot(embedded_text, embedded_text_i) / (np.linalg.norm(embedded_text) * np.linalg.norm(embedded_text_i)) for embedded_text_i in embedded_texts]
        sorted_indices = np.argsort(similarities)[::-1]
        closest_texts = [texts[i] for i in sorted_indices[:k]]
        closest_similarities = [similarities[i] for i in sorted_indices[:k]]
        return closest_texts, closest_similarities

    input_text = sys.argv[1]
    closest_texts, closest_similarities = query(input_text)

    for i, text in enumerate(closest_texts):
        print(f"{i+1}. {text.strip()} (similarity score: {closest_similarities[i]:.4f})")