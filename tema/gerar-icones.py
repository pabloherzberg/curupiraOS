#!/usr/bin/env python3
"""Gera os ícones do sistema.

1. O ícone do botão de menu da doca: o Cordel num quadrado arredondado de brasa
   (mockup/Desktop.dc.html). Sai em PNG porque o QtSvg, que o Plasma usa para ícones, não
   recorta (clip-path), e o desenho do Cordel vazaria pelos cantos.
2. O tema de ícones "Curupira" (tema/icones/Curupira/), a partir de arte/icones/:
   apps/      ladrilho cor da noite com o desenho colorido: os aplicativos do KDE
   simbolos/  traço de uma cor (22 px): bandeja do sistema e ações dos menus
   Cada arte ganha os nomes que o Plasma procura (tabelas APPS, ESTADO e ACOES abaixo).
   O que o tema não tem vem do Breeze (Inherits), então apps de terceiros ficam como são.
3. As artes dos seres (arte/icones/seres/) usadas pelo cartão rápido do widget Curupira.

    python3 tema/gerar-icones.py      reescreve tema/icones/ e sistema/plasmoide/contents/images/ser-*.svg
"""

import os
import shutil
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402

AQUI = Path(__file__).resolve().parent
CORDEL = AQUI.parent / "arte" / "cordel-busto.svg"
TAMANHOS = [32, 48, 64, 128, 256]
ARTE = AQUI.parent / "arte" / "icones"
TEMA = AQUI / "icones" / "Curupira"
SERES_DO_WIDGET = ["iara", "bluetooth", "boitata", "caipora", "saci", "mapinguari"]

# arte -> nomes de ícone que os aplicativos do KDE pedem (Icon= dos .desktop e apelidos do Breeze)
APPS = {
    "arquivos": ["system-file-manager", "org.kde.dolphin"],
    "terminal": ["utilities-terminal", "org.kde.konsole", "konsole"],
    "ajustes": ["systemsettings", "preferences-system", "org.kde.systemsettings"],
    "editor": ["kate", "org.kde.kate", "kwrite", "org.kde.kwrite", "accessories-text-editor"],
    "captura": ["spectacle", "org.kde.spectacle", "ksnapshot"],
    "compactador": ["ark", "org.kde.ark", "utilities-file-archiver"],
    "loja": ["plasmadiscover", "org.kde.discover", "muondiscover", "system-software-install"],
    "imagens": ["gwenview", "org.kde.gwenview"],
    "documentos": ["okular", "org.kde.okular", "graphics-viewer-document"],
    "calculadora": ["kcalc", "org.kde.kcalc", "accessories-calculator"],
    "monitor": ["utilities-system-monitor", "org.kde.plasma-systemmonitor", "ksysguardd"],
    "particoes": ["partitionmanager", "org.kde.partitionmanager"],
    "info": ["hwinfo", "kinfocenter", "org.kde.kinfocenter"],
    "musica": ["elisa", "org.kde.elisa"],
    "disco": ["filelight", "org.kde.filelight"],
    "ajuda": ["system-help", "help-browser", "khelpcenter", "org.kde.khelpcenter"],
    "carteira": ["kwalletmanager", "kwalletmanager2"],
}
# bandeja do sistema (cada nome também sai com o sufixo -symbolic)
ESTADO = {
    "wifi-0": ["network-wireless-signal-none", "network-wireless-connected-00", "network-wireless-0"],
    "wifi-1": ["network-wireless-signal-weak", "network-wireless-connected-25", "network-wireless-20"],
    "wifi-2": ["network-wireless-signal-ok", "network-wireless-connected-50", "network-wireless-40", "network-wireless-60"],
    "wifi-3": ["network-wireless-signal-good", "network-wireless-signal-excellent", "network-wireless-connected-75",
               "network-wireless-connected-100", "network-wireless-80", "network-wireless-100"],
    "wifi-fora": ["network-wireless-disconnected"],
    "rede-cabo": ["network-wired-activated", "network-wired"],
    "rede-cabo-fora": ["network-wired-disconnected", "network-wired-unavailable"],
    "som-alto": ["audio-volume-high"],
    "som-medio": ["audio-volume-medium"],
    "som-baixo": ["audio-volume-low"],
    "som-mudo": ["audio-volume-muted"],
    "microfone": ["microphone-sensitivity-high", "microphone-sensitivity-medium", "microphone-sensitivity-low", "mic-on"],
    "microfone-mudo": ["microphone-sensitivity-muted", "mic-off"],
    "bluetooth": ["network-bluetooth", "network-bluetooth-inactive", "preferences-system-bluetooth-inactive"],
    "bluetooth-ligado": ["network-bluetooth-activated", "preferences-system-bluetooth-activated"],
    "modo-aviao": ["network-flightmode-on"],
    "avisos": ["notifications"],
    "avisos-fora": ["notifications-disabled"],
    **{f"bateria-{p:03d}": [f"battery-{p:03d}"] for p in range(0, 101, 10)},
    **{f"bateria-{p:03d}-carregando": [f"battery-{p:03d}-charging"] for p in range(0, 101, 10)},
}
# ações que aparecem nos menus (doca, área de trabalho, sessão)
ACOES = {
    "janela-nova": ["window-new"], "janela-fechar": ["window-close"],
    "fixar": ["window-pin"], "desafixar": ["window-unpin"],
    "configurar": ["configure", "settings-configure"],
    "adicionar": ["list-add"], "atualizar": ["view-refresh"],
    "colar": ["edit-paste"], "copiar": ["edit-copy"], "lixeira": ["edit-delete", "trash-empty"],
    "renomear": ["edit-rename"], "desfazer": ["edit-undo"],
    "pasta-nova": ["folder-new"], "documento-novo": ["document-new"],
    "bloquear": ["system-lock-screen"], "sair": ["system-log-out"], "desligar": ["system-shutdown"],
    "reiniciar": ["system-reboot"], "suspender": ["system-suspend"],
    "buscar": ["edit-find", "system-search", "search"], "executar": ["system-run"],
    "inicio": ["go-home"], "favorito": ["favorite", "bookmarks"],
    "menu": ["application-menu", "open-menu"], "pessoa": ["user", "system-switch-user"],
}
TINTA_DO_SIMBOLO = "#232629"   # a cor usada nas artes de arte/icones/simbolos; vira a cor do texto do tema
INDICE = """# Gerado por tema/gerar-icones.py a partir de arte/icones/. Não edite à mão.
[Icon Theme]
Name=Curupira
Comment=Ícones da Curupira OS: apps do KDE, bandeja e menus. O resto vem do Breeze.
Inherits=breeze,hicolor
Example=system-file-manager
FollowsColorScheme=true
Directories=apps/scalable,status/scalable,actions/scalable

[apps/scalable]
Size=64
MinSize=16
MaxSize=512
Type=Scalable
Context=Applications

[status/scalable]
Size=22
MinSize=16
MaxSize=64
Type=Scalable
Context=Status

[actions/scalable]
Size=22
MinSize=16
MaxSize=64
Type=Scalable
Context=Actions
"""


def simbolo(texto: str) -> str:
    """Troca a tinta fixa da arte pela cor do texto do tema, do jeito que o Plasma recolore (folha de estilo
    "current-color-scheme" + currentColor). A cor fica num grupo: o QtSvg só resolve currentColor nos filhos."""
    abre, resto = texto.split(">", 1)
    corpo = resto.rsplit("</svg>", 1)[0].replace(TINTA_DO_SIMBOLO, "currentColor")
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 22 22" width="22" height="22">\n'
            '<style id="current-color-scheme" type="text/css">.ColorScheme-Text { color:' + TINTA_DO_SIMBOLO + '; }</style>\n'
            '<g class="ColorScheme-Text" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            'stroke-linejoin="round">' + corpo.strip() + '</g>\n</svg>\n')


def tema_de_icones():
    if TEMA.exists():
        shutil.rmtree(TEMA)
    total = 0
    for nome, apelidos in APPS.items():
        fonte = ARTE / "apps" / f"{nome}.svg"
        for apelido in apelidos:
            destino = TEMA / "apps" / "scalable" / f"{apelido}.svg"
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(fonte, destino)
            total += 1
    for pasta, tabela in (("status", ESTADO), ("actions", ACOES)):
        for nome, apelidos in tabela.items():
            texto = simbolo((ARTE / "simbolos" / f"{nome}.svg").read_text(encoding="utf-8"))
            for apelido in apelidos:
                for sufixo in ("", "-symbolic"):
                    destino = TEMA / pasta / "scalable" / f"{apelido}{sufixo}.svg"
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    destino.write_text(texto, encoding="utf-8")
                    total += 1
    (TEMA / "index.theme").write_text(INDICE, encoding="utf-8")
    sobrando = {a.stem for a in (ARTE / "simbolos").glob("*.svg")} - set(ESTADO) - set(ACOES)
    sobrando |= {a.stem for a in (ARTE / "apps").glob("*.svg")} - set(APPS)
    if sobrando:
        print("aviso: artes sem nome de ícone (acrescente nas tabelas):", ", ".join(sorted(sobrando)))
    print(f"tema/icones/Curupira: {total} ícones")
    imagens = AQUI.parent / "sistema" / "plasmoide" / "contents" / "images"
    for ser in SERES_DO_WIDGET:
        shutil.copyfile(ARTE / "seres" / f"{ser}.svg", imagens / f"ser-{ser}.svg")
    print("sistema/plasmoide/contents/images/ser-*.svg atualizados")


def icone(lado: int) -> QImage:
    img = QImage(lado, lado, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    forma = QPainterPath()
    forma.addRoundedRect(QRectF(0, 0, lado, lado), lado * 0.31, lado * 0.31)
    g = QLinearGradient(0, 0, lado, lado)
    g.setColorAt(0, QColor("#FFD08A"))
    g.setColorAt(1, QColor("#FF7A45"))
    p.fillPath(forma, g)
    p.setClipPath(forma)
    QSvgRenderer(str(CORDEL)).render(p, QRectF(0, 0, lado, lado))
    p.end()
    return img


def main():
    app = QGuiApplication([])  # noqa: F841
    for lado in TAMANHOS:
        pasta = AQUI / "icones" / f"{lado}x{lado}"
        pasta.mkdir(parents=True, exist_ok=True)
        icone(lado).save(str(pasta / "curupira-menu.png"))
    print("curupira-menu.png:", ", ".join(f"{t}x{t}" for t in TAMANHOS))
    tema_de_icones()
    # o avatar da tela de login (SDDM) é o mesmo Cordel
    shutil.copyfile(CORDEL, AQUI / "sddm" / "curupira" / "avatar.svg")
    print("tema/sddm/curupira/avatar.svg atualizado")


if __name__ == "__main__":
    main()
