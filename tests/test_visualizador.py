import unittest

import pandas as pd
import plotly.graph_objects as go

from visualizacao.visualizador import TEMA_PADRAO, Visualizador


class TestVisualizador(unittest.TestCase):
    def setUp(self):
        self.visualizador = Visualizador()
        self.datas = pd.date_range("2024-01-01", periods=3, freq="MS")

    def test_linhas_desenha_cada_serie_com_seus_valores(self):
        tabela = pd.DataFrame({1: [3.0, 3.1, 3.2], 2: [2.0, 2.1, 2.2]},
                              index=self.datas)

        figura = self.visualizador.grafico_linhas(
            tabela, "Teste", rotulos={1: "A", 2: "B"},
            unidades={1: "%", 2: "% a.m."}, eixo_direito=2,
        )

        self.assertIsInstance(figura, go.Figure)
        self.assertEqual(len(figura.data), 2)
        self.assertEqual(list(figura.data[0].y), [3.0, 3.1, 3.2])
        self.assertEqual(figura.data[0].yaxis, "y")
        self.assertEqual(figura.data[1].yaxis, "y2")
        self.assertEqual(figura.layout.yaxis2.title.text, "% a.m.")

    def test_barras_destacam_a_categoria_pedida(self):
        valores = pd.Series([2.0, 5.0, 3.0], index=[2022, 2023, 2024])

        figura = self.visualizador.grafico_barras(
            valores, "Teste", "Ano", "%", destaque=2023,
            linha_referencia=(3.3, "Média"),
        )

        barra = figura.data[0]
        self.assertEqual(list(barra.x), ["2022", "2023", "2024"])
        self.assertEqual(list(barra.y), [2.0, 5.0, 3.0])
        self.assertEqual(barra.marker.color[1], TEMA_PADRAO["destaque"])
        self.assertEqual(barra.marker.color[0], TEMA_PADRAO["cores"][0])
        referencia = figura.data[1]
        self.assertEqual(referencia.name, "Média")
        self.assertEqual(list(referencia.y), [3.3, 3.3])

    def test_treemap_usa_as_contagens(self):
        contagens = pd.Series([10, 0, 5], index=["Baixa", "Média", "Alta"])

        figura = self.visualizador.grafico_treemap(
            contagens, "Teste", descricoes={"Alta": "(acima de 4%)"}
        )

        treemap = figura.data[0]
        self.assertEqual(list(treemap.labels), ["Baixa", "Média", "Alta"])
        self.assertEqual(list(treemap.values), [10, 0, 5])
        self.assertEqual(treemap.customdata[2], "(acima de 4%)")

    def test_dispersao_separa_grupos_e_traca_tendencia(self):
        tabela = pd.DataFrame({
            "data": self.datas.append(self.datas + pd.DateOffset(years=1)),
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [2.0, 4.0, 6.0, 8.0, 10.0, 12.0],
            "grupo": ["A", "A", "A", "B", "B", "B"],
        })

        figura = self.visualizador.grafico_dispersao(tabela, "Teste",
                                                     "x", "y")

        nomes = [traco.name for traco in figura.data]
        self.assertEqual(nomes, ["A", "B", "Tendência"])
        self.assertEqual(list(figura.data[1].x), [4.0, 5.0, 6.0])
        # y = 2x: a tendência vai de (1, 2) a (6, 12)
        tendencia = figura.data[2]
        self.assertAlmostEqual(tendencia.y[0], 2.0)
        self.assertAlmostEqual(tendencia.y[1], 12.0)


if __name__ == "__main__":
    unittest.main()
