"""Seção Rede e Boto: a conexão da Iara e o laboratório de rede do Boto."""

from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout

import sistema
from visual import (ICONES, TINTA_SUAVE, VERDE_ESCURO, BRASA, Cartao, LinhaInfo, Secao, botao, Faixa, linha_ser,
                    rotulo)


class SecaoRede(Secao):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(14)
        lay.addWidget(Faixa("rede", "Rede e Boto", "A Iara cuida das ondas; o Boto, disfarçado, monta redes de laboratório."))

        # Iara: rádios
        radios = QGridLayout(); radios.setHorizontalSpacing(10)
        self.wifi = linha_ser("wifi", "Iara · Wi-Fi")
        self.bluetooth = linha_ser("bluetooth", "Iara · Bluetooth")
        radios.addWidget(self.wifi, 0, 0); radios.addWidget(self.bluetooth, 0, 1)
        radios.setColumnStretch(0, 1); radios.setColumnStretch(1, 1)
        lay.addLayout(radios)
        self.wifi.chave.toggled.connect(
            lambda v: self.executar.emit(["nmcli", "radio", "wifi", "on" if v else "off"],
                                         "Wi-Fi ligado." if v else "Wi-Fi desligado.", None))
        self.bluetooth.chave.toggled.connect(self._bluetooth)

        # conexão
        con = Cartao(areia=True)
        cl = QVBoxLayout(con); cl.setContentsMargins(16, 14, 16, 14); cl.setSpacing(2)
        self.titulo_con = rotulo("Conexão", 15, QFont.Weight.ExtraBold)
        cl.addWidget(self.titulo_con)
        self.info = {k: LinhaInfo(n) for k, n in [
            ("rede", "Rede"), ("ipv4", "IPv4"), ("ipv6", "IPv6"), ("gateway", "Roteador"),
            ("dns", "DNS"), ("mac", "MAC"),
        ]}
        for w in self.info.values():
            cl.addWidget(w)
        lay.addWidget(con)

        # Boto
        boto = Cartao()
        bl = QVBoxLayout(boto); bl.setContentsMargins(16, 14, 16, 14); bl.setSpacing(10)
        bl.addWidget(rotulo("Boto · laboratório de rede", 15, QFont.Weight.ExtraBold))
        self.lab = linha_ser("boto", "Rede isolada")
        self.lab.setStyleSheet(self.lab.styleSheet().replace("border: 1px", "border: 0px"))
        self.lab.chave.toggled.connect(self._lab)
        bl.addWidget(self.lab)
        self.dica_lab = QLabel()
        self.dica_lab.setWordWrap(True)
        self.dica_lab.setStyleSheet(f"color: {TINTA_SUAVE}; background: transparent;")
        from visual import fonte
        self.dica_lab.setFont(fonte(12))
        bl.addWidget(self.dica_lab)
        botoes = QHBoxLayout(); botoes.setSpacing(8)
        self.b_wireshark = botao("Abrir o Wireshark", icone_svg=ICONES["boto"])
        self.b_mitm = botao("mitmproxy no terminal", icone_svg=ICONES["lab"])
        self.b_terminal = botao("Terminal do Boto")
        self.b_wireshark.clicked.connect(lambda: self._abre(["wireshark"], "Wireshark aberto."))
        self.b_mitm.clicked.connect(lambda: self._abre(["konsole", "-e", "mitmproxy"], "mitmproxy aberto no Konsole."))
        self.b_terminal.clicked.connect(lambda: self._abre(["konsole"], "Terminal aberto."))
        for b in (self.b_wireshark, self.b_mitm, self.b_terminal):
            botoes.addWidget(b)
        botoes.addStretch()
        bl.addLayout(botoes)
        self.nota_grupo = rotulo("", 12, cor=TINTA_SUAVE)
        bl.addWidget(self.nota_grupo)
        lay.addWidget(boto)
        lay.addStretch()

    def _bluetooth(self, ligar: bool):
        cmd = ["sh", "-c", "rfkill unblock bluetooth && sleep 1 && bluetoothctl power on"] if ligar \
            else ["bluetoothctl", "power", "off"]
        self.executar.emit(cmd, "Bluetooth ligado." if ligar else "Bluetooth desligado.", None)

    def _lab(self, ligar: bool):
        if ligar:
            self.executar.emit(["podman", "network", "create", "--internal", sistema.REDE_LAB],
                               f'O Boto criou a rede isolada "{sistema.REDE_LAB}".', None)
        else:
            self.executar.emit(["podman", "network", "rm", sistema.REDE_LAB], "O Boto desfez a rede isolada.", None)

    def _abre(self, cmd: list[str], msg: str):
        if sistema.lanca(*cmd):
            self.avisar.emit(msg, False)
        else:
            self.avisar.emit(f"{cmd[0]} não está instalado.", True)

    def coleta(self):
        return sistema.rede()

    def mostra(self, d: dict):
        w, bt = d.get("wifi"), d.get("bluetooth")
        self.ser_no_canto("boto" if d.get("lab") else "iara" if w or bt else None)
        self.wifi.define(w, "sem Wi-Fi" if w is None else
                         (f"conectada em {d['wifi_rede']}" if d.get("wifi_rede") else "ligada, sem rede") if w else "em silêncio")
        self.bluetooth.define(bt, "sem Bluetooth" if bt is None else "ligado" if bt else "desligado")

        con = d.get("conectado")
        if con:
            tipo = "Wi-Fi" if con["tipo"] == "wifi" else "cabo"
            self.titulo_con.setText(f"Conexão por {tipo} · {con['dispositivo']}")
            rede = con["conexao"]
            if d.get("sinal") is not None:
                rede += f"  ·  sinal {d['sinal']}%"
            if d.get("seguranca"):
                rede += f"  ·  {d['seguranca']}"
            self.info["rede"].define(rede)
            self.info["ipv4"].define(", ".join(d.get("ipv4", [])))
            self.info["ipv6"].define(", ".join(d.get("ipv6", [])) or "sem IPv6 público")
            self.info["gateway"].define(d.get("gateway", ""))
            self.info["dns"].define(", ".join(d.get("dns", [])))
            mac = d.get("mac", "")
            if d.get("mac_aleatorio"):
                mac += "  (diferente em cada rede: Caipora ligada)"
            else:
                mac += "  (o de fábrica; a Caipora pode trocar por rede, em Privacidade)"
            self.info["mac"].define(mac)
        else:
            self.titulo_con.setText("Sem conexão")
            for k, w_ in self.info.items():
                w_.define("—")

        lab = d.get("lab")
        if not d.get("podman"):
            self.lab.define(None, "precisa do Podman instalado")
            self.dica_lab.setText("")
        else:
            interna = " sem saída para a internet" if lab and lab.get("interna") else ""
            self.lab.define(lab is not None, f'"{sistema.REDE_LAB}" ativa · {lab.get("subrede", "")}{interna}' if lab
                            else "parada: ligue para criar uma rede só de contêineres")
            self.dica_lab.setText(
                f"Contêineres nessa rede conversam entre si, mas não saem para a internet. "
                f"Exemplo: podman run --rm -it --network {sistema.REDE_LAB} alpine sh" if lab else
                "Uma rede do Podman marcada como interna: bom para testar serviços e ataques sem tocar na rede de casa.")

        f = d.get("ferramentas", {})
        self.b_wireshark.setEnabled(f.get("wireshark", False))
        self.b_mitm.setEnabled(f.get("mitmproxy", False) and f.get("konsole", False))
        self.b_terminal.setEnabled(f.get("konsole", False))
        if d.get("grupo_wireshark"):
            self.nota_grupo.setText("Você está no grupo wireshark: dá para capturar pacotes sem senha.")
            self.nota_grupo.setStyleSheet(f"color: {VERDE_ESCURO}; background: transparent;")
        else:
            self.nota_grupo.setText("Para capturar pacotes sem senha, entre no grupo wireshark (sudo usermod -aG wireshark $USER).")
            self.nota_grupo.setStyleSheet(f"color: {BRASA}; background: transparent;")
