"""
Módulo de verificação de robots.txt
Garante que o scraping respeita as regras definidas pelos sites
"""
import urllib.robotparser
from urllib.parse import urlparse, urljoin
import logging
from typing import Dict, Optional


logger = logging.getLogger(__name__)


class RobotsChecker:
    """Classe para verificação e cache de robots.txt"""

    def __init__(self):
        self.parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self.user_agent = "CNPJ Scraper Bot"

    def set_user_agent(self, user_agent: str):
        """
        Define o User-Agent a ser usado nas verificações

        Args:
            user_agent: String do User-Agent
        """
        self.user_agent = user_agent

    def get_robots_url(self, url: str) -> str:
        """
        Constrói a URL do robots.txt para um dado site

        Args:
            url: URL do site

        Returns:
            URL completa do robots.txt
        """
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        return robots_url

    def load_robots_txt(self, url: str) -> Optional[urllib.robotparser.RobotFileParser]:
        """
        Carrega e parseia o robots.txt de um site

        Args:
            url: URL do site

        Returns:
            Parser do robots.txt ou None em caso de erro
        """
        robots_url = self.get_robots_url(url)
        domain = urlparse(url).netloc

        # Retorna do cache se já carregado
        if domain in self.parsers:
            return self.parsers[domain]

        try:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            self.parsers[domain] = rp
            logger.info(f"robots.txt carregado com sucesso: {robots_url}")
            return rp
        except Exception as e:
            logger.warning(f"Erro ao carregar robots.txt de {robots_url}: {e}")
            logger.warning("Assumindo que o scraping NÃO é permitido por precaução")
            return None

    def can_fetch(self, url: str, user_agent: Optional[str] = None) -> bool:
        """
        Verifica se é permitido fazer scraping de uma URL

        Args:
            url: URL a ser verificada
            user_agent: User-Agent opcional (usa o padrão se não fornecido)

        Returns:
            True se permitido, False caso contrário
        """
        if user_agent is None:
            user_agent = self.user_agent

        parser = self.load_robots_txt(url)

        if parser is None:
            # Se não conseguiu carregar, não permite por precaução
            logger.warning(f"Scraping NÃO permitido (falha ao carregar robots.txt): {url}")
            return False

        can_fetch = parser.can_fetch(user_agent, url)

        if can_fetch:
            logger.debug(f"Scraping permitido: {url}")
        else:
            logger.warning(f"Scraping NÃO permitido por robots.txt: {url}")

        return can_fetch

    def get_crawl_delay(self, url: str, user_agent: Optional[str] = None) -> Optional[float]:
        """
        Obtém o delay de crawl recomendado pelo robots.txt

        Args:
            url: URL do site
            user_agent: User-Agent opcional

        Returns:
            Delay em segundos ou None se não especificado
        """
        if user_agent is None:
            user_agent = self.user_agent

        parser = self.load_robots_txt(url)

        if parser is None:
            return None

        delay = parser.crawl_delay(user_agent)

        if delay is not None:
            logger.info(f"Crawl delay recomendado: {delay}s para {url}")

        return delay

    def clear_cache(self):
        """Limpa o cache de parsers de robots.txt"""
        self.parsers.clear()
        logger.info("Cache de robots.txt limpo")

    def get_cache_info(self) -> Dict[str, str]:
        """
        Retorna informações sobre o cache de robots.txt

        Returns:
            Dicionário com domínios em cache
        """
        return {
            "cached_domains": list(self.parsers.keys()),
            "count": len(self.parsers)
        }
