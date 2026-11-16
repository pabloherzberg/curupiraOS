"""Seção Energia: consumo, perfis, Boitatá e os seres que gastam bateria."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QVBoxLayout

import sistema
from visual import (AREIA, BRASA, NOITE, ORDEM_PERFIS, VERDE_ESCURO, Avatar, CartaoPerfil, LadrilhoSer,
                    Medidor, Secao, Segmentado, linha_ser, rotulo)


def horas_txt(horas: float) -> str:
    h, m = int(horas), round((horas - int(horas)) * 60)
    if m == 60:
        h, m = h + 1, 0
    return f"{h}h{m:02d}"


class SecaoEnergia(Secao):
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
        self.rot_duracao = rotulo("", 13, QFont.Weight.DemiBold, "#E6D9FF")
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
        self.boi_ladrilho = LadrilhoSer("boitata", 44)
        b.addWidget(self.boi_ladrilho)
        bt = QVBoxLayout(); bt.setSpacing(0)
        bt.addWidget(rotulo("Boitatá · placa NVIDIA", 15, QFont.Weight.ExtraBold))
        self.boi_nota = rotulo("", 12, cor=VERDE_ESCURO)
        bt.addWidget(self.boi_nota)
        b.addLayout(bt, 1)
        self.boi_seg = Segmentado([("off", "Dormindo"), ("demanda", "Sob demanda"), ("on", "Acordado")])
        self.boi_seg.botoes["demanda"].setEnabled(False)
        self.boi_seg.botoes["demanda"].setToolTip("Por enquanto: curupira boitata rodar <programa> acorda a placa e abre o programa nela.")
        self.boi_seg.botoes["off"].setToolTip("Depois de acordada, ela só volta a dormir ao reiniciar. Parada, se desliga sozinha.")
        self.boi_seg.botoes["off"].clicked.connect(lambda: self.executar.emit(
            ["curupira", "boitata", "dormir"], "Boitatá dormindo.", None))
        self.boi_seg.botoes["on"].clicked.connect(lambda: self.executar.emit(
            ["curupira", "boitata", "acordar"], "Boitatá acordada.", None))
        b.addWidget(self.boi_seg)
        lay.addWidget(boi)

        # seres
        grade = QGridLayout(); grade.setHorizontalSpacing(10); grade.setVerticalSpacing(10)
        self.saci = linha_ser("saci", "Saci · turbo")
        self.mapinguari = linha_ser("mapinguari", "Mapinguari · HD")
        self.wifi = linha_ser("wifi", "Iara · Wi-Fi")
        self.bluetooth = linha_ser("bluetooth", "Iara · Bluetooth")
        self.caipora = linha_ser("caipora", "Caipora")
        self.boto = linha_ser("boto", "Boto · laboratório")
        for i, linha in enumerate([self.saci, self.mapinguari, self.wifi, self.bluetooth, self.caipora, self.boto]):
            grade.addWidget(linha, i // 2, i % 2)
        grade.setColumnStretch(0, 1); grade.setColumnStretch(1, 1)
        lay.addLayout(grade)
        lay.addStretch()

        self.saci.chave.setToolTip("O turbo segue o perfil: Pororoca e Correnteza ligam, Remanso e Sereno desligam.")
        self.mapinguari.chave.toggled.connect(self._hd)
        self.wifi.chave.toggled.connect(
            lambda v: self.executar.emit(["nmcli", "radio", "wifi", "on" if v else "off"],
                                         "A Iara voltou a ouvir o Wi-Fi." if v else "A Iara silenciou o Wi-Fi.", None))
        self.bluetooth.chave.toggled.connect(self._bluetooth)
        self.caipora.chave.toggled.connect(self._caipora)
        self.boto.chave.toggled.connect(self._boto)
        self.caipora.chave.setToolTip("Liga ou desliga juntos: câmera cortada e microfone mudo. Detalhes na seção Privacidade.")

    # -- ações
    def _hd(self, ligar: bool):
        if ligar:
            self.executar.emit(["curupira", "hd", "acordar"], "O Mapinguari acordou: /data está à mão.", None)
        else:
            self.executar.emit(["curupira", "hd", "dormir"], "Mapinguari hibernando: motor parado.", None)

    def _bluetooth(self, ligar: bool):
        cmd = ["sh", "-c", "rfkill unblock bluetooth && sleep 1 && bluetoothctl power on"] if ligar \
            else ["bluetoothctl", "power", "off"]
        self.executar.emit(cmd, "Bluetooth ligado." if ligar else "Bluetooth desligado.", None)

    def _caipora(self, proteger: bool):
        cur = sistema.comando_curupira()
        cmd = ["sh", "-c", f'wpctl set-mute @DEFAULT_AUDIO_SOURCE@ {1 if proteger else 0} && '
                           f'"{cur}" camera {"cortar" if proteger else "liberar"}']
        self.executar.emit(cmd, "A Caipora cortou a câmera e o microfone." if proteger
                           else "Câmera e microfone liberados.", None)

    def _boto(self, ligar: bool):
        if ligar:
            self.executar.emit(["podman", "network", "create", "--internal", sistema.REDE_LAB],
                               f'O Boto criou a rede isolada "{sistema.REDE_LAB}".', None)
        else:
            self.executar.emit(["podman", "network", "rm", sistema.REDE_LAB], "O Boto desfez a rede isolada.", None)

    # -- dados
    def coleta(self):
        return sistema.resumo_energia()

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
            cartao.clicked.connect(lambda _=False, i=p["id"], n=cartao.nome:
                                   self.executar.emit([sistema.comando_curupira(), i], f"Perfil {n} aplicado.", None))
            self.grade_perfis.addWidget(cartao)
            self.cartoes[p["id"]] = cartao

    def mostra(self, d: dict):
        en = d.get("energia", {})
        if en.get("_erro"):
            self.avisar.emit(en["_erro"], True)
        perfis = sorted(en.get("perfis", []),
                        key=lambda p: (ORDEM_PERFIS.index(p["id"]) if p["id"] in ORDEM_PERFIS else 99, p["id"]))
        self._monta_perfis(perfis)
        for ident, cartao in self.cartoes.items():
            cartao.setChecked(ident == en.get("perfil"))

        watts, wh, pct = en.get("watts"), en.get("capacidade_wh"), en.get("bateria", 0)
        if en.get("fonte") == "bateria" and watts:
            self.rot_consumo.setText("Consumo agora")
            self.val_consumo.setText(f"{watts:.1f} W".replace(".", ","))
            if wh:
                horas = wh / watts
                self.rot_duracao.setText(f"Restam ≈ {horas_txt(horas * pct / 100)} · cheia dura")
                self.val_duracao.setText(f"≈ {horas_txt(horas)}")
                cor = "#7FE3B0" if horas >= 5 else "#FFD08A" if horas >= 3.5 else "#FF8A70"
                self.medidor.define(horas / 9, cor)
        elif en.get("perfis"):
            self.rot_consumo.setText("Na tomada")
            self.val_consumo.setText(f"Bateria {pct}%")
            self.rot_duracao.setText("Capacidade real")
            self.val_duracao.setText(f"{wh:.1f} Wh".replace(".", ",") if wh else "")
            self.medidor.define(pct / 100, "#7FE3B0")
        else:
            self.rot_consumo.setText("Sem dados")
            self.val_consumo.setText("…")
            self.rot_duracao.setText(""); self.val_duracao.setText("")
            self.medidor.define(0, "#7FE3B0")

        dormindo = d.get("boitata_dormindo", True)
        self.boi_seg.seleciona("off" if dormindo else "on")
        self.boi_ladrilho.acorda(not dormindo)
        self.ser_no_canto("saci" if d.get("turbo") else "boitata" if not dormindo else "mapinguari" if d.get("hd") else None)
        self.boi_nota.setText("dormindo, fora do barramento: máxima economia" if dormindo else "acordada: gasta energia; volta a dormir ao reiniciar")
        self.boi_nota.setStyleSheet(f"color: {VERDE_ESCURO if dormindo else BRASA}; background: transparent;")

        t = d.get("turbo")
        self.saci.define(t, "girando até 3,4 GHz" if t else "calmo, processador fresco", habilitado=False)
        hd = d.get("hd")
        self.mapinguari.define(hd, "sem HD em /data" if hd is None else
                               "acordado, arquivos à mão" if hd else "hibernando, motor parado")
        w, rede = d.get("wifi"), d.get("wifi_rede")
        self.wifi.define(w, "sem Wi-Fi" if w is None else
                         (f"conectada em {rede}" if rede else "ligada, sem rede") if w else "em silêncio")
        bt = d.get("bluetooth")
        self.bluetooth.define(bt, "sem Bluetooth" if bt is None else "ligado" if bt else "desligado")

        cam, mic = en.get("camera_cortada"), d.get("microfone_mudo")
        if cam and mic:
            self.caipora.define(True, "câmera e microfone cortados")
        elif cam or mic:
            self.caipora.define(False, "só a câmera cortada" if cam else "só o microfone mudo")
        else:
            self.caipora.define(False, "câmera e microfone liberados", habilitado=cam is not None)
        lab = d.get("lab")
        self.boto.define(lab is not None, f'rede isolada "{sistema.REDE_LAB}" ativa' if lab else "laboratório parado")
