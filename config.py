"""Configurações gerais do projeto."""

from pathlib import Path

PASTA_PROJETO = Path(__file__).parent
PASTA_DADOS_BRUTOS = PASTA_PROJETO / "dados" / "brutos"
PASTA_GRAFICOS = PASTA_PROJETO / "saida" / "graficos"
ARQUIVO_DASHBOARD = PASTA_PROJETO / "docs" / "dashboard.html"

# Códigos das séries usadas em todo o projeto
INADIMPLENCIA = 21082
JUROS = 25433

# Períodos comparados na análise (pergunta 3 da Etapa 1)
PERIODOS = {
    "2011 a 2019": ("2011-01-01", "2019-12-31"),
    "2020 a 2026": ("2020-01-01", "2026-12-31"),
}

# Séries do SGS usadas no projeto: código -> (nome, unidade)
SERIES = {
    21082: ("Inadimplência da carteira de crédito - Total", "% da carteira"),
    25433: (
        "Taxa média mensal de juros das operações de crédito - Total",
        "% ao mês",
    ),
}
