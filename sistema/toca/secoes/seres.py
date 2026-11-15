"""Seção Seres da mata: o bestiário, com o estado de cada ser agora."""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QAbstractButton, QGridLayout, QHBoxLayout, QSizePolicy, QVBoxLayout

import sistema
from visual import (BORDA, BRASA, TINTA, TINTA_SUAVE, VERDE, VERDE_ESCURO, LadrilhoSer, Secao,
                    cabecalho, rotulo, tempo_relativo)

# (chave, nome, papel, descrição, seção onde se controla) - textos do mockup Main.dc.html
SERES = [
    ("curupira", "Curupira", "central de controle", "Guardião da mata. Decide quem acorda e quem dorme.", "energia"),
    ("boitata", "Boitatá", "placa de vídeo NVIDIA", "Cobra de fogo. Dorme por padrão; acordada gasta 3 a 4 W.", "energia"),
    ("mapinguari", "Mapinguari", "HD de 1 TB", "Gigante lento que hiberna até você abrir seus arquivos.", "energia"),
    ("iara", "Iara", "Wi-Fi e Bluetooth", "Mãe d'água das ondas. Silencia no modo avião.", "rede"),
    ("saci", "Saci", "turbo do processador", "Redemoinho travesso: rápido, quente e guloso de bateria.", "energia"),
    ("caipora", "Caipora", "privacidade", "Some sem deixar rastro: câmera e microfone cortados, MAC aleatório.", "privacidade"),
    ("boto", "Boto", "laboratório de rede", "O encantado disfarçado: redes isoladas, proxy e captura.", "rede"),
    ("cuca", "Cuca", "snapshots do sistema", "Guarda o passado. Quebrou algo? Ela volta no tempo.", "snapshots"),
]


class CartaoSer(QAbstractButton):
    """Cartão clicável: ladrilho, nome, papel, descrição e a situação atual."""

    def __init__(self, chave: str, nome: str, papel: str, descricao: str):
        super().__init__()
        self.chave, self.nome, self.papel, self.descricao = chave, nome, papel, descricao
        self.situacao, self.economiza = "…", True
        self.ladrilho = LadrilhoSer(chave, 52)
        self.ladrilho.setParent(self)
        self.ladrilho.move(12, 12)
        self.ladrilho.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(108)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(f"{nome}, {papel}")

    def sizeHint(self) -> QSize:
        return QSize(300, 108)

    def define(self, situacao: str, economiza: bool, acordado: bool = True):
        self.situacao, self.economiza = situacao, economiza
        self.ladrilho.acorda(acordado)
        self.setAccessibleDescription(f"{self.descricao} Agora: {situacao}")
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        p.setPen(QColor(VERDE if self.hasFocus() else BORDA))
        p.setBrush(QColor("#FFFDF9" if self.underMouse() else "#FFFFFF"))
        p.drawRoundedRect(r, 16, 16)
        x = 76
        w = r.width() - x - 14
        p.setPen(QColor(TINTA))
        from visual import fonte
        p.setFont(fonte(17, QFont.Weight.ExtraBold, titulo=True))
        p.drawText(QRectF(x, 10, w, 24), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.nome)
        p.setPen(QColor(TINTA_SUAVE))
        p.setFont(fonte(12, QFont.Weight.Bold))
        p.drawText(QRectF(x, 32, w, 16), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.papel.upper())
        p.setFont(fonte(12))
        p.drawText(QRectF(x, 48, w, 34), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                   self.descricao)
        cor = VERDE_ESCURO if self.economiza else BRASA
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(cor))
        p.drawEllipse(QRectF(x, 88, 8, 8))
        p.setPen(QColor(cor))
        p.setFont(fonte(12, QFont.Weight.ExtraBold))
        p.drawText(QRectF(x + 14, 82, w - 14, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                   p.fontMetrics().elidedText(self.situacao, Qt.TextElideMode.ElideRight, int(w - 14)))

    def enterEvent(self, e):
        self.ladrilho.espia(True); self.update(); super().enterEvent(e)

    def leaveEvent(self, e):
        self.ladrilho.espia(False); self.update(); super().leaveEvent(e)


class SecaoSeres(Secao):
    intervalo = 15000   # lê os snapshots pelo curupira (polkit): sem pressa

    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(14)
        lay.addWidget(cabecalho("Seres da mata",
                                "Cada peça do computador é um ser encantado. Clique num ser para cuidar dele."))
        grade = QGridLayout(); grade.setHorizontalSpacing(10); grade.setVerticalSpacing(10)
        self.cartoes: dict[str, CartaoSer] = {}
        for i, (chave, nome, papel, desc, secao) in enumerate(SERES):
            c = CartaoSer(chave, nome, papel, desc)
            c.clicked.connect(lambda _=False, s=secao: self.ir_para.emit(s))
            grade.addWidget(c, i // 2, i % 2)
            self.cartoes[chave] = c
        grade.setColumnStretch(0, 1); grade.setColumnStretch(1, 1)
        lay.addLayout(grade)
        lay.addStretch()

    def coleta(self):
        d = sistema.resumo_energia()
        snaps = sistema.snapshots()
        d["snapshots"] = snaps
        return d

    def mostra(self, d: dict):
        en = d.get("energia", {})
        nomes = {p["id"]: p["nome"] for p in en.get("perfis", [])}
        perfil = nomes.get(en.get("perfil", ""), "nenhum")
        self.cartoes["curupira"].define(f"perfil {perfil} · troca automática {'ligada' if en.get('auto') else 'desligada'}",
                                        en.get("perfil") != "pororoca")
        dormindo = d.get("boitata_dormindo", True)
        self.cartoes["boitata"].define("dormindo" if dormindo else "acordada, gastando energia", dormindo, not dormindo)
        hd = d.get("hd")
        self.cartoes["mapinguari"].define("sem HD em /data" if hd is None else "acordado" if hd else "hibernando", not hd, bool(hd))
        w, bt = d.get("wifi"), d.get("bluetooth")
        partes = ["Wi-Fi " + (f"em {d['wifi_rede']}" if w and d.get("wifi_rede") else "ligado" if w else "desligado")]
        partes.append("Bluetooth " + ("ligado" if bt else "desligado"))
        self.cartoes["iara"].define(" · ".join(partes), not bt, bool(w or bt))
        t = d.get("turbo")
        self.cartoes["saci"].define("girando (turbo ligado)" if t else "calmo (turbo desligado)", not t, bool(t))
        cam, mic = en.get("camera_cortada"), d.get("microfone_mudo")
        txt = ("câmera cortada" if cam else "câmera liberada") + " · " + ("microfone mudo" if mic else "microfone aberto")
        self.cartoes["caipora"].define(txt, bool(cam and mic), bool(cam or mic))
        lab = d.get("lab")
        self.cartoes["boto"].define(f'rede "{sistema.REDE_LAB}" ativa' if lab else "laboratório parado", True, bool(lab))
        snaps = d.get("snapshots", {})
        if snaps.get("_erro"):
            self.cartoes["cuca"].define(snaps["_erro"], True)
        else:
            itens = snaps.get("itens", [])
            if itens:
                ultimo = min(itens, key=lambda s: s["idade"])
                self.cartoes["cuca"].define(f"{len(itens)} snapshots · último {tempo_relativo(ultimo['idade'])}", True)
            else:
                self.cartoes["cuca"].define("nenhum snapshot ainda", True)
