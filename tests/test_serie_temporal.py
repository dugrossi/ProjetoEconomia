import unittest

import pandas as pd

from modelos.excecoes import SerieInvalidaError
from modelos.serie_temporal import SerieTemporal


class TestSerieTemporal(unittest.TestCase):
    def setUp(self):
        self.dados = pd.DataFrame({
            "data": pd.to_datetime(["2024-01-01", "2024-02-01"]),
            "valor": [3.1, 3.2],
        })

    def test_cria_serie_com_metadados(self):
        # Arrange / Act
        serie = SerieTemporal(21082, "Inadimplência", "%", self.dados)

        # Assert
        self.assertEqual(serie.codigo, 21082)
        self.assertEqual(len(serie), 2)
        self.assertEqual(str(serie), "[21082] Inadimplência (%)")

    def test_dados_nao_podem_ser_alterados_por_fora(self):
        serie = SerieTemporal(21082, "Inadimplência", "%", self.dados)

        copia = serie.dados
        copia.loc[0, "valor"] = 99.0

        self.assertEqual(serie.dados.loc[0, "valor"], 3.1)

    def test_sem_coluna_valor_gera_erro(self):
        dados = self.dados.drop(columns=["valor"])

        with self.assertRaises(SerieInvalidaError):
            SerieTemporal(21082, "Inadimplência", "%", dados)


if __name__ == "__main__":
    unittest.main()
