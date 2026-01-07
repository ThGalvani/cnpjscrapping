"""
Módulo de filtros para dados de empresas
"""
from typing import List, Dict, Any, Optional, Callable
import logging


logger = logging.getLogger(__name__)


class CompanyFilter:
    """Classe para filtrar dados de empresas"""

    @staticmethod
    def filter_by_estado(data: List[Dict[str, Any]], estado: str) -> List[Dict[str, Any]]:
        """
        Filtra empresas por estado (UF)

        Args:
            data: Lista de empresas
            estado: Sigla do estado (ex: SP, RJ)

        Returns:
            Lista filtrada
        """
        estado_upper = estado.upper()
        filtered = [
            item for item in data
            if item.get('endereco', {}).get('uf', '').upper() == estado_upper
        ]
        logger.info(f"Filtro por estado {estado}: {len(filtered)}/{len(data)} empresas")
        return filtered

    @staticmethod
    def filter_by_cidade(data: List[Dict[str, Any]], cidade: str) -> List[Dict[str, Any]]:
        """
        Filtra empresas por cidade

        Args:
            data: Lista de empresas
            cidade: Nome da cidade

        Returns:
            Lista filtrada
        """
        cidade_lower = cidade.lower()
        filtered = [
            item for item in data
            if cidade_lower in item.get('endereco', {}).get('municipio', '').lower()
        ]
        logger.info(f"Filtro por cidade {cidade}: {len(filtered)}/{len(data)} empresas")
        return filtered

    @staticmethod
    def filter_by_cnae(data: List[Dict[str, Any]], cnae: str) -> List[Dict[str, Any]]:
        """
        Filtra empresas por CNAE principal

        Args:
            data: Lista de empresas
            cnae: Código CNAE (pode ser parcial)

        Returns:
            Lista filtrada
        """
        filtered = [
            item for item in data
            if cnae in str(item.get('cnae_principal', {}).get('codigo', ''))
        ]
        logger.info(f"Filtro por CNAE {cnae}: {len(filtered)}/{len(data)} empresas")
        return filtered

    @staticmethod
    def filter_by_situacao(data: List[Dict[str, Any]], situacao: str) -> List[Dict[str, Any]]:
        """
        Filtra empresas por situação cadastral

        Args:
            data: Lista de empresas
            situacao: Situação cadastral (ATIVA, BAIXADA, etc)

        Returns:
            Lista filtrada
        """
        situacao_upper = situacao.upper()
        filtered = [
            item for item in data
            if situacao_upper in item.get('situacao_cadastral', '').upper()
        ]
        logger.info(f"Filtro por situação {situacao}: {len(filtered)}/{len(data)} empresas")
        return filtered

    @staticmethod
    def filter_by_porte(data: List[Dict[str, Any]], porte: str) -> List[Dict[str, Any]]:
        """
        Filtra empresas por porte

        Args:
            data: Lista de empresas
            porte: Porte da empresa

        Returns:
            Lista filtrada
        """
        porte_upper = porte.upper()
        filtered = [
            item for item in data
            if porte_upper in item.get('porte', '').upper()
        ]
        logger.info(f"Filtro por porte {porte}: {len(filtered)}/{len(data)} empresas")
        return filtered

    @staticmethod
    def filter_matriz_only(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtra apenas matrizes (remove filiais)

        Args:
            data: Lista de empresas

        Returns:
            Lista apenas com matrizes
        """
        from .utils import clean_cnpj

        filtered = [
            item for item in data
            if clean_cnpj(item.get('cnpj', ''))[8:12] == '0001'
        ]
        logger.info(f"Filtro matrizes: {len(filtered)}/{len(data)} empresas")
        return filtered

    @staticmethod
    def filter_custom(
        data: List[Dict[str, Any]],
        condition: Callable[[Dict[str, Any]], bool]
    ) -> List[Dict[str, Any]]:
        """
        Aplica filtro customizado

        Args:
            data: Lista de empresas
            condition: Função que retorna True para itens a manter

        Returns:
            Lista filtrada
        """
        filtered = [item for item in data if condition(item)]
        logger.info(f"Filtro customizado: {len(filtered)}/{len(data)} empresas")
        return filtered

    @staticmethod
    def remove_duplicates(data: List[Dict[str, Any]], key: str = 'cnpj') -> List[Dict[str, Any]]:
        """
        Remove empresas duplicadas baseado em uma chave

        Args:
            data: Lista de empresas
            key: Chave para identificar duplicatas

        Returns:
            Lista sem duplicatas
        """
        seen = set()
        unique = []

        for item in data:
            value = item.get(key)
            if value and value not in seen:
                seen.add(value)
                unique.append(item)

        duplicates_removed = len(data) - len(unique)
        if duplicates_removed > 0:
            logger.info(f"Removidas {duplicates_removed} duplicatas")

        return unique

    @classmethod
    def apply_filters(
        cls,
        data: List[Dict[str, Any]],
        estado: Optional[str] = None,
        cidade: Optional[str] = None,
        cnae: Optional[str] = None,
        situacao: Optional[str] = None,
        porte: Optional[str] = None,
        apenas_matriz: bool = False,
        remove_duplicates: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Aplica múltiplos filtros sequencialmente

        Args:
            data: Lista de empresas
            estado: Filtro por estado
            cidade: Filtro por cidade
            cnae: Filtro por CNAE
            situacao: Filtro por situação cadastral
            porte: Filtro por porte
            apenas_matriz: Se deve filtrar apenas matrizes
            remove_duplicates: Se deve remover duplicatas

        Returns:
            Lista filtrada
        """
        filtered = data.copy()
        original_count = len(filtered)

        logger.info(f"Iniciando filtros. Total inicial: {original_count} empresas")

        if estado:
            filtered = cls.filter_by_estado(filtered, estado)

        if cidade:
            filtered = cls.filter_by_cidade(filtered, cidade)

        if cnae:
            filtered = cls.filter_by_cnae(filtered, cnae)

        if situacao:
            filtered = cls.filter_by_situacao(filtered, situacao)

        if porte:
            filtered = cls.filter_by_porte(filtered, porte)

        if apenas_matriz:
            filtered = cls.filter_matriz_only(filtered)

        if remove_duplicates:
            filtered = cls.remove_duplicates(filtered)

        logger.info(
            f"Filtros aplicados. Total final: {len(filtered)} empresas "
            f"({len(filtered)/original_count*100:.1f}% do total)"
        )

        return filtered
