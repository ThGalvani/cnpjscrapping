#!/usr/bin/env python3
"""
CNPJ Scraper - Ferramenta ética de web scraping para dados públicos de empresas brasileiras

AVISO LEGAL:
Esta ferramenta deve ser usada apenas para coleta ética de dados públicos.
O usuário é responsável por garantir conformidade com:
- Termos de uso dos sites
- Lei Geral de Proteção de Dados (LGPD)
- Legislação aplicável

Uso recomendado:
- Pesquisa acadêmica
- Análise de mercado
- Verificação de dados públicos
"""
import argparse
import json
import sys
import os
from typing import List, Dict, Any
from tqdm import tqdm

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cnpj_scraper.utils import (
    setup_logger, validate_cnpj, clean_cnpj, format_cnpj,
    CacheManager, log_statistics
)
from cnpj_scraper.scrapers import ReceitaWSScraper, BrasilAPIScraper
from cnpj_scraper.exporters import DataExporter
from cnpj_scraper.filters import CompanyFilter


# Configuração do logger
logger = setup_logger()


def load_config(config_path: str = "config.json") -> dict:
    """Carrega configurações do arquivo JSON"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {e}")
        return {}


def print_banner():
    """Exibe banner do aplicativo"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                      CNPJ SCRAPER v1.0                       ║
║          Coleta Ética de Dados Públicos de Empresas          ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_disclaimer():
    """Exibe disclaimer legal"""
    disclaimer = """
⚠️  AVISO LEGAL:
Esta ferramenta coleta apenas dados públicos disponíveis.
Ao usar esta ferramenta, você concorda em:
  • Respeitar os termos de uso dos sites
  • Não sobrecarregar os servidores
  • Usar os dados de forma ética e legal
  • Conformidade com LGPD e legislação aplicável

Pressione ENTER para continuar ou CTRL+C para cancelar...
"""
    print(disclaimer)
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(0)


def confirm_action(message: str) -> bool:
    """Solicita confirmação do usuário"""
    while True:
        response = input(f"{message} (s/n): ").lower()
        if response in ['s', 'sim', 'y', 'yes']:
            return True
        elif response in ['n', 'não', 'nao', 'no']:
            return False
        print("Por favor, responda 's' para sim ou 'n' para não.")


def scrape_cnpj(cnpj: str, scraper, cache_manager) -> Dict[str, Any]:
    """
    Faz scraping de um único CNPJ

    Args:
        cnpj: CNPJ a buscar
        scraper: Instância do scraper
        cache_manager: Gerenciador de cache

    Returns:
        Dados da empresa ou None
    """
    cnpj_clean = clean_cnpj(cnpj)

    if not validate_cnpj(cnpj_clean):
        logger.warning(f"CNPJ inválido: {cnpj}")
        return None

    logger.info(f"Buscando dados do CNPJ: {format_cnpj(cnpj_clean)}")

    data = scraper.fetch_company_data(cnpj_clean)

    if data:
        logger.info(f"Dados coletados: {data.get('razao_social', 'N/A')}")
    else:
        logger.warning(f"Não foi possível coletar dados do CNPJ: {cnpj_clean}")

    return data


def scrape_multiple_cnpjs(
    cnpjs: List[str],
    scraper,
    cache_manager,
    show_progress: bool = True
) -> List[Dict[str, Any]]:
    """
    Faz scraping de múltiplos CNPJs

    Args:
        cnpjs: Lista de CNPJs
        scraper: Instância do scraper
        cache_manager: Gerenciador de cache
        show_progress: Se deve mostrar barra de progresso

    Returns:
        Lista com dados das empresas
    """
    results = []

    iterator = tqdm(cnpjs, desc="Coletando dados") if show_progress else cnpjs

    for cnpj in iterator:
        data = scrape_cnpj(cnpj, scraper, cache_manager)
        if data:
            results.append(data)

    return results


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="CNPJ Scraper - Coleta ética de dados públicos de empresas brasileiras",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Buscar um único CNPJ
  python scraper.py --cnpj 00000000000191

  # Buscar múltiplos CNPJs de um arquivo
  python scraper.py --cnpj-file cnpjs.txt --output empresas.csv

  # Buscar com filtros
  python scraper.py --cnpj-file cnpjs.txt --estado SP --situacao ATIVA

  # Exportar em diferentes formatos
  python scraper.py --cnpj 00000000000191 --output empresa --format json

  # Modo dry-run (teste sem fazer requisições)
  python scraper.py --cnpj-file cnpjs.txt --dry-run

  # Modo verboso para debugging
  python scraper.py --cnpj 00000000000191 --verbose

⚠️  Esta ferramenta deve ser usada apenas para fins legais e éticos.
        """
    )

    # Argumentos de entrada
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--cnpj',
        type=str,
        help='CNPJ único para consulta'
    )
    input_group.add_argument(
        '--cnpj-file',
        type=str,
        help='Arquivo com lista de CNPJs (um por linha)'
    )

    # Argumentos de configuração
    parser.add_argument(
        '--source',
        type=str,
        choices=['receitaws', 'brasilapi'],
        default='receitaws',
        help='Fonte de dados a usar (padrão: receitaws)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        help='Delay entre requisições em segundos (padrão: do config.json)'
    )
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Desabilita cache de requisições'
    )
    parser.add_argument(
        '--no-robots',
        action='store_true',
        help='Ignora robots.txt (não recomendado)'
    )

    # Argumentos de filtros
    filter_group = parser.add_argument_group('Filtros')
    filter_group.add_argument(
        '--estado',
        type=str,
        help='Filtrar por estado (UF)'
    )
    filter_group.add_argument(
        '--cidade',
        type=str,
        help='Filtrar por cidade'
    )
    filter_group.add_argument(
        '--cnae',
        type=str,
        help='Filtrar por CNAE principal'
    )
    filter_group.add_argument(
        '--situacao',
        type=str,
        help='Filtrar por situação cadastral'
    )
    filter_group.add_argument(
        '--porte',
        type=str,
        help='Filtrar por porte da empresa'
    )
    filter_group.add_argument(
        '--apenas-matriz',
        action='store_true',
        help='Filtrar apenas matrizes (excluir filiais)'
    )

    # Argumentos de saída
    output_group = parser.add_argument_group('Saída')
    output_group.add_argument(
        '--output',
        type=str,
        default='empresas',
        help='Nome do arquivo de saída (sem extensão)'
    )
    output_group.add_argument(
        '--format',
        type=str,
        choices=['csv', 'excel', 'json'],
        default='csv',
        help='Formato de exportação (padrão: csv)'
    )

    # Argumentos de controle
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Modo teste (não faz requisições reais)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Modo verboso (exibe logs detalhados)'
    )
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Não exibir banner inicial'
    )
    parser.add_argument(
        '--skip-disclaimer',
        action='store_true',
        help='Pular disclaimer (não recomendado)'
    )
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Limpar cache antes de iniciar'
    )

    args = parser.parse_args()

    # Exibe banner
    if not args.no_banner:
        print_banner()

    # Exibe disclaimer
    if not args.skip_disclaimer and not args.dry_run:
        print_disclaimer()

    # Carrega configuração
    config = load_config()

    # Configura logger
    global logger
    logger = setup_logger(
        log_level="DEBUG" if args.verbose else "INFO",
        log_dir=config.get('logging', {}).get('log_directory', 'logs'),
        verbose=args.verbose
    )

    logger.info("=" * 60)
    logger.info("Iniciando CNPJ Scraper")
    logger.info("=" * 60)

    # Modo dry-run
    if args.dry_run:
        print("\n🧪 MODO DRY-RUN ATIVADO - Nenhuma requisição será feita\n")
        logger.info("Modo dry-run ativado")

    # Configura cache
    cache_manager = None
    if not args.no_cache:
        cache_config = config.get('scraping', {})
        cache_manager = CacheManager(
            cache_dir='cache',
            duration_hours=cache_config.get('cache_duration_hours', 24)
        )

        if args.clear_cache:
            cleared = cache_manager.clear_all()
            print(f"✓ Cache limpo: {cleared} arquivos removidos")
            logger.info(f"Cache limpo: {cleared} arquivos")

    # Configura scraper
    scraping_config = config.get('scraping', {})
    delay = args.delay if args.delay else scraping_config.get('default_delay', 2)

    if args.source == 'receitaws':
        scraper = ReceitaWSScraper(
            user_agent=scraping_config.get('user_agent', 'CNPJ Scraper Bot/1.0'),
            delay=delay,
            timeout=scraping_config.get('timeout', 30),
            max_retries=scraping_config.get('max_retries', 3),
            backoff_factor=scraping_config.get('backoff_factor', 2),
            respect_robots=not args.no_robots,
            cache_manager=cache_manager
        )
    else:
        scraper = BrasilAPIScraper(
            user_agent=scraping_config.get('user_agent', 'CNPJ Scraper Bot/1.0'),
            delay=delay,
            timeout=scraping_config.get('timeout', 30),
            max_retries=scraping_config.get('max_retries', 3),
            backoff_factor=scraping_config.get('backoff_factor', 2),
            respect_robots=not args.no_robots,
            cache_manager=cache_manager
        )

    logger.info(f"Fonte de dados: {scraper.get_source_name()}")
    logger.info(f"Rate limiting: {delay}s entre requisições")

    # Coleta CNPJs
    cnpjs = []

    if args.cnpj:
        cnpjs = [args.cnpj]
    elif args.cnpj_file:
        if not os.path.exists(args.cnpj_file):
            print(f"❌ Erro: Arquivo não encontrado: {args.cnpj_file}")
            sys.exit(1)

        with open(args.cnpj_file, 'r', encoding='utf-8') as f:
            cnpjs = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

    print(f"\n📋 Total de CNPJs para processar: {len(cnpjs)}")

    if not args.dry_run and len(cnpjs) > 10:
        if not confirm_action(f"Processar {len(cnpjs)} CNPJs?"):
            print("Operação cancelada.")
            sys.exit(0)

    # Modo dry-run - apenas valida CNPJs
    if args.dry_run:
        print("\n🔍 Validando CNPJs...")
        valid = 0
        invalid = 0

        for cnpj in cnpjs:
            if validate_cnpj(clean_cnpj(cnpj)):
                valid += 1
            else:
                invalid += 1
                print(f"  ❌ CNPJ inválido: {cnpj}")

        print(f"\n✓ Válidos: {valid}")
        print(f"✗ Inválidos: {invalid}")
        print("\n🧪 Modo dry-run concluído. Nenhuma requisição foi feita.")
        sys.exit(0)

    # Coleta dados
    print("\n🔍 Coletando dados...\n")
    results = scrape_multiple_cnpjs(cnpjs, scraper, cache_manager)

    print(f"\n✓ Dados coletados: {len(results)}/{len(cnpjs)} empresas")

    # Aplica filtros
    if any([args.estado, args.cidade, args.cnae, args.situacao, args.porte, args.apenas_matriz]):
        print("\n🔧 Aplicando filtros...")
        results = CompanyFilter.apply_filters(
            results,
            estado=args.estado,
            cidade=args.cidade,
            cnae=args.cnae,
            situacao=args.situacao,
            porte=args.porte,
            apenas_matriz=args.apenas_matriz
        )
        print(f"✓ Após filtros: {len(results)} empresas")

    # Exporta dados
    if results:
        print(f"\n💾 Exportando dados para {args.format.upper()}...")

        exporter = DataExporter(
            output_dir=config.get('export', {}).get('output_directory', 'data'),
            include_timestamp=config.get('export', {}).get('include_timestamp', True)
        )

        output_path = exporter.export(results, args.output, args.format)

        if output_path:
            print(f"✓ Dados exportados com sucesso: {output_path}")

            # Exibe resumo
            summary = exporter.get_export_summary(results)
            print(f"\n📊 Resumo:")
            print(f"  • Total de registros: {summary.get('total_registros', 0)}")
            print(f"  • Total de colunas: {summary.get('total_colunas', 0)}")

            if summary.get('estados'):
                print(f"  • Estados: {', '.join(summary['estados'].keys())}")

        else:
            print("❌ Erro ao exportar dados")
    else:
        print("\n⚠️  Nenhum dado coletado para exportar")

    # Estatísticas finais
    stats = scraper.get_stats()
    print(f"\n📈 Estatísticas:")
    print(f"  • Requisições feitas: {stats['requests_made']}")
    print(f"  • Sucessos: {stats['successful_requests']}")
    print(f"  • Falhas: {stats['failed_requests']}")
    print(f"  • Do cache: {stats['cached_responses']}")
    print(f"  • Bloqueadas por robots.txt: {stats['robots_blocked']}")

    # Loga estatísticas
    log_statistics(logger, stats)

    # Cache info
    if cache_manager:
        cache_stats = cache_manager.get_stats()
        print(f"\n💾 Cache:")
        print(f"  • Itens ativos: {cache_stats.get('active', 0)}")
        print(f"  • Itens expirados: {cache_stats.get('expired', 0)}")
        print(f"  • Tamanho: {cache_stats.get('total_size_kb', 0)} KB")

    logger.info("=" * 60)
    logger.info("CNPJ Scraper concluído")
    logger.info("=" * 60)

    print("\n✅ Processamento concluído!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
