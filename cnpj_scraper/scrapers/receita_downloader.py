"""
Downloader para Dados Abertos da Receita Federal
Baixa e processa a base completa de CNPJs (incluindo MEI e ME)

Base oficial: https://www.gov.br/receitafederal/dados-publicos-cnpj
Tamanho: ~100GB (compactado: ~30GB)
Conteúdo: TODOS os CNPJs do Brasil com dados públicos
"""
import requests
import os
import zipfile
from pathlib import Path
from typing import Optional
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)


class ReceitaDataDownloader:
    """
    Baixa dados públicos da Receita Federal
    """

    # URLs dos arquivos (atualize conforme necessário)
    BASE_URL = "https://dadosabertos.rfb.gov.br/CNPJ/"

    # Arquivos principais
    FILES = {
        'empresas': [
            'Empresas0.zip',
            'Empresas1.zip',
            'Empresas2.zip',
            'Empresas3.zip',
            'Empresas4.zip',
            'Empresas5.zip',
            'Empresas6.zip',
            'Empresas7.zip',
            'Empresas8.zip',
            'Empresas9.zip',
        ],
        'estabelecimentos': [
            'Estabelecimentos0.zip',
            'Estabelecimentos1.zip',
            'Estabelecimentos2.zip',
            'Estabelecimentos3.zip',
            'Estabelecimentos4.zip',
            'Estabelecimentos5.zip',
            'Estabelecimentos6.zip',
            'Estabelecimentos7.zip',
            'Estabelecimentos8.zip',
            'Estabelecimentos9.zip',
        ],
        'socios': ['Socios0.zip', 'Socios1.zip', 'Socios2.zip', 'Socios3.zip'],
        'cnaes': ['Cnaes.zip'],
        'municipios': ['Municipios.zip'],
        'naturezas': ['Naturezas.zip'],
        'paises': ['Paises.zip'],
        'qualificacoes': ['Qualificacoes.zip'],
    }

    def __init__(self, data_dir: str = "receita_data"):
        """
        Inicializa o downloader

        Args:
            data_dir: Diretório para salvar os dados
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def download_file(self, filename: str, force: bool = False) -> bool:
        """
        Baixa um arquivo específico

        Args:
            filename: Nome do arquivo
            force: Forçar download mesmo se já existir

        Returns:
            True se sucesso
        """
        output_path = self.data_dir / filename

        if output_path.exists() and not force:
            logger.info(f"Arquivo já existe: {filename}")
            return True

        url = self.BASE_URL + filename

        try:
            logger.info(f"Baixando: {filename}")

            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(output_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            logger.info(f"Download concluído: {filename}")
            return True

        except Exception as e:
            logger.error(f"Erro ao baixar {filename}: {e}")
            if output_path.exists():
                output_path.unlink()
            return False

    def extract_file(self, filename: str) -> bool:
        """
        Extrai arquivo ZIP

        Args:
            filename: Nome do arquivo ZIP

        Returns:
            True se sucesso
        """
        zip_path = self.data_dir / filename

        if not zip_path.exists():
            logger.error(f"Arquivo não encontrado: {filename}")
            return False

        try:
            logger.info(f"Extraindo: {filename}")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.data_dir)

            logger.info(f"Extração concluída: {filename}")
            return True

        except Exception as e:
            logger.error(f"Erro ao extrair {filename}: {e}")
            return False

    def download_essentials(self) -> bool:
        """
        Baixa apenas arquivos essenciais para começar
        (Estabelecimentos contém telefones e endereços)

        Returns:
            True se sucesso
        """
        essentials = [
            'Estabelecimentos0.zip',  # ~3GB, contém telefones
            'Municipios.zip',         # ~100KB, lista de cidades
            'Cnaes.zip',             # ~500KB, CNAEs
        ]

        print("=" * 60)
        print("DOWNLOAD DE ARQUIVOS ESSENCIAIS DA RECEITA FEDERAL")
        print("=" * 60)
        print(f"\nSerão baixados {len(essentials)} arquivos (~3GB)")
        print("Isso pode demorar dependendo da sua internet...")
        print()

        success = True
        for filename in essentials:
            if not self.download_file(filename):
                success = False

            # Extrai automaticamente
            if self.data_dir / filename.exists():
                self.extract_file(filename)

        if success:
            print("\n✅ Download concluído!")
            print(f"Dados salvos em: {self.data_dir}")
        else:
            print("\n⚠️ Alguns arquivos falharam. Tente novamente.")

        return success

    def download_all(self) -> bool:
        """
        Baixa TODOS os arquivos (ATENÇÃO: ~30GB!)

        Returns:
            True se sucesso
        """
        print("=" * 60)
        print("DOWNLOAD COMPLETO DA BASE DA RECEITA FEDERAL")
        print("=" * 60)
        print("\n⚠️ ATENÇÃO: Isso vai baixar ~30GB de dados!")
        print("Tempo estimado: 1-3 horas (dependendo da internet)")
        print()

        confirm = input("Deseja continuar? (sim/não): ")
        if confirm.lower() not in ['sim', 's', 'yes', 'y']:
            print("Download cancelado.")
            return False

        all_files = []
        for file_list in self.FILES.values():
            all_files.extend(file_list)

        total_files = len(all_files)
        print(f"\nBaixando {total_files} arquivos...")

        success_count = 0
        for i, filename in enumerate(all_files, 1):
            print(f"\n[{i}/{total_files}] {filename}")

            if self.download_file(filename):
                success_count += 1
                self.extract_file(filename)

        print(f"\n✅ Download concluído: {success_count}/{total_files} arquivos")
        return success_count == total_files

    def get_info(self) -> dict:
        """
        Retorna informações sobre arquivos baixados

        Returns:
            Dicionário com informações
        """
        info = {
            'data_dir': str(self.data_dir),
            'downloaded_files': [],
            'extracted_files': [],
            'total_size_mb': 0
        }

        for file in self.data_dir.iterdir():
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                info['total_size_mb'] += size_mb

                if file.suffix == '.zip':
                    info['downloaded_files'].append(file.name)
                else:
                    info['extracted_files'].append(file.name)

        info['total_size_mb'] = round(info['total_size_mb'], 2)
        return info


def main():
    """Função principal para uso via CLI"""
    print("=" * 60)
    print("CNPJ SCRAPER - DOWNLOADER DE DADOS DA RECEITA FEDERAL")
    print("=" * 60)
    print()
    print("Escolha uma opção:")
    print("1. Download essencial (~3GB) - Recomendado para começar")
    print("2. Download completo (~30GB) - Base completa")
    print("3. Ver informações dos arquivos baixados")
    print("4. Sair")
    print()

    choice = input("Opção (1-4): ")

    downloader = ReceitaDataDownloader()

    if choice == '1':
        downloader.download_essentials()
    elif choice == '2':
        downloader.download_all()
    elif choice == '3':
        info = downloader.get_info()
        print(f"\nDiretório: {info['data_dir']}")
        print(f"Tamanho total: {info['total_size_mb']} MB")
        print(f"Arquivos ZIP: {len(info['downloaded_files'])}")
        print(f"Arquivos extraídos: {len(info['extracted_files'])}")
    elif choice == '4':
        print("Saindo...")
    else:
        print("Opção inválida!")


if __name__ == "__main__":
    main()
