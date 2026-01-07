"""
Scraper para ReceitaWS API
API pública gratuita de consulta de CNPJs
"""
from typing import Optional, Dict, Any
import logging

from .base_scraper import BaseScraper
from ..utils import clean_cnpj, validate_cnpj


logger = logging.getLogger(__name__)


class ReceitaWSScraper(BaseScraper):
    """Scraper para a API ReceitaWS"""

    BASE_URL = "https://www.receitaws.com.br/v1/cnpj/"

    def get_source_name(self) -> str:
        """Retorna o nome da fonte"""
        return "ReceitaWS"

    def fetch_company_data(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Busca dados de uma empresa na ReceitaWS

        Args:
            cnpj: CNPJ da empresa

        Returns:
            Dados da empresa ou None
        """
        # Limpa e valida CNPJ
        cnpj_clean = clean_cnpj(cnpj)

        if not validate_cnpj(cnpj_clean):
            logger.warning(f"CNPJ inválido: {cnpj}")
            return None

        # Constrói URL
        url = f"{self.BASE_URL}{cnpj_clean}"

        # Busca com cache
        data = self.get_with_cache(cnpj_clean, url)

        if data is None:
            return None

        # Verifica se houve erro na API
        if data.get('status') == 'ERROR':
            logger.warning(f"Erro na API ReceitaWS: {data.get('message')}")
            return None

        # Normaliza os dados para formato padrão
        return self._normalize_data(data)

    def _normalize_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza dados da ReceitaWS para formato padrão

        Args:
            raw_data: Dados brutos da API

        Returns:
            Dados normalizados
        """
        try:
            normalized = {
                'source': self.get_source_name(),
                'cnpj': raw_data.get('cnpj', ''),
                'razao_social': raw_data.get('nome', ''),
                'nome_fantasia': raw_data.get('fantasia', ''),
                'cnae_principal': {
                    'codigo': raw_data.get('atividade_principal', [{}])[0].get('code', '') if raw_data.get('atividade_principal') else '',
                    'descricao': raw_data.get('atividade_principal', [{}])[0].get('text', '') if raw_data.get('atividade_principal') else ''
                },
                'endereco': {
                    'logradouro': raw_data.get('logradouro', ''),
                    'numero': raw_data.get('numero', ''),
                    'complemento': raw_data.get('complemento', ''),
                    'bairro': raw_data.get('bairro', ''),
                    'municipio': raw_data.get('municipio', ''),
                    'uf': raw_data.get('uf', ''),
                    'cep': raw_data.get('cep', '')
                },
                'telefone': raw_data.get('telefone', ''),
                'email': raw_data.get('email', ''),
                'capital_social': raw_data.get('capital_social', ''),
                'data_abertura': raw_data.get('abertura', ''),
                'situacao_cadastral': raw_data.get('situacao', ''),
                'data_situacao': raw_data.get('data_situacao', ''),
                'tipo': raw_data.get('tipo', ''),
                'porte': raw_data.get('porte', ''),
                'natureza_juridica': raw_data.get('natureza_juridica', ''),
                'cnae_secundarias': raw_data.get('atividades_secundarias', []),
                'qsa': raw_data.get('qsa', []),
                'raw_data': raw_data
            }

            return normalized

        except Exception as e:
            logger.error(f"Erro ao normalizar dados: {e}")
            return {'source': self.get_source_name(), 'raw_data': raw_data}
