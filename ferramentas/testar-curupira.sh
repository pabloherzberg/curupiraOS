#!/usr/bin/env bash
# Testa o comando curupira sem root e sem mexer no sistema: simula o /sys
# (carregador, bateria, tela, CPU) numa pasta temporária.
#
#   bash ferramentas/testar-curupira.sh

set -uo pipefail
RAIZ_REPO="$(cd "$(dirname "$0")/.." && pwd)"
CURUPIRA="$RAIZ_REPO/sistema/bin/curupira"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export CURUPIRA_TESTE="$T"

mkdir -p "$T/sys/class/power_supply/ADP1" "$T/sys/class/power_supply/BAT1" \
         "$T/sys/class/backlight/intel_backlight" \
         "$T/sys/devices/system/cpu/cpufreq/policy0" "$T/sys/devices/system/cpu/intel_pstate"
echo Mains   > "$T/sys/class/power_supply/ADP1/type"
echo Battery > "$T/sys/class/power_supply/BAT1/type"
echo 1500 > "$T/sys/class/backlight/intel_backlight/max_brightness"
echo balance_performance > "$T/sys/devices/system/cpu/cpufreq/policy0/energy_performance_preference"
echo 0 > "$T/sys/devices/system/cpu/intel_pstate/no_turbo"
echo 100 > "$T/sys/devices/system/cpu/intel_pstate/max_perf_pct"

tomada()  { echo "$1" > "$T/sys/class/power_supply/ADP1/online"; }
bateria() { echo "$1" > "$T/sys/class/power_supply/BAT1/capacity"; echo "$2" > "$T/sys/class/power_supply/BAT1/status"; }
brilho()  { echo "$1" > "$T/sys/class/backlight/intel_backlight/brightness"; }
perfil()  { cat "$T/estado/perfil" 2>/dev/null; }
roda()    { "$CURUPIRA" "$@"; }

falhas=0; total=0
confere() {   # confere <descrição> <esperado> <obtido>
  total=$((total+1))
  if [[ "$2" == "$3" ]]; then printf '  ok    %s\n' "$1"
  else printf '  FALHA %s (esperado "%s", veio "%s")\n' "$1" "$2" "$3"; falhas=$((falhas+1)); fi
}

echo "Cabeçalho"
# Uma linha sem "#" no cabeçalho vira comando: em 15/11/2026 uma linha "curupira cuca lista"
# solta fez cada execução chamar a si mesma e esgotou a memória do notebook.
soltas="$(awk '/^set -euo pipefail/{exit} NR>1 && !/^#/ && !/^[[:space:]]*$/' "$CURUPIRA" "$RAIZ_REPO/sistema/bin/curupira-voltar")"
confere "nenhum comando solto no cabeçalho" "" "$soltas"
# o limite é de processos e threads do usuário inteiro: numa sessão gráfica já há centenas, por isso a folga
# é contada a partir do que está rodando agora (com 400 fixos o teste falhava dentro do Plasma)
agora="$(ps -u "$(id -u)" -L --no-headers 2>/dev/null | wc -l)"
confere "não chama a si mesmo ao iniciar" "curupira" "$(ulimit -u $((agora + 300)); timeout 5 "$CURUPIRA" versao 2>&1 | cut -d' ' -f1)"

echo "Boot na tomada"
tomada 1; bateria 100 Full; brilho 1500
roda evento boot >/dev/null
confere "perfil inicial é correnteza" correnteza "$(perfil)"
conf="$T/tlp.d/20-curupira-perfil.conf"
confere "escreve os três perfis do TLP" 3 "$(grep -c '^CPU_MAX_PERF_ON_' "$conf")"
confere "sufixo no meio do nome" 'DEVICES_TO_DISABLE_ON_SAV_NOT_IN_USE=""' "$(grep '^DEVICES_TO_DISABLE_ON_SAV' "$conf")"
confere "nada de nomes antigos (_ON_AC/_ON_BAT)" 0 "$(grep -cE '_ON_(AC|BAT)=' "$conf")"

echo "Tira da tomada"
tomada 0; bateria 80 Discharging
saida="$(roda evento tomada)"
confere "vai para remanso" remanso "$(perfil)"
confere "avisa na tela" "[notificação] Perfil Remanso: Saiu da tomada, bateria em 80%." "$saida"
confere "evento repetido não reaplica" "" "$(roda evento tomada)"

echo "Bateria descendo"
bateria 16 Discharging; roda evento bateria >/dev/null
confere "16% continua remanso" remanso "$(perfil)"
bateria 15 Discharging; roda evento bateria >/dev/null
confere "15% vira sereno" sereno "$(perfil)"
confere "sereno baixa o brilho para 30%" 450 "$(cat "$T/sys/class/backlight/intel_backlight/brightness")"
roda remanso >/dev/null
bateria 14 Discharging; roda evento bateria >/dev/null
confere "troca manual depois do aviso é respeitada" remanso "$(perfil)"

echo "Volta para a tomada"
roda sereno >/dev/null
tomada 1; bateria 15 Charging; roda evento tomada >/dev/null
confere "vai para correnteza" correnteza "$(perfil)"
confere "brilho volta ao anterior" 1500 "$(cat "$T/sys/class/backlight/intel_backlight/brightness")"

echo "Brilho mexido pela pessoa não é sobrescrito"
roda sereno >/dev/null; brilho 300; roda correnteza >/dev/null
confere "mantém o brilho escolhido" 300 "$(cat "$T/sys/class/backlight/intel_backlight/brightness")"

echo "Sai da tomada já com bateria baixa"
tomada 0; bateria 10 Discharging; roda evento tomada >/dev/null
confere "vai direto para sereno" sereno "$(perfil)"

echo "Automação desligada"
tomada 1; roda auto desligar >/dev/null; roda pororoca >/dev/null
tomada 0; roda evento tomada >/dev/null; roda evento bateria >/dev/null
confere "perfil manual fica" pororoca "$(perfil)"
roda evento boot >/dev/null
confere "boot mantém o perfil manual" pororoca "$(perfil)"
roda auto ligar >/dev/null
confere "religar aplica o perfil da fonte atual" sereno "$(perfil)"

echo "Comandos"
confere "nome com maiúscula" 0 "$(roda Correnteza >/dev/null; echo $?)"
confere "perfil inexistente falha" 1 "$(roda tsunami >/dev/null 2>&1; echo $?)"
confere "lista os quatro perfis" 4 "$(roda perfis | wc -l)"
confere "estado mostra o perfil" 1 "$(roda | grep -c 'perfil Correnteza')"

echo "Caipora"
roda camera cortar >/dev/null
confere "câmera cortada grava o bloqueio do driver" 1 "$(grep -c '^install uvcvideo /bin/true' "$T/modprobe.d/curupira-caipora.conf")"
confere "json mostra a câmera cortada" true "$(roda json | python3 -c 'import json,sys; print(str(json.load(sys.stdin)["camera_cortada"]).lower())')"
roda camera liberar >/dev/null
confere "câmera liberada apaga o bloqueio" no "$([[ -e "$T/modprobe.d/curupira-caipora.conf" ]] && echo sim || echo no)"
roda mac aleatorio >/dev/null
confere "MAC por rede no NetworkManager" 1 "$(grep -c '^wifi.cloned-mac-address=stable' "$T/NetworkManager/conf.d/90-curupira-caipora.conf")"
roda mac fixo >/dev/null
confere "MAC fixo apaga a configuração" no "$([[ -e "$T/NetworkManager/conf.d/90-curupira-caipora.conf" ]] && echo sim || echo no)"
confere "verbo errado falha" 1 "$(roda camera quebrar >/dev/null 2>&1; echo $?)"

echo "Boitatá"
jboi() { roda json | python3 -c 'import json,sys; print(str(json.load(sys.stdin)["boitata_dormindo"]).lower())'; }
confere "começa dormindo" true "$(jboi)"
roda boitata acordar >/dev/null
confere "acordar deixa o aviso para a regra do udev" sim "$([[ -e "$T/run/boitata-acordada" ]] && echo sim || echo no)"
confere "json mostra a Boitatá acordada" false "$(jboi)"
confere "acordar duas vezes não falha" 0 "$(roda boitata acordar >/dev/null 2>&1; echo $?)"
roda boitata dormir >/dev/null
confere "dormir tira a placa do barramento" true "$(jboi)"
confere "dormir apaga o aviso" no "$([[ -e "$T/run/boitata-acordada" ]] && echo sim || echo no)"
confere "rodar acorda e usa a placa" "1 false" "$(roda boitata rodar sh -c 'echo $DRI_PRIME') $(jboi)"
roda boitata dormir >/dev/null
confere "verbo errado da Boitatá falha" 1 "$(roda boitata assustar >/dev/null 2>&1; echo $?)"
confere "a regra do udev olha o mesmo aviso que o comando" 3 "$(grep -c 'TEST!="/run/curupira/boitata-acordada"' "$RAIZ_REPO/sistema/udev/00-curupira-boitata.rules")"

echo "Widget (json e brilho)"
campo() { roda json | python3 -c "import json,sys; v=json.load(sys.stdin)$1; print(str(v).lower() if isinstance(v,bool) else v)"; }
brilho 1500
roda brilho 50 >/dev/null
confere "brilho 50% grava metade do máximo" 750 "$(cat "$T/sys/class/backlight/intel_backlight/brightness")"
confere "json mostra o brilho" 50 "$(campo '["brilho"]')"
roda brilho 1 >/dev/null
confere "brilho nunca fica abaixo de 5%" 75 "$(cat "$T/sys/class/backlight/intel_backlight/brightness")"
confere "brilho com texto falha" 1 "$(roda brilho muito >/dev/null 2>&1; echo $?)"
confere "json tem o usuário" 1 "$(roda json | grep -c '"usuario":"')"
confere "json tem a carga do processador (papel de parede)" 0 "$(campo '["carga"]')"
confere "json diz se o laboratório do Boto existe" false "$(campo '["lab"]')"
tomada 1; roda auto ligar >/dev/null; tomada 0; bateria 60 Discharging; roda evento tomada >/dev/null
confere "json guarda o último aviso automático" "Perfil Remanso" "$(campo '["ultimo_evento"]["titulo"]')"

echo
if (( falhas )); then echo "$falhas de $total testes falharam."; exit 1; fi
echo "Todos os $total testes passaram."
