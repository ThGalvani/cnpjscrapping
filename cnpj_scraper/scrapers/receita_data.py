"""
Módulo para trabalhar com dados abertos da Receita Federal
Fonte oficial: https://www.gov.br/receitafederal/dados-publicos-cnpj

IMPORTANTE: Os dados abertos da Receita Federal são muito grandes (~100GB)
Este módulo fornece uma interface simplificada para trabalhar com eles.
"""
import csv
import logging
from typing import List, Dict, Any, Optional
import os


logger = logging.getLogger(__name__)


class ReceitaDataReader:
    """
    Leitor de dados abertos da Receita Federal

    NOTA: Para usar este módulo, você precisa baixar os dados públicos da Receita:
    https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/cadastros/consultas/dados-publicos-cnpj
    """

    def __init__(self, data_dir: str = "receita_data"):
        """
        Inicializa o leitor

        Args:
            data_dir: Diretório com os arquivos da Receita
        """
        self.data_dir = data_dir
        self.companies_file = os.path.join(data_dir, "empresas.csv")
        self.establishments_file = os.path.join(data_dir, "estabelecimentos.csv")

    def is_data_available(self) -> bool:
        """Verifica se os dados estão disponíveis localmente"""
        return os.path.exists(self.companies_file)

    def search_by_city(
        self,
        cidade: str,
        estado: str,
        limit: int = 100
    ) -> List[str]:
        """
        Busca CNPJs em uma cidade específica

        Args:
            cidade: Nome da cidade
            estado: UF
            limit: Limite de resultados

        Returns:
            Lista de CNPJs
        """
        if not self.is_data_available():
            logger.error(
                "Dados da Receita não disponíveis. "
                "Baixe em: https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/cadastros/consultas/dados-publicos-cnpj"
            )
            return []

        cnpjs = []

        try:
            with open(self.establishments_file, 'r', encoding='latin-1') as f:
                reader = csv.DictReader(f, delimiter=';')

                for row in reader:
                    if len(cnpjs) >= limit:
                        break

                    # Verifica se é da cidade e estado desejados
                    if (row.get('municipio', '').upper() == cidade.upper() and
                        row.get('uf', '').upper() == estado.upper()):

                        cnpj = row.get('cnpj_basico', '')
                        if cnpj:
                            cnpjs.append(cnpj)

            logger.info(f"Encontrados {len(cnpjs)} CNPJs em {cidade}/{estado}")
            return cnpjs

        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {self.establishments_file}")
            return []
        except Exception as e:
            logger.error(f"Erro ao ler dados da Receita: {e}")
            return []

    def search_by_cnae(
        self,
        cnae: str,
        estado: Optional[str] = None,
        limit: int = 100
    ) -> List[str]:
        """
        Busca CNPJs por CNAE

        Args:
            cnae: Código CNAE
            estado: Filtrar por UF (opcional)
            limit: Limite de resultados

        Returns:
            Lista de CNPJs
        """
        if not self.is_data_available():
            logger.error("Dados da Receita não disponíveis")
            return []

        cnpjs = []

        try:
            with open(self.establishments_file, 'r', encoding='latin-1') as f:
                reader = csv.DictReader(f, delimiter=';')

                for row in reader:
                    if len(cnpjs) >= limit:
                        break

                    # Verifica CNAE
                    if row.get('cnae_fiscal_principal', '').startswith(cnae):
                        # Filtra por estado se fornecido
                        if estado and row.get('uf', '').upper() != estado.upper():
                            continue

                        cnpj = row.get('cnpj_basico', '')
                        if cnpj:
                            cnpjs.append(cnpj)

            logger.info(f"Encontrados {len(cnpjs)} CNPJs com CNAE {cnae}")
            return cnpjs

        except Exception as e:
            logger.error(f"Erro ao buscar por CNAE: {e}")
            return []


def get_sample_cnpjs_by_category(category: str = "tecnologia") -> List[str]:
    """
    Retorna CNPJs de exemplo por categoria
    Útil para demonstração e testes

    Args:
        category: Categoria (tecnologia, varejo, servicos, industria)

    Returns:
        Lista de CNPJs
    """
    samples = {
        "tecnologia": [
            "02558157000162",  # Samsung
            "00066371000136",  # Microsoft
            "06990590000123",  # Positivo
            "01522368000186",  # Lenovo
            "59104422000150",  # Dell
        ],
        "varejo": [
            "60746948000112",  # Magazine Luiza
            "07526557000162",  # Extra
            "47960950000121",  # Casas Bahia
            "47866934000174",  # Americanas
            "45242914000105",  # Riachuelo
        ],
        "bancos": [
            "00000000000191",  # Banco do Brasil
            "00360305000104",  # Caixa Econômica
            "33014556000196",  # Itaú
            "60746948000112",  # Bradesco
            "02318507000104",  # Santander
        ],
        "servicos": [
            "34028316000103",  # Correios
            "60394079000140",  # Localiza
            "02012862000160",  # Azul Linhas Aéreas
            "02769076000103",  # GOL Linhas Aéreas
            "07945233000175",  # LATAM
        ],
        "industria": [
            "33000167000101",  # Petrobras
            "33683111000107",  # Braskem
            "60506100000129",  # Ambev
            "50746577000115",  # JBS
            "02916265000160",  # BRF
        ]
    }

    return samples.get(category.lower(), samples["tecnologia"])
