"""Seção Cuca: os snapshots do sistema (snapper)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

import sistema
from visual import (BORDA, DEGRADES, ICONES, TINTA_SUAVE, Cartao, Ladrilho, Secao, botao, cabecalho, rotulo,
                    tempo_relativo)

LIMITE_LISTA = 40


def descreve(item: dict) -> tuple[str, str]:
    """Título e tipo legíveis para um snapshot (ou par antes/depois)."""
    desc = item["descricao"]
    if item.get("pacotes"):
        return f"Pacotes: {item['pacotes']}", "antes e depois do pacman"
    if desc == "timeline":
        return "Automático de hora em hora", "linha do tempo"
    if desc.startswith(("pacman", "/usr/bin/pacman")):
        return desc.replace("/usr/bin/", ""), "antes e depois de pacotes"
    if not desc:
        return "Snapshot sem descrição", item["tipo"]
    return desc, "manual" if item["limpeza"] in ("number", "") else item["limpeza"]


def agrupa(itens: list[dict]) -> list[dict]:
    """Junta os pares pre/post do snap-pac numa linha só, do mais novo para o mais antigo."""
    por_numero = {i["numero"]: i for i in itens}
    usados, linhas = set(), []
    for i in sorted(itens, key=lambda x: x["numero"], reverse=True):
        if i["numero"] in usados:
            continue
        if i["tipo"] == "post" and i.get("pre") in por_numero:
            pre = por_numero[i["pre"]]
            usados.update({i["numero"], pre["numero"]})
            linhas.append({**pre, "post": i["numero"], "idade": i["idade"], "pacotes": i["descricao"]})
        else:
            usados.add(i["numero"])
            linhas.append({**i, "post": None})
    return linhas


class LinhaSnapshot(QFrame):
    def __init__(self, item: dict, ao_ver_mudancas):
        super().__init__()
        self.setObjectName("snap")
        self.setStyleSheet(f"#snap {{ border-bottom: 1px solid {BORDA}; background: transparent; }}")
        lay = QHBoxLayout(self); lay.setContentsMargins(4, 8, 4, 8); lay.setSpacing(12)
        titulo, tipo = descreve(item)
        textos = QVBoxLayout(); textos.setSpacing(0)
        t = rotulo(titulo, 13, QFont.Weight.ExtraBold)
        t.setToolTip(titulo)
        textos.addWidget(t)
        numeros = f"#{item['numero']}" + (f" → #{item['post']}" if item.get("post") else "")
        textos.addWidget(rotulo(f"{tempo_relativo(item['idade'])} · {item['data'][:16]} · {tipo} · {numeros}",
                                12, cor=TINTA_SUAVE))
        lay.addLayout(textos, 1)
        if item.get("post"):
            b = botao("O que mudou")
            b.clicked.connect(lambda: ao_ver_mudancas(item["numero"], item["post"]))
            lay.addWidget(b)


class SecaoCuca(Secao):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(12)
        lay.addWidget(cabecalho("Cuca · snapshots", "Guarda o passado. Quebrou algo? Ela volta no tempo."))

        topo = Cartao(areia=True)
        tl = QHBoxLayout(topo); tl.setContentsMargins(14, 12, 14, 12); tl.setSpacing(14)
        tl.addWidget(Ladrilho(ICONES["cuca"], *DEGRADES["cuca"], 40, 22))
        tt = QVBoxLayout(); tt.setSpacing(0)
        self.resumo = rotulo("…", 15, QFont.Weight.ExtraBold)
        self.detalhe = rotulo("Automáticos a cada hora, e um antes e um depois de cada instalação de pacote.", 12,
                              cor=TINTA_SUAVE)
        self.detalhe.setWordWrap(True)
        tt.addWidget(self.resumo); tt.addWidget(self.detalhe)
        tl.addLayout(tt, 1)
        self.b_criar = botao("Guardar agora", primario=True, icone_svg=ICONES["mais"])
        self.b_criar.clicked.connect(self._cria)
        tl.addWidget(self.b_criar)
        self.b_permissao = botao("Dar permissão", primario=True)
        self.b_permissao.clicked.connect(self._permite)
        self.b_permissao.hide()
        tl.addWidget(self.b_permissao)
        lay.addWidget(topo)

        self.rolagem = QScrollArea()
        self.rolagem.setWidgetResizable(True)
        self.rolagem.setFrameShape(QFrame.Shape.NoFrame)
        self.rolagem.setStyleSheet("QScrollArea { background: transparent; } QScrollArea > QWidget > QWidget { background: transparent; }")
        self.lista = QWidget()
        self.lista_lay = QVBoxLayout(self.lista); self.lista_lay.setContentsMargins(0, 0, 8, 0); self.lista_lay.setSpacing(0)
        self.rolagem.setWidget(self.lista)
        lay.addWidget(self.rolagem, 1)

        dica = rotulo("Para desfazer uma instalação: sudo snapper -c root undochange ANTES..DEPOIS "
                      "(os números aparecem em cada linha).", 12, cor=TINTA_SUAVE)
        dica.setWordWrap(True)
        dica.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(dica)
        self._assinatura = None

    def _cria(self):
        self.executar.emit(["snapper", "-c", "root", "create", "-d", "Ponto manual (Toca do Curupira)",
                            "-c", "number", "--print-number"], "", self._criado)

    @staticmethod
    def _criado(r) -> str:
        if r is None or r.returncode != 0:
            return sistema.ultima_linha(r, "Não consegui criar o snapshot.")
        return f"A Cuca guardou o sistema como está agora (snapshot #{r.stdout.strip()})."

    def _permite(self):
        self.executar.emit(["pkexec", "snapper", "-c", "root", "set-config", "ALLOW_GROUPS=wheel", "SYNC_ACL=yes"],
                           "Pronto: a Toca já pode ver os snapshots.", None)

    def _mudancas(self, antes: int, depois: int):
        def resume(r) -> str:
            if r is None or r.returncode != 0:
                return sistema.ultima_linha(r, "Não consegui comparar os snapshots.")
            c = sistema.conta_mudancas(r.stdout)
            total = sum(c.values())
            return (f"#{antes} → #{depois}: {total} arquivos mudaram ({c['criados']} criados, "
                    f"{c['alterados']} alterados, {c['apagados']} apagados). "
                    f"Desfazer: sudo snapper -c root undochange {antes}..{depois}")
        self.executar.emit(["snapper", "-c", "root", "status", f"{antes}..{depois}"], "", resume)

    def coleta(self):
        return sistema.snapshots()

    def mostra(self, d: dict):
        erro = d.get("_erro")
        sem_permissao = erro == "sem_permissao"
        self.b_permissao.setVisible(sem_permissao)
        self.b_criar.setVisible(not sem_permissao)
        if sem_permissao:
            self.resumo.setText("A Toca ainda não pode ver os snapshots")
            self.detalhe.setText("O snapper só mostra os snapshots para quem tem permissão. "
                                 "\"Dar permissão\" libera o grupo wheel (pede sua senha uma vez).")
            self._preenche([])
            return
        if erro:
            self.resumo.setText("A Cuca não respondeu")
            self.detalhe.setText(erro)
            self._preenche([])
            return
        linhas = agrupa(d.get("itens", []))
        self.resumo.setText(f"{len(d.get('itens', []))} snapshots guardados" if linhas else "Nenhum snapshot ainda")
        self.detalhe.setText("Automáticos a cada hora, e um antes e um depois de cada instalação de pacote.")
        self._preenche(linhas[:LIMITE_LISTA])

    def _preenche(self, linhas: list[dict]):
        assinatura = tuple((l["numero"], l.get("post"), int(l["idade"] // 60)) for l in linhas)
        if assinatura == self._assinatura:
            return
        self._assinatura = assinatura
        while self.lista_lay.count():
            w = self.lista_lay.takeAt(0).widget()
            if w:
                w.deleteLater()
        for l in linhas:
            self.lista_lay.addWidget(LinhaSnapshot(l, self._mudancas))
        self.lista_lay.addStretch()
