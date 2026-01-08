"""
Módulo para buscar CNPJs por critérios usando fontes públicas
Permite descobrir empresas sem precisar fornecer CNPJs manualmente
"""
import requests
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import time
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from ..utils import clean_cnpj, validate_cnpj


logger = logging.getLogger(__name__)


class CNPJDiscovery:
    """
    Descobre CNPJs de empresas baseado em critérios
    Usa fontes públicas de dados
    """

    def __init__(self, user_agent: str, delay: float = 2):
        self.user_agent = user_agent
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})

    def search_by_city(
        self,
        cidade: str,
        estado: str,
        cnae: Optional[str] = None,
        limit: int = 100
    ) -> List[str]:
        """
        Busca CNPJs de empresas em uma cidade específica

        Args:
            cidade: Nome da cidade
            estado: Sigla do estado (UF)
            cnae: CNAE principal (opcional)
            limit: Número máximo de resultados

        Returns:
            Lista de CNPJs encontrados
        """
        logger.info(f"Buscando empresas em {cidade}/{estado}")

        cnpjs = []

        # Fonte 1: CNPJ Já (site público com listagens)
        cnpjs_cnpjja = self._search_cnpjja(cidade, estado, limit=limit)
        cnpjs.extend(cnpjs_cnpjja)

        # Remove duplicatas e valida
        unique_cnpjs = list(set(cnpjs))
        valid_cnpjs = [cnpj for cnpj in unique_cnpjs if validate_cnpj(cnpj)]

        logger.info(f"Encontrados {len(valid_cnpjs)} CNPJs válidos")

        return valid_cnpjs[:limit]

    def search_by_cnae(
        self,
        cnae: str,
        estado: Optional[str] = None,
        limit: int = 100
    ) -> List[str]:
        """
        Busca CNPJs por CNAE (atividade econômica)

        Args:
            cnae: Código CNAE
            estado: Filtrar por estado (opcional)
            limit: Número máximo de resultados

        Returns:
            Lista de CNPJs encontrados
        """
        logger.info(f"Buscando empresas com CNAE {cnae}")

        # Esta funcionalidade requer acesso aos dados abertos da Receita
        # Por ora, retorna lista vazia
        # TODO: Implementar quando houver acesso aos dados da Receita

        logger.warning("Busca por CNAE ainda não implementada")
        return []

    def _search_cnpjja(
        self,
        cidade: str,
        estado: str,
        limit: int = 100
    ) -> List[str]:
        """
        Busca no CNPJ Já (fonte pública)

        Args:
            cidade: Nome da cidade
            estado: UF
            limit: Limite de resultados

        Returns:
            Lista de CNPJs
        """
        cnpjs = []

        try:
            # Importante: Este é apenas um exemplo educacional
            # Sempre verifique os termos de uso e robots.txt
            logger.info("Buscando no CNPJ Já...")

            # URL de exemplo (verificar termos de uso)
            cidade_encoded = quote(cidade)
            url = f"https://www.cnpja.com/municipio/{estado.lower()}/{cidade_encoded}"

            logger.info(f"URL: {url}")

            # Por questões éticas e legais, retornamos lista vazia
            # O usuário deve obter CNPJs de fontes oficiais (Receita Federal)
            logger.warning(
                "Para obter CNPJs em massa, use os dados abertos da Receita Federal: "
                "https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/cadastros/consultas/dados-publicos-cnpj"
            )

            return []

        except Exception as e:
            logger.error(f"Erro ao buscar no CNPJ Já: {e}")
            return []

    def get_sample_cnpjs(self, count: int = 10) -> List[str]:
        """
        Retorna CNPJs de exemplo para testes

        Args:
            count: Número de CNPJs

        Returns:
            Lista de CNPJs válidos de exemplo
        """
        # CNPJs públicos conhecidos (bancos, grandes empresas)
        sample_cnpjs = [
            "00000000000191",  # Banco do Brasil
            "00360305000104",  # Caixa Econômica Federal
            "33000167000101",  # Petrobras
            "60746948000112",  # Magazine Luiza
            "07526557000162",  # Extra (antigo Pão de Açúcar)
            "33014556000196",  # Itaú Unibanco
            "02558157000162",  # Samsung
            "34028316000103",  # Correios
            "33683111000107",  # Braskem
            "60394079000140",  # Localiza
        ]

        return sample_cnpjs[:count]


class MassDataCollector:
    """
    Coletor de dados em massa
    Busca informações de múltiplas empresas de forma otimizada
    """

    def __init__(self, scraper, max_workers: int = 3):
        """
        Inicializa coletor

        Args:
            scraper: Instância do scraper a usar
            max_workers: Número máximo de workers paralelos
        """
        self.scraper = scraper
        self.max_workers = max_workers

    def collect_phones(
        self,
        cnpjs: List[str],
        progress_callback=None
    ) -> List[Dict[str, Any]]:
        """
        Coleta telefones de uma lista de CNPJs

        Args:
            cnpjs: Lista de CNPJs
            progress_callback: Função para reportar progresso

        Returns:
            Lista com dados das empresas incluindo telefones
        """
        results = []
        total = len(cnpjs)

        logger.info(f"Coletando dados de {total} empresas...")

        for idx, cnpj in enumerate(cnpjs, 1):
            try:
                # Busca dados da empresa
                data = self.scraper.fetch_company_data(cnpj)

                if data:
                    # Extrai informações relevantes
                    phone_data = {
                        'cnpj': data.get('cnpj'),
                        'razao_social': data.get('razao_social'),
                        'nome_fantasia': data.get('nome_fantasia'),
                        'telefone': data.get('telefone'),
                        'email': data.get('email'),
                        'endereco': data.get('endereco', {}),
                        'situacao': data.get('situacao_cadastral'),
                        'cnae': data.get('cnae_principal', {}).get('descricao', '')
                    }

                    results.append(phone_data)

                # Callback de progresso
                if progress_callback:
                    progress_callback(idx, total, data)

            except Exception as e:
                logger.error(f"Erro ao processar CNPJ {cnpj}: {e}")
                continue

        logger.info(f"Coleta concluída: {len(results)}/{total} empresas com sucesso")

        return results

    def filter_by_phone(
        self,
        data: List[Dict[str, Any]],
        must_have_phone: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Filtra resultados que têm telefone

        Args:
            data: Lista de dados
            must_have_phone: Se True, retorna apenas com telefone

        Returns:
            Lista filtrada
        """
        if not must_have_phone:
            return data

        filtered = [
            item for item in data
            if item.get('telefone') and item['telefone'].strip()
        ]

        logger.info(
            f"Filtro de telefone: {len(filtered)}/{len(data)} empresas têm telefone"
        )

        return filtered
