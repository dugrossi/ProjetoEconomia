import unittest

import numpy as np
import pandas as pd

from analise.tratador_dados import TratadorDados
from modelos.serie_temporal import SerieTemporal


def criar_serie(datas, valores):
    dados = pd.DataFrame({"data": pd.to_datetime(datas), "valor": valores})
    return SerieTemporal(1, "Série de teste", "%", dados)


class TestTratadorDados(unittest.TestCase):
    def test_remove_duplicada_mantendo_o_ultimo_valor(self):
        serie = criar_serie(["2024-01-01", "2024-01-01", "2024-02-01"],
                            [1.0, 9.0, 2.0])
        tratador = TratadorDados()

        tratada = tratador.tratar(serie)

        self.assertEqual(len(tratada), 2)
        self.assertEqual(tratada.dados.loc[0, "valor"], 9.0)
        self.assertEqual(tratador.relatorio.loc[0, "duplicadas_removidas"], 1)

    def test_completa_mes_faltando_e_interpola(self):
        # Arrange: março está faltando entre fevereiro (2) e abril (4)
        serie = criar_serie(["2024-02-01", "2024-04-01"], [2.0, 4.0])
        tratador = TratadorDados("interpolar")

        # Act
        tratada = tratador.tratar(serie).dados

        # Assert: março entra com valor intermediário
        marco = tratada[tratada["data"] == "2024-03-01"]["valor"].iloc[0]
        self.assertAlmostEqual(marco, 3.0, places=1)
        self.assertEqual(tratador.relatorio.loc[0, "meses_incluidos"], 1)

    def test_metodo_remover_descarta_mes_sem_valor(self):
        serie = criar_serie(["2024-01-01", "2024-02-01", "2024-03-01"],
                            [1.0, np.nan, 3.0])
        tratador = TratadorDados("remover")

        tratada = tratador.tratar(serie)

        self.assertEqual(len(tratada), 2)
        self.assertEqual(tratador.relatorio.loc[0, "ausentes_tratados"], 1)

    def test_descarta_registro_sem_data(self):
        dados = pd.DataFrame({
            "data": [pd.Timestamp("2024-01-01"), pd.NaT],
            "valor": [1.0, 2.0],
        })
        tratador = TratadorDados()

        tratada = tratador.tratar(SerieTemporal(1, "Série", "%", dados))

        self.assertEqual(len(tratada), 1)
        self.assertEqual(tratador.relatorio.loc[0, "datas_invalidas"], 1)

    def test_serie_original_nao_e_alterada(self):
        serie = criar_serie(["2024-01-01", "2024-01-01"], [1.0, 2.0])

        TratadorDados().tratar(serie)

        self.assertEqual(len(serie), 2)

    def test_serie_limpa_passa_sem_mudancas(self):
        serie = criar_serie(["2024-01-01", "2024-02-01"], [1.0, 2.0])
        tratador = TratadorDados()

        tratada = tratador.tratar(serie)

        pd.testing.assert_frame_equal(tratada.dados, serie.dados)
        linha = tratador.relatorio.iloc[0]
        mudancas = (linha["duplicadas_removidas"] + linha["meses_incluidos"]
                    + linha["ausentes_tratados"])
        self.assertEqual(mudancas, 0)

    def test_metodo_invalido_gera_erro(self):
        with self.assertRaises(ValueError):
            TratadorDados("apagar tudo")


if __name__ == "__main__":
    unittest.main()
