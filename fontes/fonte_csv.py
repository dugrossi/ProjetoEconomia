"""Fonte que lê as séries de arquivos CSV baixados do Banco Central."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from fontes.fonte_dados import FonteDados
from modelos.excecoes import FonteDadosError


class FonteCSV(FonteDados):
    """Lê arquivos no formato do SGS: ``bcdata.sgs.<codigo>.csv``.

    O arquivo usa ";" como separador e "," como separador decimal.
    """

    def __init__(self, pasta: str | Path) -> None:
        self.__pasta = Path(pasta)

    @property
    def pasta(self) -> Path:
        """Pasta onde ficam os CSVs."""
        return self.__pasta

    def caminho(self, codigo: int) -> Path:
        """Caminho do arquivo da série ``codigo``."""
        return self.__pasta / f"bcdata.sgs.{codigo}.csv"

    def carregar(self, codigo: int) -> pd.DataFrame:
        """Lê o CSV da série e padroniza os tipos.

        Raises:
            FonteDadosError: se o arquivo não existir ou não tiver as
                colunas "data" e "valor".
        """
        try:
            brutos = pd.read_csv(self.caminho(codigo), sep=";", dtype=str)
            return self._padronizar(brutos, decimal=",")
        except FileNotFoundError as erro:
            raise FonteDadosError(
                f"Arquivo da série {codigo} não encontrado em {self.__pasta}"
            ) from erro
        except KeyError as erro:
            raise FonteDadosError(
                f"Arquivo da série {codigo} sem as colunas data/valor"
            ) from erro
