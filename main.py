"""Ponto de entrada: monta os objetos do sistema e mostra os resultados."""

import pandas as pd

from analise.analisador_dados import AnalisadorDados
from config import PASTA_DADOS_BRUTOS, SERIES
from dashboard.dashboard_html import DashboardHTML
from fontes.fonte_api_bcb import FonteAPIBCB
from fontes.fonte_com_reserva import FonteComReserva
from fontes.fonte_csv import FonteCSV
from fontes.fonte_dados import FonteDados
from indicadores.defasagem_correlacao import DefasagemCorrelacao
from indicadores.indicador import Indicador
from indicadores.indicadores_serie import (
    DistanciaDaMedia,
    PercentilHistorico,
    ValorAtual,
    Variacao12Meses,
)
from modelos.excecoes import FonteDadosError
from modelos.serie_temporal import SerieTemporal
from visualizacao.visualizador import Visualizador

INADIMPLENCIA = 21082
JUROS = 25433


def carregar_series(fonte: FonteDados) -> list[SerieTemporal]:
    """Carrega todas as séries de ``config.SERIES`` a partir da fonte."""
    return [
        SerieTemporal(codigo, nome, unidade, fonte.carregar(codigo))
        for codigo, (nome, unidade) in SERIES.items()
    ]


def criar_indicadores() -> list[Indicador]:
    """Indicadores exibidos no dashboard."""
    return [
        ValorAtual(
            INADIMPLENCIA, "Inadimplência atual",
            "Inadimplência da carteira de crédito no último mês", "%",
        ),
        Variacao12Meses(
            INADIMPLENCIA, "Variação em 12 meses",
            "Diferença para o mesmo mês do ano anterior", " p.p.",
        ),
        DistanciaDaMedia(
            INADIMPLENCIA, "Distância da média",
            "Desvios padrão acima (+) ou abaixo (-) da média histórica",
            " desvios padrão",
        ),
        PercentilHistorico(
            INADIMPLENCIA, "Percentil histórico",
            "Meses do histórico com inadimplência menor que a atual", "%",
            casas_decimais=0,
        ),
        ValorAtual(
            JUROS, "Juros atual",
            "Taxa média mensal de juros do crédito no último mês", "% a.m.",
        ),
        DefasagemCorrelacao(
            JUROS, INADIMPLENCIA, "Defasagem dos juros",
            "Meses que a inadimplência leva para acompanhar os juros",
        ),
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
    mostrar("Qualidade dos dados", analisador.verificar_qualidade())
    mostrar(
        "Estatísticas descritivas",
        analisador.estatisticas_descritivas().round(2),
    )

    indicadores = criar_indicadores()
    resultados = analisador.calcular_indicadores(indicadores)
    mostrar("Indicadores", resultados[["indicador", "texto"]])

    # Visualizador e dashboard já fazem parte da estrutura; os gráficos
    # e a apresentação em HTML são implementados nas Etapas 5 e 6.
    dashboard = DashboardHTML(
        "Inadimplência e custo do crédito no Brasil",
        analisador,
        Visualizador(),
        indicadores,
    )
    print(f"\nDashboard criado: {dashboard.titulo}")


if __name__ == "__main__":
    main()
