"""Fonte que tenta uma origem principal e recorre a uma reserva."""

import pandas as pd

from fontes.fonte_dados import FonteDados
from modelos.excecoes import FonteDadosError


class FonteComReserva(FonteDados):
    """Combina duas fontes: usa a principal e, se ela falhar, a reserva.

    Exemplo: ``FonteComReserva(FonteCSV("dados/brutos"), FonteAPIBCB())``
    lê o CSV e só consulta a API se o arquivo não existir.
    """

    def __init__(self, principal: FonteDados, reserva: FonteDados) -> None:
        self.__principal = principal
        self.__reserva = reserva

    def carregar(self, codigo: int) -> pd.DataFrame:
        """Carrega da principal ou, em caso de falha, da reserva.

        Raises:
            FonteDadosError: se as duas fontes falharem.
        """
        try:
            return self.__principal.carregar(codigo)
        except FonteDadosError:
            return self.__reserva.carregar(codigo)
