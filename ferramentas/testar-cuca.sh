#!/usr/bin/env bash
# Testa o curupira-voltar de verdade, como root, sem mexer no que importa:
# cria um par de snapshots com um arquivo de teste no meio, desfaz, confere e apaga o que criou.
#
#   sudo bash ferramentas/testar-cuca.sh

set -uo pipefail
[[ $EUID -eq 0 ]] || { echo "Rode como root (sudo bash $0)."; exit 1; }
VOLTAR=/usr/local/bin/curupira-voltar
ARQ=/etc/curupira-teste-cuca
falhas=0
ok()    { echo "  ok    $*"; }
falha() { echo "  FALHA $*"; falhas=$((falhas+1)); }

A=$(snapper -c root create -t pre -d "teste da Cuca" -c number --print-number)
echo "teste da Cuca" > "$ARQ"
B=$(snapper -c root create -t post --pre-number "$A" -d "teste da Cuca" -c number --print-number)
echo "Par de teste: #$A → #$B"

snapper -c root status "$A..$B" | grep -q "$ARQ" && ok "o snapper viu o arquivo de teste" || falha "o snapper não viu o arquivo"

saida="$("$VOLTAR" desfazer "$A" "$B" 2>&1)"; codigo=$?
[[ $codigo -eq 0 ]] && ok "desfazer terminou" || falha "desfazer saiu com $codigo: $saida"
[[ ! -e "$ARQ" ]] && ok "o arquivo criado entre os snapshots sumiu" || falha "o arquivo continua lá"
SEG="$(grep -o 'snapshot #[0-9]*' <<<"$saida" | head -1 | tr -dc '0-9')"
[[ -n "$SEG" && -d "/.snapshots/$SEG" ]] && ok "guardou o snapshot de segurança #$SEG" || falha "sem snapshot de segurança"
grep -q "Para refazer: curupira-voltar sistema $SEG" <<<"$saida" && ok "diz como refazer" || falha "não diz como refazer"

"$VOLTAR" desfazer "$B" "$A" >/dev/null 2>&1 && falha "aceitou a ordem invertida" || ok "recusa a ordem invertida"
"$VOLTAR" sistema 999999 >/dev/null 2>&1 && falha "aceitou snapshot inexistente" || ok "recusa snapshot inexistente"
"$VOLTAR" sistema 'abc;id' >/dev/null 2>&1 && falha "aceitou número inválido" || ok "recusa número inválido"

# a guarda do kernel: um snapshot cujo /usr/lib/modules difere do atual tem que ser recusado
K=$(snapper -c root create -d "teste da Cuca: kernel" -c number --print-number)
btrfs property set -ts "/.snapshots/$K/snapshot" ro false
mkdir "/.snapshots/$K/snapshot/usr/lib/modules/0.0.0-teste"
btrfs property set -ts "/.snapshots/$K/snapshot" ro true
saida="$("$VOLTAR" sistema "$K" 2>&1)" && falha "voltou mesmo com o kernel diferente" \
  || { grep -q "kernel" <<<"$saida" && ok "recusa quando o kernel mudou" || falha "recusou, mas por outro motivo: $saida"; }

snapper -c root delete "$A" "$B" "$K" ${SEG:+"$SEG"} && ok "apagou os snapshots de teste" || falha "não apagou os snapshots de teste"

echo
(( falhas )) && { echo "$falhas falha(s)."; exit 1; }
echo "Todos os testes da Cuca passaram."
