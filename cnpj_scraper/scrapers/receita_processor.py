"""
Processador otimizado para dados da Receita Federal
Processa arquivos CSV grandes de forma eficiente
"""
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
import json
from tqdm import tqdm

logger = logging.getLogger(__name__)


class ReceitaProcessor:
    """
    Processa dados da Receita Federal de forma otimizada
    """

    # Colunas do arquivo Estabelecimentos
    ESTABELECIMENTOS_COLS = [
        'cnpj_basico', 'cnpj_ordem', 'cnpj_dv', 'matriz_filial',
        'nome_fantasia', 'situacao_cadastral', 'data_situacao', 'motivo_situacao',
        'nome_cidade_exterior', 'pais', 'data_inicio_atividade',
        'cnae_fiscal', 'cnae_fiscal_secundaria',
        'tipo_logradouro', 'logradouro', 'numero', 'complemento',
        'bairro', 'cep', 'uf', 'municipio_codigo', 'municipio',
        'ddd_1', 'telefone_1', 'ddd_2', 'telefone_2',
        'ddd_fax', 'fax', 'correio_eletronico',
        'situacao_especial', 'data_situacao_especial'
    ]

    # Colunas do arquivo Empresas
    EMPRESAS_COLS = [
        'cnpj_basico', 'razao_social', 'natureza_juridica',
        'qualificacao_responsavel', 'capital_social', 'porte',
        'ente_federativo'
    ]

    # Códigos de porte
    PORTES = {
        '01': 'MEI',
        '03': 'ME',  # Microempresa
        '05': 'EPP',  # Empresa de Pequeno Porte
        '00': 'Não Informado',
        '02': 'Grande',
    }

    def __init__(self, data_dir: str = "receita_data"):
        """
        Inicializa o processador

        Args:
            data_dir: Diretório com dados da Receita
        """
        self.data_dir = Path(data_dir)
        self.cache_dir = self.data_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)

    def find_files(self, prefix: str) -> List[Path]:
        """
        Encontra arquivos CSV com determinado prefixo

        Args:
            prefix: Prefixo do arquivo (ex: 'Estabelecimentos', 'Empresas')

        Returns:
            Lista de arquivos encontrados
        """
        files = list(self.data_dir.glob(f"{prefix}*.{prefix.upper()}"))
        if not files:
            # Tenta sem o prefixo em maiúsculas
            files = list(self.data_dir.glob(f"*{prefix}*"))

        logger.info(f"Encontrados {len(files)} arquivos de {prefix}")
        return sorted(files)

    def read_estabelecimentos(
        self,
        uf: Optional[str] = None,
        municipio: Optional[str] = None,
        situacao: str = '02',  # 02 = Ativa
        limit: Optional[int] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Lê arquivo de estabelecimentos com filtros

        Args:
            uf: Filtrar por UF
            municipio: Filtrar por município
            situacao: Situação cadastral (02 = Ativa)
            limit: Limite de resultados

        Yields:
            Dicionário com dados do estabelecimento
        """
        files = self.find_files('Estabelecimentos')

        if not files:
            logger.error("Nenhum arquivo de estabelecimentos encontrado!")
            logger.info(
                "Execute: python -m cnpj_scraper.scrapers.receita_downloader "
                "para baixar os dados"
            )
            return

        count = 0

        for file in files:
            logger.info(f"Processando: {file.name}")

            try:
                with open(file, 'r', encoding='latin-1') as f:
                    reader = csv.reader(f, delimiter=';')

                    for row in reader:
                        if len(row) < len(self.ESTABELECIMENTOS_COLS):
                            continue

                        # Cria dicionário
                        data = dict(zip(self.ESTABELECIMENTOS_COLS, row))

                        # Aplica filtros
                        if situacao and data['situacao_cadastral'] != situacao:
                            continue

                        if uf and data['uf'].upper() != uf.upper():
                            continue

                        if municipio and municipio.upper() not in data['municipio'].upper():
                            continue

                        # Formata telefone
                        telefone = self._format_phone(
                            data.get('ddd_1', ''),
                            data.get('telefone_1', '')
                        )

                        # Monta resultado
                        result = {
                            'cnpj': f"{data['cnpj_basico']}{data['cnpj_ordem']}{data['cnpj_dv']}",
                            'nome_fantasia': data.get('nome_fantasia', ''),
                            'situacao': self._get_situacao_nome(data['situacao_cadastral']),
                            'cnae': data.get('cnae_fiscal', ''),
                            'endereco': {
                                'logradouro': data.get('logradouro', ''),
                                'numero': data.get('numero', ''),
                                'complemento': data.get('complemento', ''),
                                'bairro': data.get('bairro', ''),
                                'cep': data.get('cep', ''),
                                'municipio': data.get('municipio', ''),
                                'uf': data.get('uf', '')
                            },
                            'telefone': telefone,
                            'email': data.get('correio_eletronico', ''),
                            'data_abertura': data.get('data_inicio_atividade', ''),
                            'matriz_filial': 'Matriz' if data['matriz_filial'] == '1' else 'Filial'
                        }

                        yield result

                        count += 1
                        if limit and count >= limit:
                            return

            except Exception as e:
                logger.error(f"Erro ao processar {file}: {e}")
                continue

    def search_mei_me_by_city(
        self,
        cidade: str,
        estado: str,
        limit: int = 100,
        only_with_phone: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Busca MEI e ME em uma cidade específica

        Args:
            cidade: Nome da cidade
            estado: UF
            limit: Limite de resultados
            only_with_phone: Apenas empresas com telefone

        Returns:
            Lista de empresas
        """
        cache_key = f"{estado}_{cidade}_{limit}_{only_with_phone}"
        cache_file = self.cache_dir / f"{cache_key}.json"

        # Tenta cache
        if cache_file.exists():
            logger.info(f"Usando cache: {cache_key}")
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        logger.info(f"Buscando MEI/ME em {cidade}/{estado}...")

        results = []

        for estabelecimento in self.read_estabelecimentos(
            uf=estado,
            municipio=cidade,
            limit=limit * 3  # Busca mais para filtrar
        ):
            # Filtra apenas com telefone se solicitado
            if only_with_phone and not estabelecimento.get('telefone'):
                continue

            # Busca razão social e porte (precisa cruzar com arquivo Empresas)
            cnpj_basico = estabelecimento['cnpj'][:8]
            empresa_data = self._get_empresa_data(cnpj_basico)

            if empresa_data:
                # Filtra MEI e ME
                porte = empresa_data.get('porte', '')
                if porte not in ['01', '03']:  # MEI ou ME
                    continue

                estabelecimento['razao_social'] = empresa_data.get('razao_social', '')
                estabelecimento['porte'] = self.PORTES.get(porte, 'Desconhecido')
                estabelecimento['capital_social'] = empresa_data.get('capital_social', '')

            results.append(estabelecimento)

            if len(results) >= limit:
                break

        # Salva no cache
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Erro ao salvar cache: {e}")

        logger.info(f"Encontrados {len(results)} MEI/ME em {cidade}/{estado}")

        return results

    def _get_empresa_data(self, cnpj_basico: str) -> Optional[Dict[str, Any]]:
        """
        Busca dados da empresa (razão social, porte) pelo CNPJ básico

        Args:
            cnpj_basico: 8 primeiros dígitos do CNPJ

        Returns:
            Dicionário com dados ou None
        """
        files = self.find_files('Empresas')

        if not files:
            return None

        # TODO: Otimizar com índice
        for file in files:
            try:
                with open(file, 'r', encoding='latin-1') as f:
                    reader = csv.reader(f, delimiter=';')

                    for row in reader:
                        if len(row) < len(self.EMPRESAS_COLS):
                            continue

                        if row[0] == cnpj_basico:
                            return dict(zip(self.EMPRESAS_COLS, row))

            except Exception as e:
                logger.error(f"Erro ao ler {file}: {e}")
                continue

        return None

    def _format_phone(self, ddd: str, numero: str) -> str:
        """Formata telefone"""
        if not numero or numero == '0':
            return ''

        ddd = ddd.strip()
        numero = numero.strip()

        if ddd and numero:
            return f"({ddd}) {numero}"

        return numero

    def _get_situacao_nome(self, codigo: str) -> str:
        """Retorna nome da situação cadastral"""
        situacoes = {
            '01': 'Nula',
            '02': 'Ativa',
            '03': 'Suspensa',
            '04': 'Inapta',
            '08': 'Baixada'
        }
        return situacoes.get(codigo, 'Desconhecida')

    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        cache_files = list(self.cache_dir.glob('*.json'))

        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'total_cached': len(cache_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }

    def clear_cache(self):
        """Limpa cache"""
        for file in self.cache_dir.glob('*.json'):
            file.unlink()
        logger.info("Cache limpo")
