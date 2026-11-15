#!/usr/bin/env python3
"""Gera os pacotes de papel de parede do Plasma a partir das artes em SVG.

    python3 tema/gerar-papeis.py      reescreve tema/papeis/<nome>/

Cada pacote tem metadata.json e contents/images/<largura>x<altura>.png, que é o formato
que o seletor de papel de parede do Plasma entende. Precisa do PySide6.
"""

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRectF, Qt  # noqa: E402
from PySide6.QtGui import QGuiApplication, QImage, QPainter  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402

AQUI = Path(__file__).resolve().parent
ARTE = AQUI.parent / "arte"
TAMANHOS = [(1366, 768), (1920, 1080), (2560, 1440)]
PAPEIS = [
    ("Curupira-Brasa", "Brasa", "O Curupira de cabelo de fogo na mata à noite.", ARTE / "brasa-fundo.svg"),
    ("Curupira-Entardecer", "Entardecer", "Entardecer na praia, nas cores da Curupira OS.",
     ARTE / "propostas" / "papel-de-parede-entardecer.svg"),
]


def renderiza(svg: Path, largura: int, altura: int) -> QImage:
    render = QSvgRenderer(str(svg))
    vb = render.viewBoxF()
    # cobre a tela inteira mantendo a proporção (como object-fit: cover)
    escala = max(largura / vb.width(), altura / vb.height())
    w, h = vb.width() * escala, vb.height() * escala
    img = QImage(largura, altura, QImage.Format.Format_RGB32)
    img.fill(Qt.GlobalColor.black)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    render.render(p, QRectF((largura - w) / 2, (altura - h) / 2, w, h))
    p.end()
    return img


def main():
    app = QGuiApplication([])  # noqa: F841 - o QPainter precisa de uma aplicação
    for ident, nome, descricao, svg in PAPEIS:
        pasta = AQUI / "papeis" / ident
        imagens = pasta / "contents" / "images"
        imagens.mkdir(parents=True, exist_ok=True)
        for antigo in imagens.glob("*.png"):
            antigo.unlink()
        for w, h in TAMANHOS:
            renderiza(svg, w, h).save(str(imagens / f"{w}x{h}.png"), "PNG")
        renderiza(svg, 400, 225).save(str(pasta / "contents" / "screenshot.png"), "PNG")
        meta = {
            "KPlugin": {
                "Authors": [{"Name": "Curupira OS"}],
                "Id": ident,
                "License": "CC-BY-SA-4.0",
                "Name": nome,
                "Description": descricao,
            }
        }
        (pasta / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=4) + "\n")
        print(f"{ident}: {', '.join(f'{w}x{h}' for w, h in TAMANHOS)}")
    # a tela de login (SDDM) usa o Brasa em Full HD como fundo
    import shutil
    shutil.copyfile(AQUI / "papeis" / "Curupira-Brasa" / "contents" / "images" / "1920x1080.png",
                    AQUI / "sddm" / "curupira" / "fundo.png")
    print("tema/sddm/curupira/fundo.png atualizado")


if __name__ == "__main__":
    main()
