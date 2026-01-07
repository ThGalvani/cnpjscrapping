#!/usr/bin/env python3
"""
Exemplo de uso avançado do CNPJ Scraper

Este script demonstra como usar o CNPJ Scraper programaticamente
para casos de uso mais complexos.
"""
import sys
import os

# Adiciona o diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cnpj_scraper.scrapers import ReceitaWSScraper, BrasilAPIScraper
from cnpj_scraper.exporters import DataExporter
from cnpj_scraper.filters import CompanyFilter
from cnpj_scraper.utils import (
    setup_logger,
    validate_cnpj,
    format_cnpj,
    CacheManager,
    is_matriz
)


def exemplo_basico():
    """Exemplo básico de consulta de CNPJ"""
    print("=" * 60)
    print("EXEMPLO 1: Consulta Básica")
    print("=" * 60)

    # Configura logger
    logger = setup_logger(verbose=True)

    # Configura cache
    cache = CacheManager(cache_dir='cache', duration_hours=24)

    # Cria scraper
    scraper = ReceitaWSScraper(
        user_agent="Exemplo Uso/1.0",
        delay=2,
        cache_manager=cache
    )

    # Busca dados
    cnpj = "00000000000191"
    print(f"\nBuscando dados do CNPJ: {format_cnpj(cnpj)}")

    data = scraper.fetch_company_data(cnpj)

    if data:
        print(f"\n✓ Empresa encontrada:")
        print(f"  Razão Social: {data.get('razao_social')}")
        print(f"  CNPJ: {data.get('cnpj')}")
        print(f"  Situação: {data.get('situacao_cadastral')}")
        print(f"  Estado: {data.get('endereco', {}).get('uf')}")
    else:
        print("\n✗ Dados não encontrados")

    print()


def exemplo_multiplos_cnpjs():
    """Exemplo de consulta de múltiplos CNPJs"""
    print("=" * 60)
    print("EXEMPLO 2: Múltiplos CNPJs")
    print("=" * 60)

    # Lista de CNPJs para consultar
    cnpjs = [
        "00000000000191",
        "33000167000101",
        "07526557000162"
    ]

    # Configura scraper
    cache = CacheManager()
    scraper = ReceitaWSScraper(
        user_agent="Exemplo Uso/1.0",
        delay=2,
        cache_manager=cache
    )

    # Coleta dados
    results = []
    for cnpj in cnpjs:
        print(f"Consultando: {format_cnpj(cnpj)}...")
        data = scraper.fetch_company_data(cnpj)
        if data:
            results.append(data)

    print(f"\n✓ Total coletado: {len(results)} empresas")

    # Exibe resumo
    for empresa in results:
        print(f"  • {empresa.get('razao_social')} ({empresa.get('endereco', {}).get('uf')})")

    print()


def exemplo_com_filtros():
    """Exemplo usando filtros"""
    print("=" * 60)
    print("EXEMPLO 3: Aplicando Filtros")
    print("=" * 60)

    # Dados simulados (na prática viriam do scraper)
    dados = [
        {
            'cnpj': '00000000000191',
            'razao_social': 'Empresa A',
            'endereco': {'uf': 'SP', 'municipio': 'São Paulo'},
            'situacao_cadastral': 'ATIVA'
        },
        {
            'cnpj': '11111111000111',
            'razao_social': 'Empresa B',
            'endereco': {'uf': 'RJ', 'municipio': 'Rio de Janeiro'},
            'situacao_cadastral': 'ATIVA'
        },
        {
            'cnpj': '22222222000122',
            'razao_social': 'Empresa C',
            'endereco': {'uf': 'SP', 'municipio': 'Campinas'},
            'situacao_cadastral': 'BAIXADA'
        }
    ]

    print(f"Total de empresas: {len(dados)}")

    # Filtrar apenas empresas de SP
    filtradas_sp = CompanyFilter.filter_by_estado(dados, 'SP')
    print(f"Empresas em SP: {len(filtradas_sp)}")

    # Filtrar apenas ativas
    filtradas_ativas = CompanyFilter.filter_by_situacao(dados, 'ATIVA')
    print(f"Empresas ativas: {len(filtradas_ativas)}")

    # Aplicar múltiplos filtros
    filtradas = CompanyFilter.apply_filters(
        dados,
        estado='SP',
        situacao='ATIVA'
    )
    print(f"Empresas ativas em SP: {len(filtradas)}")

    print()


def exemplo_exportacao():
    """Exemplo de exportação em diferentes formatos"""
    print("=" * 60)
    print("EXEMPLO 4: Exportação de Dados")
    print("=" * 60)

    # Dados de exemplo
    dados = [
        {
            'cnpj': '00000000000191',
            'razao_social': 'Empresa Exemplo LTDA',
            'endereco': {
                'uf': 'SP',
                'municipio': 'São Paulo',
                'logradouro': 'Rua Exemplo'
            },
            'situacao_cadastral': 'ATIVA'
        }
    ]

    # Cria exportador
    exporter = DataExporter(
        output_dir='data',
        include_timestamp=True
    )

    # Exporta CSV
    print("Exportando CSV...")
    csv_path = exporter.export_to_csv(dados, filename='exemplo_csv')
    if csv_path:
        print(f"✓ CSV exportado: {csv_path}")

    # Exporta Excel
    print("Exportando Excel...")
    excel_path = exporter.export_to_excel(dados, filename='exemplo_excel')
    if excel_path:
        print(f"✓ Excel exportado: {excel_path}")

    # Exporta JSON
    print("Exportando JSON...")
    json_path = exporter.export_to_json(dados, filename='exemplo_json')
    if json_path:
        print(f"✓ JSON exportado: {json_path}")

    # Resumo
    summary = exporter.get_export_summary(dados)
    print(f"\nResumo da exportação:")
    print(f"  Total de registros: {summary.get('total_registros')}")
    print(f"  Total de colunas: {summary.get('total_colunas')}")

    print()


def exemplo_validacao():
    """Exemplo de validação de CNPJs"""
    print("=" * 60)
    print("EXEMPLO 5: Validação de CNPJs")
    print("=" * 60)

    cnpjs_teste = [
        "00000000000191",  # Válido
        "11222333000181",  # Válido
        "12345678901234",  # Inválido
        "00.000.000/0001-91",  # Válido (formatado)
        "11111111111111"   # Inválido (sequência)
    ]

    for cnpj in cnpjs_teste:
        valido = validate_cnpj(cnpj)
        status = "✓ VÁLIDO" if valido else "✗ INVÁLIDO"
        formatado = format_cnpj(cnpj) if valido else cnpj
        matriz = "MATRIZ" if valido and is_matriz(cnpj) else "FILIAL"

        print(f"{status} - {formatado} ({matriz})")

    print()


def exemplo_comparacao_fontes():
    """Exemplo comparando diferentes fontes"""
    print("=" * 60)
    print("EXEMPLO 6: Comparação de Fontes")
    print("=" * 60)

    cnpj = "00000000000191"
    cache = CacheManager()

    # ReceitaWS
    print("\nConsultando ReceitaWS...")
    scraper1 = ReceitaWSScraper(
        user_agent="Exemplo/1.0",
        delay=2,
        cache_manager=cache
    )
    data1 = scraper1.fetch_company_data(cnpj)

    if data1:
        print(f"✓ {data1.get('razao_social')}")
        print(f"  Fonte: {data1.get('source')}")

    # BrasilAPI
    print("\nConsultando BrasilAPI...")
    scraper2 = BrasilAPIScraper(
        user_agent="Exemplo/1.0",
        delay=2,
        cache_manager=cache
    )
    data2 = scraper2.fetch_company_data(cnpj)

    if data2:
        print(f"✓ {data2.get('razao_social')}")
        print(f"  Fonte: {data2.get('source')}")

    print()


def exemplo_tratamento_erros():
    """Exemplo de tratamento de erros"""
    print("=" * 60)
    print("EXEMPLO 7: Tratamento de Erros")
    print("=" * 60)

    scraper = ReceitaWSScraper(
        user_agent="Exemplo/1.0",
        delay=2
    )

    # CNPJ inválido
    print("\nTestando CNPJ inválido...")
    data = scraper.fetch_company_data("12345678901234")
    if data is None:
        print("✓ Erro tratado corretamente para CNPJ inválido")

    # CNPJ inexistente
    print("\nTestando CNPJ inexistente...")
    data = scraper.fetch_company_data("99999999999999")
    if data is None:
        print("✓ Erro tratado corretamente para CNPJ inexistente")

    print()


def main():
    """Executa todos os exemplos"""
    print("\n" + "=" * 60)
    print("EXEMPLOS DE USO AVANÇADO - CNPJ SCRAPER")
    print("=" * 60 + "\n")

    try:
        # Executa exemplos
        exemplo_basico()
        exemplo_multiplos_cnpjs()
        exemplo_com_filtros()
        exemplo_exportacao()
        exemplo_validacao()
        exemplo_comparacao_fontes()
        exemplo_tratamento_erros()

        print("=" * 60)
        print("TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    main()
