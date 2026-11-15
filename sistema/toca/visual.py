"""Cores, fontes e peças de interface da Toca do Curupira (seguem o mockup Central.dc.html)."""

from __future__ import annotations

import math
import os
import re
import time
from pathlib import Path

from PySide6.QtCore import QByteArray, QObject, QRectF, QRunnable, QSize, Qt, QThreadPool, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QFontDatabase, QLinearGradient, QPainter, QPainterPath, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QAbstractButton, QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy,
                               QVBoxLayout, QWidget)

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
    # pegadas ao contrário: o calcanhar fica na frente
    "curupira": "M9 4c1.7 0 2.5 1.6 2.5 3.5S10.7 11 9 11 6.5 9.4 6.5 7.5 7.3 4 9 4z M9 12.5v1.5 "
                "M15 11c1.7 0 2.5 1.6 2.5 3.5S16.7 18 15 18s-2.5-1.6-2.5-3.5S13.3 11 15 11z M15 19.5V21",
    "cuca": "M3 12a9 9 0 1 0 3-6.7 M3 4v5h5 M12 7v5l3 2",
    "microfone": "M12 3a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V6a3 3 0 0 1 3-3z M5 11a7 7 0 0 0 14 0 M12 18v3",
    "camera": "M3 7h4l2-3h6l2 3h4v12H3z M12 10a3.5 3.5 0 1 0 0 7a3.5 3.5 0 1 0 0-7",
    "mascara": "M3 8c3-2 15-2 18 0 0 6-3 9-6 9-1.5 0-2-2-3-2s-1.5 2-3 2c-3 0-6-3-6-9z M8 11h2 M14 11h2",
    "lab": "M9 3h6 M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3 M7 15h10",
    "sol": "M12 8a4 4 0 1 0 0 8a4 4 0 1 0 0-8 M12 2v2 M12 20v2 M4.9 4.9l1.4 1.4 M17.7 17.7l1.4 1.4 M2 12h2 "
           "M20 12h2 M4.9 19.1l1.4-1.4 M17.7 6.3l1.4-1.4",
    "lua": "M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z",
    "mais": "M12 5v14 M5 12h14",
}

# cores dos ladrilhos de cada ser (degradê)
DEGRADES = {
    "curupira": ("#FFD08A", "#FF7A45"),
    "boitata": ("#FF8A4A", "#C2261A"),
    "mapinguari": ("#A98BD9", "#5B3A8E"),
    "iara": ("#6FD3F2", "#2468B8"),
    "wifi": ("#6FD3F2", "#2468B8"),
    "bluetooth": ("#8FB8F2", "#3A5EB8"),
    "saci": ("#FF8FA8", "#C2265A"),
    "caipora": ("#7FE3B0", "#128A5C"),
    "boto": ("#F5A3D0", "#8E3A9E"),
    "cuca": ("#B5E08A", "#4E8A2E"),
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


def inicia_fontes():
    global FONTE_TITULO, FONTE_TEXTO
    FONTE_TITULO, FONTE_TEXTO = carrega_fontes()


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
    repo = AQUI.parent.parent / "arte"
    for base in (os.environ.get("CURUPIRA_ARTE"), AQUI / "arte", repo, repo / "propostas"):
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


# Como cada ser se mexe quando está acordado: (movimento, x, y do centro na arte de 64 px, período em s).
# O que se mexe é o grupo id="vivo" de arte/icones/seres/<ser>.svg; "base" fica parado e "frente" passa por cima.
MOVIMENTOS = {
    "curupira": ("passos", 32, 32, 1.4),      # as pegadas se alternam
    "boitata": ("pulsar", 32, 48, 1.1),       # a chama respira a partir do pé
    "mapinguari": ("girar", 32, 32, 2.6),     # o olho é o disco: gira
    "iara": ("balancar", 32, 32, 2.2),        # a onda vai e volta
    "bluetooth": ("piscar", 32, 32, 1.6),
    "saci": ("balancar", 32, 32, 0.9),        # redemoinho apressado
    "caipora": ("piscar", 32, 32, 2.4),
    "boto": ("pulsar", 32, 30, 1.8),
    "cuca": ("girar", 32, 32, -6.0),          # os ponteiros andam para trás
    "camera": ("piscar", 32, 32, 2.0),
    "microfone": ("piscar", 32, 32, 1.2),
    "mascara": ("piscar", 32, 32, 3.0),
}
ALIAS_SERES = {"wifi": "iara"}


def animacoes_ligadas() -> bool:
    """Respeita quem desligou as animações no Plasma (Configurações → velocidade das animações no mínimo)."""
    if os.environ.get("CURUPIRA_SEM_ANIMACAO"):
        return False
    try:
        for linha in (Path.home() / ".config" / "kdeglobals").read_text(encoding="utf-8", errors="ignore").splitlines():
            if linha.startswith("AnimationDurationFactor="):
                return float(linha.split("=", 1)[1]) > 0
    except (OSError, ValueError):
        pass
    return True


class _Compasso(QObject):
    """Um relógio só para todos os ladrilhos. Só bate rápido com a janela da Toca em uso e algum ser acordado
    à vista: parada ou em segundo plano, a Toca não acorda o processador à toa."""

    def __init__(self):
        super().__init__()
        self.ladrilhos: list["LadrilhoSer"] = []
        self.ligado = animacoes_ligadas()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.bate)

    def entra(self, ladrilho: "LadrilhoSer"):
        self.ladrilhos.append(ladrilho)
        ladrilho.destroyed.connect(lambda _=None, l=ladrilho: l in self.ladrilhos and self.ladrilhos.remove(l))
        if self.ligado and not self.timer.isActive():
            self.timer.start(40)

    def bate(self):
        em_uso = QApplication.activeWindow() is not None
        vivos = [l for l in self.ladrilhos if l.mexendo() and l.isVisible()] if em_uso else []
        self.timer.setInterval(40 if vivos else 700)
        for l in vivos:
            l.update()


_COMPASSO: _Compasso | None = None


class LadrilhoSer(QWidget):
    """Ladrilho cor da noite com a arte de um ser (arte/icones/seres). Acordado, o ser se mexe; dormindo, fica
    apagado e parado. Passar o mouse num ser dormindo (espiar) faz ele se mexer um pouco."""

    def __init__(self, chave: str, tamanho: int = 36):
        super().__init__()
        self.chave = ALIAS_SERES.get(chave, chave)
        self.tam = tamanho
        self.acordado = True
        self.espiando = False
        self.setFixedSize(tamanho, tamanho)
        self.camadas: dict[str, QPixmap] = {}
        caminho = arte(f"icones/seres/{self.chave}.svg")
        if caminho:
            texto = caminho.read_text(encoding="utf-8")
            for nome in ("ladrilho", "base", "vivo", "frente"):
                outros = "|".join(n for n in ("ladrilho", "base", "vivo", "frente") if n != nome)
                so_esta = re.sub(rf'<g id="(?:{outros})">.*?</g>', "", texto, flags=re.S)
                self.camadas[nome] = pixmap_svg(QByteArray(so_esta.encode()), tamanho, tamanho)
        global _COMPASSO
        if _COMPASSO is None:
            _COMPASSO = _Compasso()
        _COMPASSO.entra(self)

    def acorda(self, acordado: bool):
        if acordado != self.acordado:
            self.acordado = acordado
            self.update()

    def espia(self, espiando: bool):
        self.espiando = espiando
        self.update()

    def mexendo(self) -> bool:
        return self.acordado or self.espiando

    def paintEvent(self, _):
        if not self.camadas:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.drawPixmap(0, 0, self.camadas["ladrilho"])
        apagado = 1.0 if self.acordado else 0.7 if self.espiando else 0.5
        p.setOpacity(apagado)
        p.drawPixmap(0, 0, self.camadas["base"])
        movimento, cx, cy, periodo = MOVIMENTOS.get(self.chave, ("", 32, 32, 1.0))
        e = self.tam / 64
        p.save()
        if self.mexendo() and _COMPASSO is not None and _COMPASSO.ligado and movimento:
            onda = math.sin(2 * math.pi * time.monotonic() / abs(periodo))
            if movimento == "pulsar":
                p.translate(cx * e, cy * e); p.scale(1 + 0.09 * onda, 1 + 0.12 * onda); p.translate(-cx * e, -cy * e)
            elif movimento == "girar":
                giro = 360 * (time.monotonic() % abs(periodo)) / periodo
                p.translate(cx * e, cy * e); p.rotate(giro); p.translate(-cx * e, -cy * e)
            elif movimento == "balancar":
                p.translate(2.4 * e * onda, 0)
            elif movimento == "piscar":
                p.setOpacity(apagado * (0.62 + 0.38 * onda))
            elif movimento == "passos":
                p.setOpacity(apagado * (0.35 if onda < 0 else 1.0))
        p.drawPixmap(0, 0, self.camadas["vivo"])
        p.restore()
        p.drawPixmap(0, 0, self.camadas["frente"])


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

    def __init__(self, nome: str, chave: str):
        super().__init__()
        self.setObjectName("linhaSer")
        self.setStyleSheet(f"#linhaSer {{ border: 1px solid {BORDA}; border-radius: 16px; background: #FFFFFF; }}")
        self.setMinimumHeight(60)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(12)
        self.ladrilho = LadrilhoSer(chave)
        lay.addWidget(self.ladrilho)
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
        self.ladrilho.acorda(bool(ligado))
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




# ------------------------------------------------------------------ peças comuns às seções
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

    @staticmethod
    def inicia(funcao, ao_terminar):
        QThreadPool.globalInstance().start(Tarefa(funcao, ao_terminar))


class Secao(QWidget):
    """Base das seções. coleta() roda fora da interface; mostra() recebe o resultado.
    intervalo: de quanto em quanto tempo (ms) a seção visível é relida."""

    intervalo = 4000

    executar = Signal(list, str, object)   # comando, mensagem de sucesso, função opcional(resultado) -> mensagem
    ir_para = Signal(str)
    avisar = Signal(str, bool)

    def coleta(self):
        return None

    def mostra(self, dados):
        pass


def cabecalho(titulo: str, subtitulo: str = "") -> QWidget:
    w = QWidget()
    lay = QVBoxLayout(w); lay.setContentsMargins(0, 0, 0, 2); lay.setSpacing(0)
    lay.addWidget(rotulo(titulo, 26, QFont.Weight.ExtraBold, titulo=True))
    if subtitulo:
        s = rotulo(subtitulo, 13, cor=TINTA_SUAVE)
        s.setWordWrap(True)
        lay.addWidget(s)
    return w


class Cartao(QFrame):
    """Caixa com borda clara ou fundo areia, como no mockup."""

    _n = 0

    def __init__(self, areia: bool = False, raio: int = 16):
        super().__init__()
        Cartao._n += 1
        self.setObjectName(f"cartao{Cartao._n}")
        fundo = AREIA if areia else "#FFFFFF"
        borda = "none" if areia else f"1px solid {BORDA}"
        self.setStyleSheet(f"#{self.objectName()} {{ background: {fundo}; border: {borda}; border-radius: {raio}px; }}")


def botao(texto: str, primario: bool = False, icone_svg: str | None = None) -> QPushButton:
    b = QPushButton(texto)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setFont(fonte(13, QFont.Weight.Bold))
    b.setMinimumHeight(38)
    if primario:
        b.setStyleSheet(f"QPushButton {{ background: {VERDE}; color: #FFFFFF; border: 0; border-radius: 12px; padding: 0 16px; }}"
                        f"QPushButton:hover {{ background: {VERDE_ESCURO}; }}"
                        "QPushButton:disabled { background: #A9CDBD; }")
        cor_icone = "#FFFFFF"
    else:
        b.setStyleSheet(f"QPushButton {{ background: #FFFFFF; color: {TINTA}; border: 1px solid #E2D7C3; border-radius: 12px; padding: 0 14px; }}"
                        "QPushButton:hover { background: #FBF4E8; }"
                        "QPushButton:disabled { color: #A59C8C; }")
        cor_icone = TINTA
    if icone_svg:
        from PySide6.QtGui import QIcon
        b.setIcon(QIcon(icone(icone_svg, cor_icone, 18)))
        b.setIconSize(QSize(18, 18))
    return b


class LinhaInfo(QWidget):
    """Par rótulo: valor (para dados de rede, por exemplo)."""

    def __init__(self, nome: str, largura_nome: int = 110):
        super().__init__()
        lay = QHBoxLayout(self); lay.setContentsMargins(0, 1, 0, 1); lay.setSpacing(10)
        n = rotulo(nome, 13, cor=TINTA_SUAVE); n.setFixedWidth(largura_nome)
        self.valor = rotulo("…", 13, QFont.Weight.Bold)
        self.valor.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.valor.setWordWrap(True)
        lay.addWidget(n); lay.addWidget(self.valor, 1)

    def define(self, texto: str):
        self.valor.setText(texto or "—")


def linha_ser(chave: str, nome: str) -> "LinhaSer":
    return LinhaSer(nome, chave)


def tempo_relativo(segundos: float) -> str:
    s = int(max(0, segundos))
    if s < 90:
        return "agora há pouco"
    if s < 3600:
        return f"há {s // 60} min"
    if s < 86400:
        h = s // 3600
        return f"há {h} hora" + ("s" if h > 1 else "")
    d = s // 86400
    return f"há {d} dia" + ("s" if d > 1 else "")
