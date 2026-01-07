"""
Módulo de gerenciamento de cache
Evita requisições duplicadas e melhora performance
"""
import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Any
import logging


logger = logging.getLogger(__name__)


class CacheManager:
    """Gerenciador de cache para requisições"""

    def __init__(self, cache_dir: str = "cache", duration_hours: int = 24):
        """
        Inicializa o gerenciador de cache

        Args:
            cache_dir: Diretório para arquivos de cache
            duration_hours: Duração do cache em horas
        """
        self.cache_dir = cache_dir
        self.duration = timedelta(hours=duration_hours)
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, identifier: str) -> str:
        """
        Gera uma chave de cache única

        Args:
            identifier: Identificador (ex: CNPJ, URL)

        Returns:
            Hash MD5 do identificador
        """
        return hashlib.md5(identifier.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> str:
        """
        Obtém o caminho completo do arquivo de cache

        Args:
            cache_key: Chave do cache

        Returns:
            Caminho completo do arquivo
        """
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def get(self, identifier: str) -> Optional[dict]:
        """
        Recupera dados do cache

        Args:
            identifier: Identificador único

        Returns:
            Dados em cache ou None se não existe ou expirou
        """
        cache_key = self._get_cache_key(identifier)
        cache_path = self._get_cache_path(cache_key)

        if not os.path.exists(cache_path):
            logger.debug(f"Cache miss: {identifier}")
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # Verifica se o cache expirou
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            if datetime.now() - cached_at > self.duration:
                logger.debug(f"Cache expirado: {identifier}")
                os.remove(cache_path)
                return None

            logger.debug(f"Cache hit: {identifier}")
            return cache_data['data']

        except Exception as e:
            logger.warning(f"Erro ao ler cache: {e}")
            return None

    def set(self, identifier: str, data: Any) -> bool:
        """
        Armazena dados no cache

        Args:
            identifier: Identificador único
            data: Dados a serem armazenados

        Returns:
            True se sucesso, False caso contrário
        """
        cache_key = self._get_cache_key(identifier)
        cache_path = self._get_cache_path(cache_key)

        try:
            cache_data = {
                'identifier': identifier,
                'cached_at': datetime.now().isoformat(),
                'data': data
            }

            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Cache armazenado: {identifier}")
            return True

        except Exception as e:
            logger.warning(f"Erro ao gravar cache: {e}")
            return False

    def delete(self, identifier: str) -> bool:
        """
        Remove dados do cache

        Args:
            identifier: Identificador único

        Returns:
            True se removido, False se não existia
        """
        cache_key = self._get_cache_key(identifier)
        cache_path = self._get_cache_path(cache_key)

        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                logger.debug(f"Cache removido: {identifier}")
                return True
            except Exception as e:
                logger.warning(f"Erro ao remover cache: {e}")
                return False

        return False

    def clear_all(self) -> int:
        """
        Limpa todo o cache

        Returns:
            Número de arquivos removidos
        """
        count = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
                    count += 1

            logger.info(f"Cache limpo: {count} arquivos removidos")
            return count

        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return count

    def clear_expired(self) -> int:
        """
        Remove apenas caches expirados

        Returns:
            Número de arquivos removidos
        """
        count = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)

                    with open(file_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)

                    cached_at = datetime.fromisoformat(cache_data['cached_at'])
                    if datetime.now() - cached_at > self.duration:
                        os.remove(file_path)
                        count += 1

            logger.info(f"Caches expirados removidos: {count} arquivos")
            return count

        except Exception as e:
            logger.error(f"Erro ao limpar caches expirados: {e}")
            return count

    def get_stats(self) -> dict:
        """
        Retorna estatísticas do cache

        Returns:
            Dicionário com estatísticas
        """
        total_files = 0
        total_size = 0
        expired = 0

        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    total_files += 1
                    total_size += os.path.getsize(file_path)

                    with open(file_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)

                    cached_at = datetime.fromisoformat(cache_data['cached_at'])
                    if datetime.now() - cached_at > self.duration:
                        expired += 1

            return {
                'total_cached': total_files,
                'total_size_kb': round(total_size / 1024, 2),
                'expired': expired,
                'active': total_files - expired
            }

        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do cache: {e}")
            return {}
