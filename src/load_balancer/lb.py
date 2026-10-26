# Ao receber uma nova conexão de um cliente, seleciona um servidor
# para atender essa conexão e repassa os dados pro servidor. Deve implementar duas políticas de escolha: (i) Round-Robin;
# (ii) Least Connections. Apenas uma política de escolha deve permanecer ativa por vez,
# definindo durante a inicialização do LB.
# Possivelmente há casos de teste que só passem com uma das políticas
# então precisaremos implementar as 2.

import socket
import sys
import time
import multiprocessing

TAM_MAX = 1024
TAM_FILA = 50

def monitor_servers(tabela_servidores, lock):
    """
    Baseada na ideia de cliente UDP, porque não há necessidade de estabelecer
    conexão, enviando pings num loop temporal
    """

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.settimeout(1.5)

    print("Verificação de Servidores Disponíveis")

    while (1):
        servers_ids = list(tabela_servidores.keys())

        for srv_id in servers_ids:
            info = tabela_servidores[servers_ids]
            udp_adress = (info['ip'], info['udp_port'])

            old_status = info['status']
            current = 'DOWN'

            try:
                udp_sock.sendto(b"PING", udp_adress)
                _, _ = udp_sock.recvfrom(TAM_MAX)
                current = 'UP'
            except socket.timeout:
                print(f"Servidor {srv_id} demorou a responder (Timeout).")
            except Exception as e:
                print(f"[MONITOR] Servidor {srv_id} inacessível: {e}")

            if current != old_status:
                with lock:
                    srv_info = tabela_servidores[srv_id]
                    srv_info['status'] = current
                    if current == 'DOWN':
                        srv_info['connections'] = 0
                    tabela_servidores[srv_id] = srv_info
                print(f"Servidor {srv_id} ({info['ip']}) mudou para {current}")

        time.sleep(3)

#-------------LOAD BALANCER-----------------#

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


#-------------Monitor System-----------------


