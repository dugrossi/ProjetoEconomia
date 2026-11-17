"""Exploração e análise das séries temporais."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

import pandas as pd

from modelos.serie_temporal import SerieTemporal

if TYPE_CHECKING:
    from indicadores.indicador import Indicador

# Faixas de inadimplência (% da carteira). Cada faixa inclui o limite
# inferior e exclui o superior: 2,75% já é "Moderada".
LIMITES_FAIXAS = [0, 2.75, 3.25, 3.75, 4.25, float("inf")]
NOMES_FAIXAS = ["Baixa", "Moderada", "Alta", "Muito alta", "Crítica"]


class AnalisadorDados:
    """Reúne as séries do projeto e oferece as análises sobre elas.

    Concentra a exploração (tipos, qualidade, estatísticas), as
    análises entre séries e o cálculo dos indicadores.
    """

    def __init__(self, series: list[SerieTemporal]) -> None:
        self.__series = {serie.codigo: serie for serie in series}

    @property
    def series(self) -> list[SerieTemporal]:
        """Séries carregadas no analisador."""
        return list(self.__series.values())

    def serie(self, codigo: int) -> SerieTemporal:
        """Devolve a série de código ``codigo``.

        Raises:
            KeyError: se a série não estiver no analisador.
        """
        return self.__series[codigo]

    def descrever_variaveis(self) -> pd.DataFrame:
        """Lista as variáveis de cada série, com tipo e unidade."""
        linhas = []
        for serie in self.series:
            for coluna, tipo in serie.dados.dtypes.items():
                linhas.append({
                    "serie": serie.codigo,
                    "variavel": coluna,
                    "tipo": str(tipo),
                    "descricao": (
                        "Mês de referência" if coluna == "data"
                        else f"{serie.nome} ({serie.unidade})"
                    ),
                })
        return pd.DataFrame(linhas)

    def verificar_qualidade(self) -> pd.DataFrame:
        """Conta problemas de qualidade em cada série.

        Verifica valores ausentes (inclusive os que não puderam ser
        convertidos para número ou data), datas duplicadas, meses
        faltando no intervalo e valores negativos, que não fazem
        sentido para taxas e percentuais.
        """
        linhas = []
        for serie in self.series:
            dados = serie.dados
            datas = dados["data"].dropna()
            esperados = pd.date_range(datas.min(), datas.max(), freq="MS")
            linhas.append({
                "serie": serie.codigo,
                "registros": len(dados),
                "inicio": datas.min().date(),
                "fim": datas.max().date(),
                "datas_ausentes": int(dados["data"].isna().sum()),
                "valores_ausentes": int(dados["valor"].isna().sum()),
                "datas_duplicadas": int(datas.duplicated().sum()),
                "meses_faltando": len(esperados.difference(datas)),
                "valores_negativos": int((dados["valor"] < 0).sum()),
            })
        return pd.DataFrame(linhas)

    def estatisticas_descritivas(self) -> pd.DataFrame:
        """Estatísticas descritivas do valor de cada série."""
        tabela = pd.DataFrame({
            serie.codigo: serie.dados["valor"].describe()
            for serie in self.series
        })
        return tabela.T

    def extremos(self) -> pd.DataFrame:
        """Mês e valor do máximo e do mínimo de cada série."""
        linhas = []
        for serie in self.series:
            dados = serie.dados.dropna()
            maximo = dados.loc[dados["valor"].idxmax()]
            minimo = dados.loc[dados["valor"].idxmin()]
            linhas.append({
                "serie": serie.codigo,
                "maximo": maximo["valor"],
                "mes_maximo": maximo["data"].date(),
                "minimo": minimo["valor"],
                "mes_minimo": minimo["data"].date(),
            })
        return pd.DataFrame(linhas)

    def tabela_unificada(self) -> pd.DataFrame:
        """Junta as séries em uma tabela com uma coluna por série.

        As linhas são os meses; cada coluna leva o código da série.
        """
        colunas = {
            serie.codigo: serie.dados.set_index("data")["valor"]
            for serie in self.series
        }
        return pd.DataFrame(colunas).sort_index()

    def medias_anuais(self) -> pd.DataFrame:
        """Média de cada série por ano."""
        tabela = self.tabela_unificada()
        return tabela.groupby(tabela.index.year).mean()

    # --- Seleção e filtragem -------------------------------------------

    def filtrar_periodo(self, inicio: str, fim: str) -> AnalisadorDados:
        """Novo analisador só com os meses entre ``inicio`` e ``fim``.

        As datas são incluídas nos dois extremos. O analisador original
        não muda, então dá para comparar períodos lado a lado.
        """
        inicio_ts, fim_ts = pd.Timestamp(inicio), pd.Timestamp(fim)
        recortes = []
        for serie in self.series:
            dados = serie.dados
            no_periodo = dados[dados["data"].between(inicio_ts, fim_ts)]
            recortes.append(
                SerieTemporal(serie.codigo, serie.nome, serie.unidade,
                              no_periodo.reset_index(drop=True))
            )
        return AnalisadorDados(recortes)

    def meses_acima_de(self, codigo: int, limite: float) -> pd.DataFrame:
        """Meses em que a série ficou acima do limite, em ordem de data."""
        dados = self.serie(codigo).dados
        return dados[dados["valor"] > limite].reset_index(drop=True)

    # --- Agrupamentos --------------------------------------------------

    def agrupar_por_ano(self, codigo: int) -> pd.DataFrame:
        """Média, mínimo, máximo, desvio padrão e meses de cada ano."""
        dados = self.serie(codigo).dados
        return (
            dados.groupby(dados["data"].dt.year)["valor"]
            .agg(media="mean", minimo="min", maximo="max",
                 desvio="std", meses="count")
            .rename_axis("ano")
        )

    def classificar_faixas(self, codigo: int) -> pd.DataFrame:
        """Acrescenta a cada mês a faixa em que o valor se encaixa."""
        dados = self.serie(codigo).dados
        dados["faixa"] = pd.cut(dados["valor"], bins=LIMITES_FAIXAS,
                                labels=NOMES_FAIXAS, right=False)
        return dados

    def agrupar_por_faixa(self, codigo: int) -> pd.DataFrame:
        """Quantos meses caíram em cada faixa, e quando.

        Faixas sem nenhum mês aparecem com zero, para a tabela ter
        sempre as cinco faixas.
        """
        classificados = self.classificar_faixas(codigo)
        grupos = classificados.groupby("faixa", observed=False)
        tabela = grupos.agg(
            meses=("valor", "count"),
            primeiro_mes=("data", "min"),
            ultimo_mes=("data", "max"),
        )
        tabela["percentual"] = tabela["meses"] / tabela["meses"].sum() * 100
        return tabela

    # --- Ordenação -----------------------------------------------------

    def ranking_meses(
        self, codigo: int, n: int = 10, maiores: bool = True
    ) -> pd.DataFrame:
        """Os ``n`` meses de maior (ou menor) valor da série."""
        dados = self.serie(codigo).dados.dropna()
        ordenados = dados.sort_values("valor", ascending=not maiores)
        return ordenados.head(n).reset_index(drop=True)

    def ranking_anos(self, codigo: int) -> pd.DataFrame:
        """Os anos ordenados da maior para a menor média."""
        return self.agrupar_por_ano(codigo).sort_values("media",
                                                        ascending=False)

    # --- Estatísticas por período --------------------------------------

    def estatisticas_por_periodo(
        self, codigo: int, periodos: dict[str, tuple[str, str]]
    ) -> pd.DataFrame:
        """Estatísticas descritivas da série em cada período."""
        tabela = {}
        for nome, (inicio, fim) in periodos.items():
            recorte = self.filtrar_periodo(inicio, fim).serie(codigo)
            tabela[nome] = recorte.dados["valor"].describe()
        return pd.DataFrame(tabela).T

    def correlacao_por_periodo(
        self,
        codigo_causa: int,
        codigo_efeito: int,
        defasagem: int,
        periodos: dict[str, tuple[str, str]],
    ) -> pd.Series:
        """Correlação com defasagem calculada separadamente por período.

        A defasagem é aplicada na série inteira antes do recorte, para
        os primeiros meses de cada período usarem os juros dos meses
        anteriores, mesmo que fiquem fora do período.
        """
        tabela = self.tabela_unificada()
        pares = pd.DataFrame({
            "efeito": tabela[codigo_efeito],
            "causa": tabela[codigo_causa].shift(defasagem),
        }).dropna()
        resultado = {}
        for nome, (inicio, fim) in periodos.items():
            recorte = pares.loc[inicio:fim]
            resultado[nome] = recorte["efeito"].corr(recorte["causa"])
        return pd.Series(resultado, name="correlacao")

    def correlacao(self) -> pd.DataFrame:
        """Correlação de Pearson entre as séries, no mesmo mês."""
        return self.tabela_unificada().corr()

    def correlacao_defasada(
        self, codigo_causa: int, codigo_efeito: int, defasagens: Iterable[int]
    ) -> pd.Series:
        """Correlação entre o efeito de cada mês e a causa N meses antes.

        Devolve uma série com a defasagem N no índice e a correlação
        de Pearson como valor.
        """
        tabela = self.tabela_unificada()
        causa = tabela[codigo_causa]
        efeito = tabela[codigo_efeito]
        correlacoes = {n: efeito.corr(causa.shift(n)) for n in defasagens}
        return pd.Series(correlacoes, name="correlacao")

    def calcular_indicadores(
        self, indicadores: list[Indicador]
    ) -> pd.DataFrame:
        """Calcula uma lista de indicadores, de qualquer tipo.

        Cada indicador sabe se calcular (polimorfismo): o analisador só
        chama ``calcular()`` e ``formatar()`` em cada um.
        """
        linhas = []
        for indicador in indicadores:
            valor = indicador.calcular(self)
            linhas.append({
                "indicador": indicador.nome,
                "valor": valor,
                "texto": indicador.formatar(valor),
                "descricao": indicador.descricao,
            })
        return pd.DataFrame(linhas)
