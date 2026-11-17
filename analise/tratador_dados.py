"""Tratamento das séries antes da análise."""

from __future__ import annotations

import pandas as pd

from modelos.serie_temporal import SerieTemporal

METODOS_AUSENTES = ("interpolar", "remover")


class TratadorDados:
    """Prepara uma série para análise.

    Remove registros sem data válida e datas duplicadas, completa os
    meses que faltam no intervalo e trata os valores ausentes. Cada
    série tratada gera uma linha no relatório de tratamento.
    """

    def __init__(self, metodo_ausentes: str = "interpolar") -> None:
        """Cria o tratador.

        Args:
            metodo_ausentes: "interpolar" preenche cada valor ausente
                com base nos meses vizinhos; "remover" descarta o mês.

        Raises:
            ValueError: se o método não for um dos aceitos.
        """
        if metodo_ausentes not in METODOS_AUSENTES:
            raise ValueError(
                f"Método inválido: {metodo_ausentes}. "
                f"Use um destes: {', '.join(METODOS_AUSENTES)}"
            )
        self.__metodo = metodo_ausentes
        self.__relatorio: list[dict] = []

    @property
    def metodo_ausentes(self) -> str:
        return self.__metodo

    @property
    def relatorio(self) -> pd.DataFrame:
        """O que foi feito em cada série tratada."""
        return pd.DataFrame(self.__relatorio)

    def remover_datas_invalidas(self, dados: pd.DataFrame) -> pd.DataFrame:
        """Descarta registros sem data, que não podem ser posicionados."""
        return dados.dropna(subset=["data"])

    def remover_duplicadas(self, dados: pd.DataFrame) -> pd.DataFrame:
        """Mantém um registro por mês: o último que aparece no arquivo."""
        return dados.drop_duplicates(subset="data", keep="last")

    def completar_meses(self, dados: pd.DataFrame) -> pd.DataFrame:
        """Inclui os meses que faltam no intervalo, com valor ausente."""
        indexado = dados.set_index("data").sort_index()
        todos = pd.date_range(indexado.index.min(), indexado.index.max(),
                              freq="MS", name="data")
        return indexado.reindex(todos).reset_index()

    def tratar_ausentes(self, dados: pd.DataFrame) -> pd.DataFrame:
        """Interpola ou remove os valores ausentes, conforme o método."""
        if self.__metodo == "remover":
            return dados.dropna(subset=["valor"])
        tratado = dados.set_index("data")
        tratado["valor"] = tratado["valor"].interpolate(
            method="time", limit_direction="both"
        )
        return tratado.reset_index()

    def tratar(self, serie: SerieTemporal) -> SerieTemporal:
        """Aplica todas as etapas e devolve uma nova série tratada.

        A série original não é alterada.
        """
        dados = serie.dados
        validos = self.remover_datas_invalidas(dados)
        sem_duplicadas = self.remover_duplicadas(validos)
        completos = self.completar_meses(sem_duplicadas)
        ausentes = int(completos["valor"].isna().sum())
        tratados = self.tratar_ausentes(completos)
        tratados = tratados.sort_values("data").reset_index(drop=True)

        self.__relatorio.append({
            "serie": serie.codigo,
            "registros_originais": len(dados),
            "datas_invalidas": len(dados) - len(validos),
            "duplicadas_removidas": len(validos) - len(sem_duplicadas),
            "meses_incluidos": len(completos) - len(sem_duplicadas),
            "ausentes_tratados": ausentes,
            "metodo": self.__metodo,
            "registros_finais": len(tratados),
        })
        return SerieTemporal(serie.codigo, serie.nome, serie.unidade, tratados)
