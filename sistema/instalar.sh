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
install -Dm755 "$AQUI/bin/curupira-voltar" "$RAIZ/usr/local/bin/curupira-voltar"
install -dm755 "$RAIZ/usr/local/share/curupira/perfis"
install -m644 "$AQUI"/perfis/*.perfil "$RAIZ/usr/local/share/curupira/perfis/"
install -Dm644 "$AQUI/systemd/curupira-evento@.service" "$RAIZ/etc/systemd/system/curupira-evento@.service"
install -Dm644 "$AQUI/systemd/curupira-bateria.timer"   "$RAIZ/etc/systemd/system/curupira-bateria.timer"
install -Dm644 "$AQUI/udev/99-curupira-tomada.rules"    "$RAIZ/etc/udev/rules.d/99-curupira-tomada.rules"
install -Dm644 "$AQUI/polkit/io.github.pabloherzberg.curupira.policy" \
               "$RAIZ/usr/share/polkit-1/actions/io.github.pabloherzberg.curupira.policy"
install -Dm644 "$AQUI/polkit/io.github.pabloherzberg.curupira.voltar.policy" \
               "$RAIZ/usr/share/polkit-1/actions/io.github.pabloherzberg.curupira.voltar.policy"
install -Dm644 "$AQUI/polkit/50-curupira.rules" "$RAIZ/etc/polkit-1/rules.d/50-curupira.rules"
install -dm755 "$RAIZ/var/lib/curupira"

echo "==> Instalando a Toca do Curupira e o widget do painel"
ARTE="$AQUI/../arte"
install -Dm755 "$AQUI/bin/toca-do-curupira" "$RAIZ/usr/local/bin/toca-do-curupira"
TOCA="$RAIZ/usr/local/share/curupira/toca"
rm -rf "$TOCA"
install -dm755 "$TOCA/secoes" "$TOCA/fontes" "$TOCA/arte"
install -m755 "$AQUI/toca/toca.py" "$TOCA/"
install -m644 "$AQUI/toca/visual.py" "$AQUI/toca/sistema.py" "$TOCA/"
install -m644 "$AQUI"/toca/secoes/*.py "$TOCA/secoes/"
install -m644 "$AQUI"/toca/fontes/* "$TOCA/fontes/"
install -m644 "$ARTE/cordel-busto.svg" "$ARTE/cordel-figura.svg" "$ARTE/brasa-fundo.svg" \
              "$ARTE/propostas/papel-de-parede-entardecer.svg" "$TOCA/arte/"
# as artes dos seres, que a Toca anima (grupos base/vivo/frente)
rm -rf "$TOCA/arte/icones"
install -dm755 "$TOCA/arte/icones/seres"
install -m644 "$ARTE"/icones/seres/*.svg "$TOCA/arte/icones/seres/"
# as cenas das faixas que abrem cada seção
rm -rf "$TOCA/arte/cenas"
install -dm755 "$TOCA/arte/cenas"
install -m644 "$ARTE"/cenas/*.svg "$TOCA/arte/cenas/"

# Cuca: o snapper fica só para o root. A Toca lê pelo "curupira cuca" (só leitura e guardar)
# e volta no tempo pelo curupira-voltar, que pede senha. (A v0.2 liberava o grupo wheel no
# snapper, o que deixava qualquer programa do usuário reescrever o sistema sem senha.)
if [[ -f "$RAIZ/etc/snapper/configs/root" ]] && grep -q '^ALLOW_GROUPS="wheel"' "$RAIZ/etc/snapper/configs/root"; then
  if [[ -z "$RAIZ" ]]; then
    snapper -c root set-config "ALLOW_GROUPS=" "SYNC_ACL=no" || echo "aviso: não consegui fechar o snapper para o grupo wheel"
    setfacl -b /.snapshots 2>/dev/null || true
  else
    sed -i 's/^ALLOW_GROUPS=.*/ALLOW_GROUPS=""/; s/^SYNC_ACL=.*/SYNC_ACL="no"/' "$RAIZ/etc/snapper/configs/root"
  fi
fi
install -Dm644 "$AQUI/toca/io.github.pabloherzberg.Toca.desktop" \
               "$RAIZ/usr/local/share/applications/io.github.pabloherzberg.Toca.desktop"
install -Dm644 "$ARTE/cordel-busto.svg" \
               "$RAIZ/usr/local/share/icons/hicolor/scalable/apps/io.github.pabloherzberg.Toca.svg"
ESTILO="$RAIZ/usr/share/plasma/desktoptheme/curupira"
rm -rf "$ESTILO"
cp -r "$AQUI/../tema/plasma-estilo/curupira" "$ESTILO"
chmod -R u=rwX,go=rX "$ESTILO"
DOCA="$RAIZ/usr/share/plasma/plasmoids/io.github.pabloherzberg.doca"
rm -rf "$DOCA"
cp -r "$AQUI/doca" "$DOCA"
chmod -R u=rwX,go=rX "$DOCA"
PLASMOIDE="$RAIZ/usr/share/plasma/plasmoids/io.github.pabloherzberg.curupira"
rm -rf "$PLASMOIDE"
cp -r "$AQUI/plasmoide" "$PLASMOIDE"
chmod -R u=rwX,go=rX "$PLASMOIDE"

echo "==> Instalando o tema (cores, Konsole, papéis de parede e tela de login)"
TEMA="$AQUI/../tema"
install -dm755 "$RAIZ/usr/local/share/color-schemes" "$RAIZ/usr/local/share/konsole" "$RAIZ/usr/local/share/wallpapers"
install -m644 "$TEMA"/cores/*.colors "$RAIZ/usr/local/share/color-schemes/"
install -m644 "$TEMA"/konsole/Curupira.colorscheme "$TEMA"/konsole/Curupira.profile "$RAIZ/usr/local/share/konsole/"
for papel in "$TEMA"/papeis/*/; do
  nome="$(basename "$papel")"
  rm -rf "$RAIZ/usr/local/share/wallpapers/$nome"
  cp -r "$papel" "$RAIZ/usr/local/share/wallpapers/$nome"
  chmod -R u=rwX,go=rX "$RAIZ/usr/local/share/wallpapers/$nome"
done
SDDM_TEMA="$RAIZ/usr/share/sddm/themes/curupira"
rm -rf "$SDDM_TEMA"
cp -r "$TEMA/sddm/curupira" "$SDDM_TEMA"
chmod -R u=rwX,go=rX "$SDDM_TEMA"
# Se a tela de login não abrir: Ctrl+Alt+F2, entre no terminal e apague este arquivo.
install -dm755 "$RAIZ/etc/sddm.conf.d"
printf '%s\n' "# Curupira OS: tela de login. Para voltar ao padrão, apague este arquivo." \
  "[Theme]" "Current=curupira" > "$RAIZ/etc/sddm.conf.d/10-curupira.conf"

# Tema global do Plasma (aparece em Configurações → Tema global) com a tela de abertura.
# A tela de abertura usa as mesmas imagens da tela de boot e vira o padrão do sistema; quem
# escolher outra nas Configurações grava a sua em ~/.config/ksplashrc e ela prevalece.
LNF_ID="io.github.pabloherzberg.curupira"
LNF="$RAIZ/usr/share/plasma/look-and-feel/$LNF_ID"
rm -rf "$LNF"
cp -r "$TEMA/plasma/$LNF_ID" "$LNF"
install -dm755 "$LNF/contents/splash/images"
install -m644 "$TEMA"/plymouth/curupira/retrato.png "$TEMA"/plymouth/curupira/pegada?.png "$LNF/contents/splash/images/"
install -m644 "$AQUI/toca/fontes/Nunito[wght].ttf" "$LNF/contents/splash/images/Nunito.ttf"
chmod -R u=rwX,go=rX "$LNF"
for tam in 32 48 64 128 256; do
  install -Dm644 "$TEMA/icones/${tam}x${tam}/curupira-menu.png" \
                 "$RAIZ/usr/local/share/icons/hicolor/${tam}x${tam}/apps/curupira-menu.png"
done
# Papel de parede animado "Mata Viva" (aparece em Configurar área de trabalho → Tipo de papel de parede).
PAPEL_VIVO="$RAIZ/usr/share/plasma/wallpapers/io.github.pabloherzberg.mataviva"
rm -rf "$PAPEL_VIVO"
install -dm755 "$RAIZ/usr/share/plasma/wallpapers"
cp -r "$TEMA/papel-vivo/io.github.pabloherzberg.mataviva" "$PAPEL_VIVO"
chmod -R u=rwX,go=rX "$PAPEL_VIVO"
install -Dm755 "$TEMA/aplicar-papel-vivo.sh" "$RAIZ/usr/local/bin/curupira-papel-vivo"
# Tema de ícones "Curupira": apps do KDE, bandeja e menus; o resto vem do Breeze.
# Para voltar: Configurações → Cores e temas → Ícones → Breeze.
ICONES_TEMA="$RAIZ/usr/local/share/icons/Curupira"
rm -rf "$ICONES_TEMA"
cp -r "$TEMA/icones/Curupira" "$ICONES_TEMA"
chmod -R u=rwX,go=rX "$ICONES_TEMA"
install -Dm755 "$TEMA/aplicar-doca.sh" "$RAIZ/usr/local/bin/curupira-doca"
install -Dm644 "$TEMA/restaurar-doca.desktop" "$RAIZ/usr/local/share/applications/io.github.pabloherzberg.RestaurarDoca.desktop"
install -dm755 "$RAIZ/etc/xdg"
# Numa instalação nova, o tema Curupira (com a doca) é o padrão de quem ainda não tem configuração.
if [[ -n "$RAIZ" ]]; then
  printf '%s\n' "[KDE]" "LookAndFeelPackage=$LNF_ID" >> "$RAIZ/etc/xdg/kdeglobals"
fi
printf '%s\n' "# Curupira OS: tela de abertura do Plasma" "[KSplash]" "Engine=KSplashQML" "Theme=$LNF_ID" \
  > "$RAIZ/etc/xdg/ksplashrc"

# Modo de recuperação: o mkinitcpio do Arch deixou de gerar a imagem "fallback" por padrão,
# e a entrada da v0.1 apontava para ela. Sem a imagem, a recuperação usa a padrão.
for entrada in "$RAIZ"/boot/loader/entries/*.conf; do
  [[ -f "$entrada" ]] && grep -q 'initramfs-linux-fallback.img' "$entrada" || continue
  [[ -f "$RAIZ/boot/initramfs-linux-fallback.img" ]] || sed -i 's|/initramfs-linux-fallback.img|/initramfs-linux.img|' "$entrada"
done

# Tela de boot (Plymouth). Só se o pacote estiver instalado. A entrada "modo de recuperação"
# do boot ganha plymouth.enable=0: é sempre o caminho para iniciar sem a tela de boot.
if [[ -d "$RAIZ/usr/share/plymouth/themes" ]]; then
  echo "==> Instalando a tela de boot"
  rm -rf "$RAIZ/usr/share/plymouth/themes/curupira"
  cp -r "$TEMA/plymouth/curupira" "$RAIZ/usr/share/plymouth/themes/curupira"
  chmod -R u=rwX,go=rX "$RAIZ/usr/share/plymouth/themes/curupira"
  install -dm755 "$RAIZ/etc/plymouth"
  printf '%s\n' "# Curupira OS: tema da tela de boot" "[Daemon]" "Theme=curupira" "ShowDelay=0" \
    > "$RAIZ/etc/plymouth/plymouthd.conf"

  RECOMPILAR=0
  MKINIT="$RAIZ/etc/mkinitcpio.conf"
  if [[ -f "$MKINIT" ]] && ! grep -qE '^HOOKS=\(.*\bplymouth\b' "$MKINIT"; then
    sed -i -E '/^HOOKS=\(/ s/\b(systemd|udev)\b/\1 plymouth/' "$MKINIT"
    grep -qE '^HOOKS=\(.*\bplymouth\b' "$MKINIT" && RECOMPILAR=1 || echo "aviso: não achei onde pôr o hook plymouth em $MKINIT"
  fi
  for entrada in "$RAIZ"/boot/loader/entries/*.conf; do
    [[ -f "$entrada" ]] || continue
    if grep -q 'recupera' "$entrada"; then
      grep -q 'plymouth.enable=0' "$entrada" || sed -i -E '/^options / s/$/ plymouth.enable=0/' "$entrada"
    else
      grep -qE '^options .*\bsplash\b' "$entrada" || sed -i -E '/^options / s/$/ splash/' "$entrada"
    fi
  done
  if (( RECOMPILAR )); then
    echo "==> Recompilando o initramfs com a tela de boot (leva um minuto)"
    if [[ -z "$RAIZ" ]]; then mkinitcpio -P >/dev/null; else arch-chroot "$RAIZ" mkinitcpio -P >/dev/null; fi
  fi
fi

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
