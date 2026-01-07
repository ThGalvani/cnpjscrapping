"""
Módulo de utilitários
"""
from .cnpj_validator import (
    validate_cnpj,
    clean_cnpj,
    format_cnpj,
    extract_cnpj_from_text,
    is_matriz,
    get_cnpj_base,
    get_filial_number
)
from .robots_checker import RobotsChecker
from .logger import setup_logger, log_request, log_error, log_statistics
from .cache_manager import CacheManager

__all__ = [
    'validate_cnpj',
    'clean_cnpj',
    'format_cnpj',
    'extract_cnpj_from_text',
    'is_matriz',
    'get_cnpj_base',
    'get_filial_number',
    'RobotsChecker',
    'setup_logger',
    'log_request',
    'log_error',
    'log_statistics',
    'CacheManager'
]
