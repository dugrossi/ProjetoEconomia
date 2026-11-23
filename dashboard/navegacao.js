// Navegação entre os slides e filtros da tabela de dados.

const slides = document.querySelectorAll('.slide');
let atual = 0;

function mostrar(novo, animar = true) {
  novo = Math.max(0, Math.min(slides.length - 1, novo));
  slides.forEach(s => s.classList.remove('ativo', 'entrando'));
  slides[novo].classList.add('ativo');
  if (animar) slides[novo].classList.add('entrando');
  atual = novo;

  // o Plotly desenha errado em slides escondidos, então redimensiona ao mostrar
  slides[novo].querySelectorAll('.plotly-graph-div').forEach(g => Plotly.Plots.resize(g));

  document.querySelector('.barra').style.width = ((novo + 1) / slides.length * 100) + '%';
  document.querySelector('.contador').textContent = (novo + 1) + ' / ' + slides.length;
  history.replaceState(null, '', '#' + (novo + 1));
}

document.querySelector('.zona.dir').onclick = () => mostrar(atual + 1);
document.querySelector('.zona.esq').onclick = () => mostrar(atual - 1);
// Teclado e passador de slides (o passador manda PageDown / PageUp)
const AVANCAR = ['ArrowRight', 'ArrowDown', 'PageDown', ' ', 'Enter'];
const VOLTAR = ['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'];
document.addEventListener('keydown', e => {
  if (AVANCAR.includes(e.key)) { e.preventDefault(); mostrar(atual + 1); }
  if (VOLTAR.includes(e.key)) { e.preventDefault(); mostrar(atual - 1); }
});

// ---------- filtros da tabela ----------
function filtrarTabela() {
  const de = +document.getElementById('filtro-de').value;
  const ate = +document.getElementById('filtro-ate').value;
  const faixa = document.getElementById('filtro-faixa').value;
  let visiveis = 0;
  document.querySelectorAll('#tabela-dados tbody tr').forEach(linha => {
    const ano = +linha.dataset.ano;
    const mostra = ano >= de && ano <= ate && (faixa === '' || linha.dataset.faixa === faixa);
    linha.style.display = mostra ? '' : 'none';
    if (mostra) visiveis++;
  });
  document.getElementById('total-linhas').textContent = visiveis + ' meses';
}
// depois de usar um filtro, tira o foco dele para as setas voltarem a passar slide
document.querySelectorAll('.filtros select').forEach(s => s.onchange = () => {
  filtrarTabela();
  s.blur();
});
if (document.getElementById('tabela-dados')) filtrarTabela();

// abre no slide do endereço (ex.: dashboard.html#4) ou no primeiro
const inicial = parseInt(location.hash.slice(1), 10);
mostrar(isNaN(inicial) ? 0 : inicial - 1, false);
