#!/usr/bin/env bash
# Curupira OS - instalador (v0.1 "Pororoca")
# Roda dentro do ambiente live do Arch Linux (ISO oficial), em modo UEFI.
#
#   bash install.sh             instala de verdade (pede confirmação antes de apagar)
#   bash install.sh --simular   só mostra o plano, não toca em nenhum disco
#
# Variáveis opcionais (úteis para testar em máquina virtual):
#   DISCO_SISTEMA=/dev/vda   disco que recebe o sistema (padrão: o NVMe)
#   DISCO_DADOS=/dev/vdb     disco de dados montado em /data (padrão: o HD; "nenhum" para pular)
#   NOME_MAQUINA=curupira    TECLADO=br-abnt2    FUSO=America/Sao_Paulo

set -euo pipefail

SIMULAR=0
[[ "${1:-}" == "--simular" ]] && SIMULAR=1

NOME_MAQUINA="${NOME_MAQUINA:-curupira}"
TECLADO="${TECLADO:-br-abnt2}"
FUSO="${FUSO:-America/Sao_Paulo}"

setfont ter-v16n 2>/dev/null || true   # fonte do terminal com acentos
verde=$'\e[32m'; laranja=$'\e[33m'; vermelho=$'\e[31m'; neutro=$'\e[0m'
diz()   { printf '%s==>%s %s\n' "$verde" "$neutro" "$*"; }
avisa() { printf '%s[!]%s %s\n' "$laranja" "$neutro" "$*"; }
morre() { printf '%s[x]%s %s\n' "$vermelho" "$neutro" "$*" >&2; exit 1; }

trap 'printf "%s[x]%s Falhou na linha %s. NÃO desligue: o instalador continua na memória. Fotografe a tela; depois de corrigido, é só baixar e rodar de novo.\n" "$vermelho" "$neutro" "$LINENO" >&2' ERR

# /dev/nvme0n1 + 2 -> /dev/nvme0n1p2 ; /dev/sda + 2 -> /dev/sda2
particao() { if [[ "$1" =~ [0-9]$ ]]; then echo "${1}p$2"; else echo "${1}$2"; fi; }

# ---------------------------------------------------------------- verificações
[[ $EUID -eq 0 ]] || morre "Rode como root (no live do Arch você já é root)."
[[ -d /sys/firmware/efi ]] || morre "O computador não iniciou em modo UEFI. Confira o BIOS."
command -v pacstrap >/dev/null || morre "Este script precisa do ambiente live do Arch Linux."
ping -c1 -W3 archlinux.org >/dev/null 2>&1 || morre "Sem internet. Use cabo ou: iwctl station wlan0 connect \"NomeDaRede\""

# ---------------------------------------------------------------- discos
# Disco de onde o live iniciou (pendrive, ou a partição de instalação no HD).
MIDIA_PART="$(findmnt -no SOURCE /run/archiso/bootmnt 2>/dev/null || true)"
MIDIA_DISCO=""
[[ -n "$MIDIA_PART" && -b "$MIDIA_PART" ]] && MIDIA_DISCO="/dev/$(lsblk -no PKNAME "$MIDIA_PART" | head -n1)"

if [[ -z "${DISCO_SISTEMA:-}" ]]; then
  DISCO_SISTEMA="$(lsblk -dnpo NAME,TRAN,TYPE | awk '$2=="nvme" && $3=="disk"{print $1; exit}')"
fi
[[ -b "${DISCO_SISTEMA:-}" ]] || morre "Não achei o disco do sistema (NVMe). Informe com DISCO_SISTEMA=/dev/..."
[[ "$DISCO_SISTEMA" != "$MIDIA_DISCO" ]] || morre "O disco do sistema é o mesmo de onde o instalador iniciou."

if [[ -z "${DISCO_DADOS:-}" ]]; then
  DISCO_DADOS="$(lsblk -dnpo NAME,ROTA,TYPE | awk -v s="$DISCO_SISTEMA" '$2=="1" && $3=="disk" && $1!=s{print $1; exit}')"
  [[ -n "$DISCO_DADOS" ]] || DISCO_DADOS="nenhum"
fi
[[ "$DISCO_DADOS" == "nenhum" || -b "$DISCO_DADOS" ]] || morre "Disco de dados inválido: $DISCO_DADOS"

# Se o live está rodando a partir do HD, o HD não pode ser reparticionado agora:
# a partição do instalador fica como "resgate" e só a maior partição restante vira /data.
MODO_DADOS="nenhum"; PART_DADOS=""
if [[ "$DISCO_DADOS" != "nenhum" ]]; then
  if [[ "$DISCO_DADOS" == "$MIDIA_DISCO" ]]; then
    MODO_DADOS="preservar-resgate"
    PART_DADOS="$(lsblk -lnpbo NAME,SIZE,TYPE "$DISCO_DADOS" | awk -v m="$MIDIA_PART" '$3=="part" && $1!=m{print $2, $1}' | sort -rn | awk 'NR==1{print $2}')"
    [[ -b "$PART_DADOS" ]] || morre "Não achei a partição de dados em $DISCO_DADOS."
  else
    MODO_DADOS="disco-inteiro"
    PART_DADOS="$(particao "$DISCO_DADOS" 1)"
  fi
fi

ESP="$(particao "$DISCO_SISTEMA" 1)"
RAIZ="$(particao "$DISCO_SISTEMA" 2)"

echo
diz "Plano da instalação"
lsblk -o NAME,SIZE,MODEL,TRAN,FSTYPE,LABEL "$DISCO_SISTEMA" $([[ "$DISCO_DADOS" != "nenhum" ]] && echo "$DISCO_DADOS")
echo
echo "  Sistema : $DISCO_SISTEMA  -> APAGADO POR INTEIRO (1 GB de boot + Btrfs)"
case "$MODO_DADOS" in
  disco-inteiro)     echo "  Dados   : $DISCO_DADOS  -> APAGADO POR INTEIRO, vira /data (ext4)";;
  preservar-resgate) echo "  Dados   : $PART_DADOS  -> APAGADA, vira /data (ext4)"
                     echo "  Resgate : $MIDIA_PART  -> mantida (instalador / resgate)";;
  nenhum)            echo "  Dados   : nenhum disco de dados";;
esac
echo "  Máquina : $NOME_MAQUINA   teclado: $TECLADO   fuso: $FUSO"
echo

if (( SIMULAR )); then diz "Modo --simular: nada foi alterado."; exit 0; fi

# ---------------------------------------------------------------- perguntas
read -rp "Nome de usuário (minúsculas, sem espaço): " USUARIO
[[ "$USUARIO" =~ ^[a-z_][a-z0-9_-]{0,30}$ ]] || morre "Nome de usuário inválido."
while true; do
  read -rsp "Senha de $USUARIO: " SENHA; echo
  read -rsp "Repita a senha: " SENHA2; echo
  [[ -n "$SENHA" && "$SENHA" == "$SENHA2" ]] && break
  avisa "As senhas não conferem (ou estão vazias). Tente de novo."
done
unset SENHA2

avisa "ÚLTIMO AVISO: os discos listados acima serão apagados. Não há como desfazer."
read -rp "Digite APAGAR para continuar: " CONFIRMA
[[ "$CONFIRMA" == "APAGAR" ]] || morre "Cancelado. Nada foi alterado."

# ---------------------------------------------------------------- particionar
diz "Particionando $DISCO_SISTEMA"
timedatectl set-ntp true || true
umount -R /mnt 2>/dev/null || true
swapoff -a 2>/dev/null || true
wipefs -af "$DISCO_SISTEMA" >/dev/null || true
sgdisk --zap-all "$DISCO_SISTEMA" >/dev/null 2>&1 || true
sgdisk -n1:0:+1G -t1:ef00 -c1:CURUPIRA-BOOT -n2:0:0 -t2:8300 -c2:CURUPIRA "$DISCO_SISTEMA" >/dev/null
partprobe "$DISCO_SISTEMA"; udevadm settle
mkfs.fat -F32 -n CURUPBOOT "$ESP" >/dev/null
mkfs.btrfs -f -L curupira "$RAIZ" >/dev/null

diz "Criando subvolumes Btrfs"
mount "$RAIZ" /mnt
for sv in @ @home @log @pkg; do btrfs subvolume create "/mnt/$sv" >/dev/null; done
umount /mnt
OPC="noatime,compress=zstd:3,ssd,discard=async"
mount -o "$OPC,subvol=@" "$RAIZ" /mnt
mount --mkdir -o "$OPC,subvol=@home" "$RAIZ" /mnt/home
mount --mkdir -o "$OPC,subvol=@log"  "$RAIZ" /mnt/var/log
mount --mkdir -o "$OPC,subvol=@pkg"  "$RAIZ" /mnt/var/cache/pacman/pkg
mount --mkdir -o umask=0077 "$ESP" /mnt/boot

if [[ "$MODO_DADOS" == "disco-inteiro" ]]; then
  diz "Preparando $DISCO_DADOS como /data"
  wipefs -af "$DISCO_DADOS" >/dev/null || true
  sgdisk --zap-all "$DISCO_DADOS" >/dev/null 2>&1 || true
  sgdisk -n1:0:0 -t1:8300 -c1:CURUPIRA-DADOS "$DISCO_DADOS" >/dev/null
  partprobe "$DISCO_DADOS"; udevadm settle
fi
if [[ "$MODO_DADOS" != "nenhum" ]]; then
  diz "Formatando $PART_DADOS (ext4)"
  wipefs -af "$PART_DADOS" >/dev/null || true
  mkfs.ext4 -F -q -L dados -m 0 "$PART_DADOS"
fi

# ---------------------------------------------------------------- pacotes
BASE=(base base-devel linux linux-firmware intel-ucode btrfs-progs e2fsprogs dosfstools
      networkmanager sudo nano vim git man-db openssh reflector efibootmgr)
DESKTOP=(plasma-desktop plasma-workspace kwin xorg-server sof-firmware terminus-font sddm sddm-kcm konsole dolphin kate ark spectacle gwenview okular
         plasma-nm plasma-pa powerdevil bluedevil kscreen kde-gtk-config breeze-gtk
         xdg-desktop-portal-kde pipewire pipewire-pulse wireplumber firefox
         noto-fonts noto-fonts-emoji ttf-jetbrains-mono pyside6)
VIDEO=(mesa vulkan-intel intel-media-driver)
ENERGIA=(tlp tlp-rdw thermald zram-generator hdparm smartmontools powertop plymouth)
SISTEMA=(snapper snap-pac bluez bluez-utils)
DEV=(python nodejs npm podman)
REDE=(wireshark-qt nmap tcpdump mitmproxy iw bind traceroute)

diz "Escolhendo espelhos rápidos do Brasil"
reflector --country Brazil --latest 10 --protocol https --sort rate --save /etc/pacman.d/mirrorlist 2>/dev/null \
  || avisa "Não consegui ordenar os espelhos; sigo com os padrões."

diz "Instalando o sistema (a parte mais demorada)"
# o initramfs é gerado durante o pacstrap e já procura este arquivo
mkdir -p /mnt/etc
echo "KEYMAP=$TECLADO" > /mnt/etc/vconsole.conf
pacstrap -K /mnt "${BASE[@]}" "${DESKTOP[@]}" "${VIDEO[@]}" "${ENERGIA[@]}" "${SISTEMA[@]}" "${DEV[@]}" "${REDE[@]}"

genfstab -U /mnt >> /mnt/etc/fstab
if [[ "$MODO_DADOS" != "nenhum" ]]; then
  UUID_DADOS="$(blkid -s UUID -o value "$PART_DADOS")"
  # automount + idle-timeout: o HD só gira quando /data é usado (o "Mapinguari" hiberna).
  echo "UUID=$UUID_DADOS /data ext4 noatime,nofail,x-systemd.automount,x-systemd.idle-timeout=10min 0 2" >> /mnt/etc/fstab
  mkdir -p /mnt/data
fi

# ---------------------------------------------------------------- configuração
diz "Configurando o sistema"
UUID_RAIZ="$(blkid -s UUID -o value "$RAIZ")"

cat > /mnt/root/configura.sh <<CHROOT
#!/usr/bin/env bash
set -euo pipefail

ln -sf /usr/share/zoneinfo/$FUSO /etc/localtime
hwclock --systohc
sed -i 's/^#\(pt_BR.UTF-8\)/\1/; s/^#\(en_US.UTF-8\)/\1/' /etc/locale.gen
locale-gen >/dev/null
echo 'LANG=pt_BR.UTF-8' > /etc/locale.conf
echo 'KEYMAP=$TECLADO' > /etc/vconsole.conf
echo '$NOME_MAQUINA' > /etc/hostname
printf '127.0.0.1 localhost\n::1 localhost\n127.0.1.1 $NOME_MAQUINA\n' > /etc/hosts
mkdir -p /etc/X11/xorg.conf.d
printf 'Section "InputClass"\n  Identifier "teclado"\n  MatchIsKeyboard "on"\n  Option "XkbLayout" "br"\nEndSection\n' > /etc/X11/xorg.conf.d/00-keyboard.conf

# usuário: root fica bloqueado, o usuário usa sudo
groupadd -f wireshark
useradd -m -G wheel,wireshark -s /bin/bash '$USUARIO'
passwd -l root >/dev/null
echo '%wheel ALL=(ALL:ALL) ALL' > /etc/sudoers.d/10-wheel
chmod 440 /etc/sudoers.d/10-wheel

# zram: troca comprimida na memória (8 GB de RAM agradecem)
printf '[zram0]\nzram-size = ram / 2\ncompression-algorithm = zstd\n' > /etc/systemd/zram-generator.conf

# Boitatá (NVIDIA MX110) dormindo por padrão: sem driver e removida do barramento
printf 'blacklist nouveau\noptions nouveau modeset=0\n' > /etc/modprobe.d/curupira-boitata.conf
cat > /etc/udev/rules.d/00-curupira-boitata.rules <<'UDEV'
# Remove a placa NVIDIA e seus dispositivos auxiliares; apague este arquivo para acordá-la.
ACTION=="add", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x03[0-9]*", ATTR{power/control}="auto", ATTR{remove}="1"
ACTION=="add", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x040300", ATTR{power/control}="auto", ATTR{remove}="1"
ACTION=="add", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", ATTR{class}=="0x0c0330", ATTR{power/control}="auto", ATTR{remove}="1"
UDEV

# Mapinguari (HD de 5400 rpm): desacelera depois de 5 minutos parado
cat > /etc/udev/rules.d/69-curupira-mapinguari.rules <<'UDEV'
ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}=="1", RUN+="/usr/bin/hdparm -B 127 -S 60 /dev/%k"
UDEV

# TLP: os perfis de energia ficam com o comando "curupira" (instalado mais abaixo)

# Cuca (snapshots): um antes e um depois de cada instalação de pacote (snap-pac)
snapper --no-dbus -c root create-config / || echo 'aviso: snapper será configurado no primeiro uso'

# boot
bootctl install >/dev/null
printf 'default curupira.conf\ntimeout 2\nconsole-mode max\neditor no\n' > /boot/loader/loader.conf
printf 'title   Curupira OS\nlinux   /vmlinuz-linux\ninitrd  /intel-ucode.img\ninitrd  /initramfs-linux.img\noptions root=UUID=$UUID_RAIZ rootflags=subvol=@ rw quiet loglevel=3 nowatchdog\n' > /boot/loader/entries/curupira.conf
printf 'title   Curupira OS (modo de recuperação)\nlinux   /vmlinuz-linux\ninitrd  /intel-ucode.img\ninitrd  /initramfs-linux.img\noptions root=UUID=$UUID_RAIZ rootflags=subvol=@ rw plymouth.enable=0\n' > /boot/loader/entries/curupira-recuperacao.conf

for u in NetworkManager sddm tlp thermald bluetooth fstrim.timer systemd-timesyncd snapper-timeline.timer snapper-cleanup.timer; do
  systemctl enable "\$u" >/dev/null 2>&1 || echo "aviso: não consegui ativar \$u"
done
systemctl mask systemd-rfkill.service systemd-rfkill.socket >/dev/null 2>&1 || true
CHROOT

arch-chroot /mnt bash /root/configura.sh
printf '%s:%s\n' "$USUARIO" "$SENHA" | arch-chroot /mnt chpasswd
unset SENHA
rm -f /mnt/root/configura.sh

# Comando "curupira" (perfis de energia). Usa a pasta sistema/ ao lado deste script;
# se o script foi baixado sozinho, baixa o repositório do GitHub.
diz "Instalando o comando curupira"
SISTEMA_DIR="$(cd "$(dirname "$0")" && pwd)/sistema"
if [[ ! -f "$SISTEMA_DIR/instalar.sh" ]]; then
  TMP_REPO="$(mktemp -d)"
  curl -fsSL https://github.com/pabloherzberg/curupiraOS/archive/refs/heads/main.tar.gz \
    | tar -xz -C "$TMP_REPO" --strip-components=1
  SISTEMA_DIR="$TMP_REPO/sistema"
fi
bash "$SISTEMA_DIR/instalar.sh" /mnt

if [[ "$MODO_DADOS" != "nenhum" ]]; then
  mount "$PART_DADOS" /mnt/data
  chown 1000:1000 /mnt/data
  umount /mnt/data
fi

# Entrada de boot "Curupira Resgate" para a partição do instalador que ficou no HD.
if [[ "$MODO_DADOS" == "preservar-resgate" ]]; then
  NUM="$(lsblk -no PARTN "$MIDIA_PART" 2>/dev/null || true)"
  if [[ -n "$NUM" ]]; then
    efibootmgr -q -c -d "$DISCO_DADOS" -p "$NUM" -L "Curupira Resgate" -l '\EFI\BOOT\BOOTx64.EFI' || true
    # o sistema novo continua sendo a primeira opção
    PRIMEIRO="$(efibootmgr | awk '/Linux Boot Manager/{print substr($1,5,4); exit}')"
    RESTO="$(efibootmgr | awk -F'[ :]+' '/^BootOrder/{print $2}' | tr ',' '\n' | grep -v "^${PRIMEIRO}$" | paste -sd, -)"
    [[ -n "$PRIMEIRO" ]] && efibootmgr -q -o "${PRIMEIRO}${RESTO:+,$RESTO}" || true
  fi
fi

sync
umount -R /mnt
echo
diz "Curupira OS instalado."
echo "    Reinicie com: reboot   (se usou pendrive, retire-o antes)"
echo "    Entre com o usuário '$USUARIO'. Perfis de energia: rode 'curupira ajuda'. O tema chega na próxima versão."
