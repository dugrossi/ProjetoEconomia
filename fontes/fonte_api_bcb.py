"""Fonte que consulta a API pública do SGS do Banco Central."""

import json
from urllib.error import URLError
from urllib.request import urlopen

import pandas as pd

from fontes.fonte_dados import FonteDados
from modelos.excecoes import FonteDadosError


class FonteAPIBCB(FonteDados):
    """Busca a série na API do SGS, que devolve uma lista JSON de
    registros no formato ``{"data": "01/03/2011", "valor": "3.17"}``.
    """

    URL = (
        "https://api.bcb.gov.br/dados/serie/"
        "bcdata.sgs.{codigo}/dados?formato=json"
    )

    def __init__(self, timeout: int = 30) -> None:
        self.__timeout = timeout

    def carregar(self, codigo: int) -> pd.DataFrame:
        """Consulta a API e padroniza os tipos.

        Raises:
            FonteDadosError: se a API estiver fora do ar, sem internet
                ou devolver algo que não seja a lista esperada.
        """
        url = self.URL.format(codigo=codigo)
        try:
            with urlopen(url, timeout=self.__timeout) as resposta:
                registros = json.load(resposta)
            return self._padronizar(pd.DataFrame(registros), decimal=".")
        except (URLError, TimeoutError) as erro:
            raise FonteDadosError(
                f"Não foi possível acessar a API para a série {codigo}"
            ) from erro
        except (ValueError, KeyError) as erro:
            raise FonteDadosError(
                f"Resposta inesperada da API para a série {codigo}"
            ) from erro
