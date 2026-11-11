"""Exploração e análise das séries temporais."""

from __future__ import annotations

import pandas as pd

from modelos.serie_temporal import SerieTemporal


class AnalisadorDados:
    """Reúne as séries do projeto e oferece as análises sobre elas.

    Nesta etapa (Etapa 2) concentra a exploração inicial: tipos das
    variáveis, qualidade dos dados e estatísticas descritivas.
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

    def correlacao(self) -> pd.DataFrame:
        """Correlação de Pearson entre as séries, no mesmo mês."""
        return self.tabela_unificada().corr()
