import unittest

import numpy as np
import pandas as pd

from analise.analisador_dados import AnalisadorDados
from modelos.serie_temporal import SerieTemporal


def criar_serie(codigo, datas, valores):
    dados = pd.DataFrame({"data": pd.to_datetime(datas), "valor": valores})
    return SerieTemporal(codigo, f"Série {codigo}", "%", dados)


class TestAnalisadorDados(unittest.TestCase):
    def test_qualidade_conta_problemas(self):
        # Arrange: mês duplicado, março faltando, um valor ausente
        # e um negativo
        serie = criar_serie(
            1,
            ["2024-01-01", "2024-01-01", "2024-02-01", "2024-04-01"],
            [1.0, 1.0, np.nan, -2.0],
        )
        analisador = AnalisadorDados([serie])

        # Act
        qualidade = analisador.verificar_qualidade().iloc[0]

        # Assert
        self.assertEqual(qualidade["datas_duplicadas"], 1)
        self.assertEqual(qualidade["meses_faltando"], 1)
        self.assertEqual(qualidade["valores_ausentes"], 1)
        self.assertEqual(qualidade["valores_negativos"], 1)

    def test_tabela_unificada_alinha_pelas_datas(self):
        serie_a = criar_serie(1, ["2024-01-01", "2024-02-01"], [1.0, 2.0])
        serie_b = criar_serie(2, ["2024-02-01", "2024-03-01"], [5.0, 6.0])
        analisador = AnalisadorDados([serie_a, serie_b])

        tabela = analisador.tabela_unificada()

        self.assertEqual(len(tabela), 3)
        self.assertEqual(tabela.loc["2024-02-01", 2], 5.0)
        self.assertTrue(pd.isna(tabela.loc["2024-03-01", 1]))

    def test_extremos_trazem_mes_do_maximo(self):
        serie = criar_serie(
            1, ["2024-01-01", "2024-02-01", "2024-03-01"], [2.0, 9.0, 1.0]
        )
        analisador = AnalisadorDados([serie])

        extremos = analisador.extremos().iloc[0]

        self.assertEqual(extremos["maximo"], 9.0)
        self.assertEqual(str(extremos["mes_maximo"]), "2024-02-01")
        self.assertEqual(extremos["minimo"], 1.0)


if __name__ == "__main__":
    unittest.main()
