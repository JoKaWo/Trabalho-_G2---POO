"""Funções pequenas para ler e conferir o que o usuário digitou nos formulários de peso."""
from datetime import date

PESO_MINIMO = 20
PESO_MAXIMO = 400


def ler_numero(texto):
    """Converte '87,9' ou '87.9' em 87.9. Se não for um número, devolve None."""
    try:
        return float((texto or "").strip().replace(",", "."))
    except ValueError:
        return None


def ler_data(texto):
    """Converte '2026-10-22' (formato do campo de data do HTML) em date. Se não der, devolve None."""
    try:
        return date.fromisoformat((texto or "").strip())
    except ValueError:
        return None


def peso_valido(peso):
    """Um peso corporal só vale se for um número entre 20 kg e 400 kg."""
    return peso is not None and PESO_MINIMO <= peso <= PESO_MAXIMO
