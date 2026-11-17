"""Contrato comum a todos os indicadores do dashboard."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from analise.analisador_dados import AnalisadorDados


class Indicador(ABC):
    """Classe abstrata para qualquer indicador (KPI) do projeto.

    Todo indicador sabe se calcular a partir de um ``AnalisadorDados``
    e se apresentar como texto. Quem usa os indicadores só chama
    ``calcular()`` e ``formatar()``, sem saber qual indicador é.
    """

    def __init__(
        self, nome: str, descricao: str, sufixo: str, casas_decimais: int = 2
    ) -> None:
        self.__nome = nome
        self.__descricao = descricao
        self.__sufixo = sufixo
        self.__casas_decimais = casas_decimais

    @property
    def nome(self) -> str:
        """Nome curto do indicador, exibido no card do dashboard."""
        return self.__nome

    @property
    def descricao(self) -> str:
        """Explicação do que o indicador mede."""
        return self.__descricao

    @abstractmethod
    def calcular(self, analisador: AnalisadorDados) -> float:
        """Calcula o valor do indicador com os dados do analisador."""

    def formatar(self, valor: float) -> str:
        """Formata o valor no padrão brasileiro, com o sufixo da unidade.

        Exemplo: ``5.05`` com sufixo ``"%"`` vira ``"5,05%"``.
        """
        numero = f"{valor:.{self.__casas_decimais}f}".replace(".", ",")
        return f"{numero}{self.__sufixo}"

    def __str__(self) -> str:
        return self.__nome


class IndicadorDeSerie(Indicador):
    """Indicador calculado sobre uma única série temporal."""

    def __init__(
        self,
        codigo_serie: int,
        nome: str,
        descricao: str,
        sufixo: str,
        casas_decimais: int = 2,
    ) -> None:
        super().__init__(nome, descricao, sufixo, casas_decimais)
        self.__codigo_serie = codigo_serie

    @property
    def codigo_serie(self) -> int:
        """Código SGS da série usada no cálculo."""
        return self.__codigo_serie

    def _valores(self, analisador: AnalisadorDados) -> pd.Series:
        """Valores da série, indexados pela data, sem ausentes e em ordem."""
        dados = analisador.serie(self.__codigo_serie).dados
        return dados.dropna().set_index("data")["valor"].sort_index()
