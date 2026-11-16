# Curupira OS: instruções para o Claude

Distribuição pessoal do Pablo: Arch Linux + KDE Plasma 6 (Wayland) num Samsung Notebook 3
(i5-8250U, 8 GB, NVMe + HD de 1 TB, NVIDIA MX110). Tema: folclore brasileiro. Cada peça do
computador é um "ser da mata" que dorme até ser necessário. **Converse e escreva em português do
Brasil**: textos da interface, comentários, mensagens de commit e documentação.

Leia também o `NOTAS.md`: decisões tomadas, o que está feito, o que falta e os incidentes.
O `README.md` é a documentação para quem usa.

## Identidade visual (não invente cores ou fontes)

- **Paleta:** `#241A4A` noite · `#D2507A` urucum · `#FF7A45` brasa · `#2BB37A` mata · `#F4D3A0` areia quente
  · `#FBF4E8` areia. Tons de interface: texto `#1E2A24`, texto suave `#5B6A61`, verde de ação `#12935F`
  (escuro `#0F7A54`), borda `#EFE6D6`, alerta `#C2410C`.
- **Fontes:** Baloo 2 (títulos), Nunito (interface), JetBrains Mono (terminal). As duas primeiras vão
  junto no repositório (OFL), em `sistema/toca/fontes/`.
- **Personagens:** **Brasa** é o Curupira oficial (retrato com cabelo de fogo): papel de parede, login,
  boot. **Cordel** é o mascote da interface (xilogravura): avatares, menu da doca, Toca.
- **Seres:** Curupira (central), Boitatá (NVIDIA), Mapinguari (HD), Iara (Wi-Fi/Bluetooth), Saci (turbo),
  Caipora (privacidade), Boto (laboratório de rede), Cuca (snapshots).
- **Perfis de energia:** Pororoca (desempenho) `#FF7A45`, Correnteza (equilibrado) `#2BB37A`,
  Remanso (bateria) `#2468B8`, Sereno (extremo) `#5B3A8E`.
- **Mockups** (a fonte da verdade do visual): `mockup/*.dc.html`. `Desktop` = doca e cartão rápido,
  `Central` = Toca, `Boot` = tela de bloqueio/login, `Main` = identidade e bestiário.

## Mapa do repositório

| Caminho | O que é |
|---|---|
| `install.sh` | instalador a partir da ISO do Arch (apaga os discos; tem `--simular`) |
| `sistema/instalar.sh` | instala tudo abaixo num sistema já instalado (`sudo bash sistema/instalar.sh`) ou num `/mnt` |
| `sistema/bin/curupira` | comando de perfis de energia (bash); `curupira json` alimenta a Toca e os widgets |
| `sistema/bin/curupira-voltar` | Cuca volta no tempo (snapper undochange); pede senha toda vez |
| `sistema/perfis/*.perfil` | os quatro perfis (parâmetros do TLP 1.11, sufixos `_ON_PRF/_BAL/_SAV`) |
| `sistema/polkit`, `systemd`, `udev` | permissões sem senha (grupo wheel), timer da bateria, troca na tomada |
| `sistema/toca/` | **Toca do Curupira**, central de controle em PySide6: `toca.py` (janela), `visual.py` (peças), `sistema.py` (leitura do sistema, sem Qt), `secoes/` (uma por seção) |
| `sistema/doca/` | widget **Doca Curupira** (QML, Plasma 6): apps em ladrilhos, animações |
| `sistema/plasmoide/` | widget **Curupira** (QML): quadrado do perfil + cartão rápido do mockup |
| `tema/` | tema: cores, Konsole, papéis de parede, login (SDDM), boot (Plymouth), tema global do Plasma (`plasma/`), estilo do Plasma da doca (`plasma-estilo/`), ícone do menu |
| `tema/gerar-*.py`, `tema/gerar-tudo.sh` | geram as imagens a partir de `arte/` e da paleta |
| `arte/` | artes originais em SVG (`propostas/` = alternativas guardadas) |
| `ferramentas/` | testes (`testar-curupira.sh`, `testar-cuca.sh`), o preparo do instalador sem pendrive e a ISO (`iso/montar-iso.sh`, rodado pelo `.github/workflows/iso.yml`) |

## Artes: de onde vem cada imagem

Ao trocar ou criar uma arte, edite o SVG em `arte/`, rode `bash tema/gerar-tudo.sh` e instale com
`sudo bash sistema/instalar.sh`. **Nunca edite à mão** os PNG gerados nem os arquivos marcados "Gerado por".

| Arte | Vira | Gerador |
|---|---|---|
| `arte/brasa-fundo.svg` (1366×768) | papel de parede Brasa (3 tamanhos) + fundo do login | `gerar-papeis.py` |
| `arte/iara-fundo.svg` (1366×768) | papel de parede Iara (de corpo inteiro, sentada na pedra no rio, penteando o cabelo; o retrato anterior está em `arte/propostas/iara-retrato.svg`) | `gerar-papeis.py` |
| `arte/propostas/papel-de-parede-entardecer.svg` | papel de parede Entardecer | `gerar-papeis.py` |
| `arte/01-brasa.svg` (800×1000) | tela de boot (Plymouth) e de abertura (KSplash): retrato + 5 pegadas (`<g class="step">`) | `gerar-boot.py` |
| `arte/brasa-fundo.svg`, `arte/iara-fundo.svg` + `arte/papel-vivo/*.svg` | papel de parede animado **Mata Viva** (`tema/papel-vivo/`), com duas cenas (`brasa` e `iara`): cada arte desmontada em camadas + os seres da cena brasa | `gerar-papel-vivo.py` (escreve os PNG e o `Camadas.js`) |
| `arte/cordel-busto.svg` | ícone do menu da doca (PNG), avatar do login, avatar da Toca e do widget | `gerar-icones.py` (a Toca e o widget usam o SVG direto) |
| `arte/cordel-figura.svg` | figura de corpo inteiro (instalada com a Toca) | — |
| `arte/icones/apps/*.svg` (64 px) | ícones dos apps do KDE no tema de ícones "Curupira" (`tema/icones/Curupira/`) | `gerar-icones.py` (tabela `APPS`: arte → nomes de ícone) |
| `arte/icones/simbolos/*.svg` (22 px, uma cor) | bandeja do sistema e ações dos menus, no mesmo tema | `gerar-icones.py` (tabelas `ESTADO` e `ACOES`) |
| `arte/cenas/*.svg` (720×104) | cena da faixa que abre cada seção da Toca (uma por seção, menos a Energia) | a Toca usa o SVG direto |
| `arte/icones/seres/*.svg` (64 px) | ladrilhos dos seres na Toca (animados) e no cartão rápido do widget | a Toca usa o SVG direto; `gerar-icones.py` copia para o widget |
| paleta (em `gerar-cores.py`) | esquemas Curupira e Curupira Noite, cores do Konsole | `gerar-cores.py` |
| raio/sombra (em `gerar-painel.py`) | fundo arredondado da doca | `gerar-painel.py` |

Limites do motor de SVG do Qt (QtSvg), que o Plasma usa para ícones: **não aplica `clip-path` nem aceita
`<svg>` dentro de `<svg>`** e ignora animações CSS. Por isso o ícone do menu sai em PNG. O Plymouth não lê SVG.
Para novas artes de interface, prefira formas simples, degradês e cores sólidas da paleta.

**Ícones (direção "Brasa na noite", escolhida em 15/11/2026):** ladrilho cor da noite (`#241A4A`, fio `#3A2D6B`,
raio 18 em 64) e o desenho em formas cheias de brasa, urucum, mata e areia. Só os apps do sistema ganham ícone;
os de terceiros ficam com o original (a doca só põe o ladrilho atrás). Os símbolos de uma cor usam traço de 1,8
em 22 px e a tinta `#232629`, que o gerador troca pela cor do texto do tema.
Cada ser em `arte/icones/seres/` tem quatro grupos **sem grupos dentro**: `ladrilho`, `base` (parado), `vivo`
(o que a Toca anima quando o ser está acordado) e `frente` (passa por cima). O movimento de cada um está em
`MOVIMENTOS`, no `sistema/toca/visual.py`. As cenas de `arte/cenas/` usam os mesmos grupos (sem `ladrilho`) e a
tabela `CENAS`.

**Retratos (Brasa e Iara):** o padrão é o do `brasa-fundo.svg`: rosto em planos chapados (base na sombra, plano de
luz por cima), poucos degradês, formas fortes para sobrancelha, pálpebra e boca, fios de luz na borda, cabelo em
mechas com degradê e fios de brilho. O Pablo achou os seres pequenos do Mata Viva (Saci, Boitatá, Mapinguari,
Boto e a Iara da lagoa, em `arte/papel-vivo/`) primitivos perto disso: ao redesenhá-los, siga este padrão.

**Mata Viva (papel de parede animado):** `brasa-fundo.svg` e `iara-fundo.svg` já descrevem em CSS como cada parte se mexe (classes
`f` mechas do cabelo e tudo que gira em torno de um ponto, `lid` pálpebras, `halo`, `sp` faíscas, `ff` vaga-lumes,
`breath`, e `vai` para o que vai e volta devagar: o que boia e a correnteza, com `--dx`/`--dy`). O Plasma não roda esse
CSS, então o gerador recorta cada parte e o `Cena.qml` refaz o movimento. Ao editar a arte, mantenha essas
classes e os estilos `transform-origin`/`animation-*` nelas. Os seres entram em três vagas entre as camadas:
`ceu`, `longe` e `perto`. O que cada ser mostra está no cabeçalho do `Cena.qml`. `main.qml` lê o
`curupira json` e decide se a mata se mexe: fica parada na bateria, no Remanso/Sereno e com uma janela
maximizada por cima (animação contínua gasta energia). Todas as camadas seguem um relógio só (`relogio`, 24 q/s).
Quem usa escolhe o papel de parede na Toca (Aparência), que chama `curupira-papel-vivo`; a miniatura é o
`contents/screenshot.png`, tirado pelo `gerar-tudo.sh` com o `ver-papel-vivo.py`.

**As três artes da Toca**, cada uma com um papel (não misture os papéis ao criar arte nova):
a **paisagem** no pé da barra lateral mostra o perfil de energia (`Paisagem`, desenhada em código, cores em
`PAISAGENS`); a **faixa** cor da noite abre a seção (`Faixa`); o **ser no canto** de baixo é quem está acordado
agora e some quando ninguém está ou quando os cartões chegam até ali (`SerNoCanto`, via `Secao.ser_no_canto`).

## Testar e ver o resultado

- `bash ferramentas/testar-curupira.sh`: testes do `curupira` sem root (simula `/sys`). Rode sempre que mexer nele.
- `python3 sistema/toca/toca.py --captura-todas /tmp/telas/`: um PNG de cada seção da Toca, sem abrir janela.
- Ícone novo aparece? `kiconfinder6 system-file-manager` deve apontar para `/usr/local/share/icons/Curupira/`.
- Widget avulso: `plasmawindowed io.github.pabloherzberg.doca` (ou `.curupira`).
- Papel de parede animado fora do Plasma: `python3 ferramentas/ver-papel-vivo.py --todos` (janela) ou com
  `--captura tela.png` (sem tela); `--estado '{"turbo": true}'` usa os campos do `curupira json`.
- Login sem sair da sessão: `sddm-greeter-qt6 --test-mode --theme tema/sddm/curupira`.
- Tela de bloqueio sem bloquear: `/usr/lib/kscreenlocker_greet --testing` (fundo em `/etc/xdg/kscreenlockerrc`).
- Abertura: `ksplashqml --test --window <pasta do tema global com splash/images preenchida>`.
- Captura de tela: `spectacle -b -n -a -o arquivo.png` (janela ativa) ou `-f` (tela toda).
- Depois de instalar widgets ou ícones novos: `systemctl --user restart plasma-plasmashell`. Para ícones,
  apague antes `~/.cache/icon-cache.kcache` (o Plasma guarda o "não encontrado").

## Cuidados (aprendidos do jeito difícil)

- **Root:** o `sudo` do Claude Code não tem terminal para pedir senha. Use `pkexec <comando>`, que abre a
  janela de senha do KDE. Avise o Pablo antes, porque a janela vai aparecer.
- **Cabeçalho de scripts bash:** em 15/11/2026 uma linha de ajuda sem `#` no cabeçalho do `curupira` virou
  comando, ele chamou a si mesmo sem parar (o widget e o timer recomeçavam) e a memória esgotou. Depois de
  editar scripts, rode `bash -n` e os testes. Há um teste que barra isso.
- **Cópias de teste de widgets** em `~/.local/share/plasma/plasmoids/` têm prioridade sobre as do sistema.
  Apague-as num comando separado logo após o teste.
- **Painel do Pablo:** `curupira-doca` aplica/restaura a doca (também "Restaurar a doca" no menu e na Toca).
  O painel original do KDE está guardado em `~/.config/curupira-painel-anterior` (`curupira-doca --desfazer`).
- **Boot:** a entrada "modo de recuperação" inicia sem Plymouth (`plymouth.enable=0`). O mkinitcpio do Arch
  não gera mais a imagem fallback. A tela de login volta ao padrão apagando `/etc/sddm.conf.d/10-curupira.conf`.
- **Boitatá:** a placa NVIDIA dorme fora do barramento PCI. Para trazê-la de volta não basta o rescan: é preciso
  ligar a porta e reativar o enlace (está no `boitata acordar` do `curupira`; a história está no `NOTAS.md`).
  O `curupira` de teste (`CURUPIRA_TESTE`) não exercita esse caminho: mudanças nele pedem teste de verdade.
  **Não remova a placa do barramento com o nouveau carregado** (`echo 1 > remove`): derruba o kernel e só
  reiniciando conserta. O `boitata dormir` se recusa nesse caso; depois de acordada, ela dorme no reinício.
- **Mapinguari:** qualquer coisa que encoste em `/data` (até `findmnt --fstab /data` ou um `stat`) monta o HD, e
  qualquer comando mandado ao disco (`hdparm -C`, `smartctl`, `dd`) liga o motor. Para observar sem acordar:
  `curupira hd`, `cat /sys/block/sda/device/power/runtime_status` e `journalctl -k | grep 'sda\] St'`.
  Quem para o motor é o kernel, 5 minutos depois do último acesso.
- **Snapper** fica só para o root. A Toca lê por `curupira cuca …`; voltar no tempo é com `curupira-voltar`.
- **Commits:** em português, com corpo explicando o porquê. Só faça commit/push quando o Pablo pedir.

## Onde paramos

Veja "A fazer" no `NOTAS.md`. Estado em 15/11/2026: perfis, Toca (6 seções), Cuca com volta no tempo (testada), tema completo (cores, Konsole, papéis, login, boot,
abertura), doca com ladrilhos, animações e cartão rápido. Ainda não testado num boot completo: boot → login → abertura.
