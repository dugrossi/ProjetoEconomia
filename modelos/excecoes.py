"""Exceções personalizadas do projeto."""


class FonteDadosError(Exception):
    """Erro ao obter os dados de uma fonte (arquivo ou API)."""


class SerieInvalidaError(Exception):
    """Os dados recebidos não têm o formato esperado de uma série."""
