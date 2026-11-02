import socket
import sys
import time
import multiprocessing

TAM_MAX = 1024
TAM_FILA = 50

#-------------Monitor Sistema-----------------

def monitor_servers(tabela_servidores, lock):
    """
    Baseada na ideia de cliente UDP, porque não há necessidade de estabelecer
    conexão, enviando pings num loop temporal
    os tempos de timeout podemos variar para achar o melhor
    """

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.settimeout(1.5)

    print("Verificação de servidores disponíveis")

    while True:
        servidor_id = list(tabela_servidores.keys())

        for srv_id in servidor_id:
            info = tabela_servidores[srv_id]
            udp_adress = (info['ip'], info['porta_udp'])

            anterior = info['status']
            atual = 'DOWN'

            try:
                udp_sock.sendto(b"PING", udp_adress)
                _, _ = udp_sock.recvfrom(TAM_MAX)
                atual = 'UP'
            except socket.timeout:
                print(f"Servidor {srv_id} deu Timeout.")
            except Exception as e:
                print(f"Servidor {srv_id} inacessível: {e}")

            if atual != anterior:
                with lock:
                    srv_info = tabela_servidores[srv_id]
                    srv_info['status'] = atual

                    if atual == 'DOWN':
                        srv_info['conexoes'] = 0
                    tabela_servidores[srv_id] = srv_info
                print(f"Servidor {srv_id} ({info['ip']}) mudou para {atual}")

        time.sleep(3)

#-------------Processo filho-----------------#
def atender_cliente(connfd, client_addr, tabela_servidores, conexoes, lock, politica, rr_index):
    """
    Esqueleto do cliente_tcp.py conecta ao servidor para cuidar de cliente
    escolhe servidor destino, atualiza as métricas de carga além do repasse dos dados.
    """

    with lock:
        servidores_vivos = {i: j for i, j in tabela_servidores.items() if j['status'] == 'UP'}

        if not servidores_vivos:
            print(f"{client_addr} não atendido: Nenhum servidor disponível")
            connfd.close()
            return
        if politica == "least_connections":
            serv_escolhido = None
            menor_carga = float('inf')

            for srv_id, info in servidores_vivos.items():
                if info['conexoes'] < menor_carga:
                    menor_carga = info['conexoes']
                    serv_escolhido = srv_id
        else:
            ids_ativos = list(servidores_vivos.keys())
            rr_index.value = (rr_index.value + 1) % len(ids_ativos)
            serv_escolhido = ids_ativos[rr_index.value]

        info = tabela_servidores[serv_escolhido]
        info['conexoes'] += 1
        tabela_servidores[serv_escolhido] = info
        conexoes.value += 1

    print(f"Cliente {client_addr} atendido por Servidor:{serv_escolhido} Politica {politica}")

    servidor_info = tabela_servidores[serv_escolhido]
    backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        backend_sock.connect((servidor_info['ip'], servidor_info['porta_tcp']))

        # Fluxo de dados CLiente -> LB -> Serv Destino -> LB -> Cliente 
        while True:
            dados = connfd.recv(TAM_MAX)

            if not dados:
                break

            backend_sock.send(dados)
            resposta = backend_sock.recv(TAM_MAX)
            
            if resposta:
                connfd.send(resposta)
            else:
                break
    except Exception as e:
        print(f"Erro de comunicação com servidor {serv_escolhido}: {e}")
    finally:
        backend_sock.close()
        connfd.close()

        with lock:
            info = tabela_servidores[serv_escolhido]

            if info['conexoes'] > 0:
                info['conexoes'] -= 1
                conexoes.value -= 1
            tabela_servidores[serv_escolhido] = info

#-------------Main Process-----------------#
def main():
    # é para ser: script, porta, politica e N
    if len(sys.argv) != 4:
        print(f"Uso correto: {sys.argv[0]} <porta> <politica: rr ou lc> <N_servidores>")
        sys.exit(1)

    porta_lb = int(sys.argv[1])
    politica_arg = sys.argv[2].lower()
    N = int(sys.argv[3])

    if politica_arg == "lc":
        politica = "least_connections"
    else:
        politica = "round_robin"

    manager = multiprocessing.Manager()
    lock = manager.Lock()
    rr_index = manager.Value('i', -1)
    conexoes = manager.Value('i', 0)

    porta_tcp = 9000
    porta_udp = 10000
    tabela = {}
    
    for i in range(1, N + 1):
        tabela[i] = {
            'ip': '127.0.0.1', 
            'porta_tcp': porta_tcp + i, 
            'porta_udp': porta_udp + i, 
            'status': 'DOWN', 
            'conexoes': 0
        }

    tabela_servidores = manager.dict(tabela)

    monitoramento = multiprocessing.Process(target=monitor_servers, 
        args=(tabela_servidores, lock))

    monitoramento.daemon = True
    monitoramento.start()

    # Criação do socket, associação e modo escuta
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    sockfd.bind(('', porta_lb))
    
    sockfd.listen(TAM_FILA)

    print(f"[LB] Rodando na porta {porta_lb} | Política: {politica.upper()}")
    print("[LB] Aguardando conexoes\n")

    try:
        # Loop principal: aceita múltiplas conexoes
        while True:
            connfd, cliente_addr = sockfd.accept()
            print(f"[SERVIDOR] Cliente conectado: {cliente_addr}")

            #Processo filho para cuidar            
            processo_filho = multiprocessing.Process(target=atender_cliente,
                args=(connfd, cliente_addr, tabela_servidores, conexoes, lock, politica, rr_index))

            processo_filho.start()
            # Fecha a conexão com o cliente
            connfd.close()
    except KeyboardInterrupt:
        print("\n[LB] Encerrando Load Balancer")
    finally:
        sockfd.close()


if __name__ == '__main__':
    main()