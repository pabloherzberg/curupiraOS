"""Seção Aparência: claro ou escuro, cor de destaque e papel de parede."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QAbstractButton, QHBoxLayout, QVBoxLayout, QWidget

import sistema
from visual import (BORDA, ICONES, TINTA, TINTA_SUAVE, VERDE, Cartao, Secao, Segmentado, arte, botao, Faixa,
                    fonte, pixmap_svg, rotulo)


class Amostra(QAbstractButton):
    """Bolinha de cor de destaque."""

    def __init__(self, cor: str, nome: str):
        super().__init__()
        self.cor, self.nome = cor, nome
        self.setCheckable(True)
        self.setFixedSize(44, 44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(nome)
        self.setAccessibleName(f"Cor de destaque {nome}")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def sizeHint(self) -> QSize:
        return QSize(44, 44)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.isChecked() or self.hasFocus():
            p.setPen(QPen(QColor(TINTA if self.isChecked() else VERDE), 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QRectF(2, 2, 40, 40))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(self.cor))
        p.drawEllipse(QRectF(7, 7, 30, 30))


class Miniatura(QAbstractButton):
    """Miniatura de papel de parede (16:9)."""

    def __init__(self, caminho: Path, nome: str, selo: str = ""):
        super().__init__()
        self.caminho, self.nome, self.selo = caminho, nome, selo
        self.setCheckable(True)
        self.setFixedSize(208, 140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName(f"Papel de parede {nome}")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        if caminho.suffix == ".svg":
            self.pm = pixmap_svg(str(caminho), 192, 108)
        else:   # miniatura pronta (o papel de parede animado)
            self.pm = QPixmap(str(caminho)).scaled(384, 216, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                                    Qt.TransformationMode.SmoothTransformation)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(8, 4, 192, 108)
        caminho = QPainterPath(); caminho.addRoundedRect(r, 12, 12)
        p.save(); p.setClipPath(caminho); p.drawPixmap(r.toRect(), self.pm); p.restore()
        if self.selo:   # etiqueta no canto: "animado"
            p.setFont(fonte(11, QFont.Weight.ExtraBold))
            largura = p.fontMetrics().horizontalAdvance(self.selo) + 16
            p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor("#FF7A45"))
            p.drawRoundedRect(QRectF(r.right() - largura - 8, r.top() + 8, largura, 20), 10, 10)
            p.setPen(QColor("#241A4A"))
            p.drawText(QRectF(r.right() - largura - 8, r.top() + 8, largura, 20), Qt.AlignmentFlag.AlignCenter, self.selo)
        p.setPen(QPen(QColor(VERDE if self.isChecked() else BORDA), 3 if self.isChecked() else 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(r, 12, 12)
        p.setPen(QColor(TINTA))
        p.setFont(fonte(13, QFont.Weight.Bold))
        p.drawText(QRectF(8, 116, 192, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                   self.nome + ("  ✓" if self.isChecked() else ""))


class SecaoAparencia(Secao):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(12)
        lay.addWidget(Faixa("aparencia", "Aparência", "As cores do entardecer da Curupira no seu Plasma."))

        # claro ou escuro
        tema = Cartao(areia=True)
        tl = QHBoxLayout(tema); tl.setContentsMargins(16, 12, 14, 12)
        tt = QVBoxLayout(); tt.setSpacing(0)
        tt.addWidget(rotulo("Tema", 15, QFont.Weight.ExtraBold))
        self.nota_tema = rotulo("Curupira para o dia, Curupira Noite para a noite na mata.", 12, cor=TINTA_SUAVE)
        tt.addWidget(self.nota_tema)
        tl.addLayout(tt, 1)
        self.seg_tema = Segmentado([("claro", "Curupira"), ("escuro", "Curupira Noite")])
        self.seg_tema.botoes["claro"].clicked.connect(lambda: self._tema(escuro=False))
        self.seg_tema.botoes["escuro"].clicked.connect(lambda: self._tema(escuro=True))
        self.tem_curupira = True
        tl.addWidget(self.seg_tema)
        lay.addWidget(tema)

        # cor de destaque
        cor = Cartao()
        cl = QVBoxLayout(cor); cl.setContentsMargins(16, 12, 16, 12); cl.setSpacing(6)
        cl.addWidget(rotulo("Cor de destaque", 15, QFont.Weight.ExtraBold))
        linha = QHBoxLayout(); linha.setSpacing(6)
        self.amostras: dict[str, Amostra] = {}
        for hexa, nome in sistema.CORES_DESTAQUE:
            a = Amostra(hexa, nome)
            a.clicked.connect(lambda _=False, h=hexa, n=nome: self._destaque(h, n))
            linha.addWidget(a)
            self.amostras[hexa.upper()] = a
        self.nome_destaque = rotulo("", 13, cor=TINTA_SUAVE)
        linha.addSpacing(8); linha.addWidget(self.nome_destaque); linha.addStretch()
        cl.addLayout(linha)
        lay.addWidget(cor)

        # papel de parede
        papel = Cartao()
        pl = QVBoxLayout(papel); pl.setContentsMargins(16, 12, 16, 8); pl.setSpacing(4)
        pl.addWidget(rotulo("Papel de parede", 15, QFont.Weight.ExtraBold))
        mini = QHBoxLayout(); mini.setSpacing(4)
        self.miniaturas: list[Miniatura] = []
        for arquivo, nome, pacote in sistema.PAPEIS:
            caminho = arte(arquivo)
            if caminho:
                m = Miniatura(caminho, nome)
                m.pacote = pacote
                m.clicked.connect(lambda _=False, c=caminho, n=nome, p=pacote:
                                  self._papel(sistema.caminho_papel(c, p), n))
                mini.addWidget(m)
                self.miniaturas.append(m)
        # o papel de parede animado: os seres da mata reagem ao que o computador está fazendo
        self.mini_vivo = None
        previa = sistema.previa_papel_vivo()
        if previa:
            self.mini_vivo = Miniatura(previa, "Mata Viva", selo="animado")
            self.mini_vivo.pacote = sistema.PAPEL_VIVO
            self.mini_vivo.clicked.connect(lambda: self._papel_vivo(None))
            mini.addWidget(self.mini_vivo)
        mini.addStretch()
        pl.addLayout(mini)
        # ajustes do Mata Viva (só aparecem com ele em uso)
        self.vivo = QWidget()
        vl = QVBoxLayout(self.vivo); vl.setContentsMargins(8, 4, 8, 8); vl.setSpacing(6)
        linha_mov = QHBoxLayout(); linha_mov.setSpacing(10)
        linha_mov.addWidget(rotulo("A mata se mexe", 13, QFont.Weight.Bold))
        self.seg_mov = Segmentado([("tomada", "Só na tomada"), ("sempre", "Sempre"), ("parado", "Parada")])
        for chave in sistema.MOVIMENTOS_DO_PAPEL:
            self.seg_mov.botoes[chave].clicked.connect(lambda _=False, c=chave: self._papel_vivo(c))
        linha_mov.addWidget(self.seg_mov); linha_mov.addStretch()
        vl.addLayout(linha_mov)
        legenda = rotulo("O fogo do Curupira segue o perfil e o uso do processador; os vaga-lumes são a bateria. "
                         "Boitatá, Mapinguari, Saci, Iara, Boto e Caipora aparecem quando acordam, e a lua da Cuca marca "
                         "as horas. No Remanso e no Sereno a mata fica sempre parada, para poupar a bateria.", 12, cor=TINTA_SUAVE)
        legenda.setWordWrap(True)
        vl.addWidget(legenda)
        self.vivo.hide()
        pl.addWidget(self.vivo)
        lay.addWidget(papel)

        # doca: volta ao layout da Curupira se os widgets se bagunçarem
        doca = Cartao(areia=True)
        dl = QHBoxLayout(doca); dl.setContentsMargins(16, 12, 14, 12)
        dt = QVBoxLayout(); dt.setSpacing(0)
        dt.addWidget(rotulo("Doca", 15, QFont.Weight.ExtraBold))
        dt.addWidget(rotulo("Bagunçou os painéis ou os widgets? Volta tudo ao layout da Curupira.", 12, cor=TINTA_SUAVE))
        dl.addLayout(dt, 1)
        b_doca = botao("Restaurar a doca")
        b_doca.clicked.connect(lambda: self.executar.emit(["curupira-doca"], "Doca restaurada.", None))
        dl.addWidget(b_doca)
        lay.addWidget(doca)

        lay.addWidget(rotulo("A tela de boot e a de login também usam o tema Curupira.", 12, cor=TINTA_SUAVE))
        lay.addStretch()

    def _tema(self, escuro: bool):
        if self.tem_curupira:
            nome, msg = ("CurupiraNoite", "Tema Curupira Noite aplicado.") if escuro else ("Curupira", "Tema Curupira aplicado.")
        else:   # esquemas ainda não instalados: usa o Breeze
            nome, msg = ("BreezeDark", "Tema escuro aplicado.") if escuro else ("BreezeLight", "Tema claro aplicado.")
        self.executar.emit(["plasma-apply-colorscheme", nome], msg, None)

    def _destaque(self, hexa: str, nome: str):
        self.executar.emit(["plasma-apply-colorscheme", "--accent-color", hexa], f"Cor de destaque: {nome}.", None)

    def _papel(self, caminho: Path, nome: str):
        self.executar.emit(["plasma-apply-wallpaperimage", str(caminho)], f"Papel de parede: {nome}.", None)

    def _papel_vivo(self, movimento: str | None):
        if not sistema.papel_vivo_instalado():
            self.avisar.emit("O Mata Viva ainda não está instalado: rode o instalador da Curupira.", True)
            return
        comando = ["curupira-papel-vivo"] + (["--movimento", movimento] if movimento else [])
        frases = {None: "Papel de parede: Mata Viva.", "tomada": "A mata se mexe só na tomada.",
                  "sempre": "A mata se mexe sempre, também na bateria.", "parado": "A mata fica parada; os seres ainda aparecem."}
        self.executar.emit(comando, frases[movimento], None)

    def coleta(self):
        return sistema.aparencia()

    def mostra(self, d: dict):
        self.tem_curupira = d.get("curupira", False)
        if self.tem_curupira:
            self.seg_tema.botoes["claro"].setText("Curupira"); self.seg_tema.botoes["escuro"].setText("Curupira Noite")
        else:
            self.seg_tema.botoes["claro"].setText("Claro"); self.seg_tema.botoes["escuro"].setText("Escuro")
        e = d.get("esquema", "")
        if self.tem_curupira:   # só marca quando o esquema atual é mesmo um dos da Curupira
            self.seg_tema.seleciona("escuro" if e == "CurupiraNoite" else "claro" if e == "Curupira" else "")
        else:
            self.seg_tema.seleciona("escuro" if d.get("escuro") else "claro")
        atual = (d.get("destaque") or "").upper()
        for hexa, a in self.amostras.items():
            a.setChecked(hexa == atual)
        nomes = {h.upper(): n for h, n in sistema.CORES_DESTAQUE}
        self.nome_destaque.setText(nomes.get(atual, "cor do esquema" if not atual else f"outra cor ({atual})"))
        papel = d.get("papel", "")
        vivo = bool(d.get("papel_vivo"))
        for m in self.miniaturas:
            m.setChecked(not vivo and bool(papel) and (Path(papel).name == m.caminho.name or m.pacote in papel))
        if self.mini_vivo:
            self.mini_vivo.setChecked(vivo)
            self.vivo.setVisible(vivo)
            self.seg_mov.seleciona(d.get("movimento", "tomada"))
