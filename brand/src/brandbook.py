"""
Gera o Brandbook da Humaitá Plásticos (brand/brandbook.html).
As cores e linhas de produto vêm de humaita.py / etiqueta.py — fonte única.

Uso: python3 brand/src/brandbook.py [--fragmento saida.html]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import humaita as H  # noqa: E402
import etiqueta as E  # noqa: E402

CANVA_URL = "https://www.canva.com/d/DS0E-_djYZKPDzL"


def svg_inline(nome):
    s = open(os.path.join(H.ROOT, "logo", nome)).read()
    return s.replace('width="380" height="260"', 'role="img" aria-label="Logo Humaitá Plásticos"')


def swatch(hexa, nome, uso, claro=False):
    borda = " sw-borda" if claro else ""
    return ('<div class="sw"><span class="sw-cor%s" style="background:%s"></span>'
            '<span class="sw-nome">%s</span><code>%s</code><span class="sw-uso">%s</span></div>'
            % (borda, hexa, nome, hexa.upper(), uso))


def linhas_tabela():
    rows = []
    for p in E.PRODUTOS:
        rows.append(
            "<tr><td><strong>%s</strong></td><td>%s</td>"
            '<td><span class="chip" style="background:%s"></span><code>%s</code></td>'
            '<td><span class="chip" style="background:%s"></span><code>%s</code></td>'
            "<td>%s</td></tr>"
            % (p["volume"], p["nome_cor"], p["cor"], p["cor"], p["escura"], p["escura"],
               p["categoria"].title()))
    return "\n".join(rows)


def galeria():
    out = []
    for p in E.PRODUTOS:
        out.append('<figure class="etq"><img src="etiquetas/png/etiqueta-%s.png" '
                   'alt="Etiqueta %s na cor %s" width="397" height="559">'
                   '<figcaption><span class="chip" style="background:%s"></span>%s · %s'
                   '</figcaption></figure>' % (p["slug"], p["volume"], p["nome_cor"],
                                               p["cor"], p["volume"], p["nome_cor"]))
    return "\n".join(out)


def logos_linha():
    out = []
    for vol, _, cor, _, nome in H.LINHAS:
        slug = vol.lower().replace(" ", "-")
        arq = "humaita-logo-%s-%s.svg" % (slug, nome.lower().replace("ó", "o"))
        out.append('<figure class="logo-mini">%s<figcaption>%s · %s</figcaption></figure>'
                   % (svg_inline(arq), vol, nome))
    return "\n".join(out)


CSS = r"""
:root{
  --bg:#F5F5F2; --surface:#FFFFFF; --ink:#1E2222; --ink-2:#4A4F4E; --mute:#767C7A;
  --line:#DCDDD8; --brand:#555555; --verde:#2E9E48; --verde-ink:#1F7A35;
  --radius:10px;
  --f-display:"Quicksand", "Nunito Sans", system-ui, sans-serif;
  --f-body:"Nunito Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono:"IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#151818; --surface:#1D2121; --ink:#ECEDEA; --ink-2:#C3C7C4; --mute:#8F9592;
    --line:#2F3434; --verde-ink:#5CC377; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --bg:#151818; --surface:#1D2121; --ink:#ECEDEA; --ink-2:#C3C7C4; --mute:#8F9592;
  --line:#2F3434; --verde-ink:#5CC377; color-scheme:dark;
}
*{box-sizing:border-box}
body{background:var(--bg); color:var(--ink); font-family:var(--f-body); font-size:16px;
  line-height:1.6; margin:0; padding-inline:clamp(16px,4vw,48px); padding-block:0 64px}
.wrap{max-width:1120px; margin:0 auto}
h1,h2,h3{font-family:var(--f-display); font-weight:700; line-height:1.15; text-wrap:balance; margin:0}
h2{font-size:clamp(26px,3.4vw,34px)}
h3{font-size:19px}
p{margin:0; max-width:65ch; color:var(--ink-2)}
code{font-family:var(--f-mono); font-size:13px}
.eyebrow{font-family:var(--f-display); font-weight:700; font-size:12px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--verde-ink)}
header.capa{display:grid; grid-template-columns:minmax(0,1.1fr) minmax(0,1fr); gap:40px;
  align-items:center; padding-block:56px 48px; border-bottom:1px solid var(--line)}
.capa h1{font-size:clamp(34px,5vw,56px); letter-spacing:-.01em}
.capa .sub{margin-top:14px; font-size:18px}
.capa .logo-hero{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  padding:clamp(20px,4vw,40px); display:grid; place-items:center}
.capa .logo-hero svg{width:100%; max-width:420px; height:auto}
.meta{display:flex; flex-wrap:wrap; gap:8px 20px; margin-top:22px; font-size:14px; color:var(--mute)}
.meta strong{color:var(--ink)}
nav.indice{display:flex; flex-wrap:wrap; gap:6px 18px; padding-block:18px; border-bottom:1px solid var(--line);
  font-family:var(--f-display); font-weight:600; font-size:14px}
nav.indice a{color:var(--ink-2); text-decoration:none}
nav.indice a:hover,nav.indice a:focus-visible{color:var(--verde-ink); text-decoration:underline}
section{padding-block:56px; border-bottom:1px solid var(--line); display:grid; gap:28px}
.intro{display:grid; gap:10px}
.grid-2{display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:24px}
.painel{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); padding:22px;
  display:grid; gap:10px; align-content:start}
.painel.escuro{background:#555555; border-color:#555555}
.painel.preto{background:#1A1A1A; border-color:#1A1A1A}
.painel svg{width:100%; max-width:300px; height:auto; justify-self:center}
.painel .rot{font-size:13px; color:var(--mute)}
.painel.escuro .rot,.painel.preto .rot{color:#E6E6E6}
ul.regras{margin:0; padding-left:20px; color:var(--ink-2); display:grid; gap:6px; max-width:70ch}
.faz-nao{display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px}
.nao{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); padding:14px;
  display:grid; gap:8px}
.nao .quadro{height:110px; display:grid; place-items:center; overflow:hidden; border-radius:6px;
  background:repeating-linear-gradient(45deg,transparent 0 8px,rgba(200,16,46,.05) 8px 16px)}
.nao .quadro svg{height:86px; width:auto}
.nao p{font-size:14px}
.nao strong{color:#C8102E; font-family:var(--f-display)}
.sws{display:grid; grid-template-columns:repeat(auto-fill,minmax(170px,1fr)); gap:16px}
.sw{display:grid; gap:4px; font-size:14px}
.sw-cor{height:84px; border-radius:8px; display:block}
.sw-borda{box-shadow:inset 0 0 0 1px var(--line)}
.sw-nome{font-family:var(--f-display); font-weight:700; margin-top:6px}
.sw code{color:var(--ink-2)}
.sw-uso{color:var(--mute); font-size:13px; line-height:1.4}
.tabela{overflow-x:auto; border:1px solid var(--line); border-radius:var(--radius); background:var(--surface)}
table{border-collapse:collapse; width:100%; font-size:15px; min-width:620px}
th,td{padding:12px 16px; text-align:left; border-bottom:1px solid var(--line); white-space:nowrap}
th{font-family:var(--f-display); font-size:12px; letter-spacing:.1em; text-transform:uppercase; color:var(--mute)}
tr:last-child td{border-bottom:0}
td{font-variant-numeric:tabular-nums}
.chip{display:inline-block; width:14px; height:14px; border-radius:4px; vertical-align:-2px; margin-right:8px}
.logos-linha{display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:16px}
.logo-mini{margin:0; background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
  padding:14px; display:grid; gap:8px; justify-items:center; font-size:13px; color:var(--mute)}
.logo-mini svg{width:100%; height:auto}
.tipo{display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:24px}
.amostra{font-family:"Quicksand",sans-serif; line-height:1.1}
.amostra.a1{font-size:64px; font-weight:700}
.amostra.a2{font-size:28px; font-weight:700; letter-spacing:.06em}
.amostra.a3{font-size:18px; font-weight:500}
.escala{display:grid; gap:6px; font-size:14px; color:var(--ink-2)}
.escala div{display:flex; justify-content:space-between; gap:12px; border-bottom:1px dashed var(--line); padding-block:6px}
.anatomia{display:grid; grid-template-columns:minmax(0,340px) minmax(0,1fr); gap:32px; align-items:start}
.anatomia img{width:100%; height:auto; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,.12)}
.setores{display:grid; gap:12px; counter-reset:s}
.setor{display:grid; grid-template-columns:34px 1fr; gap:12px; align-items:start}
.setor .n{font-family:var(--f-display); font-weight:700; width:34px; height:34px; border-radius:50%;
  display:grid; place-items:center; font-size:15px; color:#fff; background:var(--brand)}
.setor.din .n{background:var(--verde)}
.setor h3{font-size:16px}
.setor p{font-size:14.5px}
.tag{font-family:var(--f-display); font-size:11px; font-weight:700; letter-spacing:.08em; text-transform:uppercase;
  padding:2px 8px; border-radius:99px; margin-left:8px; vertical-align:2px}
.tag.fixo{background:rgba(85,85,85,.14); color:var(--ink-2)}
.tag.dinamico{background:rgba(46,158,72,.16); color:var(--verde-ink)}
.galeria{display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:20px}
.etq{margin:0; display:grid; gap:8px}
.etq img{width:100%; height:auto; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,.12); background:#fff}
.etq figcaption{font-family:var(--f-display); font-weight:700; font-size:14px}
ol.passos{margin:0; padding-left:22px; display:grid; gap:10px; color:var(--ink-2); max-width:72ch}
ol.passos strong{color:var(--ink)}
.cta{display:inline-flex; align-items:center; gap:8px; background:var(--verde); color:#fff; text-decoration:none;
  font-family:var(--f-display); font-weight:700; padding:12px 20px; border-radius:8px; justify-self:start}
.cta:hover,.cta:focus-visible{background:#258a3d}
.pend{display:grid; gap:10px}
.pend div{background:var(--surface); border:1px solid var(--line); border-left:4px solid #E0A21A;
  border-radius:8px; padding:12px 16px; font-size:14.5px; color:var(--ink-2)}
.pend strong{color:var(--ink)}
footer{padding-top:32px; font-size:13px; color:var(--mute)}
@media (max-width:760px){
  header.capa{grid-template-columns:1fr}
  .anatomia{grid-template-columns:1fr}
  .amostra.a1{font-size:44px}
}
"""


def pagina():
    fixos = [(H.GRAFITE, "Grafite Humaitá", "Cor oficial do logo. Escudo em fundo claro.", False),
             ("#FFFFFF", "Branco", "Texto e filete do logo; fundo das etiquetas.", True),
             (H.VERDE_RECICLA, "Verde Reciclagem", "Faixa “Produto 100% Reciclado”. Fixa.", False),
             (H.SETA_VERDE_1, "Verde Folha", "Setas do logo nas etiquetas (tom 1).", False),
             (H.SETA_VERDE_2, "Verde Broto", "Setas do logo nas etiquetas (tom 2).", False),
             (E.CINZA_ROTULO, "Cinza Rótulo", "Rótulos da ficha técnica (DIMENSÕES:…).", False),
             (E.LINHA_FINA, "Cinza Filete", "Linhas divisórias finas.", True),
             ("#111111", "Preto Código", "Barras e números do EAN-13.", False)]
    sws = "\n".join(swatch(*f) for f in fixos)

    setores = [
        (1, False, "Topo — marca", "Logo oficial em escudo hexagonal na cor da linha, com as setas de "
         "reciclagem sempre verdes, “DESDE 1979” e “PLÁSTICOS”. Fundo branco."),
        (2, True, "Volume e categoria", "Volume em corpo grande, na vertical (20L · 40L · 60L · 80L · "
         "100L · 100L BL · 200L). Abaixo, a categoria: SACO PARA LIXO ou SACO INDUSTRIAL."),
        (3, True, "Ficha técnica", "Quatro linhas com ícone em traço: Dimensões (régua), Capacidade "
         "(balança), Tipo/Cor (saco) e Quantidade (pacote)."),
        (4, False, "Faixa de sustentabilidade", "Faixa verde sólida com “PRODUTO 100% RECICLADO” em "
         "branco. Mesma cor em todas as linhas."),
        (5, False, "Selos de qualidade", "Três colunas discretas: Qualidade Premium (estrela), "
         "Resistente e Seguro (check), Uso Doméstico e Profissional (casa)."),
        (6, False, "Rodapé legal", "Fabricante e CNPJ, avisos e composição, símbolo de reciclabilidade "
         "4 · PEBD e código de barras EAN-13 em box branco. O fundo usa o tom escuro da linha."),
    ]
    set_html = "\n".join(
        '<div class="setor%s"><span class="n">%d</span><div><h3>%s<span class="tag %s">%s</span></h3>'
        "<p>%s</p></div></div>" % (" din" if d else "", n, t, "dinamico" if d else "fixo",
                                    "dinâmico" if d else "fixo", txt)
        for n, d, t, txt in setores)

    oficial = svg_inline("humaita-logo-oficial.svg")
    preto = svg_inline("humaita-logo-preto.svg")
    negativo = svg_inline("humaita-logo-negativo.svg")
    distorcido = oficial.replace("<svg ", '<svg preserveAspectRatio="none" style="width:200px;height:70px" ', 1)
    girado = oficial.replace("<svg ", '<svg style="transform:rotate(-12deg)" ', 1)
    semcontraste = oficial.replace('fill="#555555"', 'fill="#C7C7C7"')

    return """<title>Brandbook Humaitá Plásticos</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Quicksand:wght@500;600;700&family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,700&family=IBM+Plex+Mono:wght@400&display=swap">
<style>%(css)s</style>
<div class="wrap">
<header class="capa">
  <div>
    <p class="eyebrow">Manual de identidade visual · 2026</p>
    <h1>Humaitá Plásticos</h1>
    <p class="sub">Regras de uso da marca e o padrão de etiqueta A6 para toda a linha de sacos de lixo e industriais em PEBD reciclado.</p>
    <div class="meta"><span><strong>Fundação</strong> 1979</span><span><strong>Razão social</strong> Recuperadora de Plásticos Humaitá</span><span><strong>CNPJ</strong> 45.421.146/0001-49</span></div>
  </div>
  <div class="logo-hero">%(oficial)s</div>
</header>
<nav class="indice" aria-label="Seções"><a href="#logo">Logo</a><a href="#cores">Cores</a><a href="#linhas">Cores por linha</a><a href="#tipografia">Tipografia</a><a href="#etiqueta">Etiqueta A6</a><a href="#canva">Editar no Canva</a><a href="#pendencias">Pendências</a></nav>

<section id="logo">
  <div class="intro"><p class="eyebrow">01 · Logo</p><h2>Um escudo, uma cor por vez</h2>
  <p>O logo oficial é o escudo hexagonal grafite com filete branco, as três setas de reciclagem no topo, “DESDE 1979” e o nome HUMAITÁ sobre PLÁSTICOS. Ele foi redesenhado em vetor a partir do arquivo original, com o texto convertido em curvas, para que possa ser recolorido sem perder a forma.</p></div>
  <div class="grid-2">
    <div class="painel">%(oficial)s<span class="rot">Versão oficial · Grafite <code>#555555</code> · uso preferencial em fundos claros</span></div>
    <div class="painel preto">%(preto)s<span class="rot">Versão preta · para impressão em 1 cor</span></div>
    <div class="painel escuro">%(negativo)s<span class="rot">Negativo · sobre fundos escuros ou fotos</span></div>
  </div>
  <h3>Regras de uso</h3>
  <ul class="regras">
    <li><strong>Área de proteção:</strong> mantenha em volta do escudo um espaço livre igual à altura das letras de “HUMAITÁ”.</li>
    <li><strong>Tamanho mínimo:</strong> 25 mm de largura impresso (ou 120 px em tela). Abaixo disso “DESDE 1979” deixa de ser legível.</li>
    <li><strong>Nas etiquetas,</strong> o escudo assume a cor da linha do produto e as setas ficam sempre verdes. Letras e filete continuam brancos.</li>
    <li><strong>Não use</strong> a versão com “DESDE 1979” abaixo do escudo que aparecia na etiqueta antiga: ela não é a marca oficial.</li>
  </ul>
  <h3>Usos incorretos</h3>
  <div class="faz-nao">
    <div class="nao"><div class="quadro">%(distorcido)s</div><p><strong>Não distorça.</strong> Redimensione sempre proporcionalmente.</p></div>
    <div class="nao"><div class="quadro">%(girado)s</div><p><strong>Não gire</strong> nem incline o escudo.</p></div>
    <div class="nao"><div class="quadro">%(semcontraste)s</div><p><strong>Não use tons sem contraste.</strong> O texto branco precisa de fundo firme.</p></div>
    <div class="nao"><div class="quadro"><span style="font-family:Georgia,serif;font-size:30px;font-weight:700;color:#555">HUMAITÁ</span></div><p><strong>Não troque a fonte</strong> nem escreva o nome sem o escudo como se fosse o logo.</p></div>
  </div>
</section>

<section id="cores">
  <div class="intro"><p class="eyebrow">02 · Cores institucionais</p><h2>Base fixa</h2>
  <p>Estas cores não mudam entre produtos. O grafite é a cor da marca; o verde marca o compromisso com o reciclado.</p></div>
  <div class="sws">%(sws)s</div>
</section>

<section id="linhas">
  <div class="intro"><p class="eyebrow">03 · Cores por linha</p><h2>Cada volume tem a sua cor</h2>
  <p>Cada linha usa duas cores: a <strong>cor tema</strong> (escudo, volume, barra vertical e ícones) e o <strong>tom escuro</strong> (categoria, valores da ficha, textos dos selos e fundo do rodapé). As cores podem ser trocadas; ao criar uma linha nova, escolha um par e registre aqui.</p></div>
  <div class="tabela"><table><thead><tr><th>Linha</th><th>Cor</th><th>Cor tema</th><th>Tom escuro</th><th>Categoria</th></tr></thead><tbody>%(linhas)s</tbody></table></div>
  <div class="logos-linha">%(logos)s</div>
</section>

<section id="tipografia">
  <div class="intro"><p class="eyebrow">04 · Tipografia</p><h2>Quicksand em toda a marca</h2>
  <p>A Quicksand, de terminais arredondados, é a família mais próxima do letreiro do logo. Está disponível no Canva e no Google Fonts. Use Bold para títulos, volume e valores; Medium para textos corridos e avisos.</p></div>
  <div class="tipo">
    <div class="painel"><span class="amostra a1">60L</span><span class="amostra a2">SACO INDUSTRIAL</span><span class="amostra a3">Fabricado e embalado por Recuperadora de Plásticos Humaitá.</span></div>
    <div class="painel"><h3>Escala da etiqueta A6</h3>
      <div class="escala">
        <div><span>Volume (vertical)</span><code>88–96 px · Bold</code></div>
        <div><span>Faixa “Produto 100%% reciclado”</span><code>17 px · Bold</code></div>
        <div><span>Valores da ficha técnica</span><code>15 px · Bold</code></div>
        <div><span>Categoria</span><code>13 px · Bold</code></div>
        <div><span>Rótulos da ficha · selos</span><code>8–9 px · Bold</code></div>
        <div><span>Avisos legais</span><code>7 px · Medium</code></div>
      </div></div>
  </div>
</section>

<section id="etiqueta">
  <div class="intro"><p class="eyebrow">05 · Etiqueta padrão A6 (105 × 148 mm)</p><h2>Seis setores, dois que mudam</h2>
  <p>Os setores 1, 4, 5 e 6 são fixos: não mudam layout, texto nem posição. Só os setores 2 e 3 são preenchidos conforme a ordem de produção. A cor tema troca por linha, e o fundo da área de dados é sempre branco para facilitar a leitura.</p></div>
  <div class="anatomia"><img src="etiquetas/png/etiqueta-60l.png" alt="Etiqueta A6 da linha 60L azul" width="397" height="559"><div class="setores">%(setores)s</div></div>
  <h3>Todas as linhas</h3>
  <div class="galeria">%(galeria)s</div>
</section>

<section id="canva">
  <div class="intro"><p class="eyebrow">06 · Como editar no Canva</p><h2>Um arquivo, uma página por linha</h2>
  <p>O arquivo “Humaitá Plásticos — Etiquetas A6 (padrão)” tem 7 páginas, uma por linha. Tudo nele é forma e texto nativo do Canva, então as cores e os textos são editáveis.</p></div>
  <a class="cta" href="%(canva)s" target="_blank" rel="noopener">Abrir as etiquetas no Canva ↗</a>
  <ol class="passos">
    <li><strong>Nova linha:</strong> duplique a página mais parecida (botão “Duplicar página”).</li>
    <li><strong>Trocar a cor:</strong> clique no escudo, abra a cor e escolha a nova cor tema; use “Alterar tudo” para aplicar em todos os elementos daquela cor. Repita para o tom escuro (clique no rodapé). Os ícones em traço mudam pela cor da borda.</li>
    <li><strong>Textos dinâmicos:</strong> edite o volume, a categoria e as quatro linhas da ficha técnica. Não altere os setores fixos.</li>
    <li><strong>Fonte:</strong> selecione todos os textos da página (Ctrl/Cmd + A com a página ativa) e aplique Quicksand. O logo já está em curvas e não precisa disso.</li>
    <li><strong>Código de barras:</strong> gere o EAN-13 real do produto (app “Barcodes” do Canva ou o gerador da GS1) e substitua o bloco de barras e os números.</li>
    <li><strong>Impressão:</strong> baixe em “PDF para impressão”, tamanho A6, com marcas de corte e sangria se a gráfica pedir.</li>
  </ol>
</section>

<section id="pendencias">
  <div class="intro"><p class="eyebrow">07 · Pendências</p><h2>O que ainda precisa ser confirmado</h2></div>
  <div class="pend">
    <div><strong>Dimensões</strong> de 20L, 80L, 100L, 100L BL e 200L estão como “00 cm x 00 cm”. Só 40L (40 × 50 cm) e 60L (63 × 76 cm) vieram no briefing.</div>
    <div><strong>Capacidade em kg</strong> de 20L, 80L, 100L e 200L foi estimada pela proporção do briefing (5 L por kg). Confirme com a produção.</div>
    <div><strong>Código de barras:</strong> a imagem de referência mostrava “8 789813 115151 6”, que não é um EAN-13 válido. As etiquetas usam 7898131151516 (prefixo Brasil 789, dígito verificador correto) como exemplo. Cada produto precisa do seu código registrado na GS1.</div>
    <div><strong>100L BL:</strong> confirme o significado da sigla, o tipo (usado como TRANSPARENTE CRISTAL) e a quantidade (5 KG).</div>
    <div><strong>Cores por linha:</strong> azul (60L), verde (40L) e vermelho (100L) seguem o briefing; laranja, roxo, petróleo e canela são sugestões.</div>
  </div>
</section>
<footer>Humaitá Plásticos · Manual de identidade visual. Arquivos-fonte no repositório: <code>brand/</code> (logos em SVG, gerador das etiquetas e deste manual).</footer>
</div>
""" % dict(css=CSS, oficial=oficial, preto=preto, negativo=negativo, distorcido=distorcido,
           girado=girado, semcontraste=semcontraste, sws=sws, linhas=linhas_tabela(),
           logos=logos_linha(), setores=set_html, galeria=galeria(), canva=CANVA_URL)


def main():
    frag = pagina()
    doc = ('<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width, initial-scale=1">\n%s\n</html>' % frag)
    with open(os.path.join(H.ROOT, "brandbook.html"), "w") as fh:
        fh.write(doc)
    if "--fragmento" in sys.argv:
        with open(sys.argv[sys.argv.index("--fragmento") + 1], "w") as fh:
            fh.write(frag)
    print("brandbook ok")


if __name__ == "__main__":
    main()
