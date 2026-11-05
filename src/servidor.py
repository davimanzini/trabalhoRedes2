import socket
import sys
import multiprocessing

TAM_MAX = 1024 #pq esse tamanho?

#precisamos estabelecer 2 sockets, um para os dados (TCP)
#e outro para o monitoramente feito pelo LB (UDP)

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

if __name__ == '__main__':
    main()