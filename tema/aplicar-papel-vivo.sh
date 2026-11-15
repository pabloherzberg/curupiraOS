#!/usr/bin/env bash
# Põe o papel de parede animado "Mata Viva" em todas as áreas de trabalho da sessão atual.
#
#   curupira-papel-vivo               aplica         (no repositório: bash tema/aplicar-papel-vivo.sh)
#   curupira-papel-vivo --desfazer    volta ao papel de parede Brasa, parado

set -euo pipefail
if [[ "${1:-}" == "--desfazer" ]]; then
  plasma-apply-wallpaperimage /usr/local/share/wallpapers/Curupira-Brasa
  echo "Papel de parede Brasa de volta."
  exit 0
fi
[[ -d /usr/share/plasma/wallpapers/io.github.pabloherzberg.mataviva ]] \
  || { echo "O Mata Viva não está instalado. Rode: sudo bash sistema/instalar.sh" >&2; exit 1; }
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '
  var areas = desktops();
  for (var i = 0; i < areas.length; i++) {
    areas[i].wallpaperPlugin = "io.github.pabloherzberg.mataviva";
  }'
echo "Mata Viva aplicado. Para voltar ao Brasa parado: curupira-papel-vivo --desfazer"
