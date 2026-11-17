"""Monta o dashboard como uma apresentação em HTML."""

from __future__ import annotations

from pathlib import Path

from analise.analisador_dados import AnalisadorDados
from dashboard.slide import Slide
from indicadores.indicador import Indicador
from visualizacao.visualizador import Visualizador


class DashboardHTML:
    """Organiza os componentes do painel em uma apresentação de slides.

    O resultado é um único arquivo HTML: os slides avançam com um
    clique no canto direito da tela, com transição 3D entre eles e
    cartões com estética de vidro (glassmorphism).
    """

    def __init__(
        self,
        titulo: str,
        analisador: AnalisadorDados,
        visualizador: Visualizador,
        indicadores: list[Indicador],
    ) -> None:
        self.__titulo = titulo
        self.__analisador = analisador
        self.__visualizador = visualizador
        self.__indicadores = list(indicadores)
        self.__slides: list[Slide] = []

    @property
    def titulo(self) -> str:
        return self.__titulo

    @property
    def slides(self) -> tuple[Slide, ...]:
        """Slides na ordem de apresentação (somente leitura)."""
        return tuple(self.__slides)

    def adicionar_slide(self, slide: Slide) -> None:
        """Acrescenta um slide ao final da apresentação."""
        self.__slides.append(slide)

    def montar_slides(self) -> None:
        """Cria os slides de KPIs, gráficos, tabela e conclusões."""
        raise NotImplementedError("Implementado na Etapa 6")

    def gerar(self, caminho: str | Path) -> Path:
        """Grava a apresentação em um arquivo HTML e devolve o caminho."""
        raise NotImplementedError("Implementado na Etapa 6")

    def __len__(self) -> int:
        return len(self.__slides)
