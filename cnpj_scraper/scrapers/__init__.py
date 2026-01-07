"""
Módulo de scrapers
"""
from .base_scraper import BaseScraper
from .receitaws_scraper import ReceitaWSScraper
from .brasilapi_scraper import BrasilAPIScraper

__all__ = [
    'BaseScraper',
    'ReceitaWSScraper',
    'BrasilAPIScraper'
]
