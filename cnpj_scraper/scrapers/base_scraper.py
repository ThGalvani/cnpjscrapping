"""
Módulo base para scrapers
Implementa funcionalidades comuns como rate limiting, retry logic e respeito ao robots.txt
"""
import time
import requests
from typing import Optional, Dict, Any
import logging
from abc import ABC, abstractmethod
from urllib.parse import urljoin

from ..utils import RobotsChecker, log_request, log_error
from ..utils.cache_manager import CacheManager


logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Classe base abstrata para implementação de scrapers"""

    def __init__(
        self,
        user_agent: str,
        delay: float = 2.0,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        respect_robots: bool = True,
        cache_manager: Optional[CacheManager] = None
    ):
        """
        Inicializa o scraper base

        Args:
            user_agent: User-Agent para identificação
            delay: Delay entre requisições em segundos
            timeout: Timeout para requisições
            max_retries: Número máximo de tentativas
            backoff_factor: Fator de multiplicação para backoff exponencial
            respect_robots: Se deve respeitar robots.txt
            cache_manager: Gerenciador de cache opcional
        """
        self.user_agent = user_agent
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.respect_robots = respect_robots
        self.cache_manager = cache_manager

        self.robots_checker = RobotsChecker()
        self.robots_checker.set_user_agent(user_agent)

        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})

        self.last_request_time = 0
        self.stats = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cached_responses': 0,
            'robots_blocked': 0
        }

    def _wait_for_rate_limit(self):
        """Implementa rate limiting entre requisições"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            sleep_time = self.delay - elapsed
            logger.debug(f"Rate limiting: aguardando {sleep_time:.2f}s")
            time.sleep(sleep_time)

    def _can_fetch_url(self, url: str) -> bool:
        """
        Verifica se pode fazer scraping da URL

        Args:
            url: URL a verificar

        Returns:
            True se permitido, False caso contrário
        """
        if not self.respect_robots:
            return True

        can_fetch = self.robots_checker.can_fetch(url)

        if not can_fetch:
            self.stats['robots_blocked'] += 1

        return can_fetch

    def _make_request(
        self,
        url: str,
        method: str = 'GET',
        **kwargs
    ) -> Optional[requests.Response]:
        """
        Faz uma requisição HTTP com retry logic e rate limiting

        Args:
            url: URL para requisição
            method: Método HTTP
            **kwargs: Argumentos adicionais para requests

        Returns:
            Response object ou None em caso de falha
        """
        # Verifica robots.txt
        if not self._can_fetch_url(url):
            logger.warning(f"Requisição bloqueada por robots.txt: {url}")
            return None

        # Rate limiting
        self._wait_for_rate_limit()

        # Tenta fazer a requisição com retry logic
        for attempt in range(self.max_retries):
            try:
                self.stats['requests_made'] += 1
                self.last_request_time = time.time()

                response = self.session.request(
                    method,
                    url,
                    timeout=self.timeout,
                    **kwargs
                )

                log_request(logger, url, method, response.status_code)

                response.raise_for_status()
                self.stats['successful_requests'] += 1

                return response

            except requests.exceptions.RequestException as e:
                wait_time = self.backoff_factor ** attempt

                if attempt < self.max_retries - 1:
                    logger.warning(
                        f"Tentativa {attempt + 1}/{self.max_retries} falhou. "
                        f"Aguardando {wait_time}s antes de tentar novamente..."
                    )
                    time.sleep(wait_time)
                else:
                    log_error(logger, e, f"Falha ao fazer requisição para {url}")
                    self.stats['failed_requests'] += 1
                    return None

        return None

    def get_with_cache(self, identifier: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Faz requisição GET com suporte a cache

        Args:
            identifier: Identificador único para cache (ex: CNPJ)
            url: URL para requisição

        Returns:
            Dados da resposta ou None
        """
        # Tenta recuperar do cache
        if self.cache_manager:
            cached_data = self.cache_manager.get(identifier)
            if cached_data is not None:
                logger.info(f"Dados recuperados do cache: {identifier}")
                self.stats['cached_responses'] += 1
                return cached_data

        # Faz a requisição
        response = self._make_request(url)

        if response is None:
            return None

        try:
            data = response.json()

            # Armazena no cache
            if self.cache_manager:
                self.cache_manager.set(identifier, data)

            return data

        except Exception as e:
            log_error(logger, e, f"Erro ao processar resposta de {url}")
            return None

    def get_stats(self) -> Dict[str, int]:
        """
        Retorna estatísticas de uso do scraper

        Returns:
            Dicionário com estatísticas
        """
        return self.stats.copy()

    def reset_stats(self):
        """Reseta as estatísticas"""
        for key in self.stats:
            self.stats[key] = 0

    @abstractmethod
    def fetch_company_data(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Método abstrato para buscar dados de uma empresa

        Args:
            cnpj: CNPJ da empresa

        Returns:
            Dados da empresa ou None
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """
        Retorna o nome da fonte de dados

        Returns:
            Nome da fonte
        """
        pass
