"""
Humaitá Plásticos: gerador da etiqueta padrão A6 (105 x 148 mm).

Descreve a etiqueta como uma lista de elementos (formas vetoriais + textos)
em coordenadas de página do Canva (397 x 559 px = A6 a 96 dpi). A partir
dessa descrição gera:

  • brand/etiquetas/etiqueta-<linha>.html   prévia fiel / impressão
  • brand/etiquetas/canva/<linha>.json      operações para montar no Canva

Cores:  T = cor tema da linha, D = tom escuro da linha. Todo o resto é fixo.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import humaita as H  # noqa: E402

W, PH = 397, 559
CINZA_ROTULO = "#6B6B6B"
LINHA_FINA = "#DADADA"
PRETO = "#111111"

# ── Ícones outline (viewBox 24 x 24, traço) ───────────────────────────
ICONES = {
    "regua": "M2.5 16.5 L16.5 2.5 L21.5 7.5 L7.5 21.5 Z M6 13 L8 15 M8.5 10.5 L11.5 13.5 "
             "M11 8 L13 10 M13.5 5.5 L16.5 8.5",
    "balanca": "M5 9 H19 L20.5 21 H3.5 Z M12 12.2 A3 3 0 1 1 11.99 12.2 M12 15.2 L13.4 13.8 "
               "M9 9 V6 A3 3 0 0 1 15 6 V9",
    "saco": "M8.5 8 C5 11.5 3.8 15.5 4.6 19 C5.2 21.3 18.8 21.3 19.4 19 "
            "C20.2 15.5 19 11.5 15.5 8 Z M8.5 8 L7 3.5 L10.2 5.4 L12 3 L13.8 5.4 L17 3.5 L15.5 8",
    "pacote": "M3 7.5 L12 3 L21 7.5 V16.5 L12 21 L3 16.5 Z M3 7.5 L12 12 L21 7.5 M12 12 V21 "
              "M7.5 5.2 L16.5 9.7 V13",
    "check": "M6.5 12.5 L10.5 16.5 L17.5 8.5",
    "casa": "M3.5 11.5 L12 4 L20.5 11.5 M6 9.5 V20 H18 V9.5 M10 20 V14.5 H14 V20",
}


def estrela(cx=12, cy=12, r1=8.5, r2=3.7):
    pts = []
    for i in range(10):
        r = r1 if i % 2 == 0 else r2
        a = math.radians(-90 + i * 36)
        pts.append("%s %s" % (H.fmt(cx + r * math.cos(a)), H.fmt(cy + r * math.sin(a))))
    return "M" + " L".join(pts) + " Z"


ICONES["estrela"] = estrela()

# ── EAN-13 ────────────────────────────────────────────────────────────
_L = ["0001101", "0011001", "0010011", "0111101", "0100011",
      "0110001", "0101111", "0111011", "0110111", "0001011"]
_G = ["0100111", "0110011", "0011011", "0100001", "0011101",
      "0111001", "0000101", "0010001", "0001001", "0010111"]
_R = ["1110010", "1100110", "1101100", "1000010", "1011100",
      "1001110", "1010000", "1000100", "1001000", "1110100"]
_PAR = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG",
        "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]


def ean13_digito(d12):
    s = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(d12))
    return str((10 - s % 10) % 10)


def ean13_modulos(code):
    assert len(code) == 13 and ean13_digito(code[:12]) == code[12], "EAN-13 inválido"
    first, left, right = int(code[0]), code[1:7], code[7:]
    bits = "101"
    for c, p in zip(left, _PAR[first]):
        bits += (_L if p == "L" else _G)[int(c)]
    bits += "01010"
    for c in right:
        bits += _R[int(c)]
    bits += "101"
    return bits  # 95 módulos


def ean13_path(code, w, h, guard_extra):
    """Path com as barras; viewBox = (95 módulos) x (h + guard_extra)."""
    bits = ean13_modulos(code)
    guard = set(list(range(0, 3)) + list(range(45, 50)) + list(range(92, 95)))
    d = []
    i = 0
    while i < 95:
        if bits[i] == "1":
            j = i
            while j < 95 and bits[j] == "1" and ((j in guard) == (i in guard)):
                j += 1
            hh = h + (guard_extra if i in guard else 0)
            d.append("M%d 0 H%d V%s H%d Z" % (i, j, H.fmt(hh), i))
            i = j
        else:
            i += 1
    return " ".join(d)


# ── Montagem da etiqueta ──────────────────────────────────────────────
def shape(path, left, top, width, height, vbw, vbh, fill=None, stroke=None,
          sw=None, opacity=None, role=""):
    return dict(kind="shape", path=path, left=left, top=top, width=width,
                height=height, vbw=vbw, vbh=vbh, fill=fill, stroke=stroke,
                sw=sw, opacity=opacity, role=role)


def text(txt, left, top, width, size, color, bold=False, align="start",
         lh=1.15, rotation=0, role="", spacing=0):
    return dict(kind="text", text=txt, left=left, top=top, width=width,
                size=size, color=color, bold=bold, align=align, lh=lh,
                rotation=rotation, role=role, spacing=spacing)


def rect(left, top, w, h, r=0):
    if r:
        return H.rounded_poly([(0, 0), (w, 0), (w, h), (0, h)], r), w, h
    return "M0 0 H%s V%s H0 Z" % (H.fmt(w), H.fmt(h)), w, h


def tamanho_volume(vol):
    """Tamanho de fonte para o volume vertical caber em ~166 px."""
    f = H.font("Quicksand-700")
    cmap, hmtx = f.getBestCmap(), f["hmtx"]
    adv = sum(hmtx[cmap[ord(c)]][0] for c in vol) / f["head"].unitsPerEm
    return int(min(104, 166 / adv))


def etiqueta(p):
    T, D = p["cor"], p["escura"]
    E = []
    # fundo branco (garante base branca no Canva)
    d, w, h = rect(0, 0, W, PH)
    E.append(shape(d, 0, 0, W, PH, w, h, fill="#FFFFFF", role="fundo"))

    # SETOR 1 — logo oficial recolorido (vetor)
    lw = 200
    lh_ = lw * H.LOGO_H / H.LOGO_W
    lx, ly = (W - lw) / 2, 10
    L = H.logo_layers()
    for key, fill in (("escudo", T), ("filete", "#FFFFFF"), ("seta_a", H.SETA_VERDE_1),
                      ("seta_b", H.SETA_VERDE_2), ("humaita", "#FFFFFF"),
                      ("plasticos", "#FFFFFF"), ("desde", "#FFFFFF")):
        E.append(shape(L[key], lx, ly, lw, lh_, H.LOGO_W, H.LOGO_H, fill=fill,
                       role="logo-" + key))

    # SETOR 2 — volume vertical + categoria
    top2, bot2 = 160, 352
    fs = tamanho_volume(p["volume"])
    box_w = 176
    cx, cy = 68, 238
    E.append(text(p["volume"], cx - box_w / 2, cy - fs * 0.5, box_w, fs, T, bold=True,
                  align="center", lh=1.0, rotation=-90, role="volume"))
    cat = p["categoria"].replace(" ", "\n", 1)
    E.append(text(cat, 12, 321, 118, 13, D, bold=True, lh=1.05, role="categoria"))
    # barra de destaque vertical (dois tons pela opacidade)
    bx, by, bw, bh = 132, top2 + 6, 6, bot2 - top2 - 10
    d, w, h = rect(0, 0, bw, bh, 3)
    E.append(shape(d, bx, by, bw, bh, w, h, fill=T, opacity=0.28, role="barra-fundo"))
    fh = bh * 0.58
    d, w, h = rect(0, 0, bw, fh, 3)
    E.append(shape(d, bx, by + bh - fh, bw, fh, w, h, fill=T, role="barra"))

    # SETOR 3 — ficha técnica
    rx, rw = 150, 233
    rows = [("DIMENSÕES:", p["dimensoes"], "regua"),
            ("CAPACIDADE:", p["capacidade"], "balanca"),
            ("TIPO:", p["tipo"], "saco"),
            ("QUANTIDADE:", p["quantidade"], "pacote")]
    rh = 47
    for i, (lab, val, ic) in enumerate(rows):
        y = top2 + 4 + i * rh
        E.append(text(lab, rx, y + 5, 190, 8, CINZA_ROTULO, bold=True, lh=1.0,
                      role="rotulo", spacing=40))
        E.append(text(val, rx, y + 17, 196, 15, D, bold=True, lh=1.0, role="valor-%d" % i))
        E.append(shape(ICONES[ic], rx + rw - 27, y + 9, 27, 27, 24, 24, stroke=T, sw=1.6,
                       role="icone"))
        if i < 3:
            d, w, h = rect(0, 0, rw, 0.8)
            E.append(shape(d, rx, y + rh - 1, rw, 0.8, w, h, fill=LINHA_FINA, role="linha"))

    # SETOR 4 — faixa de sustentabilidade (fixa, verde)
    fy, fhh = 358, 38
    d, w, h = rect(0, 0, W, fhh)
    E.append(shape(d, 0, fy, W, fhh, w, h, fill=H.VERDE_RECICLA, role="faixa"))
    E.append(text("PRODUTO 100% RECICLADO", 0, fy + 10.5, W, 17, "#FFFFFF", bold=True,
                  align="center", lh=1.0, role="faixa-texto", spacing=30))

    # SETOR 5 — selos de qualidade
    sy = 404
    col = W / 3
    selos = [("estrela", "Qualidade\nPremium"), ("check", "Resistente\ne Seguro"),
             ("casa", "Uso Doméstico\ne Profissional")]
    for i, (ic, lab) in enumerate(selos):
        x0 = i * col
        circ = "M13 1 A12 12 0 1 1 12.99 1 Z"
        E.append(shape(circ, x0 + 12, sy + 11, 26, 26, 26, 26, stroke=T, sw=1.3,
                       role="selo-circulo"))
        if ic == "estrela":
            E.append(shape(ICONES[ic], x0 + 18, sy + 17, 14, 14, 24, 24, fill=T, role="selo-icone"))
        else:
            E.append(shape(ICONES[ic], x0 + 17, sy + 16, 16, 16, 24, 24, stroke=T, sw=1.5,
                           role="selo-icone"))
        E.append(text(lab, x0 + 44, sy + 13.5, col - 48, 9, D, bold=True, lh=1.15,
                      role="selo-texto"))
        if i:
            d, w, h = rect(0, 0, 0.8, 30)
            E.append(shape(d, x0, sy + 9, 0.8, 30, w, h, fill=LINHA_FINA, role="linha"))

    # SETOR 6 — rodapé legal e comercial
    ry = 458
    d, w, h = rect(0, 0, W, PH - ry)
    E.append(shape(d, 0, ry, W, PH - ry, w, h, fill=D, role="rodape"))
    E.append(text("Fabricado e Embalado por:", 14, ry + 11, 190, 8, "#FFFFFF", lh=1.0,
                  role="rodape-texto"))
    E.append(text("Recuperadora de Plásticos Humaitá", 14, ry + 22, 190, 9, "#FFFFFF",
                  bold=True, lh=1.0, role="rodape-texto"))
    E.append(text("CNPJ - 45.421.146/0001-49", 14, ry + 35, 190, 10, "#FFFFFF", bold=True,
                  lh=1.0, role="rodape-texto"))
    E.append(text("MANTER FORA DO ALCANCE DE CRIANÇAS.\nPRODUTO NÃO PERECÍVEL.\n"
                  "Composição: PEBD.", 14, ry + 54, 180, 7, "#FFFFFF", lh=1.3,
                  role="rodape-texto"))
    # símbolo de reciclabilidade — PEBD (4)
    scx, scy, ss = 222, ry + 42, 40
    arrows = H.recycle_arrows(20, 21, 38)
    E.append(shape(" ".join(arrows), scx - ss / 2, scy - ss / 2, ss, ss, 40, 40,
                   fill="#FFFFFF", role="simbolo-4"))
    E.append(text("4", scx - 10, scy - 4, 20, 11, "#FFFFFF", bold=True, align="center",
                  lh=1.0, role="simbolo-4"))
    E.append(text("PEBD", scx - 20, scy + 21, 40, 7, "#FFFFFF", bold=True, align="center",
                  lh=1.0, role="simbolo-4"))
    # código de barras EAN-13 em box branco
    bxl, byt, bww, bhh = 262, ry + 10, 122, 82
    d, w, h = rect(0, 0, bww, bhh, 4)
    E.append(shape(d, bxl, byt, bww, bhh, w, h, fill="#FFFFFF", role="ean-box"))
    bars_w, bars_h, gx = 104, 52, 5
    E.append(shape(ean13_path(p["ean"], bars_w, bars_h, gx), bxl + 9, byt + 7, bars_w,
                   bars_h + gx, 95, bars_h + gx, fill=PRETO, role="ean-barras"))
    ean = p["ean"]
    E.append(text("%s  %s  %s" % (ean[0], ean[1:7], ean[7:]), bxl, byt + 65, bww, 9,
                  PRETO, align="center", lh=1.0, role="ean-numero", spacing=60))
    return E


PRODUTOS = [
    dict(slug="20l", volume="20L", categoria="SACO PARA LIXO", dimensoes="00 cm x 00 cm",
         capacidade="20 L / 4 Kg", tipo="SACO PRETO", quantidade="100 UNIDADES"),
    dict(slug="40l", volume="40L", categoria="SACO PARA LIXO", dimensoes="40 cm x 50 cm",
         capacidade="40 L / 8 Kg", tipo="SACO PRETO", quantidade="100 UNIDADES"),
    dict(slug="60l", volume="60L", categoria="SACO INDUSTRIAL", dimensoes="63 cm x 76 cm",
         capacidade="60 L / 12 Kg", tipo="SACO CANELA", quantidade="100 UNIDADES"),
    dict(slug="80l", volume="80L", categoria="SACO INDUSTRIAL", dimensoes="00 cm x 00 cm",
         capacidade="80 L / 16 Kg", tipo="SACO PRETO", quantidade="100 UNIDADES"),
    dict(slug="100l", volume="100L", categoria="SACO INDUSTRIAL", dimensoes="00 cm x 00 cm",
         capacidade="100 L / 20 Kg", tipo="SACO PRETO", quantidade="100 UNIDADES"),
    dict(slug="100l-bl", volume="100L BL", categoria="SACO INDUSTRIAL",
         dimensoes="00 cm x 00 cm", capacidade="100 L / 20 Kg",
         tipo="TRANSPARENTE CRISTAL", quantidade="5 KG"),
    dict(slug="200l", volume="200L", categoria="SACO INDUSTRIAL", dimensoes="00 cm x 00 cm",
         capacidade="200 L / 40 Kg", tipo="SACO PRETO", quantidade="100 UNIDADES"),
]
# cor por linha (mesma ordem de humaita.LINHAS)
for prod, (_, _, cor, escura, nome) in zip(PRODUTOS, H.LINHAS):
    prod.update(cor=cor, escura=escura, nome_cor=nome, ean="7898131151516")


# ── Saídas ────────────────────────────────────────────────────────────
def html(E, titulo, scale=1.0):
    fontdir = os.path.relpath(os.path.join(H.ROOT, "fontes"),
                              os.path.join(H.ROOT, "etiquetas"))
    out = ['<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
           '<title>%s</title><style>'
           '@font-face{font-family:Q;src:url(%s/Quicksand-700.ttf);font-weight:700}'
           '@font-face{font-family:Q;src:url(%s/Quicksand-500.ttf);font-weight:400}'
           '@page{size:105mm 148mm;margin:0}'
           'body{margin:0;background:#fff}'
           '.pg{position:relative;width:%dpx;height:%dpx;overflow:hidden;background:#fff;'
           'transform-origin:0 0;transform:scale(%s)}'
           '.pg>*{position:absolute}.t{font-family:Q,Quicksand,sans-serif;white-space:pre-wrap;'
           'margin:0}</style></head><body><div class="pg">'
           % (titulo, fontdir, fontdir, W, PH, scale)]
    for e in E:
        st = "left:%spx;top:%spx;width:%spx;" % (H.fmt(e["left"]), H.fmt(e["top"]), H.fmt(e["width"]))
        if e["kind"] == "shape":
            st += "height:%spx;" % H.fmt(e["height"])
            if e["opacity"] is not None:
                st += "opacity:%s;" % e["opacity"]
            attrs = 'fill="%s"' % (e["fill"] or "none")
            if e["stroke"]:
                attrs += (' stroke="%s" stroke-width="%s" vector-effect="non-scaling-stroke" '
                          'stroke-linecap="round" stroke-linejoin="round"' % (e["stroke"], e["sw"]))
            out.append('<svg style="%s" viewBox="0 0 %s %s" preserveAspectRatio="none">'
                       '<path fill-rule="nonzero" %s d="%s"/></svg>'
                       % (st, H.fmt(e["vbw"]), H.fmt(e["vbh"]), attrs, e["path"]))
        else:
            st += ("font-size:%spx;line-height:%s;color:%s;font-weight:%d;text-align:%s;"
                   "letter-spacing:%sem;" % (H.fmt(e["size"]), e["lh"], e["color"],
                                             700 if e["bold"] else 400, e["align"],
                                             e["spacing"] / 1000))
            if e["rotation"]:
                st += "transform:rotate(%sdeg);" % e["rotation"]
            out.append('<p class="t" style="%s">%s</p>' % (st, e["text"]))
    out.append("</div></body></html>")
    return "".join(out)


def canva_ops(E, page_id):
    """Fase 1: inserir formas e textos. Fase 2 (format) é aplicada depois,
    casando cada texto pelo conteúdo (ver 'textos')."""
    ops, textos = [], []
    for e in E:
        if e["kind"] == "shape":
            op = dict(type="insert_shape", page_id=page_id, top=round(e["top"], 2),
                      left=round(e["left"], 2), width=round(e["width"], 2),
                      height=round(e["height"], 2), path=e["path"],
                      view_box_width=e["vbw"], view_box_height=e["vbh"])
            if e["fill"]:
                op["color"] = e["fill"]
            if e["stroke"]:
                op["stroke_color"] = e["stroke"]
                op["stroke_weight"] = e["sw"]
            if e["opacity"] is not None:
                op["opacity"] = e["opacity"]
            ops.append(op)
        else:
            op = dict(type="add_text", page_id=page_id, text=e["text"],
                      top=round(e["top"], 2), left=round(e["left"], 2),
                      width=round(e["width"], 2))
            if e["rotation"]:
                op["rotation"] = e["rotation"]
            ops.append(op)
            textos.append(dict(text=e["text"], formatting=dict(
                font_size=max(1, round(e["size"])), color=e["color"],
                font_weight="bold" if e["bold"] else "normal",
                text_align=e["align"], line_height=e["lh"])))
    return ops, textos


def main():
    out = os.path.join(H.ROOT, "etiquetas")
    os.makedirs(os.path.join(out, "canva"), exist_ok=True)
    for p in PRODUTOS:
        E = etiqueta(p)
        with open(os.path.join(out, "etiqueta-%s.html" % p["slug"]), "w") as fh:
            fh.write(html(E, "Etiqueta %s — Humaitá Plásticos" % p["volume"]))
        ops, textos = canva_ops(E, "PAGE_ID")
        with open(os.path.join(out, "canva", "%s.json" % p["slug"]), "w") as fh:
            json.dump(dict(ops=ops, textos=textos), fh, ensure_ascii=False)
    print("etiquetas:", len(PRODUTOS))


if __name__ == "__main__":
    main()
