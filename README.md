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
   curl -fsSL https://raw.githubusercontent.com/SEU_USUARIO/curupira-os/main/install.sh -o install.sh
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

- Comando `curupira` com os perfis Pororoca, Correnteza, Remanso e Sereno.
- Central de controle "Toca do Curupira".
- Tema do Plasma, da tela de login e do boot.
