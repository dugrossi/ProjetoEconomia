"""Monta o dashboard como uma apresentação em HTML."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs

from analise.analisador_dados import (
    LIMITES_FAIXAS,
    NOMES_FAIXAS,
    AnalisadorDados,
)
from config import INADIMPLENCIA, JUROS, PERIODOS
from dashboard.slide import Slide
from dashboard.trechos_codigo import (
    TRECHOS_ENCAPSULAMENTO,
    TRECHOS_HERANCA,
    html_trechos,
)
from indicadores.indicador import Indicador
from visualizacao.visualizador import Visualizador

PASTA_DASHBOARD = Path(__file__).parent
MESES = ["jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez"]

# Perguntas definidas na Etapa 1
PERGUNTAS = [
    "Como a inadimplência do crédito evoluiu de 2011 a 2026 e em que "
    "nível ela está hoje?",
    "Os juros cobrados no crédito ajudam a explicar a inadimplência? "
    "Com quantos meses de atraso?",
    "A relação entre juros e inadimplência mudou depois de 2020?",
]

# Slide de arquitetura: cada classe do caminho dos dados, o que ela faz
# e as subclasses dela (quando tem herança)
ARQUITETURA = [
    ("FonteDados", "Lê as séries do CSV salvo ou, se faltar, da API do BC",
     "FonteAPIBCB · FonteCSV · FonteComReserva"),
    ("TratadorDados", "Remove duplicadas e preenche meses faltando", ""),
    ("AnalisadorDados", "Faz as contas com Pandas", ""),
    ("Indicador", "Calcula os seis números do slide 2",
     "ValorAtual · Variacao12Meses · DistanciaDaMedia · "
     "PercentilHistorico · DefasagemCorrelacao"),
    ("Visualizador", "Gera os gráficos com Plotly", ""),
    ("DashboardHTML", "Junta os objetos Slide em um arquivo HTML", ""),
]


def numero(valor: float, casas: int = 2) -> str:
    """Formata um número com vírgula decimal: 4.98 -> '4,98'."""
    return f"{valor:.{casas}f}".replace(".", ",")


def mes_ano(data) -> str:
    """Escreve uma data como 'set/2026'."""
    data = pd.Timestamp(data)
    return f"{MESES[data.month - 1]}/{data.year}"


def lista_html(itens: list[str]) -> str:
    """Transforma uma lista de textos em itens <li> de HTML."""
    html = ""
    for item in itens:
        html += f"<li>{item}</li>"
    return html


def ler_arquivo(nome: str) -> str:
    """Lê um arquivo de texto da pasta dashboard/."""
    with open(PASTA_DASHBOARD / nome, "r", encoding="utf-8") as arquivo:
        return arquivo.read()


class DashboardHTML:
    """Organiza os componentes do painel em uma apresentação de slides.

    O resultado é um único arquivo HTML. Os slides avançam com um
    clique no canto direito da tela ou com as setas do teclado. Cada
    slide tem o texto de análise à esquerda e o conteúdo (gráfico,
    cards de indicadores ou tabela) à direita.

    A ordem dos slides segue o roteiro da apresentação: resultados
    (slides 1 a 8), arquitetura do código (9 a 11) e conclusões (12).
    """

    def __init__(
        self,
        titulo: str,
        analisador: AnalisadorDados,
        visualizador: Visualizador,
        indicadores: list[Indicador],
    ) -> None:
        self.__titulo = titulo
        self.__analisador = analisador
        self.__visualizador = visualizador
        self.__indicadores = list(indicadores)
        self.__slides: list[Slide] = []

    @property
    def titulo(self) -> str:
        return self.__titulo

    @property
    def slides(self) -> tuple[Slide, ...]:
        """Slides na ordem de apresentação (somente leitura)."""
        return tuple(self.__slides)

    def adicionar_slide(self, slide: Slide) -> None:
        """Acrescenta um slide ao final da apresentação."""
        self.__slides.append(slide)

    # --- Montagem dos slides -------------------------------------------

    def montar_slides(self, graficos: dict[str, go.Figure]) -> None:
        """Cria os 12 slides da apresentação, na ordem do roteiro.

        Args:
            graficos: figuras da Etapa 5, com as mesmas chaves usadas
                no ``main.py`` (linhas_evolucao, barras_media_anual...).
        """
        self.__slides = []
        self.adicionar_slide(self.__slide_capa())
        self.adicionar_slide(self.__slide_indicadores())
        self.adicionar_slide(
            self.__slide_evolucao(graficos["linhas_evolucao"]))
        self.adicionar_slide(
            self.__slide_media_anual(graficos["barras_media_anual"]))
        self.adicionar_slide(
            self.__slide_faixas(graficos["treemap_faixas"]))
        self.adicionar_slide(
            self.__slide_defasagem(graficos["barras_defasagem"]))
        self.adicionar_slide(
            self.__slide_periodos(graficos["dispersao_juros_inadimplencia"]))
        self.adicionar_slide(self.__slide_tabela())
        self.adicionar_slide(self.__slide_arquitetura())
        self.adicionar_slide(self.__slide_heranca())
        self.adicionar_slide(self.__slide_encapsulamento())
        self.adicionar_slide(self.__slide_conclusoes())

    def __slide_capa(self) -> Slide:
        """Slide 1: título e as três perguntas da análise."""
        datas = self.__analisador.serie(INADIMPLENCIA).dados["data"]
        conteudo = (
            '<div class="rotulo">PERGUNTAS DA ANÁLISE</div>'
            f'<ol class="perguntas">{lista_html(PERGUNTAS)}</ol>'
        )
        nota = (
            f"Séries do Banco Central do Brasil (SGS {INADIMPLENCIA} e "
            f"{JUROS}), de <b>{mes_ano(datas.min())}</b> a "
            f"<b>{mes_ano(datas.max())}</b>."
        )
        return Slide(self.__titulo, conteudo,
                     subtitulo="Projeto final · POO · CDIA", nota=nota)

    def __slide_indicadores(self) -> Slide:
        """Slide 2: um card para cada indicador."""
        resultados = self.__analisador.calcular_indicadores(
            self.__indicadores)
        cards = ""
        for i, linha in resultados.iterrows():
            # Separa o número da unidade: "3,04 desvios padrão" fica
            # com "3,04" grande e "desvios padrão" pequeno
            partes = linha["texto"].split(" ", 1)
            valor = partes[0]
            if len(partes) > 1:
                valor += f"<small> {partes[1]}</small>"
            classe = "kpi principal" if i == 0 else "kpi"
            cards += (
                f'<div class="{classe}">'
                f'<div class="nome">{linha["indicador"]}</div>'
                f'<div class="valor">{valor}</div>'
                f'<div class="descricao">{linha["descricao"]}</div>'
                "</div>"
            )

        valores = self.__analisador.serie(INADIMPLENCIA).dados["valor"]
        atual = valores.iloc[-1]
        meses_maiores = (valores > atual).sum()
        nota = (
            f"No último mês, a inadimplência ficou em "
            f"<b>{numero(atual)}%</b>, contra <b>{numero(valores.mean())}%"
            f"</b> de média histórica. Só <b>{meses_maiores}</b> dos "
            f"{len(valores)} meses da série tiveram valor maior."
        )
        return Slide("Onde a inadimplência está hoje",
                     f'<div class="kpis">{cards}</div>',
                     subtitulo="Indicadores", nota=nota)

    def __slide_evolucao(self, figura: go.Figure) -> Slide:
        """Slide 3: linhas da inadimplência e dos juros."""
        dados = self.__analisador.serie(INADIMPLENCIA).dados
        ultimo = dados.iloc[-1]
        maximo = dados.loc[dados["valor"].idxmax()]

        figura.update_traces(line={"width": 2.5})
        # Filtro do período: botões em cima do gráfico
        figura.update_xaxes(rangeselector={
            "buttons": [
                {"count": 5, "label": "5 anos", "step": "year",
                 "stepmode": "backward"},
                {"count": 10, "label": "10 anos", "step": "year",
                 "stepmode": "backward"},
                {"label": "Tudo", "step": "all"},
            ],
            "bgcolor": "rgba(0,0,0,0.05)",
            "activecolor": "#b4cbe6",
        })

        nota = (
            f"da carteira de crédito tinha atraso acima de 90 dias em "
            f"<b>{mes_ano(ultimo['data'])}</b>. A máxima da série foi "
            f"<b>{numero(maximo['valor'])}%</b>, em "
            f"{mes_ano(maximo['data'])}. Os botões acima do gráfico "
            f"filtram o período."
        )
        return Slide("Quanto do crédito no Brasil não está sendo pago?",
                     self.__html_grafico(figura, "grafico-evolucao"),
                     subtitulo="Evolução", nota=nota,
                     destaque=f"{numero(ultimo['valor'])}%")

    def __slide_media_anual(self, figura: go.Figure) -> Slide:
        """Slide 4: barras com a média de cada ano."""
        anos = self.__analisador.agrupar_por_ano(INADIMPLENCIA)
        ano_maior = anos["media"].idxmax()
        ano_menor = anos["media"].idxmin()
        media = self.__analisador.serie(INADIMPLENCIA).dados["valor"].mean()

        aviso = ""
        if anos.loc[ano_maior, "meses"] < 12:
            aviso = f" (só {anos.loc[ano_maior, 'meses']} meses até agora)"

        nota = (
            f"foi a inadimplência média de {ano_maior}{aviso}, contra "
            f"<b>{numero(media)}%</b> de média histórica. O ano mais "
            f"baixo foi <b>{ano_menor}</b>, com "
            f"{numero(anos.loc[ano_menor, 'media'])}%."
        )
        return Slide(f"{ano_maior} tem a maior média da série",
                     self.__html_grafico(figura, "grafico-anos"),
                     subtitulo="Ano a ano", nota=nota,
                     destaque=f"{numero(anos.loc[ano_maior, 'media'])}%")

    def __slide_faixas(self, figura: go.Figure) -> Slide:
        """Slide 5: treemap com os meses de cada faixa."""
        faixas = self.__analisador.agrupar_por_faixa(INADIMPLENCIA)
        critica = faixas.index[-1]  # a última faixa é a mais alta
        mais_comum = faixas["meses"].idxmax()
        meses_criticos = faixas.loc[critica, "meses"]

        figura.update_traces(textfont={"size": 16})

        nota = (
            f"ficaram na faixa <b>{critica.lower()}</b> "
            f"({numero(LIMITES_FAIXAS[-2])}% ou mais)"
        )
        if meses_criticos > 0:
            nota += (
                f", todos entre {mes_ano(faixas.loc[critica, 'primeiro_mes'])}"
                f" e {mes_ano(faixas.loc[critica, 'ultimo_mes'])}"
            )
        nota += (
            f". A faixa mais comum é a {mais_comum.lower()}, com "
            f"{numero(faixas.loc[mais_comum, 'percentual'], 0)}% dos meses."
        )
        return Slide("Em que faixa a inadimplência costuma ficar?",
                     self.__html_grafico(figura, "grafico-faixas"),
                     subtitulo="Faixas", nota=nota,
                     destaque=f"{meses_criticos}<small> meses</small>")

    def __slide_defasagem(self, figura: go.Figure) -> Slide:
        """Slide 6: correlação para cada atraso dos juros."""
        correlacoes = self.__analisador.correlacao_defasada(
            JUROS, INADIMPLENCIA, range(25))
        melhor = int(correlacoes.idxmax())

        nota = (
            f"é o atraso com a maior correlação "
            f"(<b>{numero(correlacoes.max())}</b>). A inadimplência de "
            f"hoje acompanha melhor os juros de {melhor} meses atrás do "
            f"que os juros do mesmo mês ({numero(correlacoes[0])})."
        )
        return Slide("Os juros chegam antes da inadimplência",
                     self.__html_grafico(figura, "grafico-defasagem"),
                     subtitulo="Defasagem", nota=nota,
                     destaque=f"{melhor}<small> meses</small>")

    def __slide_periodos(self, figura: go.Figure) -> Slide:
        """Slide 7: dispersão separada em antes e depois de 2020."""
        correlacoes = self.__analisador.correlacao_por_periodo(
            JUROS, INADIMPLENCIA, 6, PERIODOS)
        antes = correlacoes.index[0]
        depois = correlacoes.index[-1]

        if correlacoes[depois] > correlacoes[antes]:
            titulo = "A relação ficou mais forte depois de 2020"
        else:
            titulo = "A relação ficou mais fraca depois de 2020"

        nota = (
            f"é a correlação entre os juros de 6 meses antes e a "
            f"inadimplência de {depois}, contra "
            f"<b>{numero(correlacoes[antes])}</b> de {antes}. Correlação "
            f"não prova causa, mas a relação aparece nos dois períodos."
        )
        return Slide(titulo,
                     self.__html_grafico(figura, "grafico-periodos"),
                     subtitulo="Antes e depois de 2020", nota=nota,
                     destaque=numero(correlacoes[depois]))

    def __slide_tabela(self) -> Slide:
        """Slide 8: tabela mês a mês com filtros de ano e faixa."""
        tabela = self.__analisador.tabela_unificada()
        faixas = self.__analisador.classificar_faixas(INADIMPLENCIA)
        faixas = faixas.set_index("data")["faixa"]
        cores = self.__cores_faixas()

        # Linhas da tabela, do mês mais recente para o mais antigo
        linhas = ""
        for data in tabela.index[::-1]:
            faixa = str(faixas[data])
            fundo, cor_texto = cores[faixa]
            linhas += (
                f'<tr data-ano="{data.year}" data-faixa="{faixa}">'
                f"<td>{mes_ano(data)}</td>"
                f"<td>{numero(tabela.loc[data, INADIMPLENCIA])}</td>"
                f"<td>{numero(tabela.loc[data, JUROS])}</td>"
                f'<td><span class="faixa" style="background:{fundo};'
                f'color:{cor_texto}">{faixa}</span></td></tr>'
            )

        # Opções dos filtros
        anos = sorted(set(tabela.index.year))
        opcoes_de = ""
        opcoes_ate = ""
        for ano in anos:
            opcoes_de += f"<option>{ano}</option>"
            marcado = " selected" if ano == anos[-1] else ""
            opcoes_ate += f"<option{marcado}>{ano}</option>"
        opcoes_faixa = '<option value="">Todas</option>'
        for nome in NOMES_FAIXAS:
            opcoes_faixa += f"<option>{nome}</option>"

        conteudo = (
            '<div class="filtros">'
            f'<label>De<select id="filtro-de">{opcoes_de}</select></label>'
            f'<label>Até<select id="filtro-ate">{opcoes_ate}</select>'
            "</label>"
            f'<label>Faixa<select id="filtro-faixa">{opcoes_faixa}'
            "</select></label>"
            '<span class="total" id="total-linhas"></span>'
            "</div>"
            '<div class="tabela-caixa"><table id="tabela-dados">'
            "<thead><tr><th>Mês</th><th>Inadimplência (%)</th>"
            "<th>Juros (% a.m.)</th><th>Faixa</th></tr></thead>"
            f"<tbody>{linhas}</tbody></table></div>"
        )
        nota = (
            "Use os filtros para escolher o período e a faixa de "
            "inadimplência. Os valores já passaram pelo "
            "<b>TratadorDados</b>: duplicadas removidas e meses faltando "
            "preenchidos."
        )
        return Slide("Os dados mês a mês", conteudo, subtitulo="Dados",
                     nota=nota)

    def __slide_arquitetura(self) -> Slide:
        """Slide 9: as classes do projeto, na ordem em que os dados passam."""
        caixas = ""
        for nome, funcao, subclasses in ARQUITETURA:
            heranca = ""
            if subclasses:
                heranca = f'<div class="heranca">↳ {subclasses}</div>'
            caixas += (
                '<div class="classe">'
                f'<div class="nome-classe">{nome}</div>'
                f'<div class="funcao">{funcao}</div>'
                f"{heranca}</div>"
            )
        nota = (
            "Cada classe tem uma responsabilidade e passa o resultado para "
            "a próxima. As setas <b>↳</b> mostram as subclasses (herança). "
            "Tudo roda com um comando: <b>python main.py</b>."
        )
        return Slide("Como o código funciona",
                     f'<div class="fluxo">{caixas}</div>',
                     subtitulo="Arquitetura", nota=nota)

    def __slide_heranca(self) -> Slide:
        """Slide 10: herança e polimorfismo nos indicadores (com código)."""
        nota = (
            "<b>1.</b> A classe abstrata <b>Indicador</b> obriga todo "
            "indicador a ter o método <b>calcular</b>. "
            "<b>2.</b> Cada subclasse faz a sua conta. "
            "<b>3.</b> O analisador chama <b>calcular</b> do mesmo jeito "
            "para os seis, sem saber qual é qual: isso é polimorfismo."
        )
        return Slide("Um contrato, vários indicadores",
                     html_trechos(TRECHOS_HERANCA),
                     subtitulo="Herança e polimorfismo", nota=nota)

    def __slide_encapsulamento(self) -> Slide:
        """Slide 11: encapsulamento e composição (com código)."""
        nota = (
            "<b>1.</b> Os dados da série ficam em um atributo privado "
            "(<b>__dados</b>) e só saem como cópia pela property, então "
            "ninguém altera por fora. "
            "<b>2.</b> A <b>FonteComReserva</b> é feita de duas outras "
            "fontes (composição): se a principal falhar, usa a reserva."
        )
        return Slide("Dados protegidos e uma fonte de reserva",
                     html_trechos(TRECHOS_ENCAPSULAMENTO),
                     subtitulo="Encapsulamento e composição", nota=nota)

    def __slide_conclusoes(self) -> Slide:
        """Slide 12: respostas às perguntas e limitações."""
        dados = self.__analisador.serie(INADIMPLENCIA).dados
        correlacoes = self.__analisador.correlacao_defasada(
            JUROS, INADIMPLENCIA, range(25))
        por_periodo = self.__analisador.correlacao_por_periodo(
            JUROS, INADIMPLENCIA, 6, PERIODOS)
        ultimo_ano = dados["data"].max().year
        meses_ultimo_ano = (dados["data"].dt.year == ultimo_ano).sum()

        conclusoes = [
            f"<b>Evolução:</b> a inadimplência oscilou entre "
            f"{numero(dados['valor'].min())}% e "
            f"{numero(dados['valor'].max())}% e está hoje perto da máxima "
            f"da série.",
            f"<b>Juros:</b> a inadimplência acompanha os juros com cerca "
            f"de <b>{int(correlacoes.idxmax())} meses</b> de atraso "
            f"(correlação de {numero(correlacoes.max())}).",
            f"<b>Depois de 2020:</b> a correlação passou de "
            f"{numero(por_periodo.iloc[0])} para "
            f"{numero(por_periodo.iloc[-1])}.",
        ]
        limitacoes = [
            "Correlação não é causa: desemprego, renda e endividamento "
            "também mexem na inadimplência e não estão na análise.",
            "As séries são do total do sistema: não separam pessoa física "
            "e jurídica nem o tipo de crédito.",
            f"{ultimo_ano} tem só {meses_ultimo_ano} meses, então a média "
            f"dele ainda pode mudar.",
        ]
        conteudo = (
            '<div class="colunas">'
            '<div><div class="rotulo">CONCLUSÕES</div>'
            f"<ul>{lista_html(conclusoes)}</ul></div>"
            '<div><div class="rotulo">LIMITAÇÕES</div>'
            f"<ul>{lista_html(limitacoes)}</ul></div>"
            "</div>"
            '<div class="fonte">Fonte: Banco Central do Brasil — Sistema '
            "Gerenciador de Séries Temporais (SGS), séries 21082 e 25433."
            "</div>"
        )
        return Slide("O que os dados mostram", conteudo,
                     subtitulo="Conclusões",
                     nota="Respostas às três perguntas da análise e o que "
                          "ela não consegue responder.")

    # --- Auxiliares ----------------------------------------------------

    def __html_grafico(self, figura: go.Figure, id_div: str) -> str:
        """Converte uma figura do Plotly em HTML para colocar no slide.

        O título sai do gráfico porque já aparece no texto do slide.
        """
        figura.update_layout(title=None,
                             margin={"l": 60, "r": 60, "t": 40, "b": 60})
        figura.update_yaxes(tickformat=".1f")  # uma casa decimal no eixo
        html = figura.to_html(
            full_html=False,
            include_plotlyjs=False,
            div_id=id_div,
            default_width="100%",
            default_height="100%",
            config={"displayModeBar": False, "responsive": True},
        )
        return f'<div class="grafico">{html}</div>'

    def __cores_faixas(self) -> dict[str, tuple[str, str]]:
        """Cor de fundo e cor do texto da etiqueta de cada faixa."""
        tema = self.__visualizador.tema
        escala = tema.get("sequencial", tema["cores"])
        cores = {}
        for i, nome in enumerate(NOMES_FAIXAS):
            # nas faixas mais escuras o texto fica branco
            cor_texto = "#1c1917" if i < 2 else "#ffffff"
            cores[nome] = (escala[i % len(escala)], cor_texto)
        return cores

    # --- Geração do arquivo --------------------------------------------

    def gerar(self, caminho: str | Path) -> Path:
        """Grava a apresentação em um arquivo HTML e devolve o caminho.

        O arquivo final junta o modelo.html com o estilo.css, o
        navegacao.js, os slides e a biblioteca do Plotly. Como o Plotly
        vai dentro do arquivo, a apresentação abre mesmo sem internet.

        Raises:
            ValueError: se ainda não houver slides.
        """
        if len(self.__slides) == 0:
            raise ValueError("Monte os slides antes de gerar o dashboard")

        html_slides = ""
        for numero_slide, slide in enumerate(self.__slides, start=1):
            html_slides += slide.para_html(numero_slide) + "\n"

        html = ler_arquivo("modelo.html")
        html = html.replace("{{TITULO}}", self.__titulo)
        html = html.replace("{{ESTILO}}", ler_arquivo("estilo.css"))
        html = html.replace("{{SLIDES}}", html_slides)
        html = html.replace("{{SCRIPT}}", ler_arquivo("navegacao.js"))
        html = html.replace("{{PLOTLY}}", get_plotlyjs())

        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(html)
        return caminho

    def __len__(self) -> int:
        return len(self.__slides)
