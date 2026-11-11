import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import URLError

import pandas as pd

from fontes.fonte_api_bcb import FonteAPIBCB
from fontes.fonte_com_reserva import FonteComReserva
from fontes.fonte_csv import FonteCSV
from modelos.excecoes import FonteDadosError


class TestFonteCSV(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        caminho = Path(self.pasta.name) / "bcdata.sgs.1.csv"
        caminho.write_text(
            '"data";"valor"\n"01/03/2011";"3,17"\n"01/04/2011";"abc"\n',
            encoding="utf-8",
        )

    def tearDown(self):
        self.pasta.cleanup()

    def test_converte_data_e_decimal_com_virgula(self):
        fonte = FonteCSV(self.pasta.name)

        dados = fonte.carregar(1)

        self.assertEqual(dados.loc[0, "data"], pd.Timestamp("2011-03-01"))
        self.assertAlmostEqual(dados.loc[0, "valor"], 3.17)

    def test_valor_invalido_vira_ausente(self):
        fonte = FonteCSV(self.pasta.name)

        dados = fonte.carregar(1)

        self.assertTrue(pd.isna(dados.loc[1, "valor"]))

    def test_arquivo_inexistente_gera_erro_da_fonte(self):
        fonte = FonteCSV(self.pasta.name)

        with self.assertRaises(FonteDadosError):
            fonte.carregar(999)


class TestFonteAPIBCB(unittest.TestCase):
    @patch("fontes.fonte_api_bcb.urlopen")
    def test_converte_resposta_da_api(self, mock_urlopen):
        # Arrange: a API "responde" sem acessar a internet
        resposta = json.dumps([{"data": "01/03/2011", "valor": "3.17"}])
        mock_urlopen.return_value.__enter__.return_value = io.StringIO(
            resposta
        )
        fonte = FonteAPIBCB()

        # Act
        dados = fonte.carregar(21082)

        # Assert
        self.assertAlmostEqual(dados.loc[0, "valor"], 3.17)
        url_chamada = mock_urlopen.call_args.args[0]
        self.assertIn("bcdata.sgs.21082", url_chamada)

    @patch("fontes.fonte_api_bcb.urlopen")
    def test_sem_internet_gera_erro_da_fonte(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("sem conexão")
        fonte = FonteAPIBCB()

        with self.assertRaises(FonteDadosError):
            fonte.carregar(21082)


class TestFonteComReserva(unittest.TestCase):
    def setUp(self):
        self.dados = pd.DataFrame({"data": [], "valor": []})

    def test_usa_principal_quando_ela_funciona(self):
        principal = Mock()
        principal.carregar.return_value = self.dados
        reserva = Mock()
        fonte = FonteComReserva(principal, reserva)

        fonte.carregar(21082)

        principal.carregar.assert_called_once_with(21082)
        reserva.carregar.assert_not_called()

    def test_usa_reserva_quando_principal_falha(self):
        principal = Mock()
        principal.carregar.side_effect = FonteDadosError("sem arquivo")
        reserva = Mock()
        reserva.carregar.return_value = self.dados
        fonte = FonteComReserva(principal, reserva)

        resultado = fonte.carregar(21082)

        reserva.carregar.assert_called_once_with(21082)
        self.assertIs(resultado, self.dados)

    def test_erro_quando_as_duas_falham(self):
        principal = Mock()
        principal.carregar.side_effect = FonteDadosError("sem arquivo")
        reserva = Mock()
        reserva.carregar.side_effect = FonteDadosError("sem internet")
        fonte = FonteComReserva(principal, reserva)

        with self.assertRaises(FonteDadosError):
            fonte.carregar(21082)


if __name__ == "__main__":
    unittest.main()
