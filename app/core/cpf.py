import re


def normalize_cpf(value: str) -> str:
    return re.sub(r"\D", "", (value or "").strip())


def is_valid_cpf(value: str) -> bool:
    cpf = normalize_cpf(value)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for position in range(9, 11):
        total = sum(int(cpf[i]) * ((position + 1) - i) for i in range(position))
        digit = (total * 10 % 11) % 10
        if int(cpf[position]) != digit:
            return False
    return True


def format_cpf_display(value: str) -> str:
    cpf = normalize_cpf(value)
    if len(cpf) != 11:
        return value
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
