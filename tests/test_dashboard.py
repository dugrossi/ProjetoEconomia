import unittest
from unittest.mock import Mock

from dashboard.dashboard_html import DashboardHTML
from dashboard.slide import Slide
from visualizacao.visualizador import TEMA_VIDRO, Visualizador


class TestSlide(unittest.TestCase):
    def test_cria_slide_com_conteudo(self):
        slide = Slide("Evolução", "<div>gráfico</div>", nota="Subiu.")

        self.assertEqual(slide.titulo, "Evolução")
        self.assertEqual(slide.nota, "Subiu.")

    def test_slide_sem_titulo_gera_erro(self):
        with self.assertRaises(ValueError):
            Slide("   ", "<div></div>")


class TestDashboardHTML(unittest.TestCase):
    def setUp(self):
        # O analisador é substituído por um Mock: o teste não lê dados
        self.dashboard = DashboardHTML("Painel", Mock(), Visualizador(), [])

    def test_slides_ficam_na_ordem_em_que_foram_adicionados(self):
        self.dashboard.adicionar_slide(Slide("Primeiro", ""))
        self.dashboard.adicionar_slide(Slide("Segundo", ""))

        titulos = [slide.titulo for slide in self.dashboard.slides]

        self.assertEqual(titulos, ["Primeiro", "Segundo"])
        self.assertEqual(len(self.dashboard), 2)

    def test_lista_de_slides_nao_pode_ser_alterada_por_fora(self):
        slides = self.dashboard.slides

        with self.assertRaises(AttributeError):
            slides.append(Slide("Intruso", ""))


class TestVisualizador(unittest.TestCase):
    def test_usa_tema_de_vidro_por_padrao(self):
        visualizador = Visualizador()

        self.assertIs(visualizador.tema, TEMA_VIDRO)
        self.assertEqual(visualizador.tema["fundo"], "rgba(0,0,0,0)")


if __name__ == "__main__":
    unittest.main()
