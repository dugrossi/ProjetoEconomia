"""Ponto de entrada: carrega as séries e mostra a exploração inicial."""

import pandas as pd

from analise.analisador_dados import AnalisadorDados
from config import PASTA_DADOS_BRUTOS, SERIES
from fontes.fonte_api_bcb import FonteAPIBCB
from fontes.fonte_com_reserva import FonteComReserva
from fontes.fonte_csv import FonteCSV
from fontes.fonte_dados import FonteDados
from modelos.excecoes import FonteDadosError
from modelos.serie_temporal import SerieTemporal


def carregar_series(fonte: FonteDados) -> list[SerieTemporal]:
    """Carrega todas as séries de ``config.SERIES`` a partir da fonte."""
    return [
        SerieTemporal(codigo, nome, unidade, fonte.carregar(codigo))
        for codigo, (nome, unidade) in SERIES.items()
    ]


def mostrar(titulo: str, tabela: pd.DataFrame) -> None:
    """Imprime uma tabela com um título."""
    print(f"\n=== {titulo} ===")
    print(tabela.to_string())


def main() -> None:
    fonte = FonteComReserva(FonteCSV(PASTA_DADOS_BRUTOS), FonteAPIBCB())
    try:
        series = carregar_series(fonte)
    except FonteDadosError as erro:
        print(f"Erro ao carregar os dados: {erro}")
        return

    for serie in series:
        print(f"{serie} - {len(serie)} registros")

    analisador = AnalisadorDados(series)
    mostrar("Variáveis", analisador.descrever_variaveis())
    mostrar("Qualidade dos dados", analisador.verificar_qualidade())
    mostrar(
        "Estatísticas descritivas",
        analisador.estatisticas_descritivas().round(2),
    )
    mostrar("Máximos e mínimos", analisador.extremos())
    mostrar("Médias anuais", analisador.medias_anuais().round(2))
    mostrar("Correlação no mesmo mês", analisador.correlacao().round(3))


if __name__ == "__main__":
    main()
