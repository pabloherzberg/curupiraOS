#!/usr/bin/env python3
"""Gera o estilo do Plasma "Curupira": só o fundo do painel (a doca), com o arredondado grande e a
sombra roxa do mockup/Desktop.dc.html. O resto (botões, menus, dicas) vem do Breeze, que o Plasma
usa sempre como reserva.

    python3 tema/gerar-painel.py      reescreve tema/plasma-estilo/curupira/

A cor não fica gravada: as peças usam a classe ColorScheme-ViewBackground, que o Plasma pinta com
a cor de fundo das vistas do esquema atual (branco no Curupira, noite no Curupira Noite).
"""

import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "plasma-estilo" / "curupira"

R = 24          # raio dos cantos (mockup: 24 px)
S = 18          # alcance da sombra
M = 4           # margem interna: espaço entre a borda da doca e os widgets
SOMBRA = "#140A28"   # rgba(20,10,40) do mockup


def canto(id_, cx, cy, ox, oy, classe="ColorScheme-ViewBackground"):
    """Quarto de círculo de raio R com o centro em (cx, cy) dentro da caixa R×R em (ox, oy)."""
    # pontos da borda do arco, conforme o canto
    sx = ox + (0 if cx == ox + R else R)
    pontos = {
        "topleft": (f"M{ox+R},{oy+R} L{ox},{oy+R} A{R},{R} 0 0 1 {ox+R},{oy} Z"),
        "topright": (f"M{ox},{oy+R} L{ox},{oy} A{R},{R} 0 0 1 {ox+R},{oy+R} Z"),
        "bottomleft": (f"M{ox+R},{oy} L{ox+R},{oy+R} A{R},{R} 0 0 1 {ox},{oy} Z"),
        "bottomright": (f"M{ox},{oy} L{ox+R},{oy} A{R},{R} 0 0 1 {ox},{oy+R} Z"),
    }
    del sx
    nome = id_.split("-")[-1]
    return f'<path id="{id_}" class="{classe}" style="fill:currentColor" d="{pontos[nome]}"/>'


def ret(id_, x, y, w, h, extra='class="ColorScheme-ViewBackground" style="fill:currentColor"'):
    return f'<rect id="{id_}" x="{x}" y="{y}" width="{w}" height="{h}" {extra}/>'


def nove_pedacos(prefixo, ox, oy):
    """Cantos R×R, bordas e centro de uma moldura arredondada, a partir de (ox, oy)."""
    p = prefixo
    e = []
    e.append(canto(f"{p}topleft", ox + R, oy + R, ox, oy))
    e.append(ret(f"{p}top", ox + R, oy, 4, R))
    e.append(canto(f"{p}topright", ox + R + 4, oy + R, ox + R + 4, oy))
    e.append(ret(f"{p}left", ox, oy + R, R, 4))
    e.append(ret(f"{p}center", ox + R, oy + R, 4, 4))
    e.append(ret(f"{p}right", ox + R + 4, oy + R, R, 4))
    e.append(canto(f"{p}bottomleft", ox + R, oy + R + 4, ox, oy + R + 4))
    e.append(ret(f"{p}bottom", ox + R, oy + R + 4, 4, R))
    e.append(canto(f"{p}bottomright", ox + R + 4, oy + R + 4, ox + R + 4, oy + R + 4))
    return e


def sombra(ox, oy):
    """Sombra em 9 pedaços: cada canto é um degradê radial que começa na curva da doca."""
    t = R + S                 # tamanho de cada canto da sombra
    defs, e = [], []
    for nome, cx, cy in [("topleft", t, t), ("topright", 0, t), ("bottomleft", t, 0), ("bottomright", 0, 0)]:
        gid = f"g-sombra-{nome}"
        defs.append(
            f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{t}">'
            f'<stop offset="{(R - 6) / t:.3f}" stop-color="{SOMBRA}" stop-opacity="0.34"/>'
            f'<stop offset="{(R + S * 0.35) / t:.3f}" stop-color="{SOMBRA}" stop-opacity="0.14"/>'
            f'<stop offset="1" stop-color="{SOMBRA}" stop-opacity="0"/></radialGradient>')
    posicoes = {"topleft": (0, 0), "topright": (t + 4, 0), "bottomleft": (0, t + 4), "bottomright": (t + 4, t + 4)}
    for nome, (x, y) in posicoes.items():
        e.append(f'<g transform="translate({ox + x},{oy + y})"><rect id="shadow-{nome}" width="{t}" height="{t}" '
                 f'style="fill:url(#g-sombra-{nome})"/></g>')
    # bordas: degradê linear perpendicular
    for nome, (x, y, w, h, x1, y1, x2, y2) in {
        "top": (t, 0, 4, t, 0, 1, 0, 0),
        "bottom": (t, t + 4, 4, t, 0, 0, 0, 1),
        "left": (0, t, t, 4, 1, 0, 0, 0),
        "right": (t + 4, t, t, 4, 0, 0, 1, 0),
    }.items():
        gid = f"g-sombra-{nome}"
        a = (R - 6) / t
        b = (R + S * 0.35) / t
        defs.append(
            f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
            f'<stop offset="{a:.3f}" stop-color="{SOMBRA}" stop-opacity="0.34"/>'
            f'<stop offset="{b:.3f}" stop-color="{SOMBRA}" stop-opacity="0.14"/>'
            f'<stop offset="1" stop-color="{SOMBRA}" stop-opacity="0"/></linearGradient>')
        e.append(f'<rect id="shadow-{nome}" x="{ox + x}" y="{oy + y}" width="{w}" height="{h}" '
                 f'style="fill:url(#{gid})"/>')
    e.append(ret("shadow-center", ox + t, oy + t, 4, 4, 'style="fill:none"'))
    # quanto a sombra passa da borda da doca, de cada lado
    for lado, (w, h) in {"top": (4, S), "bottom": (4, S + 6), "left": (S, 4), "right": (S, 4)}.items():
        e.append(ret(f"shadow-hint-{lado}-margin", ox + 200, oy + {"top": 0, "bottom": 30, "left": 60, "right": 90}[lado],
                     w, h, 'style="fill:none"'))
    return defs, e


def svg() -> str:
    defs, sombras = sombra(400, 0)
    pecas = []
    pecas += nove_pedacos("", 0, 0)
    pecas += nove_pedacos("mask-", 0, 120)       # máscara: mesma forma (área do desfoque e do recorte)
    pecas += sombras
    for lado, (w, h, y) in {"top": (4, M, 260), "bottom": (4, M, 270), "left": (M, 4, 280), "right": (M, 4, 290)}.items():
        pecas.append(ret(f"hint-{lado}-margin", 0, y, w, h, 'style="fill:none"'))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="700" height="320" viewBox="0 0 700 320">
<!-- Curupira OS: fundo da doca. Gerado por tema/gerar-painel.py; não edite à mão. -->
<defs>
<style type="text/css" id="current-color-scheme">.ColorScheme-ViewBackground {{ color:#ffffff; }}</style>
{chr(10).join(defs)}
</defs>
{chr(10).join(pecas)}
</svg>
'''


def main():
    conteudo = svg()
    for sub in ("widgets", "translucent/widgets", "opaque/widgets"):
        pasta = SAIDA / sub
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / "panel-background.svg").write_text(conteudo)
    meta = {
        "KPlugin": {
            "Authors": [{"Name": "Curupira OS"}],
            "Category": "",
            "Description": "A doca da Curupira OS: arredondado grande e sombra roxa; o resto vem do Breeze",
            "Id": "curupira",
            "License": "CC-BY-SA-4.0",
            "Name": "Curupira",
            "Version": "0.1",
            "Website": "https://github.com/pabloherzberg/curupiraOS",
        },
        "X-Plasma-API": "5.0",
    }
    (SAIDA / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=4) + "\n")
    print("Estilo Curupira gerado em tema/plasma-estilo/curupira (raio", R, "sombra", S, ")")


if __name__ == "__main__":
    main()
