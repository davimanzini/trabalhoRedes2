
# Variáveis do projeto (ex: portas, IPs, tempos de timeout)

# configs do load balancer
LB_HOST = "127.0.0.1"
LB_PORT = 8080

# configs dos servidores de destino
SERVERS = [
    {"host": "127.0.0.1", "port": 5001},
    {"host": "127.0.0.1", "port": 5002}
]

# parâmetros de rede
BUFFER_SIZE = 1024
TIMEOUT = 5.0  