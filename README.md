# Curupira OS

Uma distribuição Linux sob medida para um Samsung Notebook 3 (i5-8250U, 8 GB, NVMe de 250 GB + HD de 1 TB),
baseada em Arch Linux com KDE Plasma. O Curupira, guardião da mata, cuida da bateria: cada peça do computador
é um ser do folclore que dorme até ser necessário.

**Estado: v0.1 "Pororoca", em desenvolvimento. O instalador ainda não foi testado em máquina real.**

## O que o instalador faz

- Apaga o NVMe e cria 1 GB de boot (systemd-boot) + Btrfs com subvolumes e compressão zstd.
- Prepara o HD como `/data` (ext4), montado sob demanda para o disco ficar parado quando não é usado.
- Instala KDE Plasma, PipeWire, Firefox, ferramentas de programação e de rede (Podman, Wireshark, nmap, mitmproxy).
- Configura economia de energia: TLP, thermald, zram e a placa NVIDIA desligada por padrão.
- Ativa snapshots automáticos do sistema (snapper + snap-pac).
- Sistema em português do Brasil, teclado ABNT2, fuso de São Paulo.

## Como instalar

**Tudo nos dois discos é apagado. Faça backup antes.**

1. Inicie o computador pela ISO oficial do [Arch Linux](https://archlinux.org/download/) em modo UEFI, com Secure Boot desligado.
2. Conecte à internet. Por cabo é automático; por Wi-Fi:
   ```bash
   iwctl station wlan0 connect "NomeDaRede"
   ```
3. Baixe o instalador:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/pabloherzberg/curupiraOS/main/install.sh -o install.sh
   ```
4. Veja o plano sem alterar nada:
   ```bash
   bash install.sh --simular
   ```
5. Instale:
   ```bash
   bash install.sh
   ```

O script pede usuário e senha e só apaga os discos depois que você digitar `APAGAR`.

### Sem pendrive

Se a ISO foi copiada para uma partição do próprio HD, o instalador percebe isso sozinho: ele mantém essa
partição como "Curupira Resgate" e usa o restante do HD como `/data`.

### Teste em máquina virtual

```bash
DISCO_SISTEMA=/dev/vda DISCO_DADOS=nenhum bash install.sh
```

## Perfis de energia

O comando `curupira` troca o computador entre quatro perfis. Quem aplica os ajustes é o TLP.

| Perfil | Quando | O que faz |
|---|---|---|
| Pororoca | desempenho | turbo e processador no máximo, sem economia |
| Correnteza | equilibrado (tomada) | turbo ligado, economia leve |
| Remanso | bateria | sem turbo, processador até 80%, Wi-Fi econômico |
| Sereno | economia extrema | processador até 50%, vídeo contido, brilho até 30% |

```bash
curupira               # perfil atual, bateria e automação
curupira remanso       # troca de perfil (sem senha para quem está no grupo wheel)
curupira perfis        # lista os perfis
curupira auto desligar # fixa o perfil escolhido
```

A troca é automática: saiu da tomada, Remanso; voltou, Correnteza; bateria em 15%, Sereno. Uma troca
manual vale até o próximo desses eventos. Os limites ficam em `/etc/curupira.conf` e os perfis em
`/usr/local/share/curupira/perfis/` (no repositório, `sistema/perfis/`).

Num sistema já instalado: `sudo bash sistema/instalar.sh`. Para testar sem root:
`bash ferramentas/testar-curupira.sh`.

## Toca do Curupira

Central de controle em Qt/Python (PySide6), no menu como **Toca do Curupira** ou pelo comando
`toca-do-curupira`. Seis seções:

| Seção | O que faz |
|---|---|
| Energia | consumo, duração da bateria, os quatro perfis; liga e desliga Wi-Fi, Bluetooth, HD, Caipora e Boto |
| Seres da mata | o bestiário, com o estado de cada ser agora |
| Rede e Boto | conexão (sinal, IP, roteador, DNS, MAC), Wireshark e mitmproxy, rede isolada do Podman |
| Privacidade | Caipora: corta a câmera, silencia o microfone, MAC diferente em cada rede, quem está usando agora |
| Cuca · snapshots | lista os snapshots, guarda um agora, conta o que mudou em cada instalação de pacote |
| Aparência | tema claro ou escuro, cor de destaque e papel de parede |

No painel, o widget **Curupira** (botão direito no painel → Adicionar widgets) mostra o perfil pela cor e troca
de perfil com um clique.

## Tema

| Peça | Onde fica | Como usar |
|---|---|---|
| Esquemas de cores Curupira e Curupira Noite | `tema/cores/` → `/usr/local/share/color-schemes` | Toca → Aparência, ou Configurações do sistema → Cores |
| Perfil do Konsole (JetBrains Mono, cores da paleta) | `tema/konsole/` → `/usr/local/share/konsole` | Konsole → Configurações → perfil Curupira |
| Papéis de parede Brasa e Entardecer | `tema/papeis/` → `/usr/local/share/wallpapers` | Toca → Aparência, ou clique direito na área de trabalho |
| Tela de login | `tema/sddm/curupira/` → `/usr/share/sddm/themes/curupira` | ativa pelo instalador (`/etc/sddm.conf.d/10-curupira.conf`) |

As cores saem de `tema/gerar-cores.py` e os papéis de parede de `tema/gerar-papeis.py`. Para ver a tela de login
sem sair da sessão: `sddm-greeter-qt6 --test-mode --theme tema/sddm/curupira`.

## Seres da mata

| Ser | Papel |
|---|---|
| Curupira | mascote e central de controle |
| Boitatá | placa de vídeo NVIDIA |
| Mapinguari | HD de 1 TB |
| Iara | Wi-Fi e Bluetooth |
| Saci | turbo do processador |
| Caipora | privacidade |
| Boto | laboratório de rede |
| Cuca | snapshots do sistema |

## Próximos passos

- Demais seções da Toca do Curupira.
- Tela de boot (Plymouth) e tema global do Plasma (tela de abertura).
