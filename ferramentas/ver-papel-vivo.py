#!/usr/bin/env python3
"""Mostra a cena do papel de parede "Mata Viva" fora do Plasma, com o estado que você quiser.

    python3 ferramentas/ver-papel-vivo.py                                   abre uma janela
    python3 ferramentas/ver-papel-vivo.py --estado '{"turbo": true}'        com o Saci girando
    python3 ferramentas/ver-papel-vivo.py --todos --captura tela.png        desenha num PNG e sai (sem tela)
    python3 ferramentas/ver-papel-vivo.py --captura q.png --quadros 4       q-1.png … q-4.png, 0,4 s entre eles

--estado recebe os mesmos campos de "curupira json". --todos acorda todos os seres. --parado desliga o movimento.
"""

import argparse
import json
import os
import sys
from pathlib import Path

CENA = Path(__file__).resolve().parent.parent / "tema/papel-vivo/io.github.pabloherzberg.mataviva/contents/ui/Cena.qml"
TODOS = {"perfil": "pororoca", "bateria": 100, "carga": 60, "boitata_dormindo": False, "hd_acordado": True, "turbo": True,
         "wifi": True, "bluetooth": True, "lab": True, "camera_cortada": True, "microfone_mudo": True}


def main() -> int:
    args = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    args.add_argument("--estado", default="{}", help="JSON com os campos de 'curupira json'")
    args.add_argument("--todos", action="store_true", help="acorda todos os seres")
    args.add_argument("--parado", action="store_true", help="sem movimento")
    args.add_argument("--arte", default="brasa", choices=["brasa", "iara"], help="a cena")
    args.add_argument("--hora", type=float, help="hora do dia (0 a 24) para a lua da Cuca")
    args.add_argument("--captura", metavar="PNG")
    args.add_argument("--quadros", type=int, default=1)
    args.add_argument("--espera", type=float, default=0.4, help="segundos antes da primeira captura (os seres surgem aos poucos)")
    args.add_argument("--tamanho", default="1366x768")
    op = args.parse_args()
    if op.captura:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        os.environ.setdefault("QT_QUICK_BACKEND", "software")

    from PySide6.QtCore import QTimer, QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQuick import QQuickView

    app = QGuiApplication(sys.argv)
    estado = dict(TODOS) if op.todos else {"bateria": 100}
    estado.update(json.loads(op.estado))
    w, h = (int(v) for v in op.tamanho.split("x"))
    vista = QQuickView()
    vista.setResizeMode(QQuickView.ResizeMode.SizeRootObjectToView)
    vista.setTitle("Mata Viva")
    vista.resize(w, h)
    vista.setSource(QUrl.fromLocalFile(str(CENA)))
    if vista.status() != QQuickView.Status.Ready:
        for erro in vista.errors():
            print(erro.toString(), file=sys.stderr)
        return 1
    raiz = vista.rootObject()
    raiz.setProperty("arte", op.arte)
    raiz.setProperty("estado", estado)
    raiz.setProperty("mover", not op.parado)
    if op.hora is not None:
        raiz.setProperty("hora", op.hora)
    vista.show()
    if not op.captura:
        return app.exec()

    feitos = []

    def captura():
        nome = op.captura if op.quadros == 1 else op.captura.replace(".png", f"-{len(feitos) + 1}.png")
        vista.grabWindow().save(nome)
        feitos.append(nome)
        if len(feitos) >= op.quadros:
            app.quit()

    relogio = QTimer()
    relogio.timeout.connect(captura)
    QTimer.singleShot(int(op.espera * 1000), lambda: (captura(), relogio.start(400)))
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
