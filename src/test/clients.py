import socket
import time
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# adiciona o diretório src ao path pra importar o log_config.
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

from config import LB_HOST, LB_PORT, BUFFER_SIZE, TIMEOUT
from log_config import configurar_log

# log dos clientes
logger = configurar_log("CLIENTES", "clientes.log")

# ------------ Parâmetros dos clientes -------------------
# valores que pode alterar pros testes :)
# aqui ficava também o número de clientes e o intervalo entre mensagens
INTERVALO_ENVIO = 0.5

# envia uma mensagem pro LB e recebe a resposta correspondente
def send_request(client_id):
    mensagens_enviadas = 0
    respostas_recebidas = 0

    tempo_final = time.monotonic() + K_segundos

    while time.monotonic() < tempo_final:
        try:
            #conexão persistente
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.settimeout(TIMEOUT)

                # conexão com o lb
                client_socket.connect((LB_HOST, LB_PORT))

                while time.monotonic() < tempo_final:

                    mensagem = (
                        f"Requisição do Cliente #{client_id} "
                        f"Mensagem #{mensagens_enviadas + 1}"
                    )

                    client_socket.sendall(mensagem.encode("utf-8"))
                    mensagens_enviadas += 1

                    # o servidor atual envia uma resposta sem \\n e fecha
                    # a conexão por isso usamos recv() em vez de readline().
                    resposta = client_socket.recv(BUFFER_SIZE)

                    if not resposta:
                        raise ConnectionError(
                            "O Load Balancer encerrou a conexão sem resposta."
                        )

                    resposta = resposta.decode("utf-8", errors="replace")
                    respostas_recebidas += 1

                    print(
                        f"[Cliente {client_id}] "
                        f"Resposta recebida: {resposta}"
                    )

                    logger.info(
                        f"Cliente {client_id}: mensagem {mensagens_enviadas} "
                        f"enviada e resposta recebida."
                    )

                    # tempo antes de abrir nova conexão
                    tempo_restante = tempo_final - time.monotonic()
                
                    if tempo_restante > 0:
                        time.sleep(min(INTERVALO_ENVIO, tempo_restante))

        except ConnectionRefusedError:
            print(
                f"[Cliente {client_id}] Conexão recusada. "
                "Verifique se o Load Balancer está em execução."
            )
            logger.error(
                f"Cliente {client_id}: conexão recusada pelo Load Balancer."
            )
            break

        except (socket.timeout, ConnectionResetError, BrokenPipeError,
                ConnectionError, OSError) as e:
            # pode acontecer se o monitoramento do LB ainda
            # não identificou nenhum servidor como UP.
            print(f"[Cliente {client_id}] Falha na requisição: {e}")
            logger.warning(
                f"Cliente {client_id}: falha na requisição - {e}"
            )
            tempo_restante = tempo_final - time.monotonic()
            if tempo_restante > 0:
                time.sleep(min(INTERVALO_ENVIO, tempo_restante))

        except Exception:
            print(f"[Cliente {client_id}] Erro inesperado.")
            logger.exception(
                f"Cliente {client_id}: erro inesperado."
            )
            break

    print(
        f"[Cliente {client_id}] "
        f"Enviadas: {mensagens_enviadas} | "
        f"Recebidas: {respostas_recebidas}"
    )

    logger.info(
        f"Cliente {client_id} finalizado. "
        f"Mensagens enviadas: {mensagens_enviadas}. "
        f"Respostas recebidas: {respostas_recebidas}."
    )

    return mensagens_enviadas, respostas_recebidas

# executa a função principal só quando o arquivo é executado diretamente
if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(f"Uso correto: {sys.argv[0]} <M clientes> <K segundos>")
        sys.exit(1)

    K_segundos = int(sys.argv[2])
    M_clientes = int(sys.argv[1])

    print("=== Iniciando Simulação de Clientes ===")
    print(f"Quantidade de clientes: {M_clientes}")
    print(f"Duração: {K_segundos} segundos")
    print(f"Intervalo entre mensagens: {INTERVALO_ENVIO} segundos")
    print(f"Load Balancer: {LB_HOST}:{LB_PORT}\n")

    total_enviadas = 0
    total_recebidas = 0

    logger.info(
        f"Iniciando simulação com {M_clientes} clientes "
        f"durante {K_segundos} segundos."
    )

    # executa os clientes ao mesmo tempo
    with ThreadPoolExecutor(max_workers=M_clientes) as executor:

        tarefas = [
            executor.submit(send_request, i)
            for i in range(1, M_clientes + 1)
        ]

        # aguarda os clientes terminarem
        for tarefa in as_completed(tarefas):
            enviadas, recebidas = tarefa.result()

            total_enviadas += enviadas
            total_recebidas += recebidas

    print("\n=== Resultado da Simulação ===")
    print(f"Total de mensagens enviadas: {total_enviadas}")
    print(f"Total de respostas recebidas: {total_recebidas}")

    logger.info(
        f"Simulação finalizada. "
        f"Clientes: {M_clientes}. "
        f"Mensagens enviadas: {total_enviadas}. "
        f"Respostas recebidas: {total_recebidas}."
    )