"""Configurações gerais do projeto."""

from pathlib import Path

PASTA_PROJETO = Path(__file__).parent
PASTA_DADOS_BRUTOS = PASTA_PROJETO / "dados" / "brutos"

# Séries do SGS usadas no projeto: código -> (nome, unidade)
SERIES = {
    21082: ("Inadimplência da carteira de crédito - Total", "% da carteira"),
    25433: (
        "Taxa média mensal de juros das operações de crédito - Total",
        "% ao mês",
    ),
}
