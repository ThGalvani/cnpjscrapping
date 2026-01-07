"""
Módulo de validação de CNPJ
Implementa o algoritmo oficial de validação de CNPJ da Receita Federal
"""
import re
from typing import Optional


def clean_cnpj(cnpj: str) -> str:
    """
    Remove caracteres não numéricos do CNPJ

    Args:
        cnpj: CNPJ com ou sem formatação

    Returns:
        CNPJ apenas com dígitos
    """
    return re.sub(r'\D', '', cnpj)


def format_cnpj(cnpj: str) -> str:
    """
    Formata CNPJ no padrão XX.XXX.XXX/XXXX-XX

    Args:
        cnpj: CNPJ sem formatação

    Returns:
        CNPJ formatado
    """
    cnpj = clean_cnpj(cnpj)
    if len(cnpj) != 14:
        return cnpj

    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def calculate_digit(cnpj: str, weights: list) -> int:
    """
    Calcula dígito verificador do CNPJ

    Args:
        cnpj: Primeiros dígitos do CNPJ
        weights: Pesos para cálculo

    Returns:
        Dígito verificador calculado
    """
    total = sum(int(digit) * weight for digit, weight in zip(cnpj, weights))
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def validate_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ usando o algoritmo oficial da Receita Federal

    Args:
        cnpj: CNPJ a ser validado

    Returns:
        True se CNPJ é válido, False caso contrário
    """
    cnpj = clean_cnpj(cnpj)

    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False

    # Verifica se não é uma sequência de números iguais
    if cnpj == cnpj[0] * 14:
        return False

    # Calcula primeiro dígito verificador
    weights_first = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    first_digit = calculate_digit(cnpj[:12], weights_first)

    if int(cnpj[12]) != first_digit:
        return False

    # Calcula segundo dígito verificador
    weights_second = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    second_digit = calculate_digit(cnpj[:13], weights_second)

    if int(cnpj[13]) != second_digit:
        return False

    return True


def extract_cnpj_from_text(text: str) -> Optional[str]:
    """
    Extrai CNPJ de um texto usando regex

    Args:
        text: Texto contendo CNPJ

    Returns:
        CNPJ encontrado ou None
    """
    # Padrão para CNPJ formatado ou não
    patterns = [
        r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',  # Formatado
        r'\d{14}'  # Sem formatação
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            cnpj = clean_cnpj(match.group())
            if validate_cnpj(cnpj):
                return cnpj

    return None


def is_matriz(cnpj: str) -> bool:
    """
    Verifica se o CNPJ é de uma matriz (filial é identificada pelos dígitos 9-12)

    Args:
        cnpj: CNPJ a ser verificado

    Returns:
        True se é matriz, False se é filial
    """
    cnpj = clean_cnpj(cnpj)
    if len(cnpj) != 14:
        return False

    # Os dígitos 9-12 são 0001 para matriz
    return cnpj[8:12] == '0001'


def get_cnpj_base(cnpj: str) -> str:
    """
    Retorna a base do CNPJ (primeiros 8 dígitos) - identifica a empresa

    Args:
        cnpj: CNPJ completo

    Returns:
        Base do CNPJ (8 primeiros dígitos)
    """
    cnpj = clean_cnpj(cnpj)
    return cnpj[:8] if len(cnpj) == 14 else ""


def get_filial_number(cnpj: str) -> str:
    """
    Retorna o número da filial (dígitos 9-12)

    Args:
        cnpj: CNPJ completo

    Returns:
        Número da filial
    """
    cnpj = clean_cnpj(cnpj)
    return cnpj[8:12] if len(cnpj) == 14 else ""
