"""Trechos do código do projeto mostrados nos slides de arquitetura.

Os trechos são cópias do código real, só sem as docstrings e sem as
linhas que não ajudam a explicar o conceito do slide (no lugar delas
aparece ``...``). Se o código mudar, atualize aqui também.
"""

import html
import re

# Slide 10: herança e polimorfismo nos indicadores
TRECHOS_HERANCA = [
    ("indicadores/indicador.py", '''\
class Indicador(ABC):

    @abstractmethod
    def calcular(self, analisador: AnalisadorDados) -> float:
        ...'''),
    ("indicadores/indicadores_serie.py", '''\
class ValorAtual(IndicadorDeSerie):

    def calcular(self, analisador: AnalisadorDados) -> float:
        return float(self._valores(analisador).iloc[-1])'''),
    ("analise/analisador_dados.py", '''\
for indicador in indicadores:
    valor = indicador.calcular(self)
    linhas.append({
        "indicador": indicador.nome,
        "valor": valor,
        "texto": indicador.formatar(valor),
        "descricao": indicador.descricao,
    })'''),
]

# Slide 11: encapsulamento na série e composição na fonte de dados
TRECHOS_ENCAPSULAMENTO = [
    ("modelos/serie_temporal.py", '''\
class SerieTemporal:

    def __init__(
        self, codigo: int, nome: str, unidade: str, dados: pd.DataFrame
    ) -> None:
        ...
        self.__dados = dados[self.COLUNAS].copy()

    @property
    def dados(self) -> pd.DataFrame:
        return self.__dados.copy()'''),
    ("fontes/fonte_com_reserva.py", '''\
class FonteComReserva(FonteDados):

    def __init__(self, principal: FonteDados, reserva: FonteDados) -> None:
        self.__principal = principal
        self.__reserva = reserva

    def carregar(self, codigo: int) -> pd.DataFrame:
        try:
            return self.__principal.carregar(codigo)
        except FonteDadosError:
            return self.__reserva.carregar(codigo)'''),
]

PALAVRAS_CHAVE = ["class", "def", "return", "for", "in", "try", "except"]


def destacar_codigo(codigo: str) -> str:
    """Transforma o código em HTML, colorindo palavras-chave e decorators.

    Primeiro o texto passa por ``html.escape`` (para o ``<`` e o ``>``
    não virarem tags) e depois cada palavra-chave ganha um <span>.
    """
    resultado = html.escape(codigo, quote=False)
    for palavra in PALAVRAS_CHAVE:
        # \\b = começo/fim de palavra, para não pintar "in" dentro de "indicador"
        resultado = re.sub(rf"\b{palavra}\b",
                           f'<span class="chave">{palavra}</span>', resultado)
    resultado = re.sub(r"(@\w+)", r'<span class="decorator">\1</span>',
                       resultado)
    return resultado


def html_trechos(trechos: list[tuple[str, str]]) -> str:
    """Monta os blocos de código de um slide, com o arquivo em cima."""
    blocos = ""
    for arquivo, codigo in trechos:
        blocos += (
            '<div class="trecho">'
            f'<div class="arquivo">{arquivo}</div>'
            f"<pre><code>{destacar_codigo(codigo)}</code></pre>"
            "</div>"
        )
    return f'<div class="trechos">{blocos}</div>'
