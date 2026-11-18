import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# diretorio que os arquivos de log vao ser armazenados :)
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def configurar_log(nome, arquivo):
    logger = logging.getLogger(nome)
    logger.setLevel(logging.INFO)

    caminho = (LOG_DIR / arquivo).resolve()

    # evita adicionar de novo um handler pro mesmo arquivo
    # isso também permite que o mesmo logger seja associado a
    # arquivos diferentes
    handler_existente = any(
        getattr(handler, "_caminho_log", None) == caminho
        for handler in logger.handlers
    )

    if not handler_existente:
        handler = logging.FileHandler(
            caminho,
            encoding="utf-8"
        )

        formato = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        handler.setFormatter(formato)
        handler._caminho_log = caminho
        logger.addHandler(handler)

    # impede a duplicação de mensagens
    logger.propagate = False

    return logger