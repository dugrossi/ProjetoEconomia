"""Representação de uma série temporal do Banco Central."""

from __future__ import annotations

import pandas as pd

from modelos.excecoes import SerieInvalidaError


class SerieTemporal:
    """Série temporal do SGS com seus metadados e valores.

    Os valores ficam em um DataFrame com as colunas "data"
    (datetime) e "valor" (float).
    """

    COLUNAS = ["data", "valor"]

    def __init__(
        self, codigo: int, nome: str, unidade: str, dados: pd.DataFrame
    ) -> None:
        """Cria a série validando o formato dos dados.

        Raises:
            SerieInvalidaError: se faltar a coluna "data" ou "valor".
        """
        faltando = [c for c in self.COLUNAS if c not in dados.columns]
        if faltando:
            raise SerieInvalidaError(
                f"Série {codigo} sem as colunas: {', '.join(faltando)}"
            )
        self.__codigo = codigo
        self.__nome = nome
        self.__unidade = unidade
        self.__dados = dados[self.COLUNAS].copy()

    @property
    def codigo(self) -> int:
        """Código da série no SGS."""
        return self.__codigo

    @property
    def nome(self) -> str:
        """Nome descritivo da série."""
        return self.__nome

    @property
    def unidade(self) -> str:
        """Unidade de medida dos valores."""
        return self.__unidade

    @property
    def dados(self) -> pd.DataFrame:
        """Cópia dos dados, para que não sejam alterados por fora."""
        return self.__dados.copy()

    def __len__(self) -> int:
        return len(self.__dados)

    def __str__(self) -> str:
        return f"[{self.__codigo}] {self.__nome} ({self.__unidade})"
