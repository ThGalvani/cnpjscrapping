"""
Módulo de scrapers
"""
from .base_scraper import BaseScraper
from .receitaws_scraper import ReceitaWSScraper
from .brasilapi_scraper import BrasilAPIScraper
from .discovery import CNPJDiscovery, MassDataCollector
from .receita_data import ReceitaDataReader, get_sample_cnpjs_by_category

__all__ = [
    'BaseScraper',
    'ReceitaWSScraper',
    'BrasilAPIScraper',
    'CNPJDiscovery',
    'MassDataCollector',
    'ReceitaDataReader',
    'get_sample_cnpjs_by_category'
]
