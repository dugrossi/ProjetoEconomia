"""Contrato comum a todas as fontes de dados."""

from abc import ABC, abstractmethod

import pandas as pd


class FonteDados(ABC):
    """Classe abstrata para qualquer origem de séries do SGS.

    Toda fonte devolve um DataFrame com as colunas "data" (datetime)
    e "valor" (float), não importa de onde os dados vieram.
    """

    @abstractmethod
    def carregar(self, codigo: int) -> pd.DataFrame:
        """Carrega a série de código ``codigo``.

        Raises:
            FonteDadosError: se a fonte não conseguir entregar a série.
        """

    @staticmethod
    def _padronizar(dados: pd.DataFrame, decimal: str) -> pd.DataFrame:
        """Converte "data" e "valor" para os tipos certos.

        Valores que não puderem ser convertidos viram NaN/NaT, para
        serem contados na verificação de qualidade, em vez de
        interromper a leitura.
        """
        resultado = pd.DataFrame()
        resultado["data"] = pd.to_datetime(
            dados["data"], format="%d/%m/%Y", errors="coerce"
        )
        valores = dados["valor"].astype(str).str.strip()
        if decimal == ",":
            valores = valores.str.replace(",", ".", regex=False)
        resultado["valor"] = pd.to_numeric(valores, errors="coerce")
        return resultado
