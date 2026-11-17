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


class TestAnalisadorEtapa4(unittest.TestCase):
    def setUp(self):
        # 2023: 2, 3, 4 (jan-mar) | 2024: 5, 6 (jan-fev)
        datas = ["2023-01-01", "2023-02-01", "2023-03-01",
                 "2024-01-01", "2024-02-01"]
        self.analisador = AnalisadorDados(
            [criar_serie(1, datas, [2.0, 3.0, 4.0, 5.0, 6.0])]
        )

    def test_filtrar_periodo_inclui_os_extremos(self):
        recorte = self.analisador.filtrar_periodo("2023-02-01", "2024-01-01")

        valores = list(recorte.serie(1).dados["valor"])

        self.assertEqual(valores, [3.0, 4.0, 5.0])
        self.assertEqual(len(self.analisador.serie(1)), 5)

    def test_meses_acima_do_limite(self):
        acima = self.analisador.meses_acima_de(1, 4.0)

        self.assertEqual(list(acima["valor"]), [5.0, 6.0])

    def test_agrupar_por_ano(self):
        anos = self.analisador.agrupar_por_ano(1)

        self.assertEqual(anos.loc[2023, "media"], 3.0)
        self.assertEqual(anos.loc[2024, "maximo"], 6.0)
        self.assertEqual(anos.loc[2023, "meses"], 3)

    def test_ranking_de_anos_ordena_pela_media(self):
        ranking = self.analisador.ranking_anos(1)

        self.assertEqual(list(ranking.index), [2024, 2023])

    def test_ranking_de_meses(self):
        maiores = self.analisador.ranking_meses(1, n=2)
        menores = self.analisador.ranking_meses(1, n=1, maiores=False)

        self.assertEqual(list(maiores["valor"]), [6.0, 5.0])
        self.assertEqual(menores.loc[0, "valor"], 2.0)

    def test_limite_da_faixa_pertence_a_faixa_de_cima(self):
        analisador = AnalisadorDados([criar_serie(
            1, ["2024-01-01", "2024-02-01", "2024-03-01"], [2.74, 2.75, 4.25]
        )])

        faixas = list(analisador.classificar_faixas(1)["faixa"])

        self.assertEqual(faixas, ["Baixa", "Moderada", "Crítica"])

    def test_agrupar_por_faixa_mostra_faixas_vazias(self):
        tabela = self.analisador.agrupar_por_faixa(1)

        self.assertEqual(len(tabela), 5)
        self.assertEqual(tabela.loc["Baixa", "meses"], 1)
        self.assertEqual(tabela.loc["Moderada", "meses"], 1)
        self.assertEqual(tabela.loc["Alta", "meses"], 0)
        self.assertAlmostEqual(tabela["percentual"].sum(), 100.0)

    def test_estatisticas_por_periodo(self):
        periodos = {"A": ("2023-01-01", "2023-12-31"),
                    "B": ("2024-01-01", "2024-12-31")}

        tabela = self.analisador.estatisticas_por_periodo(1, periodos)

        self.assertEqual(tabela.loc["A", "mean"], 3.0)
        self.assertEqual(tabela.loc["B", "count"], 2)

    def test_correlacao_por_periodo_usa_defasagem_de_antes_do_recorte(self):
        # O efeito repete a causa com 1 mês de atraso
        datas = pd.date_range("2023-01-01", periods=8, freq="MS")
        causa = [1.0, 3.0, 2.0, 5.0, 4.0, 6.0, 5.0, 8.0]
        efeito = [0.0] + causa[:-1]
        analisador = AnalisadorDados([
            criar_serie(10, datas, causa), criar_serie(20, datas, efeito)
        ])

        resultado = analisador.correlacao_por_periodo(
            10, 20, 1, {"segunda metade": ("2023-05-01", "2023-08-01")}
        )

        self.assertAlmostEqual(resultado["segunda metade"], 1.0)

    def test_dados_dispersao_pareia_causa_defasada_com_efeito(self):
        datas = pd.date_range("2023-01-01", periods=4, freq="MS")
        analisador = AnalisadorDados([
            criar_serie(10, datas, [1.0, 2.0, 3.0, 4.0]),
            criar_serie(20, datas, [5.0, 6.0, 7.0, 8.0]),
        ])

        pares = analisador.dados_dispersao(
            10, 20, 1, {"todo": ("2023-01-01", "2023-12-31")}
        )

        # fevereiro (efeito 6) usa a causa de janeiro (1)
        self.assertEqual(len(pares), 3)
        self.assertEqual(pares.loc[0, "x"], 1.0)
        self.assertEqual(pares.loc[0, "y"], 6.0)
        self.assertEqual(str(pares.loc[0, "data"].date()), "2023-02-01")
        self.assertEqual(set(pares["grupo"]), {"todo"})

if __name__ == "__main__":
    unittest.main()
