import unittest

import pandas as pd

from analise.analisador_dados import AnalisadorDados
from indicadores.defasagem_correlacao import DefasagemCorrelacao
from indicadores.indicador import Indicador
from indicadores.indicadores_serie import (
    DistanciaDaMedia,
    PercentilHistorico,
    ValorAtual,
    Variacao12Meses,
)
from modelos.serie_temporal import SerieTemporal


def criar_analisador(series_valores):
    """Monta um analisador com séries mensais a partir de jan/2020."""
    series = []
    for codigo, valores in series_valores.items():
        datas = pd.date_range("2020-01-01", periods=len(valores), freq="MS")
        dados = pd.DataFrame({"data": datas, "valor": valores})
        series.append(SerieTemporal(codigo, f"Série {codigo}", "%", dados))
    return AnalisadorDados(series)


class TestIndicadoresDeSerie(unittest.TestCase):
    def setUp(self):
        # 13 meses: 1, 2, ..., 13 (jan/2020 a jan/2021)
        valores = [float(v) for v in range(1, 14)]
        self.analisador = criar_analisador({1: valores})

    def test_valor_atual_e_o_ultimo_mes(self):
        indicador = ValorAtual(1, "Atual", "", "%")

        self.assertEqual(indicador.calcular(self.analisador), 13.0)

    def test_variacao_compara_com_mesmo_mes_do_ano_anterior(self):
        indicador = Variacao12Meses(1, "Variação", "", " p.p.")

        # jan/2021 (13) - jan/2020 (1)
        self.assertEqual(indicador.calcular(self.analisador), 12.0)

    def test_percentil_do_maior_valor_e_100(self):
        indicador = PercentilHistorico(1, "Percentil", "", "%")

        self.assertEqual(indicador.calcular(self.analisador), 100.0)

    def test_distancia_da_media_em_desvios(self):
        analisador = criar_analisador({1: [1.0, 2.0, 3.0]})
        indicador = DistanciaDaMedia(1, "Distância", "", "")

        # média 2, desvio padrão 1 -> (3 - 2) / 1
        self.assertAlmostEqual(indicador.calcular(analisador), 1.0)


class TestDefasagemCorrelacao(unittest.TestCase):
    def test_encontra_o_atraso_entre_as_series(self):
        # Arrange: o efeito repete a causa com 3 meses de atraso
        causa = [float(v % 7) for v in range(40)]
        efeito = [0.0, 0.0, 0.0] + causa[:-3]
        analisador = criar_analisador({10: causa, 20: efeito})
        indicador = DefasagemCorrelacao(10, 20, "Defasagem", "", 6)

        # Act
        defasagem = indicador.calcular(analisador)

        # Assert
        self.assertEqual(defasagem, 3.0)
        self.assertAlmostEqual(indicador.correlacao_maxima(analisador), 1.0)


class TestPolimorfismo(unittest.TestCase):
    def test_analisador_calcula_indicadores_de_tipos_diferentes(self):
        analisador = criar_analisador({1: [1.0, 2.0, 3.0]})
        indicadores = [
            ValorAtual(1, "Atual", "", "%"),
            PercentilHistorico(1, "Percentil", "", "%", casas_decimais=0),
        ]

        resultado = analisador.calcular_indicadores(indicadores)

        self.assertEqual(list(resultado["texto"]), ["3,00%", "100%"])

    def test_indicador_abstrato_nao_pode_ser_criado(self):
        with self.assertRaises(TypeError):
            Indicador("Qualquer", "", "")

    def test_formatar_usa_virgula_decimal(self):
        indicador = ValorAtual(1, "Atual", "", "% a.m.")

        self.assertEqual(indicador.formatar(2.3567), "2,36% a.m.")


if __name__ == "__main__":
    unittest.main()
