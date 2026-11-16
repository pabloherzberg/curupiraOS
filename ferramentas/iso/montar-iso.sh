#!/usr/bin/env bash
# Monta a ISO da Curupira OS: a ISO oficial do Arch (perfil "releng" do archiso) com este repositório
# dentro, em /root/curupiraOS, e o comando "instalar-curupira" pronto no ambiente live.
# Roda num Arch, como root, com o pacote archiso instalado. É o que o GitHub Actions executa
# (.github/workflows/iso.yml).
#
#   sudo bash ferramentas/iso/montar-iso.sh [pasta de saída]     (padrão: saida/)

set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "Rode como root (sudo bash $0)." >&2; exit 1; }
MODELO=/usr/share/archiso/configs/releng
[[ -d "$MODELO" ]] || { echo "Falta o archiso: pacman -S archiso" >&2; exit 1; }

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
SAIDA="${1:-$REPO/saida}"; mkdir -p "$SAIDA"; SAIDA="$(cd "$SAIDA" && pwd)"
TRAB="${TRAB:-$(mktemp -d /var/tmp/curupira-iso.XXXXXX)}"
PERFIL="$TRAB/perfil"
trap 'rm -rf "$TRAB"' EXIT

echo "==> Preparando o perfil em $PERFIL"
cp -r "$MODELO" "$PERFIL"
sed -i -E 's/^iso_name=.*/iso_name="curupira"/; s/^iso_publisher=.*/iso_publisher="Curupira OS <https:\/\/github.com\/pabloherzberg\/curupiraOS>"/; s/^iso_application=.*/iso_application="Instalador da Curupira OS"/' "$PERFIL/profiledef.sh"

# o repositório vai junto: o instalador não precisa baixar nada além dos pacotes
DESTINO="$PERFIL/airootfs/root/curupiraOS"
mkdir -p "$DESTINO"
if git -c safe.directory='*' -C "$REPO" rev-parse --git-dir >/dev/null 2>&1; then
  git -c safe.directory='*' -C "$REPO" archive HEAD | tar -x -C "$DESTINO"
else
  cp -r "$REPO"/. "$DESTINO"/ && rm -rf "$DESTINO/.git" "$DESTINO/saida"
fi

install -Dm755 /dev/stdin "$PERFIL/airootfs/usr/local/bin/instalar-curupira" <<'CMD'
#!/usr/bin/env bash
# Instalador da Curupira OS (o repositório vem dentro da ISO).
exec bash /root/curupiraOS/install.sh "$@"
CMD
grep -q '^file_permissions=(' "$PERFIL/profiledef.sh" \
  || { echo "O profiledef.sh do archiso mudou de formato: não achei file_permissions." >&2; exit 1; }
sed -i '/^file_permissions=(/a\  ["/usr/local/bin/instalar-curupira"]="0:0:755"' "$PERFIL/profiledef.sh"

cat >> "$PERFIL/airootfs/etc/motd" <<'MOTD'

  Curupira OS: para instalar, conecte a internet (cabo, ou: iwctl station wlan0 connect "NomeDaRede") e rode

      instalar-curupira --simular     mostra o plano, sem tocar nos discos
      instalar-curupira               instala (pede confirmação antes de apagar)

MOTD

echo "==> Montando a ISO (demora: baixa os pacotes do ambiente live)"
mkarchiso -v -w "$TRAB/trabalho" -o "$SAIDA" "$PERFIL"
echo "==> Pronto:"
ls -lh "$SAIDA"/*.iso
