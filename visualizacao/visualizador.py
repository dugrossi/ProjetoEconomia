"""Geração dos gráficos interativos com Plotly."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Tema neutro, usando o visual padrão do Plotly. O estilo final da
# apresentação será aplicado na Etapa 6 trocando apenas este dicionário.
TEMA_PADRAO = {
    "template": "plotly_white",
    "cores": ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#8c564b"],
    "destaque": "#d62728",
    "referencia": "#555555",
}

# Tema da apresentação (Etapa 6): fundo transparente para o gráfico
# ficar por cima da cor da página, azul com laranja e grade bem clara.
_GRADE = "rgba(0,0,0,0.06)"
TEMA_EDITORIAL = {
    "template": go.layout.Template(layout={
        "font": {"family": "Inter, Arial, sans-serif", "size": 13,
                 "color": "#57534e"},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "xaxis": {"gridcolor": _GRADE, "zeroline": False,
                  "linecolor": "rgba(0,0,0,0.15)"},
        "yaxis": {"gridcolor": _GRADE, "zeroline": False},
        "hoverlabel": {"bgcolor": "#1c1917", "bordercolor": "#1c1917",
                       "font": {"color": "#f3efe7"}},
    }),
    "cores": ["#1d4e89", "#d97706", "#6f9bd1", "#78716c", "#f2b46d"],
    "destaque": "#d97706",
    "referencia": "#a8a29e",
    # Do mais claro ao mais escuro: usado no treemap, em que as
    # categorias têm ordem (faixa baixa -> faixa crítica).
    "sequencial": ["#e3ecf6", "#b4cbe6", "#6f9bd1", "#2f64a8", "#163a6b"],
}


class Visualizador:
    """Cria as figuras Plotly do projeto.

    Cada método recebe dados já preparados pelo AnalisadorDados e
    devolve uma figura (``plotly.graph_objects.Figure``). O Visualizador
    não lê arquivos nem faz cálculos de análise: só desenha.
    """

    def __init__(self, tema: dict | None = None) -> None:
        self.__tema = tema if tema is not None else TEMA_PADRAO

    @property
    def tema(self) -> dict:
        """Template e cores aplicados a todos os gráficos."""
        return self.__tema

    def __cor(self, indice: int) -> str:
        cores = self.__tema["cores"]
        return cores[indice % len(cores)]

    def __layout(self, figura: go.Figure, titulo: str) -> go.Figure:
        figura.update_layout(
            title=titulo, template=self.__tema["template"],
            hovermode="closest", separators=",.",
            legend={"orientation": "h", "y": -0.2},
        )
        return figura

    def grafico_linhas(
        self,
        tabela: pd.DataFrame,
        titulo: str,
        rotulos: dict,
        unidades: dict,
        eixo_direito=None,
    ) -> go.Figure:
        """Evolução de uma ou mais séries ao longo do tempo.

        Args:
            tabela: uma coluna por série, com as datas no índice.
            rotulos: nome exibido de cada coluna.
            unidades: unidade de cada coluna, usada nos eixos e dicas.
            eixo_direito: coluna desenhada num segundo eixo, à direita,
                quando as séries têm escalas diferentes.
        """
        figura = go.Figure()
        for i, coluna in enumerate(tabela.columns):
            direita = coluna == eixo_direito
            figura.add_trace(go.Scatter(
                x=tabela.index, y=tabela[coluna], mode="lines",
                name=rotulos[coluna], line={"color": self.__cor(i)},
                yaxis="y2" if direita else "y",
                hovertemplate=(f"%{{x|%m/%Y}}: %{{y:.2f}} {unidades[coluna]}"
                               f"<extra>{rotulos[coluna]}</extra>"),
            ))
        principais = [c for c in tabela.columns if c != eixo_direito]
        figura.update_layout(yaxis={"title": unidades[principais[0]]})
        if eixo_direito is not None:
            figura.update_layout(yaxis2={
                "title": unidades[eixo_direito], "overlaying": "y",
                "side": "right", "showgrid": False,
            })
        return self.__layout(figura, titulo)

    def grafico_barras(
        self,
        valores: pd.Series,
        titulo: str,
        rotulo_x: str,
        rotulo_y: str,
        destaque=None,
        linha_referencia: tuple[float, str] | None = None,
    ) -> go.Figure:
        """Compara valores entre categorias.

        Args:
            valores: um valor por categoria, com as categorias no índice.
            destaque: categoria pintada com a cor de destaque.
            linha_referencia: (valor, texto) de uma linha horizontal,
                como a média histórica.
        """
        categorias = [str(c) for c in valores.index]
        cores = [self.__tema["destaque"] if c == destaque
                 else self.__cor(0) for c in valores.index]
        figura = go.Figure(go.Bar(
            x=categorias, y=valores.values, marker_color=cores,
            hovertemplate="%{x}: %{y:.2f}<extra></extra>",
        ))
        figura.data[0].showlegend = False
        figura.update_layout(
            xaxis={"title": rotulo_x, "type": "category"},
            yaxis={"title": rotulo_y},
        )
        if linha_referencia is not None:
            valor, texto = linha_referencia
            figura.add_trace(go.Scatter(
                x=[categorias[0], categorias[-1]], y=[valor, valor],
                mode="lines", name=texto,
                line={"color": self.__tema["referencia"], "dash": "dash"},
                hoverinfo="skip",
            ))
        return self.__layout(figura, titulo)

    def grafico_treemap(
        self,
        contagens: pd.Series,
        titulo: str,
        descricoes: dict | None = None,
    ) -> go.Figure:
        """Participação de cada categoria no total (treemap).

        Args:
            contagens: quantidade por categoria, com os nomes no índice.
            descricoes: texto extra por categoria, mostrado na dica.
        """
        nomes = [str(n) for n in contagens.index]
        descricoes = descricoes or {}
        # Se o tema tiver uma escala sequencial, ela é usada no lugar
        # das cores comuns, porque as categorias aqui têm ordem.
        escala = self.__tema.get("sequencial", self.__tema["cores"])
        cores = [escala[i % len(escala)] for i in range(len(nomes))]
        figura = go.Figure(go.Treemap(
            labels=nomes, parents=[""] * len(nomes),
            values=contagens.values,
            customdata=[descricoes.get(n, "") for n in nomes],
            textinfo="label+value+percent root",
            hovertemplate=("<b>%{label}</b> %{customdata}<br>"
                           "%{value} meses (%{percentRoot:.1%})"
                           "<extra></extra>"),
            marker={"colors": cores},
            sort=False,
        ))
        return self.__layout(figura, titulo)

    def grafico_dispersao(
        self,
        tabela: pd.DataFrame,
        titulo: str,
        rotulo_x: str,
        rotulo_y: str,
        tendencia: bool = True,
    ) -> go.Figure:
        """Relação entre duas variáveis, um ponto por observação.

        Args:
            tabela: colunas "x", "y" e "data"; uma coluna opcional
                "grupo" separa os pontos por cor.
            tendencia: desenha a reta de tendência (mínimos quadrados).
        """
        figura = go.Figure()
        grupos = (tabela.groupby("grupo", sort=False)
                  if "grupo" in tabela.columns else [(None, tabela)])
        for i, (grupo, pontos) in enumerate(grupos):
            figura.add_trace(go.Scatter(
                x=pontos["x"], y=pontos["y"], mode="markers",
                name=str(grupo) if grupo is not None else rotulo_y,
                marker={"color": self.__cor(i), "size": 7},
                customdata=pontos["data"].dt.strftime("%m/%Y"),
                hovertemplate=("%{customdata}<br>x: %{x:.2f}<br>"
                               "y: %{y:.2f}<extra></extra>"),
            ))
        if tendencia:
            inclinacao, intercepto = np.polyfit(tabela["x"], tabela["y"], 1)
            xs = np.array([tabela["x"].min(), tabela["x"].max()])
            figura.add_trace(go.Scatter(
                x=xs, y=inclinacao * xs + intercepto, mode="lines",
                name="Tendência",
                line={"color": self.__tema["referencia"], "dash": "dash"},
                hoverinfo="skip",
            ))
        figura.update_layout(xaxis={"title": rotulo_x},
                             yaxis={"title": rotulo_y})
        return self.__layout(figura, titulo)
