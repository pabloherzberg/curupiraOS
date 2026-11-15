"""Seção Privacidade: a Caipora corta câmera e microfone e esconde o MAC."""

from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout

import sistema
from visual import BRASA, TINTA_SUAVE, VERDE_ESCURO, Cartao, LinhaSer, Secao, Faixa, rotulo


class SecaoPrivacidade(Secao):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(12)
        lay.addWidget(Faixa("privacidade", "Privacidade", "A Caipora some sem deixar rastro. Ligue o que você quer esconder."))

        self.camera = LinhaSer("Cortar a câmera", "camera")
        self.microfone = LinhaSer("Silenciar o microfone", "microfone")
        self.mac = LinhaSer("MAC diferente em cada rede", "mascara")
        for linha in (self.camera, self.microfone, self.mac):
            lay.addWidget(linha)
        cur = sistema.comando_curupira()
        self.camera.chave.toggled.connect(lambda v: self.executar.emit(
            [cur, "camera", "cortar" if v else "liberar"],
            "A Caipora cortou a câmera." if v else "Câmera liberada.", None))
        self.microfone.chave.toggled.connect(lambda v: self.executar.emit(
            ["wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "1" if v else "0"],
            "Microfone mudo." if v else "Microfone aberto.", None))
        self.mac.chave.toggled.connect(lambda v: self.executar.emit(
            [cur, "mac", "aleatorio" if v else "fixo"],
            "MAC diferente em cada rede. Vale a partir da próxima conexão." if v
            else "MAC de fábrica de volta. Vale a partir da próxima conexão.", None))

        uso = Cartao(areia=True)
        ul = QVBoxLayout(uso); ul.setContentsMargins(16, 14, 16, 14); ul.setSpacing(4)
        ul.addWidget(rotulo("Usando agora", 15, QFont.Weight.ExtraBold))
        self.uso_mic = rotulo("", 13)
        self.uso_cam = rotulo("", 13)
        self.uso_mic.setWordWrap(True); self.uso_cam.setWordWrap(True)
        ul.addWidget(self.uso_mic); ul.addWidget(self.uso_cam)
        nota = rotulo("A lista da câmera só enxerga programas abertos por você.", 12, cor=TINTA_SUAVE)
        ul.addWidget(nota)
        lay.addWidget(uso)
        lay.addStretch()

    def coleta(self):
        return sistema.privacidade()

    def mostra(self, d: dict):
        if d.get("_erro"):
            self.avisar.emit(d["_erro"], True)
        cam = d.get("camera_cortada")
        if not d.get("camera_presente") and not cam:
            self.camera.define(None, "nenhuma câmera encontrada")
        else:
            self.camera.define(cam, "cortada: nenhum programa consegue usá-la, nem depois de reiniciar" if cam
                               else "liberada: programas podem pedir a câmera")
        mic = d.get("microfone_mudo")
        self.ser_no_canto("caipora" if cam or mic else None)
        self.microfone.define(mic, "sem microfone" if mic is None else
                              "mudo: os programas recebem silêncio" if mic else "aberto")
        mac = d.get("mac_aleatorio")
        self.mac.define(mac, "ligado: cada rede vê um MAC diferente (o mesmo quando você volta a ela)" if mac
                        else "desligado: toda rede vê o MAC de fábrica deste computador")

        apps_mic, apps_cam = d.get("apps_microfone", []), d.get("apps_camera", [])
        self._uso(self.uso_mic, "Microfone", apps_mic)
        self._uso(self.uso_cam, "Câmera", apps_cam)

    @staticmethod
    def _uso(rot, nome: str, apps: list[str]):
        if apps:
            rot.setText(f"{nome}: {', '.join(apps)}")
            rot.setStyleSheet(f"color: {BRASA}; background: transparent; font-weight: 800;")
        else:
            rot.setText(f"{nome}: ninguém")
            rot.setStyleSheet(f"color: {VERDE_ESCURO}; background: transparent;")
