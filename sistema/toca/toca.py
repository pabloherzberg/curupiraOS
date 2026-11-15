#!/usr/bin/env python3
"""Toca do Curupira: central de controle da Curupira OS.

    toca-do-curupira                         abre a janela
    toca-do-curupira --secao seres           abre numa seção
    toca-do-curupira --captura tela.png      desenha a janela num PNG e sai (sem tela)

O estado de energia vem de "curupira json"; trocar de perfil chama "curupira <perfil>".
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from PySide6.QtCore import QByteArray, QObject, QRectF, QRunnable, QSize, Qt, QThreadPool, QTimer, Signal
from PySide6.QtGui import (QColor, QFont, QFontDatabase, QIcon, QLinearGradient, QPainter, QPainterPath,
                           QPixmap)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QAbstractButton, QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel,
                               QPushButton, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget)

VERSAO = "0.1"
AQUI = Path(__file__).resolve().parent

# ------------------------------------------------------------------ cores e fontes (NOTAS.md / mockup)
TINTA = "#1E2A24"
TINTA_SUAVE = "#5B6A61"
AREIA = "#FBF4E8"
BORDA = "#EFE6D6"
NOITE = "#241A4A"
VERDE = "#12935F"
VERDE_ESCURO = "#0F7A54"
BRASA = "#B4380B"

PERFIS_VISUAL = {
    "pororoca":   ("#FF7A45", "#FFF1E8"),
    "correnteza": ("#2BB37A", "#E8F7EF"),
    "remanso":    ("#2468B8", "#EAF1FB"),
    "sereno":     ("#5B3A8E", "#F1EBF8"),
}
ORDEM_PERFIS = ["pororoca", "correnteza", "remanso", "sereno"]

ICONES = {
    "energia": "M13 2L4 14h7l-1 8 9-12h-7z",
    "seres": "M12 3c4 3 6 6 6 10a6 6 0 0 1-12 0c0-4 2-7 6-10z M12 9v9",
    "rede": "M2 9a15 15 0 0 1 20 0 M5 12.5a10 10 0 0 1 14 0 M8.5 16a5 5 0 0 1 7 0 M12 19.5h.01",
    "privacidade": "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z",
    "snapshots": "M3 12a9 9 0 1 0 3-6.7 M3 4v5h5 M12 7v5l3 2",
    "aparencia": "M12 3a9 9 0 1 0 0 18c1 0 2-1 2-2 0-1.5-1-2 0-3s3 0 4-1c2-1 3-3 3-5 0-4-4-7-9-7z "
                 "M7.5 11h.01 M10 7.5h.01 M15 7.5h.01",
    "boitata": "M12 3c3 4 5 6 5 10a5 5 0 0 1-10 0c0-2 1-4 2-5 0 2 1 3 2 3 0-3 0-5 1-8z",
    "saci": "M4 8h11a3 3 0 1 0-3-3 M4 12h15a3 3 0 1 1-3 3 M4 16h7",
    "mapinguari": "M4 7c0-2 16-2 16 0v10c0 2-16 2-16 0z M4 7c0 2 16 2 16 0 M8 14h.01",
    "wifi": "M2 9a15 15 0 0 1 20 0 M5 12.5a10 10 0 0 1 14 0 M8.5 16a5 5 0 0 1 7 0 M12 19.5h.01",
    "bluetooth": "M7 7l10 10-5 5V2l5 5L7 17",
    "caipora": "M3 3l18 18 M10.6 6.1A10 10 0 0 1 22 12a14 14 0 0 1-3 3.6 M6.6 6.6A14 14 0 0 0 2 12s4 7 10 7"
               "a9 9 0 0 0 4.2-1",
    "boto": "M4 6a2 2 0 1 0 4 0a2 2 0 1 0-4 0 M16 6a2 2 0 1 0 4 0a2 2 0 1 0-4 0 M10 18a2 2 0 1 0 4 0"
            "a2 2 0 1 0-4 0 M8 6h8 M7 8l4 8 M17 8l-4 8",
}

SECOES = [
    ("energia", "Energia"),
    ("seres", "Seres da mata"),
    ("rede", "Rede e Boto"),
    ("privacidade", "Privacidade"),
    ("snapshots", "Cuca · snapshots"),
    ("aparencia", "Aparência"),
]


def carrega_fontes() -> tuple[str, str]:
    titulo, texto = "sans-serif", "sans-serif"
    for nome in ("Baloo2[wght].ttf", "Nunito[wght].ttf"):
        caminho = AQUI / "fontes" / nome
        if caminho.exists():
            fid = QFontDatabase.addApplicationFont(str(caminho))
            familias = QFontDatabase.applicationFontFamilies(fid) if fid >= 0 else []
            if familias:
                if nome.startswith("Baloo"):
                    titulo = familias[0]
                else:
                    texto = familias[0]
    return titulo, texto


FONTE_TITULO, FONTE_TEXTO = "sans-serif", "sans-serif"


def fonte(tamanho: float, peso: QFont.Weight = QFont.Weight.Normal, titulo: bool = False) -> QFont:
    f = QFont(FONTE_TITULO if titulo else FONTE_TEXTO)
    f.setPixelSize(round(tamanho))
    f.setWeight(peso)
    # as fontes são variáveis: sem o eixo "wght" o Qt usa sempre o peso padrão
    peso_num = {QFont.Weight.Normal: 400, QFont.Weight.Medium: 500, QFont.Weight.DemiBold: 600,
                QFont.Weight.Bold: 700, QFont.Weight.ExtraBold: 800}.get(peso, 400)
    if titulo:
        peso_num = max(peso_num, 600)
    f.setVariableAxis(QFont.Tag("wght"), float(peso_num))
    return f


def arte(nome: str) -> Path | None:
    for base in (os.environ.get("CURUPIRA_ARTE"), AQUI / "arte", AQUI.parent.parent / "arte"):
        if base and (Path(base) / nome).exists():
            return Path(base) / nome
    return None


def icone(caminho_svg: str, cor: str, tamanho: int = 20, escala: float = 2.0) -> QPixmap:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{tamanho}" height="{tamanho}" '
           f'fill="none" stroke="{cor}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
           f'<path d="{caminho_svg}"/></svg>')
    return pixmap_svg(QByteArray(svg.encode()), tamanho, tamanho, escala)


def pixmap_svg(dados: QByteArray | str, largura: int, altura: int, escala: float = 2.0) -> QPixmap:
    render = QSvgRenderer(dados)
    pm = QPixmap(int(largura * escala), int(altura * escala))
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    render.render(p, QRectF(0, 0, pm.width(), pm.height()))
    p.end()
    pm.setDevicePixelRatio(escala)
    return pm


# ------------------------------------------------------------------ leitura do sistema
@dataclass
class Estado:
    energia: dict = field(default_factory=dict)
    turbo: bool | None = None
    hd_acordado: bool | None = None
    wifi: bool | None = None
    wifi_rede: str = ""
    bluetooth: bool | None = None
    boitata_dormindo: bool = True
    erro: str = ""


def roda(*cmd: str, tempo: float = 5) -> subprocess.CompletedProcess | None:
    if not shutil.which(cmd[0]) and not Path(cmd[0]).exists():
        return None
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=tempo)
    except (OSError, subprocess.TimeoutExpired):
        return None


def comando_curupira() -> str:
    if os.environ.get("CURUPIRA_BIN"):
        return os.environ["CURUPIRA_BIN"]
    local = AQUI.parent / "bin" / "curupira"
    if os.environ.get("CURUPIRA_TESTE") and local.exists():
        return str(local)
    return shutil.which("curupira") or "/usr/local/bin/curupira"


def le_estado() -> Estado:
    e = Estado()
    r = roda(comando_curupira(), "json")
    if r and r.returncode == 0:
        try:
            e.energia = json.loads(r.stdout)
        except json.JSONDecodeError:
            e.erro = "Não entendi a resposta do comando curupira."
    else:
        e.erro = "O comando curupira não respondeu. Ele está instalado?"

    try:
        e.turbo = Path("/sys/devices/system/cpu/intel_pstate/no_turbo").read_text().strip() == "0"
    except OSError:
        pass

    r = roda("findmnt", "-no", "FSTYPE", "/data")
    if r and r.returncode == 0:
        e.hd_acordado = any(t != "autofs" for t in r.stdout.split())

    r = roda("nmcli", "-t", "-f", "WIFI", "radio")
    if r and r.returncode == 0:
        e.wifi = r.stdout.strip() in ("enabled", "habilitado")
        # conexões ativas (o "dev wifi" refaz a busca de redes e demora)
        r2 = roda("nmcli", "-t", "-f", "NAME,TYPE", "connection", "show", "--active")
        if r2 and r2.returncode == 0:
            for linha in r2.stdout.splitlines():
                nome, _, tipo = linha.rpartition(":")
                if tipo == "802-11-wireless" and nome:
                    e.wifi_rede = nome.replace("\\:", ":")
                    break

    r = roda("bluetoothctl", "show")
    if r and r.returncode == 0 and "Powered:" in r.stdout:
        e.bluetooth = "Powered: yes" in r.stdout

    e.boitata_dormindo = Path("/etc/udev/rules.d/00-curupira-boitata.rules").exists()
    return e


class _Sinais(QObject):
    pronto = Signal(object)


class Tarefa(QRunnable):
    """Roda uma função fora da interface e devolve o resultado por sinal."""

    def __init__(self, funcao, ao_terminar):
        super().__init__()
        self.funcao = funcao
        self.sinais = _Sinais()
        self.sinais.pronto.connect(ao_terminar)
        self.setAutoDelete(False)
        Tarefa.vivas.add(self)   # o Python segura a tarefa até ela terminar

    vivas: set = set()

    def run(self):
        try:
            resultado = self.funcao()
        except Exception as erro:  # noqa: BLE001 - qualquer falha vira mensagem na tela
            resultado = erro
        self.sinais.pronto.emit(resultado)
        Tarefa.vivas.discard(self)


# ------------------------------------------------------------------ peças da interface
class Chave(QAbstractButton):
    """Interruptor no estilo do mockup (50×30, bolinha branca)."""

    def __init__(self, nome_acessivel: str):
        super().__init__()
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(50, 30)
        self.setAccessibleName(nome_acessivel)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def sizeHint(self) -> QSize:
        return QSize(50, 30)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        ligado = self.isChecked()
        trilho = QColor(VERDE if ligado else "#D9CFBE")
        if not self.isEnabled():
            trilho.setAlpha(110)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(trilho)
        p.drawRoundedRect(QRectF(0, 0, 50, 30), 15, 15)
        p.setBrush(QColor(0, 0, 0, 40))
        x = 24 if ligado else 4
        p.drawEllipse(QRectF(x, 5, 22, 22))
        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(QRectF(x, 4, 22, 22))
        if self.hasFocus():
            p.setPen(QColor(VERDE))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(QRectF(1, 1, 48, 28), 14, 14)


class CartaoPerfil(QAbstractButton):
    """Botão de perfil: quadradinho colorido, nome e descrição."""

    def __init__(self, ident: str, nome: str, descricao: str):
        super().__init__()
        self.ident, self.nome, self.descricao = ident, nome, descricao
        self.cor, self.suave = PERFIS_VISUAL.get(ident, ("#5B6A61", "#F2F2F2"))
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(80)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAccessibleName(f"Perfil {nome}, {descricao}")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def sizeHint(self) -> QSize:
        return QSize(150, 80)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        sel = self.isChecked()
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        p.setPen(QColor(self.cor if sel else BORDA).toRgb())
        pen = p.pen(); pen.setWidthF(2); p.setPen(pen)
        p.setBrush(QColor(self.suave if sel else "#FFFFFF"))
        p.drawRoundedRect(r, 16, 16)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(self.cor))
        p.drawRoundedRect(QRectF(13, 11, 26, 26), 9, 9)
        p.setPen(QColor(TINTA))
        p.setFont(fonte(15, QFont.Weight.ExtraBold))
        p.drawText(QRectF(13, 40, r.width() - 20, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.nome)
        p.setPen(QColor(TINTA_SUAVE))
        p.setFont(fonte(12))
        p.drawText(QRectF(13, 58, r.width() - 20, 16), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.descricao)
        if self.hasFocus():
            p.setPen(QColor(VERDE))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(r.adjusted(-0.5, -0.5, 0.5, 0.5), 17, 17)


class Medidor(QWidget):
    def __init__(self):
        super().__init__()
        self.fracao, self.cor = 0.0, "#7FE3B0"
        self.setFixedSize(300, 8)

    def define(self, fracao: float, cor: str):
        self.fracao, self.cor = max(0.0, min(1.0, fracao)), cor
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#3E3270"))
        p.drawRoundedRect(QRectF(0, 0, 300, 8), 4, 4)
        if self.fracao > 0:
            p.setBrush(QColor(self.cor))
            p.drawRoundedRect(QRectF(0, 0, max(8, 300 * self.fracao), 8), 4, 4)


class Ladrilho(QLabel):
    """Quadradinho com degradê e um ícone branco (os seres da mata)."""

    def __init__(self, icone_svg: str, c1: str, c2: str, tamanho: int = 36, icone_tam: int = 20):
        super().__init__()
        self.c1, self.c2, self.tam = c1, c2, tamanho
        self.setFixedSize(tamanho, tamanho)
        self.pm = icone(icone_svg, "#FFFFFF", icone_tam)
        self.icone_tam = icone_tam

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        g = QLinearGradient(0, 0, self.tam, self.tam)
        g.setColorAt(0, QColor(self.c1)); g.setColorAt(1, QColor(self.c2))
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(g)
        p.drawRoundedRect(QRectF(0, 0, self.tam, self.tam), self.tam * 0.31, self.tam * 0.31)
        off = (self.tam - self.icone_tam) / 2
        p.drawPixmap(int(off), int(off), self.pm)


class Avatar(QWidget):
    """Retrato do Cordel dentro de um quadrado arredondado com degradê."""

    def __init__(self, tamanho: int, raio: float, degrade: tuple[str, str] | None = ("#FFD08A", "#FF7A45")):
        super().__init__()
        self.tam, self.raio, self.degrade = tamanho, raio, degrade
        self.setFixedSize(tamanho, tamanho)
        caminho = arte("cordel-busto.svg")
        self.pm = pixmap_svg(str(caminho), tamanho, tamanho) if caminho else None

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        caminho = QPainterPath()
        caminho.addRoundedRect(QRectF(0, 0, self.tam, self.tam), self.raio, self.raio)
        p.setClipPath(caminho)
        if self.degrade:
            g = QLinearGradient(0, 0, self.tam, self.tam)
            g.setColorAt(0, QColor(self.degrade[0])); g.setColorAt(1, QColor(self.degrade[1]))
            p.fillPath(caminho, g)
        if self.pm:
            p.drawPixmap(0, 0, self.pm)


def rotulo(texto: str, tamanho: float, peso=QFont.Weight.Normal, cor: str = TINTA, titulo: bool = False) -> QLabel:
    l = QLabel(texto)
    l.setFont(fonte(tamanho, peso, titulo))
    l.setStyleSheet(f"color: {cor}; background: transparent;")
    return l


class LinhaSer(QFrame):
    """Linha de um ser da mata: ladrilho, nome, situação e interruptor."""

    def __init__(self, nome: str, icone_svg: str, c1: str, c2: str):
        super().__init__()
        self.setObjectName("linhaSer")
        self.setStyleSheet(f"#linhaSer {{ border: 1px solid {BORDA}; border-radius: 16px; background: #FFFFFF; }}")
        self.setMinimumHeight(60)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(12)
        lay.addWidget(Ladrilho(icone_svg, c1, c2))
        textos = QVBoxLayout(); textos.setSpacing(0)
        self.nome = rotulo(nome, 14, QFont.Weight.ExtraBold)
        self.situacao = rotulo("", 12, cor=TINTA_SUAVE)
        textos.addWidget(self.nome); textos.addWidget(self.situacao)
        lay.addLayout(textos, 1)
        self.chave = Chave(nome)
        lay.addWidget(self.chave)

    def define(self, ligado: bool | None, situacao: str, habilitado: bool = True):
        self.chave.blockSignals(True)
        self.chave.setChecked(bool(ligado))
        self.chave.blockSignals(False)
        self.chave.setEnabled(habilitado and ligado is not None)
        self.situacao.setText(situacao)


class Segmentado(QFrame):
    """Controle de três opções (Boitatá: Dormindo / Sob demanda / Acordado)."""

    def __init__(self, opcoes: list[tuple[str, str]]):
        super().__init__()
        self.setObjectName("segmentado")
        self.setStyleSheet("#segmentado { background: #EDE4D4; border-radius: 12px; }")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(3, 3, 3, 3); lay.setSpacing(2)
        self.botoes: dict[str, QPushButton] = {}
        for ident, texto in opcoes:
            b = QPushButton(texto)
            b.setCheckable(True)
            b.setMinimumHeight(38)
            b.setFont(fonte(13, QFont.Weight.Bold))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(
                "QPushButton { border: 0; border-radius: 10px; padding: 0 12px; background: transparent; color: #4E5C54; }"
                f"QPushButton:checked {{ background: #FFFFFF; color: {BRASA}; }}"
                "QPushButton:disabled { color: #A59C8C; }"
                "QPushButton:checked:disabled { color: #B4380B; }")
            lay.addWidget(b)
            self.botoes[ident] = b

    def seleciona(self, ident: str):
        for k, b in self.botoes.items():
            b.setChecked(k == ident)


# ------------------------------------------------------------------ seções
class SecaoEnergia(QWidget):
    pedir_perfil = Signal(str)
    pedir_acao = Signal(str, bool)

    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        # cartão de consumo
        self.cartao = QFrame(); self.cartao.setObjectName("consumo")
        self.cartao.setStyleSheet(f"#consumo {{ background: {NOITE}; border-radius: 20px; }}")
        self.cartao.setFixedHeight(112)
        c = QHBoxLayout(self.cartao); c.setContentsMargins(22, 0, 12, 0); c.setSpacing(20)
        esq = QVBoxLayout(); esq.setSpacing(2); esq.addStretch()
        self.rot_consumo = rotulo("Consumo agora", 13, QFont.Weight.DemiBold, "#E6D9FF")
        self.val_consumo = rotulo("…", 40, QFont.Weight.ExtraBold, "#FFFFFF", titulo=True)
        self.medidor = Medidor()
        esq.addWidget(self.rot_consumo); esq.addWidget(self.val_consumo); esq.addSpacing(6); esq.addWidget(self.medidor)
        esq.addStretch()
        c.addLayout(esq, 1)
        dir_ = QVBoxLayout(); dir_.setSpacing(2); dir_.addStretch()
        self.rot_duracao = rotulo("Bateria cheia dura", 13, QFont.Weight.DemiBold, "#E6D9FF")
        self.rot_duracao.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.val_duracao = rotulo("", 34, QFont.Weight.ExtraBold, "#FFD08A", titulo=True)
        self.val_duracao.setAlignment(Qt.AlignmentFlag.AlignRight)
        dir_.addWidget(self.rot_duracao); dir_.addWidget(self.val_duracao); dir_.addStretch()
        c.addLayout(dir_)
        c.addWidget(Avatar(96, 18), 0, Qt.AlignmentFlag.AlignVCenter)
        lay.addWidget(self.cartao)

        # perfis
        self.grade_perfis = QHBoxLayout(); self.grade_perfis.setSpacing(10)
        self.cartoes: dict[str, CartaoPerfil] = {}
        lay.addLayout(self.grade_perfis)

        # Boitatá
        boi = QFrame(); boi.setObjectName("boitata")
        boi.setStyleSheet(f"#boitata {{ background: {AREIA}; border-radius: 16px; }}")
        b = QHBoxLayout(boi); b.setContentsMargins(14, 12, 14, 12); b.setSpacing(14)
        b.addWidget(Ladrilho(ICONES["boitata"], "#FF8A4A", "#C2261A", 40, 22))
        bt = QVBoxLayout(); bt.setSpacing(0)
        bt.addWidget(rotulo("Boitatá · placa NVIDIA", 15, QFont.Weight.ExtraBold))
        self.boi_nota = rotulo("", 12, cor=VERDE_ESCURO)
        bt.addWidget(self.boi_nota)
        b.addLayout(bt, 1)
        self.boi_seg = Segmentado([("off", "Dormindo"), ("demanda", "Sob demanda"), ("on", "Acordado")])
        for k in ("demanda", "on"):
            self.boi_seg.botoes[k].setEnabled(False)
            self.boi_seg.botoes[k].setToolTip("Acordar a Boitatá chega numa próxima versão.")
        self.boi_seg.botoes["off"].setEnabled(False)
        b.addWidget(self.boi_seg)
        lay.addWidget(boi)

        # seres
        grade = QGridLayout(); grade.setHorizontalSpacing(10); grade.setVerticalSpacing(10)
        self.saci = LinhaSer("Saci · turbo", ICONES["saci"], "#FF8FA8", "#C2265A")
        self.mapinguari = LinhaSer("Mapinguari · HD", ICONES["mapinguari"], "#A98BD9", "#5B3A8E")
        self.wifi = LinhaSer("Iara · Wi-Fi", ICONES["wifi"], "#6FD3F2", "#2468B8")
        self.bluetooth = LinhaSer("Iara · Bluetooth", ICONES["bluetooth"], "#8FB8F2", "#3A5EB8")
        self.caipora = LinhaSer("Caipora", ICONES["caipora"], "#7FE3B0", "#128A5C")
        self.boto = LinhaSer("Boto · laboratório", ICONES["boto"], "#F5A3D0", "#8E3A9E")
        for i, linha in enumerate([self.saci, self.mapinguari, self.wifi, self.bluetooth, self.caipora, self.boto]):
            grade.addWidget(linha, i // 2, i % 2)
        grade.setColumnStretch(0, 1); grade.setColumnStretch(1, 1)
        lay.addLayout(grade)
        self.saci.chave.setToolTip("O turbo segue o perfil: Pororoca e Correnteza ligam, Remanso e Sereno desligam.")
        self.mapinguari.chave.toggled.connect(lambda v: self.pedir_acao.emit("hd", v))
        self.wifi.chave.toggled.connect(lambda v: self.pedir_acao.emit("wifi", v))
        self.bluetooth.chave.toggled.connect(lambda v: self.pedir_acao.emit("bluetooth", v))

        self.mensagem = rotulo("", 13, QFont.Weight.Bold, VERDE_ESCURO)
        self.mensagem.setMinimumHeight(18)
        self.mensagem.setAccessibleDescription("mensagens da Toca")
        lay.addWidget(self.mensagem)
        lay.addStretch()

    def _monta_perfis(self, perfis: list[dict]):
        ids = [p["id"] for p in perfis]
        if list(self.cartoes) == ids:
            return
        while self.grade_perfis.count():
            w = self.grade_perfis.takeAt(0).widget()
            if w:
                w.deleteLater()
        self.cartoes.clear()
        for p in perfis:
            cartao = CartaoPerfil(p["id"], p.get("nome") or p["id"].title(), p.get("descricao", ""))
            cartao.clicked.connect(lambda _=False, i=p["id"]: self.pedir_perfil.emit(i))
            self.grade_perfis.addWidget(cartao)
            self.cartoes[p["id"]] = cartao

    def mostra(self, e: Estado):
        en = e.energia
        perfis = sorted(en.get("perfis", []),
                        key=lambda p: (ORDEM_PERFIS.index(p["id"]) if p["id"] in ORDEM_PERFIS else 99, p["id"]))
        self._monta_perfis(perfis)
        for ident, cartao in self.cartoes.items():
            cartao.setChecked(ident == en.get("perfil"))

        watts = en.get("watts")
        wh = en.get("capacidade_wh")
        pct = en.get("bateria", 0)
        if en.get("fonte") == "bateria" and watts:
            self.rot_consumo.setText("Consumo agora")
            self.val_consumo.setText(f"{watts:.1f} W".replace(".", ","))
            if wh:
                horas = wh / watts
                h, m = int(horas), round((horas - int(horas)) * 60)
                if m == 60:
                    h, m = h + 1, 0
                self.rot_duracao.setText("Bateria cheia dura")
                self.val_duracao.setText(f"≈ {h}h{m:02d}")
                cor = "#7FE3B0" if horas >= 5 else "#FFD08A" if horas >= 3.5 else "#FF8A70"
                self.medidor.define(horas / 9, cor)
        elif en:
            self.rot_consumo.setText("Na tomada")
            self.val_consumo.setText(f"Bateria {pct}%")
            self.rot_duracao.setText("Capacidade real")
            self.val_duracao.setText(f"{wh:.1f} Wh".replace(".", ",") if wh else "")
            self.medidor.define(pct / 100, "#7FE3B0")
        else:
            self.rot_consumo.setText("Sem dados")
            self.val_consumo.setText("…")
            self.val_duracao.setText("")
            self.medidor.define(0, "#7FE3B0")

        self.boi_seg.seleciona("off" if e.boitata_dormindo else "on")
        self.boi_nota.setText("desligada de vez: máxima economia" if e.boitata_dormindo
                              else "acordada: gasta energia mesmo parada")
        self.boi_nota.setStyleSheet(f"color: {VERDE_ESCURO if e.boitata_dormindo else BRASA}; background: transparent;")

        self.saci.define(e.turbo, "girando até 3,4 GHz" if e.turbo else "calmo, processador fresco", habilitado=False)
        if e.hd_acordado is None:
            self.mapinguari.define(None, "sem HD em /data")
        else:
            self.mapinguari.define(e.hd_acordado, "acordado, arquivos à mão" if e.hd_acordado else "hibernando, motor parado")
        if e.wifi is None:
            self.wifi.define(None, "sem Wi-Fi")
        else:
            self.wifi.define(e.wifi, (f"conectada em {e.wifi_rede}" if e.wifi_rede else "ligada, sem rede") if e.wifi
                             else "em silêncio")
        self.bluetooth.define(e.bluetooth, "sem Bluetooth" if e.bluetooth is None else "ligado" if e.bluetooth else "desligado")
        self.caipora.define(False, "em breve: câmera e microfone", habilitado=False)
        self.boto.define(False, "em breve: redes de laboratório", habilitado=False)

    def avisa(self, texto: str, erro: bool = False):
        self.mensagem.setText(texto)
        self.mensagem.setStyleSheet(f"color: {BRASA if erro else VERDE_ESCURO}; background: transparent;")


class SecaoEmBreve(QWidget):
    def __init__(self, titulo: str):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.addStretch()
        caminho = arte("cordel-figura.svg")
        if caminho:
            fig = QLabel()
            fig.setPixmap(pixmap_svg(str(caminho), 101, 200))
            fig.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(fig)
        t = rotulo(titulo, 24, QFont.Weight.ExtraBold, titulo=True)
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(t)
        s = rotulo("Esta seção chega numa próxima versão da Toca. Por enquanto, a seção Energia já funciona.",
                   14, cor=TINTA_SUAVE)
        s.setWordWrap(True); s.setAlignment(Qt.AlignmentFlag.AlignCenter); s.setFixedWidth(380)
        s.setMinimumHeight(s.heightForWidth(380))
        lay.addWidget(s, 0, Qt.AlignmentFlag.AlignHCenter)
        lay.addStretch()


# ------------------------------------------------------------------ janela
class Toca(QWidget):
    def __init__(self, secao_inicial: str = "energia"):
        super().__init__()
        self.setWindowTitle("Toca do Curupira")
        self.setWindowIcon(QIcon(str(arte("cordel-busto.svg") or "")))
        self.resize(960, 640)
        self.setMinimumSize(900, 600)
        self.setObjectName("toca")
        self.setStyleSheet(f"#toca {{ background: #FFFFFF; }} QToolTip {{ font-size: 12px; }}")
        self.pool = QThreadPool.globalInstance()
        self.ocupado = False

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

        self.pilha = QStackedWidget()
        self.botoes_nav: dict[str, QPushButton] = {}
        for ident, titulo in SECOES:
            b = QPushButton(titulo)
            b.setCheckable(True); b.setAutoExclusive(True)
            b.setMinimumHeight(44)
            b.setFont(fonte(14, QFont.Weight.Bold))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setIconSize(QSize(20, 20))
            b.setStyleSheet(
                "QPushButton { text-align: left; padding: 0 12px; border: 0; border-radius: 12px;"
                " background: transparent; color: #3E4C44; }"
                "QPushButton:hover { background: #F4EADB; }"
                f"QPushButton:checked {{ background: #FFFFFF; color: {VERDE_ESCURO}; }}")
            b.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            b.toggled.connect(lambda marcado, i=ident, bt=b: self._troca_secao(i, bt, marcado))
            n.addWidget(b)
            self.botoes_nav[ident] = b
            if ident == "energia":
                self.energia = SecaoEnergia()
                self.pilha.addWidget(self.energia)
            else:
                self.pilha.addWidget(SecaoEmBreve(titulo))
        n.addStretch()
        n.addWidget(rotulo(f"Curupira OS · Toca {VERSAO}", 11, cor="#8A968F"))
        raiz.addWidget(nav)

        conteudo = QWidget()
        cl = QVBoxLayout(conteudo); cl.setContentsMargins(24, 22, 24, 22)
        cl.addWidget(self.pilha)
        raiz.addWidget(conteudo, 1)

        self.energia.pedir_perfil.connect(self.troca_perfil)
        self.energia.pedir_acao.connect(self.acao)

        self.botoes_nav.get(secao_inicial, self.botoes_nav["energia"]).setChecked(True)
        self._icones_nav()

        self.relogio = QTimer(self)
        self.relogio.timeout.connect(self.atualiza)
        self.relogio.start(4000)

    def _icones_nav(self):
        for ident, b in self.botoes_nav.items():
            b.setIcon(QIcon(icone(ICONES[ident], VERDE_ESCURO if b.isChecked() else "#3E4C44")))

    def _troca_secao(self, ident: str, botao: QPushButton, marcado: bool):
        if marcado:
            self.pilha.setCurrentIndex([s[0] for s in SECOES].index(ident))
        self._icones_nav()

    # -- dados
    def atualiza(self):
        if self.ocupado:
            return
        self.ocupado = True
        self.pool.start(Tarefa(le_estado, self._recebe))

    def _recebe(self, e):
        self.ocupado = False
        if isinstance(e, Exception):
            self.energia.avisa(f"Erro ao ler o sistema: {e}", erro=True)
            return
        self.energia.mostra(e)
        if e.erro:
            self.energia.avisa(e.erro, erro=True)

    def _executa(self, cmd: list[str], sucesso: str):
        self.energia.avisa("Um instante…")

        def trabalho():
            r = roda(*cmd, tempo=60)
            if r is None:
                return f"Não consegui rodar {cmd[0]}."
            if r.returncode != 0:
                return (r.stderr or r.stdout).strip().splitlines()[-1] if (r.stderr or r.stdout).strip() else "Falhou."
            return ""

        def fim(erro):
            erro = str(erro) if isinstance(erro, Exception) else erro
            self.energia.avisa(erro or sucesso, erro=bool(erro))
            self.atualiza()

        self.pool.start(Tarefa(trabalho, fim))

    def troca_perfil(self, ident: str):
        nome = self.energia.cartoes[ident].nome if ident in self.energia.cartoes else ident
        self._executa([comando_curupira(), ident], f"Perfil {nome} aplicado.")

    def acao(self, qual: str, ligar: bool):
        if qual == "wifi":
            self._executa(["nmcli", "radio", "wifi", "on" if ligar else "off"],
                          "A Iara voltou a ouvir o Wi-Fi." if ligar else "A Iara silenciou o Wi-Fi.")
        elif qual == "bluetooth":
            cmd = ["sh", "-c", "rfkill unblock bluetooth && sleep 1 && bluetoothctl power on"] if ligar \
                else ["bluetoothctl", "power", "off"]
            self._executa(cmd, "Bluetooth ligado." if ligar else "Bluetooth desligado.")
        elif qual == "hd":
            if ligar:
                self._executa(["ls", "/data"], "O Mapinguari acordou: /data está à mão.")
            else:
                self.energia.avisa("O Mapinguari volta a hibernar sozinho depois de 10 minutos sem uso.")
                self.atualiza()


def main() -> int:
    global FONTE_TITULO, FONTE_TEXTO
    args = argparse.ArgumentParser(description="Toca do Curupira: central de controle da Curupira OS")
    args.add_argument("--secao", default="energia", choices=[s[0] for s in SECOES])
    args.add_argument("--captura", metavar="PNG", help="desenha a janela num PNG e sai")
    op = args.parse_args()

    if op.captura:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication(sys.argv)
    app.setApplicationName("Toca do Curupira")
    app.setDesktopFileName("io.github.pabloherzberg.Toca")
    FONTE_TITULO, FONTE_TEXTO = carrega_fontes()
    app.setFont(fonte(14))

    janela = Toca(op.secao)
    if op.captura:
        janela.energia.mostra(le_estado())
        janela.show()
        app.processEvents()
        janela.grab().save(op.captura)
        return 0
    janela.show()
    janela.atualiza()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
