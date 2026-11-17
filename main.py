"""Ponto de entrada: monta os objetos do sistema e mostra os resultados."""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from analise.analisador_dados import (
    LIMITES_FAIXAS,
    NOMES_FAIXAS,
    AnalisadorDados,
)
from analise.tratador_dados import TratadorDados
from config import PASTA_DADOS_BRUTOS, PASTA_GRAFICOS, PERIODOS, SERIES
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


def descricoes_faixas() -> dict[str, str]:
    """Texto com os limites de cada faixa, para as dicas do treemap."""
    textos = {}
    for nome, inferior, superior in zip(NOMES_FAIXAS, LIMITES_FAIXAS,
                                        LIMITES_FAIXAS[1:]):
        if inferior == 0:
            textos[nome] = f"(abaixo de {superior:.2f}%)"
        elif superior == float("inf"):
            textos[nome] = f"({inferior:.2f}% ou mais)"
        else:
            textos[nome] = f"({inferior:.2f}% a {superior:.2f}%)"
    return textos


def criar_graficos(
    analisador: AnalisadorDados, visualizador: Visualizador
) -> dict[str, go.Figure]:
    """Os cinco gráficos do projeto, cada um com os dados do analisador."""
    inadimplencia = analisador.serie(INADIMPLENCIA)
    juros = analisador.serie(JUROS)
    anos = analisador.agrupar_por_ano(INADIMPLENCIA)
    correlacoes = analisador.correlacao_defasada(JUROS, INADIMPLENCIA,
                                                 range(25))
    media = inadimplencia.dados["valor"].mean()
    return {
        "linhas_evolucao": visualizador.grafico_linhas(
            analisador.tabela_unificada(),
            "Inadimplência e taxa média de juros do crédito",
            rotulos={INADIMPLENCIA: "Inadimplência", JUROS: "Juros"},
            unidades={INADIMPLENCIA: inadimplencia.unidade,
                      JUROS: juros.unidade},
            eixo_direito=JUROS,
        ),
        "barras_media_anual": visualizador.grafico_barras(
            anos["media"], "Média anual da inadimplência",
            rotulo_x="Ano", rotulo_y=inadimplencia.unidade,
            destaque=int(anos["media"].idxmax()),
            linha_referencia=(
                media, f"Média histórica: {media:.2f}%".replace(".", ",")
            ),
        ),
        "barras_defasagem": visualizador.grafico_barras(
            correlacoes,
            "Correlação entre inadimplência e juros de N meses antes",
            rotulo_x="Defasagem dos juros (meses)",
            rotulo_y="Correlação de Pearson",
            destaque=int(correlacoes.idxmax()),
        ),
        "treemap_faixas": visualizador.grafico_treemap(
            analisador.agrupar_por_faixa(INADIMPLENCIA)["meses"],
            "Meses por faixa de inadimplência",
            descricoes=descricoes_faixas(),
        ),
        "dispersao_juros_inadimplencia": visualizador.grafico_dispersao(
            analisador.dados_dispersao(JUROS, INADIMPLENCIA, 6, PERIODOS),
            "Juros de 6 meses antes x inadimplência",
            rotulo_x="Juros de 6 meses antes (% ao mês)",
            rotulo_y="Inadimplência (% da carteira)",
        ),
    }


def salvar_graficos(graficos: dict[str, go.Figure], pasta: Path) -> None:
    """Grava cada gráfico como um arquivo HTML interativo."""
    pasta.mkdir(parents=True, exist_ok=True)
    for nome, figura in graficos.items():
        figura.write_html(pasta / f"{nome}.html", include_plotlyjs=True)


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

    # Etapa 4: tratamento antes da análise
    tratador = TratadorDados(metodo_ausentes="interpolar")
    series = [tratador.tratar(serie) for serie in series]
    mostrar("Tratamento dos dados", tratador.relatorio)

    analisador = AnalisadorDados(series)
    mostrar("Qualidade dos dados", analisador.verificar_qualidade())
    mostrar(
        "Estatísticas descritivas",
        analisador.estatisticas_descritivas().round(2),
    )
    mostrar(
        "Inadimplência por período",
        analisador.estatisticas_por_periodo(INADIMPLENCIA, PERIODOS).round(2),
    )
    mostrar(
        "Correlação com juros de 6 meses antes, por período",
        analisador.correlacao_por_periodo(JUROS, INADIMPLENCIA, 6, PERIODOS)
        .round(2).to_frame(),
    )
    mostrar(
        "Inadimplência por ano (do maior para o menor)",
        analisador.ranking_anos(INADIMPLENCIA).round(2),
    )
    mostrar(
        "Meses por faixa de inadimplência",
        analisador.agrupar_por_faixa(INADIMPLENCIA).round({"percentual": 1}),
    )
    mostrar(
        "Os 10 meses de maior inadimplência",
        analisador.ranking_meses(INADIMPLENCIA, 10),
    )
    acima = analisador.meses_acima_de(INADIMPLENCIA, 4.0)
    print(f"\nMeses com inadimplência acima de 4%: {len(acima)}")

    indicadores = criar_indicadores()
    resultados = analisador.calcular_indicadores(indicadores)
    mostrar("Indicadores", resultados[["indicador", "texto"]])

    # Etapa 5: gráficos interativos
    visualizador = Visualizador()
    graficos = criar_graficos(analisador, visualizador)
    salvar_graficos(graficos, PASTA_GRAFICOS)
    print(f"\n{len(graficos)} gráficos salvos em {PASTA_GRAFICOS}")

    # A apresentação em HTML é implementada na Etapa 6.
    dashboard = DashboardHTML(
        "Inadimplência e custo do crédito no Brasil",
        analisador,
        visualizador,
        indicadores,
    )
    print(f"\nDashboard criado: {dashboard.titulo}")


if __name__ == "__main__":
    main()
