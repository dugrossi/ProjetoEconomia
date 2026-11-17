"""Um slide da apresentação do dashboard."""


class Slide:
    """Uma tela da apresentação: título, conteúdo e interpretação.

    O conteúdo é um trecho de HTML (um gráfico, cards de indicadores
    ou uma tabela). A nota é a análise interpretativa daquele slide.
    """

    def __init__(
        self, titulo: str, conteudo: str, subtitulo: str = "", nota: str = ""
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

    def __str__(self) -> str:
        return f"Slide: {self.__titulo}"
