import re


def normalize_cpf_cnpj(value: str) -> str:
    return re.sub(r"\D", "", (value or "").strip())


def is_valid_cpf_cnpj(value: str) -> bool:
    digits = normalize_cpf_cnpj(value)
    return len(digits) in (11, 14)
