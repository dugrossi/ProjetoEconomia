"""Indicadores calculados sobre uma série: nível, variação e posição
em relação ao histórico."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from indicadores.indicador import IndicadorDeSerie

if TYPE_CHECKING:
    from analise.analisador_dados import AnalisadorDados


class ValorAtual(IndicadorDeSerie):
    """Valor do mês mais recente da série."""

    def calcular(self, analisador: AnalisadorDados) -> float:
        return float(self._valores(analisador).iloc[-1])


class Variacao12Meses(IndicadorDeSerie):
    """Diferença entre o último mês e o mesmo mês do ano anterior.

    Para séries em %, o resultado é em pontos percentuais (p.p.).
    """

    def calcular(self, analisador: AnalisadorDados) -> float:
        valores = self._valores(analisador)
        ultimo_mes = valores.index[-1]
        ano_anterior = ultimo_mes - pd.DateOffset(years=1)
        return float(valores.iloc[-1] - valores.loc[ano_anterior])


class DistanciaDaMedia(IndicadorDeSerie):
    """Quantos desvios padrão o último valor está acima (positivo) ou
    abaixo (negativo) da média histórica."""

    def calcular(self, analisador: AnalisadorDados) -> float:
        valores = self._valores(analisador)
        return float((valores.iloc[-1] - valores.mean()) / valores.std())


class PercentilHistorico(IndicadorDeSerie):
    """Percentual dos meses do histórico com valor menor que o atual.

    100% significa que o valor atual é o maior da série.
    """

    def calcular(self, analisador: AnalisadorDados) -> float:
        valores = self._valores(analisador)
        anteriores = valores.iloc[:-1]
        return float((anteriores < valores.iloc[-1]).mean() * 100)
