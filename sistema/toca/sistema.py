"""Leitura do sistema para a Toca do Curupira.

Tudo aqui roda fora da interface (numa thread) e não depende do Qt. Cada função
devolve dados simples; um valor None significa "não deu para saber".
"""

from __future__ import annotations

import grp
import json
import os
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REDE_LAB = "curupira-lab"


def roda(*cmd: str, tempo: float = 5) -> subprocess.CompletedProcess | None:
    if not shutil.which(cmd[0]) and not Path(cmd[0]).exists():
        return None
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=tempo)
    except (OSError, subprocess.TimeoutExpired):
        return None


def saida(*cmd: str, tempo: float = 5) -> str | None:
    r = roda(*cmd, tempo=tempo)
    return r.stdout if r and r.returncode == 0 else None


def lanca(*cmd: str) -> bool:
    """Abre um programa sem esperar por ele."""
    if not shutil.which(cmd[0]):
        return False
    subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    return True


def comando_curupira() -> str:
    if os.environ.get("CURUPIRA_BIN"):
        return os.environ["CURUPIRA_BIN"]
    local = AQUI.parent / "bin" / "curupira"
    if os.environ.get("CURUPIRA_TESTE") and local.exists():
        return str(local)
    return shutil.which("curupira") or "/usr/local/bin/curupira"


def ultima_linha(r: subprocess.CompletedProcess | None, padrao: str = "Falhou.") -> str:
    if r is None:
        return "Não consegui rodar o comando."
    texto = (r.stderr or r.stdout or "").strip()
    return texto.splitlines()[-1] if texto else padrao


# ------------------------------------------------------------------ energia e seres da seção Energia
def energia() -> dict:
    """Estado do comando curupira (perfil, bateria, watts, Caipora)."""
    texto = saida(comando_curupira(), "json")
    if texto is None:
        return {"_erro": "O comando curupira não respondeu. Ele está instalado?"}
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return {"_erro": "Não entendi a resposta do comando curupira."}


def turbo() -> bool | None:
    try:
        return Path("/sys/devices/system/cpu/intel_pstate/no_turbo").read_text().strip() == "0"
    except OSError:
        return None


def hd_acordado() -> bool | None:
    texto = saida("findmnt", "-no", "FSTYPE", "/data")
    if texto is None:
        return None
    montado = any(t != "autofs" for t in texto.split())
    # acordado = motor girando: o kernel para o disco sozinho, mesmo com o /data montado (ler isto não o acorda)
    disco = _hd_disco()
    if disco:
        try:
            estado = open(f"/sys/block/{disco}/device/power/runtime_status").read().strip()
        except OSError:
            estado = ""
        if estado == "suspended":
            return False
        if estado in ("active", "suspending", "resuming"):
            return True
    return montado


def _hd_disco() -> str | None:
    """O disco inteiro ("sda") onde mora o /data, lendo o fstab sem encostar na pasta."""
    try:
        linhas = open("/etc/fstab").read().splitlines()
    except OSError:
        return None
    for linha in linhas:
        campos = linha.split()
        if len(campos) < 2 or campos[0].startswith("#") or campos[1] != "/data":
            continue
        fonte = campos[0]
        for prefixo, pasta in (("UUID=", "by-uuid"), ("LABEL=", "by-label"), ("PARTUUID=", "by-partuuid")):
            if fonte.startswith(prefixo):
                fonte = f"/dev/disk/{pasta}/{fonte[len(prefixo):]}"
        nome = os.path.basename(os.path.realpath(fonte))
        no_sys = os.path.realpath(f"/sys/class/block/{nome}")
        if os.path.exists(os.path.join(no_sys, "partition")):
            nome = os.path.basename(os.path.dirname(no_sys))
        return nome if os.path.isdir(f"/sys/block/{nome}") else None
    return None


def wifi() -> tuple[bool | None, str]:
    texto = saida("nmcli", "-t", "-f", "WIFI", "radio")
    if texto is None:
        return None, ""
    ligado = texto.strip() in ("enabled", "habilitado")
    rede = ""
    ativas = saida("nmcli", "-t", "-f", "NAME,TYPE", "connection", "show", "--active") or ""
    for linha in ativas.splitlines():
        nome, _, tipo = linha.rpartition(":")
        if tipo == "802-11-wireless" and nome:
            rede = nome.replace("\\:", ":")
            break
    return ligado, rede


def bluetooth() -> bool | None:
    texto = saida("bluetoothctl", "show")
    if not texto or "Powered:" not in texto:
        return None
    return "Powered: yes" in texto


def boitata_dormindo() -> bool:
    """Dormindo = a placa NVIDIA não está no barramento PCI (a regra do udev a remove até alguém acordá-la)."""
    for vendedor in Path("/sys/bus/pci/devices").glob("*/vendor"):
        try:
            if vendedor.read_text().strip() == "0x10de":
                return False
        except OSError:
            pass
    return True


def microfone_mudo() -> bool | None:
    texto = saida("wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@")
    if texto is None:
        return None
    return "MUTED" in texto


def lab() -> dict | None:
    """Rede isolada do Boto (Podman). None se não existe."""
    texto = saida("podman", "network", "inspect", REDE_LAB, tempo=10)
    if not texto:
        return None
    try:
        dados = json.loads(texto)
        info = dados[0] if isinstance(dados, list) and dados else {}
    except json.JSONDecodeError:
        info = {}
    subredes = [s.get("subnet", "") for s in info.get("subnets", []) if isinstance(s, dict)]
    return {"subrede": ", ".join(x for x in subredes if x), "interna": bool(info.get("internal"))}


def resumo_energia() -> dict:
    """Tudo que a seção Energia mostra."""
    ligado, rede = wifi()
    return {
        "energia": energia(),
        "turbo": turbo(),
        "hd": hd_acordado(),
        "wifi": ligado,
        "wifi_rede": rede,
        "bluetooth": bluetooth(),
        "boitata_dormindo": boitata_dormindo(),
        "microfone_mudo": microfone_mudo(),
        "lab": lab(),
    }


# ------------------------------------------------------------------ Caipora
def apps_microfone() -> list[str]:
    texto = saida("pactl", "-f", "json", "list", "source-outputs")
    if not texto:
        return []
    try:
        saidas = json.loads(texto)
    except json.JSONDecodeError:
        return []
    nomes = []
    for s in saidas:
        props = s.get("properties", {})
        nome = props.get("application.name") or props.get("application.process.binary") or "programa sem nome"
        if nome not in nomes:
            nomes.append(nome)
    return nomes


def apps_camera() -> list[str]:
    """Programas (do próprio usuário) com a câmera aberta, olhando os descritores em /proc."""
    nomes: list[str] = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        fd_dir = f"/proc/{pid}/fd"
        try:
            for fd in os.listdir(fd_dir):
                try:
                    alvo = os.readlink(f"{fd_dir}/{fd}")
                except OSError:
                    continue
                if alvo.startswith("/dev/video"):
                    nome = Path(f"/proc/{pid}/comm").read_text().strip()
                    if nome not in nomes:
                        nomes.append(nome)
                    break
        except OSError:
            continue
    return nomes


def camera_presente() -> bool:
    return any(Path("/sys/class/video4linux").glob("video*")) or Path("/sys/bus/usb/drivers/uvcvideo").exists()


def privacidade() -> dict:
    en = energia()
    return {
        "camera_cortada": en.get("camera_cortada"),
        "mac_aleatorio": en.get("mac_aleatorio"),
        "camera_presente": camera_presente(),
        "microfone_mudo": microfone_mudo(),
        "apps_microfone": apps_microfone(),
        "apps_camera": apps_camera(),
        "_erro": en.get("_erro", ""),
    }


# ------------------------------------------------------------------ rede
def rede() -> dict:
    d: dict = {}
    ligado, nome = wifi()
    d["wifi"], d["wifi_rede"], d["bluetooth"] = ligado, nome, bluetooth()

    dispositivos = saida("nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device") or ""
    conectado = None
    for linha in dispositivos.splitlines():
        partes = linha.split(":")
        if len(partes) >= 4 and partes[1] in ("wifi", "ethernet") and partes[2].startswith(("connected", "conectado")):
            conectado = {"dispositivo": partes[0], "tipo": partes[1], "conexao": ":".join(partes[3:])}
            break
    d["conectado"] = conectado

    if conectado:
        dev = conectado["dispositivo"]
        if conectado["tipo"] == "wifi":
            lista = saida("nmcli", "-t", "-f", "IN-USE,SIGNAL,SSID,SECURITY", "dev", "wifi", "list", "--rescan", "no") or ""
            for linha in lista.splitlines():
                if linha.startswith("*"):
                    _, sinal, *resto = linha.split(":")
                    d["sinal"] = int(sinal) if sinal.isdigit() else None
                    d["seguranca"] = resto[-1] if resto else ""
                    break
        enderecos = saida("ip", "-j", "addr", "show", "dev", dev)
        try:
            info = json.loads(enderecos)[0] if enderecos else {}
        except (json.JSONDecodeError, IndexError):
            info = {}
        d["ipv4"] = [f"{a['local']}/{a['prefixlen']}" for a in info.get("addr_info", []) if a.get("family") == "inet"]
        d["ipv6"] = [a["local"] for a in info.get("addr_info", [])
                     if a.get("family") == "inet6" and a.get("scope") == "global"]
        d["mac"] = info.get("address", "")
        rotas = saida("ip", "-j", "route", "show", "default", "dev", dev)
        try:
            d["gateway"] = json.loads(rotas)[0].get("gateway", "") if rotas else ""
        except (json.JSONDecodeError, IndexError):
            d["gateway"] = ""
        dns = saida("nmcli", "-t", "-f", "IP4.DNS,IP6.DNS", "dev", "show", dev) or ""
        d["dns"] = [l.split(":", 1)[1] for l in dns.splitlines() if ":" in l and l.split(":", 1)[1]]

    d["mac_aleatorio"] = energia().get("mac_aleatorio")
    d["lab"] = lab()
    d["podman"] = shutil.which("podman") is not None
    d["ferramentas"] = {f: shutil.which(f) is not None for f in ("wireshark", "mitmproxy", "nmap", "tcpdump", "konsole")}
    try:
        d["grupo_wireshark"] = grp.getgrnam("wireshark").gr_gid in os.getgroups()
    except KeyError:
        d["grupo_wireshark"] = False
    return d


# ------------------------------------------------------------------ Cuca (snapper)
def snapshots() -> dict:
    """Lista pelo "curupira cuca lista" (o snapper só responde ao root; o polkit libera esse comando)."""
    r = roda(comando_curupira(), "cuca", "lista", tempo=30)
    if r is None:
        return {"_erro": "O comando curupira não respondeu. Ele está instalado?"}
    if r.returncode in (126, 127):
        return {"_erro": "A Toca não recebeu permissão para ler os snapshots."}
    if r.returncode != 0:
        return {"_erro": ultima_linha(r)}
    try:
        dados = json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"_erro": "Não entendi a resposta do snapper."}
    lista = dados.get("root", []) if isinstance(dados, dict) else []
    agora = time.time()
    itens = []
    for s in lista:
        if s.get("number") == 0:
            continue
        try:
            quando = datetime.strptime(s.get("date", ""), "%Y-%m-%d %H:%M:%S").timestamp()
        except ValueError:
            quando = agora
        itens.append({
            "numero": s.get("number"),
            "tipo": s.get("type", "single"),
            "pre": s.get("pre-number"),
            "data": s.get("date", ""),
            "idade": agora - quando,
            "descricao": s.get("description", "") or "",
            "limpeza": s.get("cleanup", "") or "",
            "userdata": s.get("userdata") or {},
        })
    return {"itens": itens}


def conta_mudancas(texto: str) -> dict:
    """Resume a saída de "snapper status A..B" (primeira coluna: + criado, - apagado, c alterado).
    "kernel" diz se algum módulo do kernel mudou (aí não dá para voltar sem quebrar o boot)."""
    c = {"criados": 0, "apagados": 0, "alterados": 0, "kernel": False}
    for linha in texto.splitlines():
        if not linha.strip():
            continue
        partes = linha.split(maxsplit=1)
        if len(partes) == 2 and partes[1].startswith("/usr/lib/modules/"):
            c["kernel"] = True
        marca = linha[0]
        if marca == "+":
            c["criados"] += 1
        elif marca == "-":
            c["apagados"] += 1
        else:
            c["alterados"] += 1
    return c


def previa(antes: int, depois: int) -> dict:
    """O que muda entre dois snapshots (depois=0 é o sistema atual)."""
    r = roda(comando_curupira(), "cuca", "mudancas", str(antes), str(depois), tempo=180)
    if r is None or r.returncode != 0:
        return {"_erro": ultima_linha(r, "Não consegui comparar os snapshots.")}
    return conta_mudancas(r.stdout)


def comando_voltar() -> str:
    local = AQUI.parent / "bin" / "curupira-voltar"
    if os.environ.get("CURUPIRA_TESTE") and local.exists():
        return str(local)
    return shutil.which("curupira-voltar") or "/usr/local/bin/curupira-voltar"


# ------------------------------------------------------------------ aparência
# (arte para a miniatura, nome, pacote do Plasma instalado pelo instalar.sh)
PAPEIS = [
    ("brasa-fundo.svg", "Brasa", "Curupira-Brasa"),
    ("iara-fundo.svg", "Iara", "Curupira-Iara"),
    ("papel-de-parede-entardecer.svg", "Entardecer", "Curupira-Entardecer"),
]
DIR_PAPEIS = Path("/usr/local/share/wallpapers")
# o papel de parede animado (plugin do Plasma, tema/papel-vivo); a Toca aplica com o curupira-papel-vivo
PAPEL_VIVO = "io.github.pabloherzberg.mataviva"
MOVIMENTOS_DO_PAPEL = ["tomada", "sempre", "parado"]    # na ordem do ajuste "Movimento" do plugin (0, 1, 2)
# cenas do papel de parede animado, na ordem do ajuste "Cena": (chave, nome na Toca, miniatura)
CENAS_DO_PAPEL = [("brasa", "Mata Viva", "screenshot.png"), ("iara", "Iara Viva", "screenshot-iara.png")]


def previa_papel_vivo(arquivo: str = "screenshot.png") -> Path | None:
    """A miniatura de uma cena do Mata Viva: do pacote instalado ou, no repositório, da pasta do tema."""
    for base in (Path("/usr/share/plasma/wallpapers"), Path(__file__).resolve().parent.parent.parent / "tema" / "papel-vivo"):
        p = base / PAPEL_VIVO / "contents" / arquivo
        if p.exists():
            return p
    return None


def papel_vivo_instalado() -> bool:
    return (Path("/usr/share/plasma/wallpapers") / PAPEL_VIVO / "metadata.json").exists()
ESQUEMAS = [("Curupira", "Curupira"), ("CurupiraNoite", "Curupira Noite")]


def esquemas_curupira() -> bool:
    return all((Path(d) / "color-schemes" / f"{e}.colors").exists() or
               (Path.home() / ".local/share/color-schemes" / f"{e}.colors").exists()
               for e, _ in ESQUEMAS for d in ["/usr/local/share"])


def caminho_papel(arte_svg: Path, pacote: str) -> str:
    """O pacote instalado (PNG em vários tamanhos) se existir; senão, a arte em SVG."""
    p = DIR_PAPEIS / pacote
    return str(p) if (p / "metadata.json").exists() else str(arte_svg)
CORES_DESTAQUE = [
    ("#2BB37A", "Mata"),
    ("#FF7A45", "Brasa"),
    ("#D2507A", "Urucum"),
    ("#2468B8", "Rio"),
    ("#5B3A8E", "Noite"),
    ("#3DAEE9", "Azul do Plasma"),
]


def aparencia() -> dict:
    esquema = (saida("kreadconfig6", "--file", "kdeglobals", "--group", "General", "--key", "ColorScheme") or "").strip()
    destaque = (saida("kreadconfig6", "--file", "kdeglobals", "--group", "General", "--key", "AccentColor") or "").strip()
    cor = ""
    partes = destaque.split(",")
    if len(partes) >= 3 and all(p.strip().isdigit() for p in partes[:3]):
        cor = "#{:02X}{:02X}{:02X}".format(*(int(p) for p in partes[:3]))
    papel, plugin, movimento, cena, grupo = "", "", 0, 0, ""
    cfg = Path.home() / ".config/plasma-org.kde.plasma.desktop-appletsrc"
    try:
        for linha in cfg.read_text().splitlines():
            if linha.startswith("["):
                grupo = linha
            elif linha.startswith("Image=") and not papel:
                papel = linha.split("=", 1)[1].removeprefix("file://")
            elif linha.startswith("wallpaperplugin=") and not plugin:
                plugin = linha.split("=", 1)[1].strip()
            elif linha.startswith("Movimento=") and PAPEL_VIVO in grupo:
                movimento = int(linha.split("=", 1)[1]) if linha.split("=", 1)[1].strip().isdigit() else 0
            elif linha.startswith("Cena=") and PAPEL_VIVO in grupo:
                cena = int(linha.split("=", 1)[1]) if linha.split("=", 1)[1].strip().isdigit() else 0
    except OSError:
        pass
    return {"esquema": esquema, "escuro": any(x in esquema.lower() for x in ("dark", "noite")),
            "destaque": cor, "papel": papel, "curupira": esquemas_curupira(),
            "papel_vivo": plugin == PAPEL_VIVO, "papel_vivo_instalado": papel_vivo_instalado(),
            "movimento": MOVIMENTOS_DO_PAPEL[movimento] if 0 <= movimento < 3 else "tomada",
            "cena": CENAS_DO_PAPEL[cena][0] if 0 <= cena < len(CENAS_DO_PAPEL) else "brasa"}
