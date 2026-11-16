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
- Se você quiser, criptografa o disco do sistema (LUKS2): o instalador pergunta. A senha do disco passa a ser
  pedida em todo boot; o `/boot` e o `/data` ficam abertos. (Ainda não testado numa instalação de verdade.)

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

### Pela ISO da Curupira

O repositório também gera uma ISO própria: a do Arch com o instalador dentro. No GitHub, em Actions →
"ISO da Curupira OS" → Run workflow, a ISO sai nos artefatos da execução; a cada etiqueta `v*` ela é anexada
ao lançamento. Iniciando por ela, basta conectar a internet e rodar `instalar-curupira` (aceita `--simular`).
Para montar num Arch: `sudo bash ferramentas/iso/montar-iso.sh`.

### Sem pendrive

Se a ISO foi copiada para uma partição do próprio HD, o instalador percebe isso sozinho: ele mantém essa
partição como "Curupira Resgate" e usa o restante do HD como `/data`.

### Teste em máquina virtual

```bash
DISCO_SISTEMA=/dev/vda DISCO_DADOS=nenhum bash install.sh
```

`CRIPTOGRAFIA=sim` (ou `nao`) responde de antemão a pergunta da criptografia.

## Atualizar

```
curupira atualizar
```

Baixa a versão nova do repositório (`git pull`; se a pasta não existir, clona em `~/curupiraOS`) e instala de
novo, pedindo a senha. Mostra o que mudou e avisa quando já está em dia. `curupira versao` diz qual commit está
instalado.

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
| Tela de abertura do Plasma | `tema/plasma/io.github.pabloherzberg.curupira/` (tema global "Curupira") | padrão do sistema em `/etc/xdg/ksplashrc` |
| Doca (painel do mockup) | layout do tema global + widget `sistema/doca` | `curupira-doca` troca o painel atual (guarda uma cópia; `--desfazer` volta) |
| Tela de boot (Plymouth) | `tema/plymouth/curupira/` → `/usr/share/plymouth/themes/curupira` | ativa pelo instalador: hook `plymouth` e `splash` no boot |

A doca some quando uma janela em tela cheia ou maximizada encosta nela e volta subindo quando o mouse toca a
borda de baixo. Os apps ficam no widget Doca Curupira: quando a doca surge, cada ícone sobe girando, solta uma
faísca de brasa e no fim passa uma onda; o ícone sob o mouse "respira"; pulam ao abrir; clique do meio abre outra janela, botão direito fixa, tira ou fecha.

O fundo arredondado da doca vem do estilo do Plasma "Curupira" (`tema/gerar-painel.py`), que só troca o fundo do
painel e acompanha o esquema de cores. Os apps aparecem em ladrilhos coloridos com o símbolo branco. O widget
Curupira abre o cartão rápido do mockup: perfil, os seis seres (clique para ligar ou desligar), volume, brilho
e o último aviso automático.

As cores saem de `tema/gerar-cores.py`, os papéis de parede de `tema/gerar-papeis.py` e as imagens da tela de
boot de `tema/gerar-boot.py`. Se a tela de boot der problema, escolha "modo de recuperação" no menu do boot
(segure Espaço ao ligar): ela inicia sem o Plymouth. Para ver a tela de login
sem sair da sessão: `sddm-greeter-qt6 --test-mode --theme tema/sddm/curupira`.

## Seres da mata

| Ser | Papel |
|---|---|
| Curupira | mascote e central de controle |
| Boitatá | placa de vídeo NVIDIA: dorme por padrão; `curupira boitata acordar` ou `rodar <programa>`; depois de acordada, volta a dormir ao reiniciar |
| Mapinguari | HD de 1 TB em `/data`: acorda ao abrir a pasta; `curupira hd dormir` fecha e para o motor; para sozinho depois de 5 min sem uso |
| Iara | Wi-Fi e Bluetooth |
| Saci | turbo do processador |
| Caipora | privacidade |
| Boto | laboratório de rede |
| Cuca | snapshots do sistema |

## Trabalhando no projeto com o Claude

O arquivo [`CLAUDE.md`](CLAUDE.md) tem o mapa do repositório, a identidade visual, de onde vem cada arte,
como testar e os cuidados. O Claude Code lê esse arquivo sozinho ao abrir o projeto. Para trocar uma arte:
edite o SVG em `arte/`, rode `bash tema/gerar-tudo.sh` e `sudo bash sistema/instalar.sh`.

## Próximos passos

- Demais seções da Toca do Curupira.
