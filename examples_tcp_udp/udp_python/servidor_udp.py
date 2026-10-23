#!/usr/bin/env python3
# ***************************************************************
#
# Nome do arquivo: servidor_udp.py
#
# Descrição: Servidor UDP simples iterativo.
#            Recebe mensagens e envia de volta.
#
# Autor: Giovanni Venâncio
# Data: 29/10/2025
#
# Execução:
#     python3 servidor_udp.py <porta>
#
# Exemplo:
#     python3 servidor_udp.py 8500
#
# ***************************************************************

import socket
import sys

TAM_MAX = 1024  # Tamanho máximo do buffer de dados

# Verifica uso correto
if len(sys.argv) != 2:
    print(f"Uso correto: {sys.argv[0]} <porta>")
    sys.exit(1)

porta = int(sys.argv[1])  # Porta do servidor

# Cria socket UDP (IPv4 + datagrama)
sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Faz o bind do socket para escutar em todas as interfaces locais
sockfd.bind(('', porta))

print("[SERVIDOR] Aguardando mensagens...")

# Loop principal, bloqueia aguardando mensagens de clientes
while True:
    # recvfrom recebe mensagem e endereço do cliente
    mensagem, cliente_addr = sockfd.recvfrom(TAM_MAX)
    mensagem = mensagem.decode()

    print(f"[SERVIDOR] Mensagem recebida de {cliente_addr}: {mensagem}")

    # Envia a mesma mensagem de volta ao cliente
    sockfd.sendto(mensagem.encode(), cliente_addr)

# Fecha o socket
sockfd.close()