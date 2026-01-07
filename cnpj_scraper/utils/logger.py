"""
Módulo de configuração de logging
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "cnpj_scraper",
    log_level: str = "INFO",
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    verbose: bool = False
) -> logging.Logger:
    """
    Configura o sistema de logging

    Args:
        name: Nome do logger
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Diretório para arquivos de log
        max_bytes: Tamanho máximo do arquivo de log
        backup_count: Número de backups a manter
        verbose: Se True, também exibe logs no console

    Returns:
        Logger configurado
    """
    # Cria diretório de logs se não existir
    os.makedirs(log_dir, exist_ok=True)

    # Configura o logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove handlers existentes para evitar duplicação
    logger.handlers.clear()

    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para arquivo com rotação
    log_filename = os.path.join(
        log_dir,
        f"cnpj_scraper_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para console (se verbose)
    if verbose:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def log_request(logger: logging.Logger, url: str, method: str = "GET", status: Optional[int] = None):
    """
    Loga uma requisição HTTP

    Args:
        logger: Logger a usar
        url: URL da requisição
        method: Método HTTP
        status: Código de status da resposta
    """
    if status:
        logger.info(f"{method} {url} - Status: {status}")
    else:
        logger.info(f"{method} {url}")


def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """
    Loga um erro com contexto

    Args:
        logger: Logger a usar
        error: Exceção ocorrida
        context: Contexto adicional do erro
    """
    error_msg = f"{context} - {type(error).__name__}: {str(error)}" if context else f"{type(error).__name__}: {str(error)}"
    logger.error(error_msg, exc_info=True)


def log_statistics(logger: logging.Logger, stats: dict):
    """
    Loga estatísticas de coleta

    Args:
        logger: Logger a usar
        stats: Dicionário com estatísticas
    """
    logger.info("=" * 50)
    logger.info("ESTATÍSTICAS DA COLETA")
    logger.info("=" * 50)
    for key, value in stats.items():
        logger.info(f"{key}: {value}")
    logger.info("=" * 50)
