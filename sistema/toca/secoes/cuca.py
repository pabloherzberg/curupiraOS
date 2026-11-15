"""Seção Cuca: os snapshots do sistema e a volta no tempo.

Ler e guardar passa pelo "curupira cuca" (sem senha). Voltar no tempo passa pelo
curupira-voltar, que pede a senha de administrador toda vez. Antes de voltar, a seção
conta o que vai mudar, recusa se o kernel estiver no meio e pede confirmação.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QMessageBox, QScrollArea, QVBoxLayout, QWidget

import sistema
from visual import (BORDA, ICONES, TINTA_SUAVE, Cartao, LadrilhoSer, Secao, Tarefa, botao, cabecalho,
                    rotulo, tempo_relativo)

LIMITE_LISTA = 40


def descreve(item: dict) -> tuple[str, str]:
    """Título e tipo legíveis para um snapshot (ou par antes/depois)."""
    desc = item["descricao"]
    if item.get("pacotes"):
        return f"Pacotes: {item['pacotes']}", "antes e depois do pacman"
    if desc == "timeline":
        return "Automático de hora em hora", "linha do tempo"
    if desc.startswith("Antes de voltar no tempo"):
        return desc, "segurança da Cuca"
    if desc.startswith(("pacman", "/usr/bin/pacman")):
        return desc.replace("/usr/bin/", ""), "pacman"
    if not desc:
        return "Snapshot sem descrição", item["tipo"]
    return desc, "manual"


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


def plural(n: int, singular: str, plural_: str) -> str:
    return f"{n} {singular if n == 1 else plural_}"


class LinhaSnapshot(QFrame):
    def __init__(self, item: dict, ao_desfazer, ao_voltar):
        super().__init__()
        self.setObjectName("snap")
        self.setStyleSheet(f"#snap {{ border-bottom: 1px solid {BORDA}; background: transparent; }}")
        lay = QHBoxLayout(self); lay.setContentsMargins(4, 8, 4, 8); lay.setSpacing(8)
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
            b = botao("Desfazer")
            b.setToolTip("Desfaz só o que essa instalação mudou")
            b.clicked.connect(lambda: ao_desfazer(item))
            lay.addWidget(b)
        v = botao("Voltar até aqui")
        v.setToolTip("Volta os arquivos do sistema a como estavam neste ponto")
        v.clicked.connect(lambda: ao_voltar(item))
        lay.addWidget(v)


class SecaoCuca(Secao):
    intervalo = 30000   # lê pelo curupira (polkit): sem pressa

    def __init__(self):
        super().__init__()
        self.ocupado = False
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(12)
        lay.addWidget(cabecalho("Cuca · snapshots", "Guarda o passado. Quebrou algo? Ela volta no tempo."))

        topo = Cartao(areia=True)
        tl = QHBoxLayout(topo); tl.setContentsMargins(14, 12, 14, 12); tl.setSpacing(14)
        tl.addWidget(LadrilhoSer("cuca", 44))
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
        lay.addWidget(topo)

        self.rolagem = QScrollArea()
        self.rolagem.setWidgetResizable(True)
        self.rolagem.setFrameShape(QFrame.Shape.NoFrame)
        self.rolagem.setStyleSheet("QScrollArea { background: transparent; } QScrollArea > QWidget > QWidget { background: transparent; }")
        self.lista = QWidget()
        self.lista_lay = QVBoxLayout(self.lista); self.lista_lay.setContentsMargins(0, 0, 8, 0); self.lista_lay.setSpacing(0)
        self.rolagem.setWidget(self.lista)
        lay.addWidget(self.rolagem, 1)

        dica = rotulo("Voltar no tempo pede sua senha e não toca em /home, /data, /boot nem nos logs. "
                      "Antes, a Cuca guarda o sistema atual, para dar para refazer.", 12, cor=TINTA_SUAVE)
        dica.setWordWrap(True)
        lay.addWidget(dica)
        self._assinatura = None

    # -- guardar
    def _cria(self):
        self.executar.emit([sistema.comando_curupira(), "cuca", "guardar"], "", self._criado)

    @staticmethod
    def _criado(r) -> str:
        if r is None or r.returncode != 0:
            return sistema.ultima_linha(r, "Não consegui criar o snapshot.")
        return f"A Cuca guardou o sistema como está agora (snapshot #{r.stdout.strip()})."

    # -- voltar no tempo
    def _desfazer(self, item: dict):
        antes, depois = item["numero"], item["post"]
        titulo, _ = descreve(item)
        self._prepara(antes, depois, ["desfazer", str(antes), str(depois)],
                      f"Desfazer “{titulo}”?",
                      "Arquivos que essa instalação criou serão apagados, e os que ela mudou ou apagou voltam "
                      "como eram antes.")

    def _voltar(self, item: dict):
        n = item["numero"]
        self._prepara(n, 0, ["sistema", str(n)],
                      f"Voltar o sistema ao snapshot #{n} ({item['data'][:16]})?",
                      "Tudo que foi instalado ou configurado no sistema depois desse ponto some, inclusive "
                      "programas e ajustes em /etc. Seus arquivos em /home não são tocados.")

    def _prepara(self, antes: int, depois: int, args: list[str], pergunta: str, explicacao: str):
        if self.ocupado:
            return
        self.ocupado = True
        self.avisar.emit("A Cuca está contando o que vai mudar…", False)
        Tarefa.inicia(lambda: sistema.previa(antes, depois),
                      lambda p: self._confirma(p, args, pergunta, explicacao))

    def _confirma(self, p, args: list[str], pergunta: str, explicacao: str):
        self.ocupado = False
        if isinstance(p, Exception) or p.get("_erro"):
            self.avisar.emit(str(p) if isinstance(p, Exception) else p["_erro"], True)
            return
        total = p["criados"] + p["alterados"] + p["apagados"]
        if total == 0:
            self.avisar.emit("Nada mudou desde esse ponto: não há o que voltar.", False)
            return
        if p["kernel"]:
            self.avisar.emit("O kernel mudou nesse intervalo. Voltar deixaria o kernel do /boot sem os módulos "
                             "dele e o sistema poderia não iniciar, então a Cuca não faz isso.", True)
            return
        self.avisar.emit("", False)
        caixa = QMessageBox(self)
        caixa.setIcon(QMessageBox.Icon.Warning)
        caixa.setWindowTitle("Voltar no tempo")
        caixa.setText(pergunta)
        caixa.setInformativeText(
            f"{explicacao}\n\n"
            f"• {plural(p['criados'], 'arquivo criado será apagado', 'arquivos criados serão apagados')}\n"
            f"• {plural(p['alterados'], 'arquivo alterado volta', 'arquivos alterados voltam')} à versão antiga\n"
            f"• {plural(p['apagados'], 'arquivo apagado volta', 'arquivos apagados voltam')}\n\n"
            "Antes, a Cuca guarda o sistema atual num snapshot, para dar para refazer. "
            "Depois, reinicie o computador.")
        sim = caixa.addButton("Voltar no tempo", QMessageBox.ButtonRole.DestructiveRole)
        cancelar = caixa.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        caixa.setDefaultButton(cancelar)   # Enter sem querer não volta no tempo
        caixa.exec()
        if caixa.clickedButton() is not sim:
            self.avisar.emit("Nada foi mudado.", False)
            return
        self.executar.emit([sistema.comando_voltar(), *args], "", self._voltou)

    @staticmethod
    def _voltou(r) -> str:
        if r is None:
            return "Não consegui rodar o curupira-voltar."
        if r.returncode in (126, 127):
            return "Cancelado: a senha não foi confirmada. Nada foi mudado."
        if r.returncode != 0:
            return sistema.ultima_linha(r, "A Cuca não conseguiu voltar no tempo.")
        return sistema.ultima_linha(r, "Pronto. Reinicie o computador.")

    # -- dados
    def coleta(self):
        return sistema.snapshots()

    def mostra(self, d: dict):
        erro = d.get("_erro")
        self.b_criar.setEnabled(not erro)
        if erro:
            self.resumo.setText("A Cuca não respondeu")
            self.detalhe.setText(erro)
            self._preenche([])
            return
        linhas = agrupa(d.get("itens", []))
        self.resumo.setText(plural(len(d.get("itens", [])), "snapshot guardado", "snapshots guardados")
                            if linhas else "Nenhum snapshot ainda")
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
            self.lista_lay.addWidget(LinhaSnapshot(l, self._desfazer, self._voltar))
        self.lista_lay.addStretch()
