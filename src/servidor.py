import socket
import sys
import multiprocessing #importante para possibilitar que o servidor escute por ambas as portas (TCP e UDP)

TAM_MAX = 1024 #pq esse tamanho?

#precisamos estabelecer 2 sockets, um para os dados (TCP)
#e outro para o monitoramente feito pelo LB (UDP)

def atender_cliente(socketCliente, clienteAddr):

    print(f"==== SERVIDOR ==== Cliente conectado: {clienteAddr}")

    mensagemLida = socketCliente.recv(TAM_MAX).decode()
    print(f"==== SERVIDOR ==== Mensagem recebida: {mensagemLida}")

    socketCliente.sendall(b"Mensagem recebida")

    socketCliente.close()


def escutar_clientes(portaTCP):

    #stream -> fluxo continuo, ja que eh TCP
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind(('', portaTCP))

    #porta em modo de escuta
    tcp_sock.listen(TAM_MAX)

    while True:

        #accept devolve um novo socket e o end do cliente
        socketCliente, clienteAddr = tcp_sock.accept()

        #um processo novo criado para cada cliente
        #assim o servidor não fica esperando um cliente de cada vez
        conexaoCliente = multiprocessing.Process(target = atender_cliente,
           args = (socketCliente, clienteAddr))

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

        #o que exatamente isso ta fazendo?
        mensagem, lb_addr = udp_sock.recvfrom(TAM_MAX)
        mensagem = mensagem.decode()

        #placa de rede só transmite bytes
        udp_sock.sendto(b"PONG", lb_addr)


def main():

    #2 argumentos: porta TCP para dados e porta UDP para monitoramento
    #argv[0] eh servidor.py

    if len(sys.argv) != 3:
        print(f"Uso correto: {sys.argv[0]} <porta>")
        sys.exit(1)
    
    portaTCP = int(sys.argv[1])
    portaUDP = int(sys.argv[2])

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