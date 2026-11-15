#!/usr/bin/env python3
"""Gera as imagens da tela de boot (Plymouth) a partir de arte/01-brasa.svg.

    python3 tema/gerar-boot.py      reescreve as PNG em tema/plymouth/curupira/

- retrato.png: a arte inteira sem as cinco pegadas
- pegada0.png … pegada4.png: cada pegada (com o brilho de brasa), recortada em volta do centro
- posicoes.txt: centro de cada pegada nas coordenadas da arte (800×1000), para conferência
O Plymouth não lê SVG; o script curupira.script posiciona e anima as pegadas.
"""

import os
import re
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QByteArray, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QGuiApplication, QImage, QPainter  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402

AQUI = Path(__file__).resolve().parent
ARTE = AQUI.parent / "arte" / "01-brasa.svg"
SAIDA = AQUI / "plymouth" / "curupira"
ESCALA = 2            # as PNG saem com o dobro da resolução da arte (telas grandes ficam nítidas)
CAIXA = (88, 60)      # recorte de cada pegada, em unidades da arte


def grupos_pegada(svg: str) -> list[tuple[int, int]]:
    """Início e fim de cada <g class="step"> (contando os <g> internos)."""
    faixas = []
    for m in re.finditer(r'<g class="step"', svg):
        i, nivel, pos = m.start(), 0, m.start()
        while True:
            prox_abre = svg.find("<g", pos)
            prox_fecha = svg.find("</g>", pos)
            if prox_abre != -1 and prox_abre < prox_fecha:
                nivel += 1
                pos = prox_abre + 2
            else:
                nivel -= 1
                pos = prox_fecha + 4
                if nivel == 0:
                    faixas.append((i, pos))
                    break
    return faixas


def renderiza(svg: str, largura: int, altura: int) -> QImage:
    img = QImage(largura, altura, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    QSvgRenderer(QByteArray(svg.encode())).render(p, QRectF(0, 0, largura, altura))
    p.end()
    return img


def funde_laterais(img: QImage, faixa: float = 0.16):
    """Esmaece as laterais até a transparência, para o retrato se fundir com o fundo da tela
    (o fundo da arte é um pouco mais claro e marcaria um retângulo)."""
    from PySide6.QtGui import QColor, QLinearGradient
    g = QLinearGradient(0, 0, img.width(), 0)
    g.setColorAt(0.0, QColor(0, 0, 0, 0))
    g.setColorAt(faixa, QColor(0, 0, 0, 255))
    g.setColorAt(1 - faixa, QColor(0, 0, 0, 255))
    g.setColorAt(1.0, QColor(0, 0, 0, 0))
    p = QPainter(img)
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
    p.fillRect(img.rect(), g)
    p.end()


def main():
    app = QGuiApplication([])  # noqa: F841
    svg = ARTE.read_text()
    faixas = grupos_pegada(svg)
    assert len(faixas) == 5, f"esperava 5 pegadas, achei {len(faixas)}"
    SAIDA.mkdir(parents=True, exist_ok=True)

    # retrato sem as pegadas
    sem = svg
    for ini, fim in reversed(faixas):
        sem = sem[:ini] + sem[fim:]
    retrato = renderiza(sem, 800 * ESCALA, 1000 * ESCALA)
    funde_laterais(retrato)
    retrato.save(str(SAIDA / "retrato.png"))

    # cada pegada sozinha: o SVG inteiro com o "palco" vazio, só os <defs> e aquela pegada
    abertura = re.search(r"<svg[^>]*>", svg)
    defs = re.search(r"<defs>.*?</defs>", svg, re.S)
    posicoes = []
    for n, (ini, fim) in enumerate(faixas):
        grupo = svg[ini:fim]
        cx, cy = map(float, re.search(r'<ellipse cx="([\d.]+)" cy="([\d.]+)"', grupo).groups())
        w, h = CAIXA
        cabeca = re.sub(r'viewBox="[^"]*"', f'viewBox="{cx - w / 2} {cy - h / 2} {w} {h}"', abertura.group(0))
        cabeca = re.sub(r'\swidth="[^"]*"', f' width="{w}"', cabeca)
        cabeca = re.sub(r'\sheight="[^"]*"', f' height="{h}"', cabeca)
        pe = f'{cabeca}{defs.group(0) if defs else ""}{grupo}</svg>'
        renderiza(pe, w * ESCALA, h * ESCALA).save(str(SAIDA / f"pegada{n}.png"))
        posicoes.append(f"{n} {cx:g} {cy:g}")
    (SAIDA / "posicoes.txt").write_text(
        "# pegada  centro_x  centro_y  (coordenadas de arte/01-brasa.svg, 800×1000)\n" + "\n".join(posicoes) + "\n")

    # cor de fundo: a borda da arte, para o retrato se fundir com a tela
    ret = QImage(str(SAIDA / "retrato.png"))
    meio = ret.width() // 2
    topo, base = ret.pixelColor(meio, 4), ret.pixelColor(meio, ret.height() - 5)
    print(f"retrato.png e 5 pegadas gerados. Fundo: topo {topo.name()} base {base.name()}")
    print("\n".join(posicoes))


if __name__ == "__main__":
    main()
