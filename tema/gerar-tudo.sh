#!/usr/bin/env bash
# Regenera tudo que sai das artes (arte/*.svg) e da paleta. Rode depois de trocar qualquer arte ou cor;
# depois instale com: sudo bash sistema/instalar.sh
#
#   bash tema/gerar-tudo.sh

set -euo pipefail
cd "$(dirname "$0")"
python3 gerar-cores.py      # paleta -> esquemas de cores do Plasma e do Konsole
python3 gerar-papeis.py     # arte/brasa-fundo.svg, arte/propostas/papel-de-parede-entardecer.svg -> papéis de parede + fundo do login
python3 gerar-boot.py       # arte/01-brasa.svg -> tela de boot (Plymouth) e de abertura (KSplash)
python3 gerar-icones.py     # arte/cordel-busto.svg -> ícone do menu + avatar do login; arte/icones/ -> tema de ícones "Curupira"
python3 gerar-papel-vivo.py # arte/brasa-fundo.svg + arte/papel-vivo/ -> camadas do papel de parede animado "Mata Viva"
python3 gerar-painel.py     # raio e sombra da doca -> estilo do Plasma "Curupira"
echo "Pronto. Instale com: sudo bash sistema/instalar.sh"
