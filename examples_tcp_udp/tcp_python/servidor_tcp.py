#!/usr/bin/env python3
#
# ***************************************************************
# 
# Nome do arquivo: servidor_tcp.py
#
# Descrição: Servidor TCP simples iterativo.
#            Recebe mensagens e envia de volta.
#
# Autor: Giovanni Venâncio
# Data: 29/10/2025
#
# Execução:
#     python3 servidor_tcp.py <porta>
#
# Exemplo:
#     python3 servidor_tcp.py 8500
#
# ***************************************************************

import socket
import sys

TAM_MAX = 1024   # Tamanho máximo do buffer de dados
TAM_FILA = 5     # Tamanho da fila de conexões

# Verifica uso correto
if len(sys.argv) != 2:
    print(f"Uso correto: {sys.argv[0]} <porta>")
    sys.exit(1)

porta = int(sys.argv[1])  # Porta do servidor, converte para int

# Cria socket TCP (IPv4 + TCP)
sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Associa o socket a todas as interfaces locais
sockfd.bind(('', porta))

# Coloca o socket em modo de escuta
sockfd.listen(TAM_FILA)

print("[SERVIDOR] Aguardando conexões...")

# Loop principal: aceita conexões iterativamente
while True:
    connfd, cliente_addr = sockfd.accept()
    print(f"[SERVIDOR] Cliente conectado: {cliente_addr}")

    # Recebe dados (em bytes) do cliente e decodifica para str
    buffer = connfd.recv(TAM_MAX).decode()

    print(f"[SERVIDOR] Mensagem recebida: {buffer}")

    # Envia a mesma mensagem (codificada em bytes)
    connfd.send(buffer.encode())

    # Fecha a conexão com o cliente
    connfd.close()
    print("[SERVIDOR] Conexão encerrada.\n")
