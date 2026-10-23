#!/usr/bin/env python3
# ***************************************************************
# 
# Nome do arquivo: cliente_tcp.py
#
# Descrição: Cliente TCP simples.
#            Envia uma mensagem e recebe de volta.
#
# Autor: Giovanni Venâncio
# Data: 29/10/2025
#
# Execução:
#     python3 cliente_tcp.py <host> <porta>
#
# Exemplo:
#     python3 cliente_tcp.py 127.0.1.1 8500
#
# ***************************************************************

import socket
import sys

TAM_MAX = 1024  # Tamanho máximo da mensagem

# Verifica uso correto
if len(sys.argv) != 3:
    print(f"Uso correto: {sys.argv[0]} <host> <porta>")
    sys.exit(1)

host = sys.argv[1]        # Endereço do servidor
porta = int(sys.argv[2])  # Porta do servidor

# Cria socket TCP (IPv4 + TCP)
sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta ao servidor
sockfd.connect((host, porta))

# Lê mensagem do usuário
buffer = input("[CLIENTE] Mensagem: ")

# Envia mensagem para o servidor
sockfd.send(buffer.encode())

# Recebe resposta do servidor
resposta = sockfd.recv(TAM_MAX).decode()

print(f"[CLIENTE] Resposta recebida: {resposta}")

# Fecha socket
sockfd.close()