"""
Logo editável: o mesmo desenho do logo oficial, separado em camadas para trocar
as cores em Illustrator, Inkscape, Figma, Affinity ou Canva.

  Fundo  -> o hexágono
  Setas  -> Seta 1, Seta 2 e Seta 3, cada uma com a sua cor
  Texto  -> HUMAITÁ + PLÁSTICOS + DESDE 1979 + filete, um único elemento

No logo oficial o HUMAITÁ leva um traço de 1,4 para ficar tão encorpado quanto
o original. Traço vira "borda" nos editores e teria de ser recolorido à parte,
então aqui ele é incorporado ao contorno das letras: o texto inteiro é um
preenchimento só, com uma cor só.

Uso: python3 brand/src/logo_editavel.py
Saídas: brand/logo/humaita-logo-editavel.svg e brand/logo/editavel/camadas.json
"""
import json
import math
import os
import re
import sys

from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import humaita as H  # noqa: E402

TRACO_HUMAITA = 1.4  # mesmo stroke-width do logo oficial

CORES_OFICIAIS = {
    "fundo": H.GRAFITE,
    "seta_1": H.RECICLA_CLARO,
    "seta_2": H.RECICLA_MEDIO,
    # Um tom abaixo da seta 1 (diferença invisível): o Canva agrupa a edição de
    # cor de um SVG por valor de cor, então cores iguais mudariam juntas.
    "seta_3": "#D8D8D8",
    "texto": H.BRANCO,
}


# ── Caminho SVG -> polígonos ─────────────────────────────────────────
def _tokens(d):
    return re.findall(r"[MLHVCSAZmlhvcsaz]|-?\d*\.?\d+(?:e-?\d+)?", d)


def aneis(d, passos=10):
    """Achata um path (M/L/H/V/C/Z absolutos, saída do SVGPathPen) em anéis."""
    t = _tokens(d)
    i, cmd = 0, None
    x = y = 0.0
    anel, saida = [], []

    def num():
        nonlocal i
        v = float(t[i])
        i += 1
        return v

    while i < len(t):
        if re.match(r"[A-Za-z]", t[i]):
            cmd = t[i]
            i += 1
            if cmd in "Zz":
                if len(anel) > 2:
                    saida.append(anel)
                anel = []
                continue
        if cmd == "M":
            if len(anel) > 2:
                saida.append(anel)
            x, y = num(), num()
            anel = [(x, y)]
            cmd = "L"
        elif cmd == "L":
            x, y = num(), num()
            anel.append((x, y))
        elif cmd == "H":
            x = num()
            anel.append((x, y))
        elif cmd == "V":
            y = num()
            anel.append((x, y))
        elif cmd == "C":
            x1, y1, x2, y2, x3, y3 = (num() for _ in range(6))
            for k in range(1, passos + 1):
                s = k / passos
                a, b, c, e = (1 - s) ** 3, 3 * (1 - s) ** 2 * s, 3 * (1 - s) * s ** 2, s ** 3
                anel.append((a * x + b * x1 + c * x2 + e * x3, a * y + b * y1 + c * y2 + e * y3))
            x, y = x3, y3
        else:
            raise ValueError("comando não suportado: %s" % cmd)
    if len(anel) > 2:
        saida.append(anel)
    return saida


def _area(r):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(r, r[1:] + r[:1])) / 2


def poligono_nonzero(d):
    """Une os anéis como a regra nonzero (a do SVG e das fontes).

    Na Quicksand as hastes e barras se sobrepõem (a barra do H cruza as hastes),
    então par-ímpar abriria furos nas sobreposições. Contornos no sentido do
    maior são "cheios"; os do sentido oposto são os miolos (A, Á) e furam.
    """
    rs = aneis(d)
    sinal = 1 if _area(max(rs, key=lambda r: abs(_area(r)))) > 0 else -1
    cheios = [Polygon(r).buffer(0) for r in rs if _area(r) * sinal > 0]
    furos = [Polygon(r).buffer(0) for r in rs if _area(r) * sinal < 0]
    return unary_union(cheios).difference(unary_union(furos))


def path_de(geo):
    """Polígono(s) -> path só com M/L/Z; externo anti-horário, furo horário (nonzero ok)."""
    partes = []
    geoms = getattr(geo, "geoms", [geo])
    for g in geoms:
        g = orient(g, sign=1.0)
        for anel in [g.exterior, *g.interiors]:
            pts = list(anel.coords)[:-1]
            partes.append("M" + "L".join("%s %s" % (H.fmt(px), H.fmt(py)) for px, py in pts) + "Z")
    return "".join(partes)


# ── Camadas ──────────────────────────────────────────────────────────
def camadas():
    L = H.logo_layers()
    rc = (191, 79)
    setas = H.recycle_arrows(rc[0], rc[1], 86)  # mesma chamada de logo_layers

    humaita = poligono_nonzero(L["humaita"]).buffer(
        TRACO_HUMAITA / 2, join_style="round", quad_segs=4
    ).simplify(0.03)

    texto = " ".join([L["filete"], path_de(humaita), L["plasticos"], L["desde"]])
    return {
        "fundo": L["escudo"],
        # Ordem: 1 = topo, 2 = direita, 3 = esquerda (sentido horário).
        "seta_1": setas[0],
        "seta_2": setas[1],
        "seta_3": setas[2],
        "texto": texto,
    }


def svg_editavel(c, cores=CORES_OFICIAIS):
    ink = 'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"'

    def camada(id_, rotulo, corpo):
        return ('<g id="%s" inkscape:groupmode="layer" inkscape:label="%s">\n%s\n</g>'
                % (id_, rotulo, corpo))

    def path(id_, rotulo, cor, d):
        return ('  <path id="%s" inkscape:label="%s" fill="%s" d="%s"><title>%s</title></path>'
                % (id_, rotulo, cor, d, rotulo))

    return "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" %s viewBox="0 0 %d %d" width="%d" height="%d">'
        % (ink, H.LOGO_W, H.LOGO_H, H.LOGO_W, H.LOGO_H),
        "<title>Humaitá Plásticos — logo editável</title>",
        "<desc>Camadas: Fundo (hexágono), Setas (3, uma cor cada) e Texto (uma cor). "
        "Troque a cor pelo preenchimento de cada elemento.</desc>",
        camada("Fundo", "Fundo", path("Fundo_hexagono", "Fundo", cores["fundo"], c["fundo"])),
        camada("Setas", "Setas", "\n".join([
            path("Seta_1_topo", "Seta 1 (topo)", cores["seta_1"], c["seta_1"]),
            path("Seta_2_direita", "Seta 2 (direita)", cores["seta_2"], c["seta_2"]),
            path("Seta_3_esquerda", "Seta 3 (esquerda)", cores["seta_3"], c["seta_3"]),
        ])),
        camada("Texto", "Texto", path("Texto", "Texto", cores["texto"], c["texto"])),
        "</svg>",
    ])


def main():
    c = camadas()
    out = os.path.join(H.ROOT, "logo")
    with open(os.path.join(out, "humaita-logo-editavel.svg"), "w") as fh:
        fh.write(svg_editavel(c))
    os.makedirs(os.path.join(out, "editavel"), exist_ok=True)
    with open(os.path.join(out, "editavel", "camadas.json"), "w") as fh:
        json.dump({"viewBox": [H.LOGO_W, H.LOGO_H], "cores": CORES_OFICIAIS, "paths": c},
                  fh, ensure_ascii=False)
    for k, d in c.items():
        print(k, len(d))


if __name__ == "__main__":
    main()
