#!/usr/bin/env python3
#
# ***************************************************************
#
# Nome do arquivo: cliente_udp.py
#
# Descrição: Cliente UDP simples.
#            Envia uma mensagem e espera receber a mesma
#            mensagem de volta.
#
# Autor: Giovanni Venâncio
# Data: 29/10/2025
#
# Execução:
#     python3 cliente_udp.py <host> <porta>
#
# Exemplo:
#     python3 cliente_udp.py 127.0.1.1 8500
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

# Cria socket UDP
sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Lê mensagem do usuário e remove '\n' do final
buffer = input("[CLIENTE] Mensagem: ").strip()

# Envia mensagem para o servidor
sockfd.sendto(buffer.encode(), (host, porta))

# Recebe resposta do servidor (recvfrom retorna dados e endereço)
resposta, addr = sockfd.recvfrom(TAM_MAX)

print(f"[CLIENTE] Resposta recebida: {resposta.decode()}")

# Fecha o socket
sockfd.close()