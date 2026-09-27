"""
Humaitá Plásticos: gerador dos ativos vetoriais da marca.

Gera o logo oficial (texto convertido em curvas) e suas variações de cor,
e o símbolo de reciclagem usado no logo. Tudo em SVG puro, com as cores
isoladas em poucas camadas, para que o Canva/Illustrator permitam recolorir.

Uso:  python3 brand/src/humaita.py   (gera os arquivos em brand/logo)
"""
import math
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import BasePen


class CubicSVGPathPen(SVGPathPen):
    """Como SVGPathPen, mas converte curvas quadráticas em cúbicas
    (o Canva só aceita comandos M/L/H/V/C/S/A/Z)."""
    _qCurveToOne = BasePen._qCurveToOne


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fontes")

# ── Paleta institucional ─────────────────────────────────────────────
GRAFITE = "#555555"      # cor oficial do logo (amostrada do original)
BRANCO = "#FFFFFF"
RECICLA_CLARO = "#D9D9D9"  # tons das setas no logo oficial cinza
RECICLA_MEDIO = "#A6A6A6"

_fonts = {}


def font(name):
    if name not in _fonts:
        _fonts[name] = TTFont(os.path.join(FONTS, name + ".ttf"))
    return _fonts[name]


def text_path(txt, fontname, x, y, height=None, width=None, anchor="middle",
              tracking=0.0):
    """Converte texto em um único path SVG.
    height = altura da versal (cap height) desejada; width = largura final.
    (x, y) = ponto de ancoragem na linha de base."""
    f = font(fontname)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    upm = f["head"].unitsPerEm
    cap = getattr(f["OS/2"], "sCapHeight", 700) or 700
    hmtx = f["hmtx"]
    # largura natural
    adv = 0
    glyphs = []
    for ch in txt:
        g = cmap[ord(ch)]
        glyphs.append((g, adv))
        adv += hmtx[g][0] + tracking * upm
    adv -= tracking * upm
    if height is not None:
        s = height / cap
    else:
        s = width / adv
    total = adv * s
    x0 = {"start": x, "middle": x - total / 2, "end": x - total}[anchor]
    pen = CubicSVGPathPen(gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
    for g, off in glyphs:
        tp = TransformPen(pen, (s, 0, 0, -s, x0 + off * s, y))
        gs[g].draw(tp)
    return pen.getCommands(), total


def fmt(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


def rounded_poly(pts, r):
    """Polígono com cantos arredondados (arcos) — path SVG."""
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        u1, u2 = (v1[0] / l1, v1[1] / l1), (v2[0] / l2, v2[1] / l2)
        ang = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
        d = r / math.tan(ang / 2)
        a = (p1[0] + u1[0] * d, p1[1] + u1[1] * d)
        b = (p1[0] + u2[0] * d, p1[1] + u2[1] * d)
        cross = u1[0] * u2[1] - u1[1] * u2[0]
        sweep = 0 if cross > 0 else 1
        out.append((a, b, sweep))
    d = "M%s %s" % (fmt(out[0][0][0]), fmt(out[0][0][1]))
    for i, (a, b, sw) in enumerate(out):
        if i > 0:
            d += "L%s %s" % (fmt(a[0]), fmt(a[1]))
        d += "A%s %s 0 0 %d %s %s" % (fmt(r), fmt(r), sw, fmt(b[0]), fmt(b[1]))
    return d + "Z"


def shield_points(x, y, w, h, inset=0.0):
    """Escudo hexagonal do logo (ponta em cima e embaixo, laterais retas).
    Proporções medidas no logo oficial (344 x 235)."""
    # proporções relativas do original
    top = 0.0
    shoulder = 50 / 235
    hip = 177 / 235
    pts = [(0.5, top), (1, shoulder), (1, hip), (0.5, 1), (0, hip), (0, shoulder)]
    P = [(x + px * w, y + py * h) for px, py in pts]
    if inset:
        P = offset_convex(P, -inset)
    return P


def offset_convex(P, dist):
    """Desloca um polígono convexo (sentido horário na tela) por dist (+ fora)."""
    n = len(P)
    lines = []
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        nx, ny = dy / L, -dx / L  # normal para fora (horário em coords de tela)
        lines.append(((a[0] + nx * dist, a[1] + ny * dist), (dx, dy)))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        out.append((p1[0] + d1[0] * t, p1[1] + d1[1] * t))
    return out


def recycle_arrows(cx, cy, size):
    """Três setas de reciclagem (triângulo de Möbius simplificado).
    size = largura aproximada do símbolo. Retorna lista de 3 paths."""
    R = size * 0.50
    V = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)))
         for a in (-90, 30, 150)]
    L = math.dist(V[0], V[1])
    h = 0.105 * L       # meia largura da faixa
    H = 0.215 * L        # meia largura da cabeça da seta
    paths = []
    for k in range(3):
        Vp, Vk, Vn = V[k - 1], V[k], V[(k + 1) % 3]
        din = ((Vk[0] - Vp[0]) / L, (Vk[1] - Vp[1]) / L)
        dout = ((Vn[0] - Vk[0]) / L, (Vn[1] - Vk[1]) / L)

        def outward(d, a):
            n = (d[1], -d[0])
            mx, my = a[0] - cx, a[1] - cy
            if n[0] * mx + n[1] * my < 0:
                n = (-n[0], -n[1])
            return n
        n1 = outward(din, Vk)
        n2 = outward(dout, Vk)
        tail = (Vk[0] - din[0] * 0.40 * L, Vk[1] - din[1] * 0.40 * L)
        base = (Vk[0] + dout[0] * 0.30 * L, Vk[1] + dout[1] * 0.30 * L)
        tip = (Vk[0] + dout[0] * 0.56 * L, Vk[1] + dout[1] * 0.56 * L)
        k_in = 1 + (n1[0] * n2[0] + n1[1] * n2[1])
        cin = (Vk[0] - h * (n1[0] + n2[0]) / k_in, Vk[1] - h * (n1[1] + n2[1]) / k_in)
        pts_out1 = (Vk[0] + n1[0] * h, Vk[1] + n1[1] * h)
        pts_out2 = (Vk[0] + n2[0] * h, Vk[1] + n2[1] * h)

        def P(p):
            return "%s %s" % (fmt(p[0]), fmt(p[1]))
        # cauda chanfrada (efeito dobra da fita de Möbius)
        t_out = (tail[0] + n1[0] * h + din[0] * h * 0.9, tail[1] + n1[1] * h + din[1] * h * 0.9)
        t_in = (tail[0] - n1[0] * h - din[0] * h * 0.9, tail[1] - n1[1] * h - din[1] * h * 0.9)
        d = "M" + P(t_out)
        d += "L" + P(pts_out1)
        d += "A%s %s 0 0 1 %s" % (fmt(h), fmt(h), P(pts_out2))
        d += "L" + P((base[0] + n2[0] * h, base[1] + n2[1] * h))
        d += "L" + P((base[0] + n2[0] * H, base[1] + n2[1] * H))
        d += "L" + P(tip)
        d += "L" + P((base[0] - n2[0] * H, base[1] - n2[1] * H))
        d += "L" + P((base[0] - n2[0] * h, base[1] - n2[1] * h))
        d += "L" + P(cin)
        d += "L" + P(t_in) + "Z"
        paths.append(d)
    return paths


# ── Logo ─────────────────────────────────────────────────────────────
# Sistema de coordenadas do logo: 380 x 260 (proporções do original).
LOGO_W, LOGO_H = 380, 260


def logo_layers(ox=0, oy=0, scale=1.0):
    """Camadas do logo: dict nome -> path (coordenadas já transformadas)."""
    def T(x, y):
        return ox + x * scale, oy + y * scale
    s = scale
    sx, sy = T(18, 11)
    shield = shield_points(sx, sy, 344 * s, 235 * s)
    layers = {}
    layers["escudo"] = rounded_poly(shield, 22 * s)
    outer_line = shield_points(sx, sy, 344 * s, 235 * s, inset=8 * s)
    inner_line = shield_points(sx, sy, 344 * s, 235 * s, inset=10.6 * s)
    layers["filete"] = rounded_poly(outer_line, 15 * s) + " " + \
        rounded_poly(list(reversed(inner_line)), 12.5 * s)
    cx, _ = T(190, 0)
    txt, _ = text_path("HUMAITÁ", "Quicksand-700", cx, T(0, 168)[1], width=283 * s)
    layers["humaita"] = txt
    txt, _ = text_path("PLÁSTICOS", "Quicksand-700", cx, T(0, 189)[1], width=91 * s,
                       tracking=0.06)
    layers["plasticos"] = txt
    txt, _ = text_path("DESDE", "Quicksand-700", T(108.5, 0)[0], T(0, 83)[1],
                       width=36 * s, tracking=0.08)
    t2, _ = text_path("1979", "Quicksand-700", T(265.5, 0)[0], T(0, 83)[1],
                      width=24 * s, tracking=0.08)
    layers["desde"] = txt + " " + t2
    rc = T(191, 79)
    a = recycle_arrows(rc[0], rc[1], 86 * s)
    layers["seta_a"] = a[0] + " " + a[2]
    layers["seta_b"] = a[1]
    return layers


def logo_svg(fundo, texto=BRANCO, seta1=RECICLA_CLARO, seta2=RECICLA_MEDIO,
             filete=None, titulo="Humaitá Plásticos"):
    L = logo_layers()
    filete = filete or texto
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">'
        % (LOGO_W, LOGO_H, LOGO_W, LOGO_H),
        "<title>%s</title>" % titulo,
        '<path id="escudo" fill="%s" d="%s"/>' % (fundo, L["escudo"]),
        '<path id="filete" fill="%s" fill-rule="evenodd" d="%s"/>' % (filete, L["filete"]),
        '<path id="seta-a" fill="%s" d="%s"/>' % (seta1, L["seta_a"]),
        '<path id="seta-b" fill="%s" d="%s"/>' % (seta2, L["seta_b"]),
        '<path id="humaita" fill="%s" stroke="%s" stroke-width="1.4" stroke-linejoin="round" d="%s"/>' % (texto, texto, L["humaita"]),
        '<path id="texto" fill="%s" d="%s %s"/>' % (texto, L["plasticos"], L["desde"]),
        "</svg>",
    ]
    return "\n".join(parts)


# ── Linhas de produto (cor temática editável) ────────────────────────
LINHAS = [
    # volume, categoria, cor tema, cor escura, nome da cor
    ("20L", "SACO PARA LIXO", "#E07B1A", "#7A3A06", "Laranja"),
    ("40L", "SACO PARA LIXO", "#2E8B3E", "#12461D", "Verde"),
    ("60L", "SACO INDUSTRIAL", "#0B5CAD", "#0A2A5C", "Azul"),
    ("80L", "SACO INDUSTRIAL", "#6B3FA0", "#321A55", "Roxo"),
    ("100L", "SACO INDUSTRIAL", "#C8102E", "#5C0814", "Vermelho"),
    ("100L BL", "SACO INDUSTRIAL", "#0A6B6B", "#053B3B", "Petróleo"),
    ("200L", "SACO INDUSTRIAL", "#8B5A2B", "#3E2711", "Canela"),
]
VERDE_RECICLA = "#2E9E48"   # faixa "PRODUTO 100% RECICLADO" (fixa)
SETA_VERDE_1 = "#8CC63F"    # setas do logo nas etiquetas (sempre verdes)
SETA_VERDE_2 = "#C7E39A"


def main():
    out = os.path.join(ROOT, "logo")
    os.makedirs(out, exist_ok=True)
    files = {
        "humaita-logo-oficial.svg": logo_svg(GRAFITE),
        "humaita-logo-preto.svg": logo_svg("#1A1A1A", seta1="#CFCFCF", seta2="#9C9C9C"),
        "humaita-logo-negativo.svg": logo_svg(BRANCO, texto=GRAFITE, seta1=GRAFITE,
                                              seta2="#8A8A8A"),
    }
    for vol, cat, cor, escura, nome in LINHAS:
        slug = vol.lower().replace(" ", "-")
        files["humaita-logo-%s-%s.svg" % (slug, nome.lower().replace("ó", "o"))] = \
            logo_svg(cor, seta1=SETA_VERDE_1, seta2=SETA_VERDE_2)
    for name, svg in files.items():
        with open(os.path.join(out, name), "w") as fh:
            fh.write(svg)
    print("gerados:", len(files))


if __name__ == "__main__":
    main()
