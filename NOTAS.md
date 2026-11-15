# Notas do projeto

Registro do que foi decidido, para retomar o trabalho depois da formatação (a conversa original ficou no Windows).

## Máquina
Samsung Notebook 3 (340XAA/350XAA/550XAA), i5-8250U, 8 GB DDR4 (2×4 GB), NVMe Kingston de 250 GB,
HD Toshiba de 1 TB (5400 rpm), Intel UHD 620 + NVIDIA MX110, tela 1366×768, Wi-Fi QCA9377 (ath10k),
bateria com 74% da capacidade original (31,9 Wh).

## Identidade
- **Brasa** é o Curupira oficial: retrato com cabelo de fogo. Vira papel de parede (`arte/brasa-fundo.svg`)
  e tela de boot (`arte/01-brasa.svg`, com as pegadas ao contrário como indicador de carregamento).
- **Cordel** é o mascote dentro da interface: `arte/cordel-figura.svg` (modais) e `arte/cordel-busto.svg` (avatares).
- Interface clara e moderna, no estilo do Deepin, sem transparências. Fontes: Baloo 2, Nunito, JetBrains Mono.
- Cores: #241A4A, #D2507A, #FF7A45, #2BB37A, #F4D3A0, #FBF4E8.
- Outras propostas guardadas em `arte/propostas/`. O mockup das telas está em `mockup/`.

## Seres e perfis
Curupira (central de controle), Boitatá (NVIDIA), Mapinguari (HD), Iara (Wi-Fi/Bluetooth), Saci (turbo),
Caipora (privacidade), Boto (laboratório de rede), Cuca (snapshots).

Perfis de energia: Pororoca (desempenho), Correnteza (equilibrado), Remanso (bateria), Sereno (extremo).
Gatilhos planejados: saiu da tomada = Remanso; voltou = Correnteza; bateria em 15% = Sereno.

## Feito
- `install.sh`: Arch + KDE Plasma, Btrfs com snapshots, HD em `/data` sob demanda, TLP, zram, NVIDIA desligada.
- `ferramentas/preparar-instalador.ps1`: boot do instalador sem pendrive, a partir de uma partição no NVMe.
- Sistema instalado no notebook em 15/11/2026 (Arch + KDE pelo `install.sh`).
- Comando `curupira` (`sistema/`): os quatro perfis viram configuração do TLP 1.11 (nomes `_ON_PRF/_BAL/_SAV`;
  os antigos `_ON_AC/_ON_BAT` foram descontinuados). O TLP fica parado no perfil BAL e o curupira reescreve
  `/etc/tlp.d/20-curupira-perfil.conf`. Tomada via udev, bateria via timer de 1 min, polkit libera o grupo wheel.
  Testado no notebook: Sereno deixa EPP `power`, sem turbo, CPU em 50% e brilho em 30%. Tirar e pôr o
  carregador troca Remanso/Correnteza com aviso na tela. Falta ver o Sereno disparar sozinho em 15%.
- Toca do Curupira v0.1 (`sistema/toca/toca.py`, PySide6): seção Energia segue o mockup `mockup/Central.dc.html`
  com dados reais (`curupira json`: watts, Wh, perfil). Wi-Fi via nmcli, Bluetooth via rfkill+bluetoothctl,
  HD pelo automount de /data. Boitatá, Caipora e Boto aparecem desabilitados ("em breve").
  `--captura arquivo.png` desenha a janela sem tela (bom para conferir mudanças).
- Toca v0.2: código dividido em `visual.py` (peças), `sistema.py` (leitura do sistema, sem Qt) e `secoes/`.
  Seções novas: Seres da mata, Rede e Boto (rede Podman interna "curupira-lab"), Privacidade (câmera via
  `curupira camera cortar|liberar`, que bloqueia o uvcvideo no modprobe; MAC via `curupira mac aleatorio|fixo`,
  que usa cloned-mac-address=stable no NetworkManager; microfone via wpctl), Cuca (snapper liberado para o grupo
  wheel com ALLOW_GROUPS) e Aparência (plasma-apply-colorscheme e plasma-apply-wallpaperimage).
  `--captura-todas pasta/` gera um PNG de cada seção.
- Cuca volta no tempo (Toca 0.3): `curupira-voltar desfazer A B` / `sistema N` (snapper undochange), com
  senha toda vez (polkit próprio, auth_admin), snapshot de segurança antes e recusa se /usr/lib/modules
  mudou (o /boot fica fora dos snapshots). O snapper voltou a ser só do root: a Toca lê por
  `curupira cuca lista|mudancas|guardar`. Conferido: o snapper não entra em /home, /var/log, cache do pacman,
  /data nem /boot. **Falta rodar `sudo bash ferramentas/testar-cuca.sh`** (interrompido) e apagar snapshots
  "teste da Cuca" que tenham sobrado.
- Tema (`tema/`): esquemas Curupira (claro, barra de título noite) e Curupira Noite, gerados por
  `gerar-cores.py`; perfil do Konsole; papéis de parede Brasa e Entardecer em PNG (1366×768, 1920×1080,
  2560×1440) por `gerar-papeis.py`; tela de login SDDM em QML puro seguindo `mockup/Boot.dc.html`
  (avatar do Cordel quando não há foto; testada com `sddm-greeter-qt6 --test-mode`). A Toca troca os esquemas.
- Tela de boot (Plymouth, `tema/plymouth/curupira/`): retrato de `arte/01-brasa.svg` com as laterais esmaecidas
  e as cinco pegadas da arte acendendo em sequência (script do Plymouth). Hook `plymouth` depois de `systemd`,
  `splash` na entrada normal e `plymouth.enable=0` na de recuperação. Prévia sem reiniciar: plymouthd como root
  com DISPLAY/XAUTHORITY do Xwayland usa o renderizador X11 (o tema vem de /etc/plymouth/plymouthd.conf).
- A entrada de recuperação da v0.1 apontava para initramfs-linux-fallback.img, que o mkinitcpio do Arch não gera
  mais (PRESETS=('default')); agora usa initramfs-linux.img.
- Tema global do Plasma "Curupira" (`tema/plasma/io.github.pabloherzberg.curupira/`): tela de abertura (KSplash)
  com o retrato e as pegadas da tela de boot, uma pegada por etapa do Plasma; padrão em /etc/xdg/ksplashrc.
  Layout com a doca do `mockup/Desktop.dc.html` (painel flutuante, centralizado, do tamanho do conteúdo: menu
  com o Cordel, 7 apps fixados, widget Curupira, bandeja, relógio com data). `curupira-doca` aplica na sessão
  e guarda o painel em ~/.config/curupira-painel-anterior. O ícone do menu é PNG (`tema/gerar-icones.py`): o
  QtSvg não recorta (clip-path) nem aceita <svg> aninhado. Depois de instalar ícones novos, limpar
  ~/.cache/icon-cache.kcache, senão o Plasma lembra do ícone "não encontrado".
- Doca v2: painel em "desviar das janelas" (panelVisibility=2): tela cheia e maximizadas usam a tela toda e a
  doca volta ao tocar a borda de baixo. Widget próprio `sistema/doca` (io.github.pabloherzberg.doca, TasksModel
  do Plasma) no lugar do icontasks. Ao surgir (mouse entra depois de 0,9 s fora, a janela do painel reaparece, ou o
  ícone nasce logo após o surgimento), cada ícone, do centro para as pontas, nasce pequeno e girado embaixo, sobe
  com balanço elástico, solta uma faísca de brasa (anel dourado) e no fim passa uma onda da esquerda para a
  direita. Mouse em cima: só aquele ícone "respira" (1,16 ↔ 0,92). Pulo ao abrir, ponto/traço de aberto, menu
  Nova janela/Fixar/Fechar. Para ver a entrada em câmera lenta, multiplique as durações numa cópia em
  ~/.local/share/plasma/plasmoids (e apague depois: ela tem prioridade sobre a do sistema).
  Relógio com fonte fixa (11 pt, negrito, data embaixo: dateDisplayFormat=2). `curupira-doca` só guarda o painel
  na primeira vez.
- Acabamento da doca: estilo do Plasma "Curupira" (`tema/plasma-estilo/curupira`, gerado por `gerar-painel.py`) só
  com o panel-background: raio 24, sombra roxa, cor por ColorScheme-ViewBackground (branco no claro, noite no
  escuro); o resto vem do Breeze. Doca com 70 px. Apps em ladrilhos (degradês do mockup, símbolo branco do Breeze
  com isMask; app desconhecido ganha cor pelo AppId e o ícone original). Cartão rápido do widget Curupira como no
  mockup; `curupira json` ganhou usuário, Wi-Fi/rede, Bluetooth (rfkill), turbo, HD, Boitatá, volume, microfone,
  brilho e o último aviso automático; `curupira brilho N` (polkit, sem senha).
- `tema/gerar-tudo.sh` regenera todas as imagens a partir de `arte/` e da paleta (inclusive as cópias do login).
  Instruções para continuar em outra conversa do Claude: `CLAUDE.md`.
- Incidente de 15/11/2026: uma linha "curupira cuca lista" sem "#" no cabeçalho fez o curupira chamar a si
  mesmo; o widget e o timer recomeçavam a cadeia e a memória esgotou (~14 mil processos root). Corrigido e
  coberto por teste em `ferramentas/testar-curupira.sh`.
- Widget do painel (`sistema/plasmoide/`, QML do Plasma 6): ícone na cor do perfil, lista de perfis, botão para a Toca.
- Fontes Baloo 2 e Nunito (OFL) vão junto em `sistema/toca/fontes/`.
- Ícones "Brasa na noite" (15/11/2026, escolhida entre três propostas: ladrilho de traço, xilogravura e esta):
  tema de ícones "Curupira" (`tema/icones/Curupira`, gerado de `arte/icones/`, herda do Breeze) com 17 apps do
  KDE, a bandeja (Wi-Fi, cabo, som, microfone, bateria, Bluetooth, avisos) e as ações dos menus (janela, fixar,
  sessão, busca etc.). Apps de terceiros ficam com o ícone original. A doca passou a ter todos os ladrilhos na
  cor da noite. `curupira-doca` aplica o tema de ícones (e `--desfazer` volta ao Breeze). Na Toca e no cartão
  rápido, os seres ganharam arte própria; na Toca eles se mexem quando acordados (chama do Boitatá, olho do
  Mapinguari girando, ponteiros da Cuca para trás) e ficam apagados quando dormem. A animação para com a janela
  em segundo plano e respeita as animações desligadas no Plasma.
  Arte na Toca (as três propostas juntas, cada uma com um papel): paisagem no pé da barra lateral na cor do
  perfil, com as pegadas ao contrário; faixa cor da noite abrindo Seres, Rede, Privacidade, Cuca e Aparência;
  e o ser acordado grande no canto de baixo (Energia: Saci, Boitatá ou Mapinguari; Rede: Boto ou Iara;
  Privacidade: Caipora).
  Feito numa sessão na nuvem: desenhos conferidos com o QtSvg e a Toca por captura; **falta ver no Plasma de
  verdade** a doca, o cartão rápido, a bandeja e os menus (os nomes de ícone vieram do Breeze 5.115).
- Papel de parede animado "Mata Viva" (15/11/2026, `tema/papel-vivo/`, plugin de papel de parede do Plasma 6):
  um só, com todos os seres. A arte do Brasa é desmontada em 47 camadas e o cabelo de fogo, as pálpebras, o halo,
  as faíscas e os vaga-lumes se mexem como a própria arte descreve. Reage ao `curupira json` (que ganhou `carga`
  e `lab`): perfil e uso do processador dão o vigor do fogo; bateria = vaga-lumes acesos e força do halo; Sereno
  fecha os olhos do Curupira; Boitatá (cobra de fogo atrás dos troncos) = NVIDIA acordada; Mapinguari abre o olho
  = HD; Saci no redemoinho = turbo; Iara sobe na lagoa = Wi-Fi, fogos azuis = Bluetooth; Boto salta = rede de
  laboratório; névoa e olhos da Caipora = câmera e microfone cortados; a lua da Cuca marca as horas.
  Só se mexe na tomada (ajustável) e nunca no Remanso/Sereno. Escolhe-se na Toca, em Aparência → Papel de
  parede (miniatura "Mata Viva" com o selo "animado"; com ele em uso aparece o ajuste "A mata se mexe": só na
  tomada, sempre ou parada). A Toca chama o `curupira-papel-vivo` (`--movimento …`, `--desfazer`).
  Segunda cena: **Iara** (`arte/iara-fundo.svg`), retrato no padrão do Brasa: a Iara na lagoa sob a lua cheia, com
  vitórias-régias. Existe parada (pacote Curupira-Iara, olhos fechados) e animada ("Iara Viva": o cabelo ondula na
  água com o vigor, grãos de luz sobem, os anéis na água são o Wi-Fi, vaga-lumes = bateria, olhos fechados no
  Sereno). O Pablo achou os seres pequenos da cena Brasa primitivos: redesenhar no padrão dos retratos.
  Conferido fora do Plasma com `ferramentas/ver-papel-vivo.py`; **falta ver como papel de parede de verdade**
  (`main.qml`, a tela de ajustes e o consumo de energia não foram testados).

## A fazer
1. Cuca: terminar o teste do curupira-voltar; depois, boot direto num snapshot (exige um subvolume
   @snapshots fora do @).
2. Conferir tela de boot, login e abertura num boot de verdade.
3. Acordar a Boitatá sob demanda (hoje ela fica sempre desligada; apagar
   `/etc/udev/rules.d/00-curupira-boitata.rules` e `/etc/modprobe.d/curupira-boitata.conf` a religa).
   O módulo nouveau ainda carrega apesar da blacklist (provavelmente pelo hook kms do initramfs).
4. Criptografia de disco (LUKS) como opção do instalador.
5. Gerar uma ISO própria pelo GitHub Actions.
6. Ícones: conferir no notebook (doca, bandeja, menus, cartão rápido); depois, menu de apps próprio no lugar do
   Kickoff (widget QML como a doca: busca, apps em ladrilhos, Cordel, botões de sessão). Mais arte na Toca:
   ícones das seções, o Cordel reagindo ao perfil, transição entre seções.
7. Mata Viva: redesenhar Saci, Boitatá, Mapinguari, Boto e a Iara da lagoa no padrão dos retratos (Brasa e Iara).
