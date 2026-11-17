"""Indicador que relaciona duas séries com defasagem no tempo."""

from __future__ import annotations

from typing import TYPE_CHECKING

from indicadores.indicador import Indicador

if TYPE_CHECKING:
    from analise.analisador_dados import AnalisadorDados


class DefasagemCorrelacao(Indicador):
    """Com quantos meses de atraso uma série acompanha a outra.

    Compara a série ``codigo_efeito`` de cada mês com a série
    ``codigo_causa`` de N meses antes e devolve o N de maior correlação.
    No projeto: a inadimplência acompanha os juros com quantos meses?
    """

    def __init__(
        self,
        codigo_causa: int,
        codigo_efeito: int,
        nome: str,
        descricao: str,
        defasagem_maxima: int = 24,
    ) -> None:
        super().__init__(nome, descricao, sufixo=" meses", casas_decimais=0)
        self.__codigo_causa = codigo_causa
        self.__codigo_efeito = codigo_efeito
        self.__defasagem_maxima = defasagem_maxima

    def calcular(self, analisador: AnalisadorDados) -> float:
        return float(self.correlacoes(analisador).idxmax())

    def correlacao_maxima(self, analisador: AnalisadorDados) -> float:
        """Correlação obtida na melhor defasagem."""
        return float(self.correlacoes(analisador).max())

    def correlacoes(self, analisador: AnalisadorDados):
        """Correlação para cada defasagem, de 0 até a máxima."""
        return analisador.correlacao_defasada(
            self.__codigo_causa,
            self.__codigo_efeito,
            range(self.__defasagem_maxima + 1),
        )
