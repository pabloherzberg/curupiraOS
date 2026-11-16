#!/usr/bin/env bash
# Põe o papel de parede animado "Mata Viva" em todas as áreas de trabalho da sessão atual.
# Na Toca do Curupira isso fica em Aparência → Papel de parede; este comando é o que ela chama.
#
#   curupira-papel-vivo                        aplica         (no repositório: bash tema/aplicar-papel-vivo.sh)
#   curupira-papel-vivo --cena brasa           o Curupira e os seres da mata (padrão)
#   curupira-papel-vivo --cena iara            a Iara na lagoa
#   curupira-papel-vivo --cena encante         a cidade dos botos no fundo do rio
#   curupira-papel-vivo --movimento tomada     a mata só se mexe na tomada (padrão)
#   curupira-papel-vivo --movimento sempre     se mexe também na bateria
#   curupira-papel-vivo --movimento parado     os seres aparecem e somem, mas sem movimento
#   curupira-papel-vivo --desfazer             volta ao papel de parede Brasa, parado

set -euo pipefail
ID=io.github.pabloherzberg.mataviva
movimento="" cena=""
while (( $# )); do
  case "$1" in
    --desfazer)
      plasma-apply-wallpaperimage /usr/local/share/wallpapers/Curupira-Brasa
      echo "Papel de parede Brasa de volta."
      exit 0 ;;
    --movimento)
      case "${2:-}" in
        tomada) movimento=0 ;;
        sempre) movimento=1 ;;
        parado) movimento=2 ;;
        *) echo "Use: curupira-papel-vivo --movimento tomada|sempre|parado" >&2; exit 1 ;;
      esac
      shift 2 ;;
    --cena)
      case "${2:-}" in
        brasa) cena=0 ;;
        iara) cena=1 ;;
        encante) cena=2 ;;
        *) echo "Use: curupira-papel-vivo --cena brasa|iara|encante" >&2; exit 1 ;;
      esac
      shift 2 ;;
    *) echo "Opção desconhecida: $1" >&2; exit 1 ;;
  esac
done
[[ -d "/usr/share/plasma/wallpapers/$ID" ]] \
  || { echo "O Mata Viva não está instalado. Rode: sudo bash sistema/instalar.sh" >&2; exit 1; }
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
  var areas = desktops();
  for (var i = 0; i < areas.length; i++) {
    areas[i].wallpaperPlugin = '$ID';
    areas[i].currentConfigGroup = ['Wallpaper', '$ID', 'General'];
    if ('$movimento' !== '') areas[i].writeConfig('Movimento', '$movimento');
    if ('$cena' !== '') areas[i].writeConfig('Cena', '$cena');
  }"
echo "Mata Viva aplicado. Para voltar ao Brasa parado: curupira-papel-vivo --desfazer"
