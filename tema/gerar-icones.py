#!/usr/bin/env python3
"""Gera o ícone do botão de menu da doca: o Cordel num quadrado arredondado de brasa
(mockup/Desktop.dc.html). Sai em PNG porque o QtSvg, que o Plasma usa para ícones, não
recorta (clip-path), e o desenho do Cordel vazaria pelos cantos.

    python3 tema/gerar-icones.py      reescreve tema/icones/<tamanho>/curupira-menu.png
"""

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402

AQUI = Path(__file__).resolve().parent
CORDEL = AQUI.parent / "arte" / "cordel-busto.svg"
TAMANHOS = [32, 48, 64, 128, 256]


def icone(lado: int) -> QImage:
    img = QImage(lado, lado, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    forma = QPainterPath()
    forma.addRoundedRect(QRectF(0, 0, lado, lado), lado * 0.31, lado * 0.31)
    g = QLinearGradient(0, 0, lado, lado)
    g.setColorAt(0, QColor("#FFD08A"))
    g.setColorAt(1, QColor("#FF7A45"))
    p.fillPath(forma, g)
    p.setClipPath(forma)
    QSvgRenderer(str(CORDEL)).render(p, QRectF(0, 0, lado, lado))
    p.end()
    return img


def main():
    app = QGuiApplication([])  # noqa: F841
    for lado in TAMANHOS:
        pasta = AQUI / "icones" / f"{lado}x{lado}"
        pasta.mkdir(parents=True, exist_ok=True)
        icone(lado).save(str(pasta / "curupira-menu.png"))
    print("curupira-menu.png:", ", ".join(f"{t}x{t}" for t in TAMANHOS))
    # o avatar da tela de login (SDDM) é o mesmo Cordel
    import shutil
    shutil.copyfile(CORDEL, AQUI / "sddm" / "curupira" / "avatar.svg")
    print("tema/sddm/curupira/avatar.svg atualizado")


if __name__ == "__main__":
    main()
