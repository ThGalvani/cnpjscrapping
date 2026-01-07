"""
Módulo de exportação de dados
Suporta exportação para CSV, Excel e JSON
"""
import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging


logger = logging.getLogger(__name__)


class DataExporter:
    """Classe para exportação de dados coletados"""

    def __init__(self, output_dir: str = "data", include_timestamp: bool = True):
        """
        Inicializa o exportador

        Args:
            output_dir: Diretório de saída
            include_timestamp: Se deve incluir timestamp no nome do arquivo
        """
        self.output_dir = output_dir
        self.include_timestamp = include_timestamp
        os.makedirs(output_dir, exist_ok=True)

    def _get_output_path(self, filename: str, extension: str) -> str:
        """
        Gera o caminho completo do arquivo de saída

        Args:
            filename: Nome base do arquivo
            extension: Extensão do arquivo

        Returns:
            Caminho completo
        """
        if self.include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}"

        return os.path.join(self.output_dir, f"{filename}.{extension}")

    def _flatten_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aplaina estruturas aninhadas para exportação tabular

        Args:
            data: Lista de dados com estruturas aninhadas

        Returns:
            Lista com dados aplanados
        """
        flattened = []

        for item in data:
            flat_item = {}

            for key, value in item.items():
                if isinstance(value, dict):
                    # Aplaina dicionários com prefixo
                    for subkey, subvalue in value.items():
                        flat_item[f"{key}_{subkey}"] = subvalue
                elif isinstance(value, list):
                    # Converte listas para string JSON
                    flat_item[key] = json.dumps(value, ensure_ascii=False)
                else:
                    flat_item[key] = value

            flattened.append(flat_item)

        return flattened

    def export_to_csv(
        self,
        data: List[Dict[str, Any]],
        filename: str = "empresas",
        flatten: bool = True
    ) -> Optional[str]:
        """
        Exporta dados para CSV

        Args:
            data: Lista de dicionários com dados
            filename: Nome do arquivo (sem extensão)
            flatten: Se deve aplanar estruturas aninhadas

        Returns:
            Caminho do arquivo gerado ou None em caso de erro
        """
        if not data:
            logger.warning("Nenhum dado para exportar")
            return None

        try:
            # Aplana dados se necessário
            export_data = self._flatten_data(data) if flatten else data

            # Cria DataFrame
            df = pd.DataFrame(export_data)

            # Gera caminho de saída
            output_path = self._get_output_path(filename, "csv")

            # Exporta
            df.to_csv(output_path, index=False, encoding='utf-8-sig')

            logger.info(f"Dados exportados para CSV: {output_path}")
            logger.info(f"Total de registros: {len(df)}")

            return output_path

        except Exception as e:
            logger.error(f"Erro ao exportar para CSV: {e}", exc_info=True)
            return None

    def export_to_excel(
        self,
        data: List[Dict[str, Any]],
        filename: str = "empresas",
        flatten: bool = True,
        sheet_name: str = "Empresas"
    ) -> Optional[str]:
        """
        Exporta dados para Excel

        Args:
            data: Lista de dicionários com dados
            filename: Nome do arquivo (sem extensão)
            flatten: Se deve aplanar estruturas aninhadas
            sheet_name: Nome da planilha

        Returns:
            Caminho do arquivo gerado ou None em caso de erro
        """
        if not data:
            logger.warning("Nenhum dado para exportar")
            return None

        try:
            # Aplana dados se necessário
            export_data = self._flatten_data(data) if flatten else data

            # Cria DataFrame
            df = pd.DataFrame(export_data)

            # Gera caminho de saída
            output_path = self._get_output_path(filename, "xlsx")

            # Exporta com formatação
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Auto-ajusta largura das colunas
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter

                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass

                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            logger.info(f"Dados exportados para Excel: {output_path}")
            logger.info(f"Total de registros: {len(df)}")

            return output_path

        except Exception as e:
            logger.error(f"Erro ao exportar para Excel: {e}", exc_info=True)
            return None

    def export_to_json(
        self,
        data: List[Dict[str, Any]],
        filename: str = "empresas",
        indent: int = 2
    ) -> Optional[str]:
        """
        Exporta dados para JSON

        Args:
            data: Lista de dicionários com dados
            filename: Nome do arquivo (sem extensão)
            indent: Indentação do JSON

        Returns:
            Caminho do arquivo gerado ou None em caso de erro
        """
        if not data:
            logger.warning("Nenhum dado para exportar")
            return None

        try:
            # Gera caminho de saída
            output_path = self._get_output_path(filename, "json")

            # Exporta
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)

            logger.info(f"Dados exportados para JSON: {output_path}")
            logger.info(f"Total de registros: {len(data)}")

            return output_path

        except Exception as e:
            logger.error(f"Erro ao exportar para JSON: {e}", exc_info=True)
            return None

    def export(
        self,
        data: List[Dict[str, Any]],
        filename: str = "empresas",
        format: str = "csv"
    ) -> Optional[str]:
        """
        Exporta dados no formato especificado

        Args:
            data: Lista de dicionários com dados
            filename: Nome do arquivo (sem extensão)
            format: Formato de exportação (csv, excel, json)

        Returns:
            Caminho do arquivo gerado ou None em caso de erro
        """
        format_lower = format.lower()

        if format_lower == "csv":
            return self.export_to_csv(data, filename)
        elif format_lower in ["excel", "xlsx"]:
            return self.export_to_excel(data, filename)
        elif format_lower == "json":
            return self.export_to_json(data, filename)
        else:
            logger.error(f"Formato não suportado: {format}")
            return None

    def get_export_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera um resumo dos dados a serem exportados

        Args:
            data: Lista de dados

        Returns:
            Dicionário com estatísticas
        """
        if not data:
            return {"total": 0}

        df = pd.DataFrame(self._flatten_data(data))

        summary = {
            "total_registros": len(df),
            "colunas": list(df.columns),
            "total_colunas": len(df.columns),
            "estados": df.get('endereco_uf', pd.Series()).value_counts().to_dict() if 'endereco_uf' in df.columns else {},
            "situacoes": df.get('situacao_cadastral', pd.Series()).value_counts().to_dict() if 'situacao_cadastral' in df.columns else {}
        }

        return summary
