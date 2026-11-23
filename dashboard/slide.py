"""Um slide da apresentação do dashboard."""


class Slide:
    """Uma tela da apresentação: título, conteúdo e interpretação.

    O conteúdo é um trecho de HTML (um gráfico, cards de indicadores
    ou uma tabela) e fica do lado direito da tela. Do lado esquerdo
    ficam o subtítulo (a etiqueta pequena acima do título), o título,
    o número em destaque e a nota, que é a análise interpretativa
    daquele slide.
    """

    def __init__(
        self,
        titulo: str,
        conteudo: str,
        subtitulo: str = "",
        nota: str = "",
        destaque: str = "",
    ) -> None:
        """Cria o slide.

        Raises:
            ValueError: se o título estiver vazio.
        """
        if not titulo.strip():
            raise ValueError("Todo slide precisa de um título")
        self.__titulo = titulo
        self.__conteudo = conteudo
        self.__subtitulo = subtitulo
        self.__nota = nota
        self.__destaque = destaque

    @property
    def titulo(self) -> str:
        return self.__titulo

    @property
    def subtitulo(self) -> str:
        return self.__subtitulo

    @property
    def conteudo(self) -> str:
        return self.__conteudo

    @property
    def nota(self) -> str:
        return self.__nota

    @property
    def destaque(self) -> str:
        """Número grande mostrado abaixo do título (pode ficar vazio)."""
        return self.__destaque

    def para_html(self, numero: int) -> str:
        """Monta o HTML do slide; ``numero`` aparece na etiqueta."""
        etiqueta = f"{numero:02d} — {self.__subtitulo.upper()}"
        destaque = (f'<div class="grande">{self.__destaque}</div>'
                    if self.__destaque else "")
        nota = f"<p>{self.__nota}</p>" if self.__nota else ""
        return (
            '<section class="slide">\n'
            '  <div class="texto">\n'
            f'    <div class="num-slide">{etiqueta}</div>\n'
            f"    <h2>{self.__titulo}</h2>\n"
            f"    {destaque}\n"
            f"    {nota}\n"
            "  </div>\n"
            f'  <div class="conteudo">{self.__conteudo}</div>\n'
            "</section>"
        )

    def __str__(self) -> str:
        return f"Slide: {self.__titulo}"
