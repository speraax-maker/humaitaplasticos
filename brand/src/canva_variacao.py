"""
Gera as operações do Canva para transformar uma cópia da página-modelo (60L azul)
em outra linha de produto: troca a cor tema (T), o tom escuro (D) e os textos
dinâmicos (Setores 2 e 3).

Uso: python3 canva_variacao.py <read-design.json> <slug-do-produto>
Imprime a lista JSON de operações para o edit-design.
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import etiqueta as E  # noqa: E402

MODELO = next(p for p in E.PRODUTOS if p["slug"] == "60l")


def main(path, slug):
    doc = json.load(open(path))
    page = doc["design_content"]["pages"][0]
    p = next(x for x in E.PRODUTOS if x["slug"] == slug)
    T0, D0 = MODELO["cor"].lower(), MODELO["escura"].lower()
    T, D = p["cor"], p["escura"]
    troca_txt = {MODELO[k]: p[k] for k in ("volume", "dimensoes", "capacidade", "tipo",
                                             "quantidade")}
    troca_txt[MODELO["categoria"].replace(" ", "\n", 1)] = p["categoria"].replace(" ", "\n", 1)
    ops = []
    for el in page["elements"]:
        loc = el["locator_id"]
        if el["type"] == "shape":
            path0 = el["paths"][0]
            fill = (path0.get("fill", {}).get("color") or {}).get("color")
            stroke = path0["stroke"]["color"].get("color") if path0["stroke"]["weight"] else None
            if stroke == T0:
                # a API não troca a cor do contorno: recria o ícone com a nova cor
                vb = el["viewBox"]
                ops.append(dict(type="delete_element", locator_id=loc))
                ops.append(dict(type="insert_shape", page_id=page["id"], top=el["top"],
                                left=el["left"], width=el["width"], height=el["height"],
                                path=path0["d"], view_box_width=vb["width"],
                                view_box_height=vb["height"], stroke_color=T,
                                stroke_weight=path0["stroke"]["weight"]))
            elif fill == T0:
                ops.append(dict(type="recolor_element", locator_id=loc, color=T))
            elif fill == D0:
                ops.append(dict(type="recolor_element", locator_id=loc, color=D))
        elif el["type"] == "text":
            reg = el["textRegions"][0]
            chars = "".join(r["characters"] for r in el["textRegions"])
            color = reg["formatting"]["color"]
            if chars in troca_txt and troca_txt[chars] != chars:
                ops.append(dict(type="replace_text", locator_id=loc, text=troca_txt[chars]))
            if color == T0:
                ops.append(dict(type="format_text", locator_id=loc, formatting=dict(color=T)))
            elif color == D0:
                ops.append(dict(type="format_text", locator_id=loc, formatting=dict(color=D)))
            if chars == MODELO["volume"] and p["volume"] != MODELO["volume"]:
                fs = volume_fs(p["volume"])
                ops.append(dict(type="format_text", locator_id=loc,
                                formatting=dict(font_size=fs)))
                # caixa girada: posição = canto do retângulo já rotacionado
                ops.append(dict(type="position_element", locator_id=loc,
                                top=150, left=round(68 - fs * 0.6, 1)))
    print(json.dumps(ops, ensure_ascii=False))


def volume_fs(vol):
    """Tamanho do volume vertical na fonte padrão do Canva (60L = 88 px)."""
    return {"20L": 88, "40L": 88, "60L": 88, "80L": 88, "100L": 70, "100L BL": 42,
            "200L": 70}[vol]


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
