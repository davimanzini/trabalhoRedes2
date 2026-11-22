import socket
import sys
import multiprocessing #importante para possibilitar que o servidor escute por ambas as portas (TCP e UDP)

from log_config import configurar_log

TAM_MAX = 1024 #revisar tamanho

#precisamos estabelecer 2 sockets, um para os dados (TCP)
#e outro para o monitoramente feito pelo LB (UDP)

def atender_cliente(socketCliente, clienteAddr, portaTCP):

    logger = configurar_log(f"SERVIDOR_{portaTCP}", f"servidor_{portaTCP}.log")

    print(f"==== SERVIDOR ==== Cliente conectado: {clienteAddr}")
    logger.info(f"Cliente conectado: {clienteAddr}")

    while(True):

        mensagemLida = socketCliente.recv(TAM_MAX).decode()
        
        if not mensagemLida:
            break
        
        print(f"==== SERVIDOR ==== Mensagem recebida: {mensagemLida}")
        logger.info(f"Mensagem recebida de {clienteAddr}: {mensagemLida}")

        socketCliente.sendall(b"Mensagem recebida")

    logger.info(f"Cliente desconectado: {clienteAddr}")
    socketCliente.close()


def escutar_clientes(portaTCP):

    #stream -> fluxo continuo, ja que eh TCP
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #importante para evitar erro address already in use se derrubarmos servidores no teste
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind(('', portaTCP))

    #porta em modo de escuta
    tcp_sock.listen(TAM_MAX)

    while True:

        #accept devolve um novo socket e o end do cliente
        socketCliente, clienteAddr = tcp_sock.accept()

        #um processo novo criado para cada cliente
        #assim o servidor não fica esperando um cliente de cada vez
        conexaoCliente = multiprocessing.Process(target = atender_cliente,
           args = (socketCliente, clienteAddr, portaTCP))

        conexaoCliente.daemon = True
        conexaoCliente.start()

        #o processo "filho" ja assumiu o socket, o processo "pai" ja pode desconectar
        socketCliente.close()

#recebe o PING do load balancer
def escutar_monitoramento(portaUDP):

    #cria socket UDP
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('', portaUDP))

    while True:

        #revisar
        mensagem, lb_addr = udp_sock.recvfrom(TAM_MAX)
        mensagem = mensagem.decode()

        #placa de rede só transmite bytes
        udp_sock.sendto(b"PONG", lb_addr)


def main():

    #2 argumentos: porta TCP para dados e porta UDP para monitoramento
    #argv[0] eh servidor.py

    if len(sys.argv) != 3:
        print(f"Uso correto: {sys.argv[0]} <portaTCP> <portaUDP")
        sys.exit(1)
    
    portaTCP = int(sys.argv[1])
    portaUDP = int(sys.argv[2])

    logger = configurar_log(f"SERVIDOR_{portaTCP}", f"servidor_{portaTCP}.log")
    logger.info(f"Servidor iniciado nas portas TCP {portaTCP} e UDP {portaUDP}")

    #variavel referente ao processo (ele inicia "pausado")
    escutaMonitoramento = multiprocessing.Process(target = escutar_monitoramento,
        args = (portaUDP,))
    
    escutaMonitoramento.daemon = True

    #inicia de fato o processo
    escutaMonitoramento.start()

    #processo principal
    escutar_clientes(portaTCP)

if __name__ == '__main__':
    main()