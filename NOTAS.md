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
- Incidente de 15/11/2026: uma linha "curupira cuca lista" sem "#" no cabeçalho fez o curupira chamar a si
  mesmo; o widget e o timer recomeçavam a cadeia e a memória esgotou (~14 mil processos root). Corrigido e
  coberto por teste em `ferramentas/testar-curupira.sh`.
- Widget do painel (`sistema/plasmoide/`, QML do Plasma 6): ícone na cor do perfil, lista de perfis, botão para a Toca.
- Fontes Baloo 2 e Nunito (OFL) vão junto em `sistema/toca/fontes/`.

## A fazer
1. Cuca: terminar o teste do curupira-voltar; depois, boot direto num snapshot (exige um subvolume
   @snapshots fora do @).
2. Conferir tela de boot, login e abertura num boot de verdade. Doca: raio maior e ícones em ladrilhos
   (estilo próprio do Plasma); o popup do widget Curupira mais perto do cartão rápido do mockup.
3. Acordar a Boitatá sob demanda (hoje ela fica sempre desligada; apagar
   `/etc/udev/rules.d/00-curupira-boitata.rules` e `/etc/modprobe.d/curupira-boitata.conf` a religa).
   O módulo nouveau ainda carrega apesar da blacklist (provavelmente pelo hook kms do initramfs).
4. Criptografia de disco (LUKS) como opção do instalador.
5. Gerar uma ISO própria pelo GitHub Actions.
