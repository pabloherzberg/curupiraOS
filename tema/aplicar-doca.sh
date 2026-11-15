#!/usr/bin/env bash
# Troca o painel da sessão atual pela doca da Curupira (mockup/Desktop.dc.html).
# Antes, guarda uma cópia da configuração do painel.
#
#   curupira-doca               aplica a doca   (no repositório: bash tema/aplicar-doca.sh)
#   curupira-doca --desfazer    volta ao painel guardado na última vez

set -euo pipefail
LAYOUT=/usr/share/plasma/look-and-feel/io.github.pabloherzberg.curupira/contents/layouts/org.kde.plasma.desktop-layout.js
[[ -f "$LAYOUT" ]] || LAYOUT="$(cd "$(dirname "$0")" && pwd)/plasma/io.github.pabloherzberg.curupira/contents/layouts/org.kde.plasma.desktop-layout.js"
COPIA="$HOME/.config/curupira-painel-anterior"
ARQUIVOS=(plasma-org.kde.plasma.desktop-appletsrc plasmashellrc)

if [[ "${1:-}" == "--desfazer" ]]; then
  [[ -d "$COPIA" ]] || { echo "Não há painel guardado em $COPIA." >&2; exit 1; }
  for a in "${ARQUIVOS[@]}"; do [[ -f "$COPIA/$a" ]] && cp -f "$COPIA/$a" "$HOME/.config/$a"; done
  systemctl --user restart plasma-plasmashell
  echo "Painel anterior de volta."
  exit 0
fi

# guarda só na primeira vez: rodar de novo não pode trocar o painel original pela própria doca
if [[ ! -d "$COPIA" ]]; then
  mkdir -p "$COPIA"
  for a in "${ARQUIVOS[@]}"; do [[ -f "$HOME/.config/$a" ]] && cp -f "$HOME/.config/$a" "$COPIA/$a"; done
fi
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$(cat "$LAYOUT")"
echo "Doca aplicada. Para voltar ao painel anterior: bash $0 --desfazer"
