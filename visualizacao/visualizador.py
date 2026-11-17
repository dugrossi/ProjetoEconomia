"""Geração dos gráficos interativos do dashboard."""

from __future__ import annotations

import pandas as pd

# Tema pensado para a apresentação com estética de vidro: fundos
# transparentes, para o gráfico "flutuar" sobre o cartão de vidro,
# e texto claro sobre o fundo escuro.
TEMA_VIDRO = {
    "fundo": "rgba(0,0,0,0)",
    "texto": "#EEF3FA",
    "grade": "rgba(255,255,255,0.12)",
    "fonte": "Inter, Segoe UI, sans-serif",
    "cores": {
        "inadimplencia": "#7CC8FF",
        "juros": "#FFA37A",
        "destaque": "#F4D35E",
    },
}


class Visualizador:
    """Cria as figuras Plotly usadas nos slides do dashboard.

    Cada método recebe um DataFrame já preparado pelo AnalisadorDados
    e devolve uma figura Plotly; o Visualizador não lê arquivos nem
    calcula indicadores.
    """

    def __init__(self, tema: dict | None = None) -> None:
        self.__tema = tema if tema is not None else TEMA_VIDRO

    @property
    def tema(self) -> dict:
        """Cores e fontes aplicadas a todos os gráficos."""
        return self.__tema

    def grafico_linhas(self, tabela: pd.DataFrame, titulo: str):
        """Evolução das séries ao longo do tempo (gráfico de linhas)."""
        raise NotImplementedError("Implementado na Etapa 5")

    def grafico_barras(self, tabela: pd.DataFrame, titulo: str):
        """Comparação entre categorias, como médias anuais (barras)."""
        raise NotImplementedError("Implementado na Etapa 5")

    def grafico_treemap(self, tabela: pd.DataFrame, titulo: str):
        """Meses por faixa de inadimplência (treemap)."""
        raise NotImplementedError("Implementado na Etapa 5")

    def grafico_dispersao(self, tabela: pd.DataFrame, titulo: str):
        """Juros defasados contra inadimplência (dispersão)."""
        raise NotImplementedError("Implementado na Etapa 5")
