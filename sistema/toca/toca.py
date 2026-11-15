#!/usr/bin/env python3
"""Toca do Curupira: central de controle da Curupira OS.

    toca-do-curupira                          abre a janela
    toca-do-curupira --secao seres            abre numa seção
    toca-do-curupira --captura tela.png       desenha a janela num PNG e sai (sem tela)
    toca-do-curupira --captura-todas pasta/   um PNG por seção

Os dados vêm do sistema (sistema.py) e as seções ficam em secoes/.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtCore import QObject, QRunnable, QSize, Qt, QThreadPool, QTimer, Signal  # noqa: E402
from PySide6.QtGui import QFont, QIcon  # noqa: E402
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QPushButton, QScrollArea,  # noqa: E402
                               QStackedWidget, QVBoxLayout, QWidget)

import sistema  # noqa: E402
import visual  # noqa: E402
from secoes.aparencia import SecaoAparencia  # noqa: E402
from secoes.cuca import SecaoCuca  # noqa: E402
from secoes.energia import SecaoEnergia  # noqa: E402
from secoes.privacidade import SecaoPrivacidade  # noqa: E402
from secoes.rede import SecaoRede  # noqa: E402
from secoes.seres import SecaoSeres  # noqa: E402
from visual import (AREIA, BRASA, ICONES, SECOES, TINTA_SUAVE, VERDE_ESCURO, Avatar, arte, icone,  # noqa: E402
                    rotulo)

VERSAO = "0.2"
CLASSES = {
    "energia": SecaoEnergia,
    "seres": SecaoSeres,
    "rede": SecaoRede,
    "privacidade": SecaoPrivacidade,
    "snapshots": SecaoCuca,
    "aparencia": SecaoAparencia,
}
COM_ROLAGEM_PROPRIA = {"snapshots"}


class _Sinais(QObject):
    pronto = Signal(object)


class Tarefa(QRunnable):
    """Roda uma função fora da interface e devolve o resultado por sinal."""

    vivas: set = set()

    def __init__(self, funcao, ao_terminar):
        super().__init__()
        self.funcao = funcao
        self.sinais = _Sinais()
        self.sinais.pronto.connect(ao_terminar)
        self.setAutoDelete(False)
        Tarefa.vivas.add(self)   # o Python segura a tarefa até ela terminar

    def run(self):
        try:
            resultado = self.funcao()
        except Exception as erro:  # noqa: BLE001 - qualquer falha vira mensagem na tela
            resultado = erro
        self.sinais.pronto.emit(resultado)
        Tarefa.vivas.discard(self)


def com_rolagem(w: QWidget) -> QScrollArea:
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setFrameShape(QFrame.Shape.NoFrame)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    area.setStyleSheet("QScrollArea { background: transparent; } QScrollArea > QWidget > QWidget { background: transparent; }")
    area.setWidget(w)
    return area


class Toca(QWidget):
    def __init__(self, secao_inicial: str = "energia"):
        super().__init__()
        self.setWindowTitle("Toca do Curupira")
        self.setWindowIcon(QIcon(str(arte("cordel-busto.svg") or "")))
        self.resize(960, 640)
        self.setMinimumSize(900, 600)
        self.setObjectName("toca")
        self.setStyleSheet(
            "#toca { background: #FFFFFF; } QToolTip { font-size: 12px; }"
            "QScrollBar:vertical { width: 8px; background: transparent; margin: 0; }"
            "QScrollBar::handle:vertical { background: #E2D7C3; border-radius: 4px; min-height: 30px; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }")
        self.pool = QThreadPool.globalInstance()
        self.lendo: set[str] = set()

        raiz = QHBoxLayout(self); raiz.setContentsMargins(0, 0, 0, 0); raiz.setSpacing(0)

        nav = QFrame(); nav.setObjectName("nav"); nav.setFixedWidth(228)
        nav.setStyleSheet(f"#nav {{ background: {AREIA}; }}")
        n = QVBoxLayout(nav); n.setContentsMargins(14, 20, 14, 20); n.setSpacing(4)
        cab = QHBoxLayout(); cab.setContentsMargins(6, 0, 6, 16); cab.setSpacing(10)
        cab.addWidget(Avatar(48, 16))
        ct = QVBoxLayout(); ct.setSpacing(0)
        ct.addWidget(rotulo("Toca do Curupira", 17, QFont.Weight.ExtraBold, titulo=True))
        ct.addWidget(rotulo("central de controle", 12, cor=TINTA_SUAVE))
        cab.addLayout(ct, 1)
        n.addLayout(cab)

        conteudo = QWidget()
        cl = QVBoxLayout(conteudo); cl.setContentsMargins(24, 22, 24, 14); cl.setSpacing(8)
        self.pilha = QStackedWidget()
        cl.addWidget(self.pilha, 1)
        self.mensagem = rotulo("", 13, QFont.Weight.Bold, VERDE_ESCURO)
        self.mensagem.setMinimumHeight(20)
        self.mensagem.setWordWrap(True)
        self.mensagem.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        cl.addWidget(self.mensagem)

        self.secoes: dict[str, visual.Secao] = {}
        self.botoes_nav: dict[str, QPushButton] = {}
        for ident, titulo in SECOES:
            b = QPushButton(titulo)
            b.setCheckable(True); b.setAutoExclusive(True)
            b.setMinimumHeight(44)
            b.setFont(visual.fonte(14, QFont.Weight.Bold))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setIconSize(QSize(20, 20))
            b.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            b.setStyleSheet(
                "QPushButton { text-align: left; padding: 0 12px; border: 0; border-radius: 12px;"
                " background: transparent; color: #3E4C44; }"
                "QPushButton:hover { background: #F4EADB; }"
                f"QPushButton:checked {{ background: #FFFFFF; color: {VERDE_ESCURO}; }}")
            b.toggled.connect(lambda marcado, i=ident: marcado and self.abre(i))
            n.addWidget(b)
            self.botoes_nav[ident] = b

            secao = CLASSES[ident]()
            secao.executar.connect(self.executa)
            secao.ir_para.connect(self.vai_para)
            secao.avisar.connect(self.avisa)
            self.secoes[ident] = secao
            self.pilha.addWidget(secao if ident in COM_ROLAGEM_PROPRIA else com_rolagem(secao))
        n.addStretch()
        n.addWidget(rotulo(f"Curupira OS · Toca {VERSAO}", 11, cor="#8A968F"))
        raiz.addWidget(nav)
        raiz.addWidget(conteudo, 1)

        self.atual = ""
        self.vai_para(secao_inicial if secao_inicial in self.secoes else "energia")

        self.relogio = QTimer(self)
        self.relogio.timeout.connect(self.atualiza)
        self.relogio.start(4000)

    # -- navegação
    def vai_para(self, ident: str):
        self.botoes_nav[ident].setChecked(True)
        self.abre(ident)

    def abre(self, ident: str):
        if ident == self.atual:
            return
        self.atual = ident
        self.pilha.setCurrentIndex([s[0] for s in SECOES].index(ident))
        for i, b in self.botoes_nav.items():
            b.setIcon(QIcon(icone(ICONES[i], VERDE_ESCURO if i == ident else "#3E4C44")))
        self.avisa("")
        self.atualiza()

    # -- dados
    def atualiza(self):
        ident = self.atual
        if not ident or ident in self.lendo:
            return
        self.lendo.add(ident)
        secao = self.secoes[ident]
        self.pool.start(Tarefa(secao.coleta, lambda d, i=ident: self._recebe(i, d)))

    def _recebe(self, ident: str, dados):
        self.lendo.discard(ident)
        if isinstance(dados, Exception):
            self.avisa(f"Erro ao ler o sistema: {dados}", True)
            return
        self.secoes[ident].mostra(dados)

    def avisa(self, texto: str, erro: bool = False):
        self.mensagem.setText(texto)
        self.mensagem.setStyleSheet(f"color: {BRASA if erro else VERDE_ESCURO}; background: transparent;")

    def executa(self, cmd: list, sucesso: str, ao_terminar=None):
        """Roda um comando fora da interface. ao_terminar(resultado) pode montar a mensagem final."""
        self.avisa("Um instante…")

        def trabalho():
            r = sistema.roda(*cmd, tempo=120)
            if ao_terminar is not None:
                return ao_terminar(r), False
            if r is None:
                return f"Não consegui rodar {cmd[0]}.", True
            if r.returncode != 0:
                return sistema.ultima_linha(r), True
            return sucesso, False

        def fim(res):
            if isinstance(res, Exception):
                self.avisa(str(res), True)
            else:
                texto, erro = res
                self.avisa(texto, erro)
            self.atualiza()

        self.pool.start(Tarefa(trabalho, fim))


def captura(app: QApplication, janela: Toca, ident: str, arquivo: str):
    janela.vai_para(ident)
    janela.secoes[ident].mostra(janela.secoes[ident].coleta())
    janela.avisa("")
    app.processEvents()
    janela.grab().save(arquivo)


def main() -> int:
    args = argparse.ArgumentParser(description="Toca do Curupira: central de controle da Curupira OS")
    args.add_argument("--secao", default="energia", choices=[s[0] for s in SECOES])
    args.add_argument("--captura", metavar="PNG", help="desenha a janela num PNG e sai")
    args.add_argument("--captura-todas", metavar="PASTA", help="um PNG por seção e sai")
    op = args.parse_args()

    if op.captura or op.captura_todas:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication(sys.argv)
    app.setApplicationName("Toca do Curupira")
    app.setDesktopFileName("io.github.pabloherzberg.Toca")
    visual.inicia_fontes()
    app.setFont(visual.fonte(14))

    janela = Toca(op.secao)
    if op.captura or op.captura_todas:
        janela.relogio.stop()
        janela.show()
        if op.captura:
            captura(app, janela, op.secao, op.captura)
        else:
            Path(op.captura_todas).mkdir(parents=True, exist_ok=True)
            for ident, _ in SECOES:
                captura(app, janela, ident, str(Path(op.captura_todas) / f"{ident}.png"))
        QThreadPool.globalInstance().waitForDone(5000)
        return 0
    janela.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
