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

## A fazer
1. Comando `curupira` com os quatro perfis, automação tomada/bateria e regras do polkit.
2. "Toca do Curupira": central de controle em Qt/Python e widget do painel.
3. Tema do Plasma, do SDDM, do Plymouth e do Konsole com as artes acima.
4. Acordar a Boitatá sob demanda (hoje ela fica sempre desligada; apagar
   `/etc/udev/rules.d/00-curupira-boitata.rules` e `/etc/modprobe.d/curupira-boitata.conf` a religa).
5. Criptografia de disco (LUKS) como opção do instalador.
6. Gerar uma ISO própria pelo GitHub Actions.
