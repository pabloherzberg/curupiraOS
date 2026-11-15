#!/usr/bin/env bash
# Instala o comando curupira e seus arquivos de sistema.
#
#   sudo bash sistema/instalar.sh          neste computador (já ativa tudo)
#   bash sistema/instalar.sh /mnt          num sistema montado (usado pelo install.sh)

set -euo pipefail

RAIZ="${1:-/}"; RAIZ="${RAIZ%/}"
AQUI="$(cd "$(dirname "$0")" && pwd)"
[[ $EUID -eq 0 ]] || { echo "Rode como root (sudo bash $0 $*)." >&2; exit 1; }
[[ -d "$RAIZ/etc" ]] || { echo "Não parece um sistema instalado: $RAIZ" >&2; exit 1; }

echo "==> Instalando o comando curupira em ${RAIZ:-/}"
install -Dm755 "$AQUI/bin/curupira" "$RAIZ/usr/local/bin/curupira"
install -dm755 "$RAIZ/usr/local/share/curupira/perfis"
install -m644 "$AQUI"/perfis/*.perfil "$RAIZ/usr/local/share/curupira/perfis/"
install -Dm644 "$AQUI/systemd/curupira-evento@.service" "$RAIZ/etc/systemd/system/curupira-evento@.service"
install -Dm644 "$AQUI/systemd/curupira-bateria.timer"   "$RAIZ/etc/systemd/system/curupira-bateria.timer"
install -Dm644 "$AQUI/udev/99-curupira-tomada.rules"    "$RAIZ/etc/udev/rules.d/99-curupira-tomada.rules"
install -Dm644 "$AQUI/polkit/io.github.pabloherzberg.curupira.policy" \
               "$RAIZ/usr/share/polkit-1/actions/io.github.pabloherzberg.curupira.policy"
install -Dm644 "$AQUI/polkit/50-curupira.rules" "$RAIZ/etc/polkit-1/rules.d/50-curupira.rules"
install -dm755 "$RAIZ/var/lib/curupira"

echo "==> Instalando a Toca do Curupira e o widget do painel"
ARTE="$AQUI/../arte"
install -Dm755 "$AQUI/bin/toca-do-curupira" "$RAIZ/usr/local/bin/toca-do-curupira"
install -Dm755 "$AQUI/toca/toca.py" "$RAIZ/usr/local/share/curupira/toca/toca.py"
install -dm755 "$RAIZ/usr/local/share/curupira/toca/fontes" "$RAIZ/usr/local/share/curupira/toca/arte"
install -m644 "$AQUI"/toca/fontes/* "$RAIZ/usr/local/share/curupira/toca/fontes/"
install -m644 "$ARTE/cordel-busto.svg" "$ARTE/cordel-figura.svg" "$RAIZ/usr/local/share/curupira/toca/arte/"
install -Dm644 "$AQUI/toca/io.github.pabloherzberg.Toca.desktop" \
               "$RAIZ/usr/local/share/applications/io.github.pabloherzberg.Toca.desktop"
install -Dm644 "$ARTE/cordel-busto.svg" \
               "$RAIZ/usr/local/share/icons/hicolor/scalable/apps/io.github.pabloherzberg.Toca.svg"
PLASMOIDE="$RAIZ/usr/share/plasma/plasmoids/io.github.pabloherzberg.curupira"
rm -rf "$PLASMOIDE"
install -Dm644 "$AQUI/plasmoide/metadata.json" "$PLASMOIDE/metadata.json"
install -Dm644 "$AQUI/plasmoide/contents/ui/main.qml" "$PLASMOIDE/contents/ui/main.qml"

if [[ ! -e "$RAIZ/etc/curupira.conf" ]]; then
  cat > "$RAIZ/etc/curupira.conf" <<'CONF'
# Curupira: troca automática de perfil (veja "curupira ajuda").
#PERFIL_TOMADA=correnteza
#PERFIL_BATERIA=remanso
#PERFIL_CRITICO=sereno
#LIMITE_CRITICO=15
CONF
fi

# O TLP não troca mais de perfil sozinho: quem decide é o curupira.
# (Substitui o 10-curupira.conf da v0.1, que usava os nomes antigos _ON_AC/_ON_BAT.)
install -dm755 "$RAIZ/etc/tlp.d"
cat > "$RAIZ/etc/tlp.d/10-curupira.conf" <<'TLP'
# Curupira OS: os perfis de energia são do comando "curupira", que grava o
# perfil escolhido em 20-curupira-perfil.conf. O TLP fica sempre no perfil BAL.
TLP_AUTO_SWITCH=0
TLP_PROFILE_DEFAULT=BAL
TLP

if [[ -z "$RAIZ" ]]; then
  systemctl daemon-reload
  udevadm control --reload
  # o evento de boot vem antes do timer, para o primeiro disparo não parecer uma troca de tomada
  /usr/local/bin/curupira evento boot
  systemctl enable curupira-evento@boot.service >/dev/null 2>&1
  systemctl enable --now curupira-bateria.timer >/dev/null 2>&1
  echo "==> Pronto. Perfil atual:"
  /usr/local/bin/curupira estado
else
  systemctl --root="$RAIZ" enable curupira-bateria.timer curupira-evento@boot.service >/dev/null 2>&1
  echo "==> Pronto: o perfil é escolhido no primeiro boot."
fi
