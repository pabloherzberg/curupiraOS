#!/usr/bin/env python3
"""Gera os esquemas de cores do Plasma e do Konsole da Curupira OS a partir da paleta.

    python3 tema/gerar-cores.py      reescreve tema/cores/*.colors e tema/konsole/*.colorscheme

Paleta (NOTAS.md): #241A4A noite, #D2507A urucum, #FF7A45 brasa, #2BB37A mata, #F4D3A0 areia
quente, #FBF4E8 areia. Os tons de interface vêm do mockup da Toca (mockup/Central.dc.html).
"""

from pathlib import Path

AQUI = Path(__file__).resolve().parent


def rgb(h: str) -> str:
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


# Tons comuns aos dois esquemas
COMUM = {
    "negativo": "#C2410C", "neutro": "#B07A1E", "positivo": "#12935F", "visitado": "#8E3A9E",
}

CLARO = {
    "nome": "Curupira", "id": "Curupira",
    "texto": "#1E2A24", "texto_suave": "#5B6A61",
    "janela": "#FBF4E8", "janela_alt": "#F3EEE4",
    "vista": "#FFFFFF", "vista_alt": "#FBF8F2",
    "botao": "#FFFFFF", "botao_alt": "#EDE4D4",
    "cabecalho": "#F3EBDD", "cabecalho_alt": "#FBF4E8",
    "destaque": "#12935F", "destaque_claro": "#7FE3B0", "link": "#0F7A54",
    "selecao_texto": "#FFFFFF",
    "dica": "#241A4A", "dica_texto": "#FFFFFF",
    "complementar": "#241A4A", "complementar_alt": "#1B1338", "complementar_texto": "#FFFFFF",
    # barra de título: noite, como o cartão de consumo da Toca
    "titulo": "#241A4A", "titulo_texto": "#FFFFFF", "titulo_inativo": "#3E3270", "titulo_inativo_texto": "#C9BFEA",
}

NOITE = {
    "nome": "Curupira Noite", "id": "CurupiraNoite",
    "texto": "#F3EEE4", "texto_suave": "#B9AED6",
    "janela": "#1E1640", "janela_alt": "#191236",
    "vista": "#251B4D", "vista_alt": "#2B2057",
    "botao": "#2E2360", "botao_alt": "#3E3270",
    "cabecalho": "#191236", "cabecalho_alt": "#1E1640",
    "destaque": "#2BB37A", "destaque_claro": "#1E6E4D", "link": "#7FE3B0",
    "selecao_texto": "#FFFFFF",
    "dica": "#FBF4E8", "dica_texto": "#1E2A24",
    "complementar": "#140E2C", "complementar_alt": "#0F0A22", "complementar_texto": "#F3EEE4",
    "titulo": "#140E2C", "titulo_texto": "#FFD08A", "titulo_inativo": "#1E1640", "titulo_inativo_texto": "#8A7FB3",
}


# Encante: o fundo do rio. Verde-petróleo, com o rosa do boto no destaque, a luz viva (ciano) nos links e a
# luz das casas (âmbar) no título das janelas. É o tema do papel de parede animado Encante.
ENCANTE = {
    "nome": "Encante", "id": "Encante",
    "texto": "#E9F7F3", "texto_suave": "#9CC8C6",
    "janela": "#062A38", "janela_alt": "#052230",
    "vista": "#0B3A48", "vista_alt": "#0E4250",
    "botao": "#125565", "botao_alt": "#186472",
    "cabecalho": "#052230", "cabecalho_alt": "#062A38",
    "destaque": "#F08FB5", "destaque_claro": "#B8457A", "link": "#5FE3D9",
    "selecao_texto": "#062A38",
    "dica": "#E9F7F3", "dica_texto": "#062A38",
    "complementar": "#031822", "complementar_alt": "#021119", "complementar_texto": "#E9F7F3",
    "titulo": "#031822", "titulo_texto": "#FFC46B", "titulo_inativo": "#062A38", "titulo_inativo_texto": "#6E9C9C",
}


def grupo(nome: str, fundo: str, fundo_alt: str, texto: str, p: dict, texto_ativo: str | None = None) -> str:
    d = p["destaque"]
    return f"""[{nome}]
BackgroundAlternate={rgb(fundo_alt)}
BackgroundNormal={rgb(fundo)}
DecorationFocus={rgb(d)}
DecorationHover={rgb(d)}
ForegroundActive={rgb(texto_ativo or d)}
ForegroundInactive={rgb(p['texto_suave'] if texto == p['texto'] else texto)}
ForegroundLink={rgb(p['link'])}
ForegroundNegative={rgb(COMUM['negativo'])}
ForegroundNeutral={rgb(COMUM['neutro'])}
ForegroundNormal={rgb(texto)}
ForegroundPositive={rgb(COMUM['positivo'] if p is CLARO else '#7FE3B0')}
ForegroundVisited={rgb(COMUM['visitado'] if p is CLARO else '#F5A3D0')}
"""


def esquema_plasma(p: dict) -> str:
    partes = [f"""# Curupira OS: esquema de cores "{p['nome']}". Gerado por tema/gerar-cores.py; não edite à mão.
[ColorEffects:Disabled]
Color=56,56,56
ColorAmount=0
ColorEffect=0
ContrastAmount=0.65
ContrastEffect=1
IntensityAmount=0.1
IntensityEffect=2

[ColorEffects:Inactive]
ChangeSelectionColor=true
Color=112,111,110
ColorAmount=0.025
ColorEffect=2
ContrastAmount=0.1
ContrastEffect=2
Enable=false
IntensityAmount=0
IntensityEffect=0
"""]
    partes.append(grupo("Colors:Button", p["botao"], p["botao_alt"], p["texto"], p))
    partes.append(grupo("Colors:Complementary", p["complementar"], p["complementar_alt"], p["complementar_texto"], p))
    partes.append(grupo("Colors:Header", p["cabecalho"], p["cabecalho_alt"], p["texto"], p))
    partes.append(grupo("Colors:Header][Inactive", p["cabecalho_alt"], p["cabecalho"], p["texto"], p))
    partes.append(grupo("Colors:Selection", p["destaque"], p["destaque_claro"], p["selecao_texto"], p,
                        texto_ativo=p["selecao_texto"]))
    partes.append(grupo("Colors:Tooltip", p["dica"], p["dica"], p["dica_texto"], p))
    partes.append(grupo("Colors:View", p["vista"], p["vista_alt"], p["texto"], p))
    partes.append(grupo("Colors:Window", p["janela"], p["janela_alt"], p["texto"], p))
    partes.append(f"""[General]
ColorScheme={p['id']}
Name={p['nome']}
shadeSortColumn=true

[KDE]
contrast=4

[WM]
activeBackground={rgb(p['titulo'])}
activeBlend={rgb(p['titulo'])}
activeForeground={rgb(p['titulo_texto'])}
inactiveBackground={rgb(p['titulo_inativo'])}
inactiveBlend={rgb(p['titulo_inativo'])}
inactiveForeground={rgb(p['titulo_inativo_texto'])}
""")
    return "\n".join(partes)


# Konsole: fundo noite, texto areia, cores ANSI tiradas da paleta
KONSOLE = {
    "nome": "Curupira",
    "Background": "#1E1640", "Foreground": "#F3EEE4",
    "Color0": "#2E2360", "Color1": "#E2531F", "Color2": "#2BB37A", "Color3": "#F2D27A",
    "Color4": "#6FB6F2", "Color5": "#D2507A", "Color6": "#7FE3B0", "Color7": "#F3EEE4",
    "Color0Intense": "#5B4E8E", "Color1Intense": "#FF7A45", "Color2Intense": "#7FF5C2", "Color3Intense": "#FFD08A",
    "Color4Intense": "#8FB8F2", "Color5Intense": "#F5A3D0", "Color6Intense": "#B5F2D5", "Color7Intense": "#FFFFFF",
}


KONSOLE_ENCANTE = {
    "nome": "Encante",
    "Background": "#041C28", "Foreground": "#E9F7F3",
    "Color0": "#0B3A48", "Color1": "#FF8A70", "Color2": "#7FE3B0", "Color3": "#FFC46B",
    "Color4": "#6FB6F2", "Color5": "#F08FB5", "Color6": "#5FE3D9", "Color7": "#E9F7F3",
    "Color0Intense": "#1C7C84", "Color1Intense": "#FFA994", "Color2Intense": "#A8F2CE", "Color3Intense": "#FFD896",
    "Color4Intense": "#9CCBF7", "Color5Intense": "#FFB3CF", "Color6Intense": "#9FF0E8", "Color7Intense": "#FFFFFF",
}


def esquema_konsole(k: dict = KONSOLE) -> str:
    nome = k["nome"]
    KONSOLE = {c: v for c, v in k.items() if c != "nome"}
    linhas = ["# Curupira OS: cores do Konsole. Gerado por tema/gerar-cores.py; não edite à mão.",
              "[General]", f"Description={nome}", "Opacity=1", "Wallpaper=", ""]
    for chave, cor in KONSOLE.items():
        linhas += [f"[{chave}]", f"Color={rgb(cor)}", ""]
        if chave in ("Background", "Foreground"):
            linhas += [f"[{chave}Intense]", f"Color={rgb(cor)}", ""]
            linhas += [f"[{chave}Faint]", f"Color={rgb(cor)}", ""]
    for i in range(8):
        linhas += [f"[Color{i}Faint]", f"Color={rgb(KONSOLE[f'Color{i}'])}", ""]
    return "\n".join(linhas)


def main():
    (AQUI / "cores").mkdir(exist_ok=True)
    (AQUI / "konsole").mkdir(exist_ok=True)
    for p in (CLARO, NOITE, ENCANTE):
        (AQUI / "cores" / f"{p['id']}.colors").write_text(esquema_plasma(p))
    (AQUI / "konsole" / "Curupira.colorscheme").write_text(esquema_konsole())
    (AQUI / "konsole" / "Encante.colorscheme").write_text(esquema_konsole(KONSOLE_ENCANTE))
    # o perfil do Encante é o do Curupira com as outras cores
    perfil = (AQUI / "konsole" / "Curupira.profile").read_text()
    perfil = perfil.replace("ColorScheme=Curupira", "ColorScheme=Encante").replace("Name=Curupira", "Name=Encante")
    # o rosa do boto onde se olha: cursor (com a letra embaixo na cor do fundo) e a marca da aba;
    # o bash abre com o encante.bashrc, que pinta prompt, grep e man nas cores do rio
    rosa, fundo = rgb(ENCANTE["destaque"]), rgb(ENCANTE["janela"])
    perfil = perfil.replace("[Appearance]\n", f"[Appearance]\nTabColor={rosa}\n", 1)
    perfil = perfil.replace("[General]\n", "[General]\nCommand=/bin/bash --rcfile /usr/local/share/curupira/encante.bashrc\n", 1)
    perfil += f"\n[Cursor Options]\nCursorShape=1\nUseCustomCursorColor=true\nCustomCursorColor={rosa}\nCustomCursorTextColor={fundo}\n"
    (AQUI / "konsole" / "Encante.profile").write_text(perfil)
    print("Esquemas gerados em tema/cores e tema/konsole.")


if __name__ == "__main__":
    main()
