# Curupira OS: início do bash no perfil Encante do Konsole (o perfil abre "bash --rcfile" com este arquivo).
# Carrega o de sempre (/etc/bash.bashrc e ~/.bashrc) e depois acende as cores do fundo do rio:
# rosa do boto #F08FB5, luz viva #5FE3D9, luz das casas #FFC46B, texto suave #9CC8C6, alerta #FF8A70.

[[ -r /etc/bash.bashrc ]] && . /etc/bash.bashrc
[[ -r ~/.bashrc ]] && . ~/.bashrc

__boto=$'\e[38;2;240;143;181m'
__luz=$'\e[38;2;95;227;217m'
__casas=$'\e[38;2;255;196;107m'
__suave=$'\e[38;2;156;200;198m'
__alerta=$'\e[38;2;255;138;112m'
__negrito=$'\e[1m'
__fim=$'\e[0m'

# o "$" do prompt fica rosa; se o último comando falhou, fica cor de alerta e mostra o código
__encante_prompt() {
  local st=$?
  if (( st == 0 )); then __encante_fim="\[$__boto$__negrito\]\$"
  else __encante_fim="\[$__alerta$__negrito\]$st \$"; fi
  PS1="\[$__suave\][\[$__boto$__negrito\]\u\[$__fim$__suave\]@\h \[$__luz\]\W\[$__suave\]] $__encante_fim\[$__fim\] "
}
PROMPT_COMMAND=(__encante_prompt "${PROMPT_COMMAND[@]}")

# grep: o trecho achado em rosa, nome do arquivo em luz viva, número da linha em âmbar
export GREP_COLORS="ms=01;38;2;240;143;181:mc=01;38;2;240;143;181:fn=38;2;95;227;217:ln=38;2;255;196;107:bn=38;2;255;196;107:se=38;2;156;200;198"

# man e less: títulos em rosa, termos sublinhados em luz viva, busca e barra de baixo em rosa com texto escuro
export GROFF_NO_SGR=1
export LESS_TERMCAP_md=$'\e[1;38;2;240;143;181m'
export LESS_TERMCAP_us=$'\e[4;38;2;95;227;217m'
export LESS_TERMCAP_so=$'\e[38;2;6;42;56;48;2;240;143;181m'
export LESS_TERMCAP_me=$'\e[0m' LESS_TERMCAP_ue=$'\e[0m' LESS_TERMCAP_se=$'\e[0m'
