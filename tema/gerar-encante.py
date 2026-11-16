#!/usr/bin/env python3
"""Gera o papel de parede animado "Encante": a cidade dos botos, suspensa na mata alagada do rio.

    python3 tema/gerar-encante.py

Aqui o desenho não vem de um SVG feito à mão: ele é este programa. Mexeu na arte, rode de novo. Sai:
  arte/encante-fundo.svg                                        o desenho inteiro, parado (gerado; não edite)
  tema/papel-vivo/…mataviva/contents/images/encante/*.png       cada camada, aparada até o que tem desenho
  tema/papel-vivo/…mataviva/contents/ui/EncanteRecortes.js      onde cada camada aparada fica na cena
  tema/papel-vivo/…mataviva/contents/ui/encante/*.qsb           os programas da placa de vídeo (de tema/papel-vivo/encante/)
  tema/papel-vivo/…mataviva/contents/screenshot-encante.png     a miniatura que a Toca mostra

A cidade é de quem nada: não tem chão, rua nem porta. As casas são cabaças e búzios presos aos troncos
da mata alagada, com bocas acesas em qualquer altura; torres sobem do escuro; as "ruas" são correntes de
luzes vivas. A água é a do Amazonas: turva e alaranjada ao longe, verde-azulada perto.

Só formas, degradês e opacidade: nada de filtro nem clip-path, que o QtSvg não desenha.
camada("nome") diz a que peça da animação pertence o que vem depois; as "parado-*" só existem no desenho
parado (na animação, quem as desenha e move é o Encante.qml). Precisa do qsb (pacote qt6-shadertools).
"""
import json
import math
import os
import random
import shutil
import subprocess
from pathlib import Path

R = random.Random(23)
W, H = 1366, 768
PARTES = []          # (camada, texto), na ordem do desenho
CAMADA = ["cabecalho"]


def A(texto, camada=None):
    PARTES.append((camada or CAMADA[0], texto))


def camada(nome):
    """Daqui em diante o desenho pertence a esta camada (para exportar as peças da animação)."""
    CAMADA[0] = nome


camada("defs")
A('''<defs>
<linearGradient id="agua" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#7FD6B4"/><stop offset=".13" stop-color="#2A9A93"/>
 <stop offset=".42" stop-color="#0F5C68"/><stop offset=".76" stop-color="#072E3C"/><stop offset="1" stop-color="#03141D"/></linearGradient>
<radialGradient id="barro" cx="800" cy="400" r="600" gradientUnits="userSpaceOnUse" gradientTransform="translate(0 130) scale(1 .68)">
 <stop offset="0" stop-color="#F2A458" stop-opacity=".66"/><stop offset=".38" stop-color="#C9773A" stop-opacity=".36"/>
 <stop offset=".72" stop-color="#8A5A3A" stop-opacity=".12"/><stop offset="1" stop-color="#8A5A3A" stop-opacity="0"/></radialGradient>
<linearGradient id="abismo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#03141D" stop-opacity="0"/><stop offset=".55" stop-color="#03141D" stop-opacity=".62"/><stop offset="1" stop-color="#020C12" stop-opacity=".96"/></linearGradient>
<linearGradient id="troncoLonge" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B9814C"/><stop offset="1" stop-color="#6A4630"/></linearGradient>
<linearGradient id="casaLonge" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A9703F"/><stop offset="1" stop-color="#6A4630"/></linearGradient>
<linearGradient id="casaMeio" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1C7379"/><stop offset="1" stop-color="#0A4350"/></linearGradient>
<linearGradient id="casaPerto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0F505B"/><stop offset="1" stop-color="#052B38"/></linearGradient>
<radialGradient id="boca" cx=".5" cy=".42" r=".6"><stop offset="0" stop-color="#FFF6DA"/><stop offset=".6" stop-color="#FFC46B"/><stop offset="1" stop-color="#E58A3C"/></radialGradient>
<radialGradient id="sol" cx="560" cy="-40" r="700" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#FAFFF4" stop-opacity="1"/><stop offset=".14" stop-color="#C9F8E6" stop-opacity=".62"/>
 <stop offset=".45" stop-color="#5FE3D9" stop-opacity=".18"/><stop offset="1" stop-color="#5FE3D9" stop-opacity="0"/></radialGradient>
<linearGradient id="raio" x1="0" y1="0" x2="0" y2="690" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#F2FFF6" stop-opacity=".40"/><stop offset=".5" stop-color="#A8F2DF" stop-opacity=".12"/>
 <stop offset="1" stop-color="#A8F2DF" stop-opacity="0"/></linearGradient>
<radialGradient id="cidadeHalo" cx="930" cy="470" r="520" gradientUnits="userSpaceOnUse">
 <stop offset="0" stop-color="#FFD58A" stop-opacity=".62"/><stop offset=".3" stop-color="#FFB37A" stop-opacity=".26"/>
 <stop offset=".6" stop-color="#F08FB5" stop-opacity=".10"/><stop offset="1" stop-color="#F08FB5" stop-opacity="0"/></radialGradient>
<linearGradient id="nevoa" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#229A97" stop-opacity="0"/><stop offset=".7" stop-color="#1A7C82" stop-opacity=".55"/>
 <stop offset="1" stop-color="#1A7C82" stop-opacity=".0"/></linearGradient>
<linearGradient id="paredao" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1F8689" stop-opacity=".0"/><stop offset=".35" stop-color="#17727A" stop-opacity=".8"/><stop offset="1" stop-color="#0E5562"/></linearGradient>
<linearGradient id="areia1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1D7478"/><stop offset="1" stop-color="#0C4552"/></linearGradient>
<linearGradient id="areia2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#115560"/><stop offset="1" stop-color="#062C3A"/></linearGradient>
<linearGradient id="areia3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#083443"/><stop offset="1" stop-color="#031822"/></linearGradient>
<linearGradient id="predio" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#136069"/><stop offset="1" stop-color="#083A47"/></linearGradient>
<linearGradient id="predioPerto" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0D4A56"/><stop offset="1" stop-color="#052B38"/></linearGradient>
<linearGradient id="boto" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#FFC4D9"/><stop offset=".42" stop-color="#F08FB5"/><stop offset=".82" stop-color="#C95588"/><stop offset="1" stop-color="#A63B72"/></linearGradient>
<linearGradient id="botoLuz" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF0F5" stop-opacity=".85"/><stop offset="1" stop-color="#FFD0E0" stop-opacity="0"/></linearGradient>
<linearGradient id="botoBarriga" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE3EC" stop-opacity="0"/><stop offset="1" stop-color="#FFDCE8" stop-opacity=".55"/></linearGradient>
<linearGradient id="nadadeira" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7A3C2"/><stop offset="1" stop-color="#B8457A"/></linearGradient>
<radialGradient id="botoHalo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFB3CF" stop-opacity=".36"/><stop offset="1" stop-color="#F08FB5" stop-opacity="0"/></radialGradient>
<radialGradient id="bio" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#D9FFF8" stop-opacity=".95"/><stop offset=".22" stop-color="#5FE3D9" stop-opacity=".5"/><stop offset="1" stop-color="#5FE3D9" stop-opacity="0"/></radialGradient>
<radialGradient id="janela" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFEDC2" stop-opacity=".95"/><stop offset=".3" stop-color="#FFC46B" stop-opacity=".5"/><stop offset="1" stop-color="#FFC46B" stop-opacity="0"/></radialGradient>
<linearGradient id="portal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF4D2"/><stop offset="1" stop-color="#FFB85A"/></linearGradient>
<radialGradient id="chaoLuz" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFD58A" stop-opacity=".55"/><stop offset="1" stop-color="#FFC46B" stop-opacity="0"/></radialGradient>
<radialGradient id="vinheta" cx=".5" cy=".42" r=".78"><stop offset=".6" stop-color="#020E16" stop-opacity="0"/><stop offset="1" stop-color="#020E16" stop-opacity=".62"/></radialGradient>
</defs>''')


# ------------------------------------------------------------------ água do rio, o barro ao longe e a luz de cima
camada("fundo")
A('<g class="camada-agua">')
A(f'<rect width="{W}" height="{H}" fill="url(#agua)"/>')
A(f'<rect width="{W}" height="{H}" fill="url(#barro)"/>')
A(f'<rect width="{W}" height="{H}" fill="url(#sol)"/>')


def onda(y, amp, per, fase):
    pts = [f"{x},{y + amp * math.sin(x / per + fase):.1f}" for x in range(-200, W + 240, 40)]
    return "M-200,0 L" + " L".join(pts) + f" L{W + 200},0 Z"


A(f'<path class="superficie" d="{onda(30, 8, 74, .4)}" fill="#EFFFE8" opacity=".24"/>', "superficie-0")
A(f'<path class="superficie" d="{onda(17, 6, 48, 1.9)}" fill="#F8FFF0" opacity=".38"/>', "superficie-1")
A(f'<path class="superficie" d="{onda(8, 3, 30, 3.1)}" fill="#FFFFFF" opacity=".55"/>', "superficie-2")
ox, oy = 560, -70
n_raio = 0
for ang, larg, op in [(-44, 4, .4), (-35, 7, .7), (-25, 5, .5), (-17, 11, .95), (-6, 6, .6), (2, 14, 1), (13, 6, .65),
                      (21, 10, .85), (31, 5, .5), (39, 8, .6), (50, 4, .35)]:
    a1, a2 = math.radians(90 + ang - larg / 2), math.radians(90 + ang + larg / 2)
    L = 980
    n_raio += 1
    A(f'<polygon class="raio" points="{ox - 10},{oy} {ox + 10},{oy} {ox + L * math.cos(a2):.0f},{oy + L * math.sin(a2):.0f} '
      f'{ox + L * math.cos(a1):.0f},{oy + L * math.sin(a1):.0f}" fill="url(#raio)" opacity="{op}"/>', "parado-raios")
A('</g>')

LUZES = []      # (x, y, raio, grupo): desenhadas no fim de cada camada; o grupo decide o ritmo do cintilar


def tronco(x0, x1, larg, fill, op=1.0, barriga=0.0, luz=None):
    """Tronco da mata alagada: desce de cima da tela até sumir embaixo."""
    xm = (x0 + x1) / 2 + barriga
    e = f"M{x0 - larg / 2:.0f},-20 C{xm - larg * .42:.0f},240 {xm - larg * .55:.0f},520 {x1 - larg * .6:.0f},800"
    d = f"L{x1 + larg * .6:.0f},800 C{xm + larg * .55:.0f},520 {xm + larg * .42:.0f},240 {x0 + larg / 2:.0f},-20 Z"
    s = f'<path d="{e} {d}" fill="{fill}" opacity="{op}"/>'
    if luz:
        s += f'<path d="{e}" fill="none" stroke="{luz}" stroke-width="{max(1.2, larg * .035):.1f}" opacity="{.5 * op:.2f}"/>'
    return s


def cabaca(x, y, w, h, fill, grupo, op=1.0, luz="#9FF0DD", boca=True, bico=True, nervuras=2, pescoco=False, enfeite=False, franja=False):
    """Casa de cabaça: bojuda, com bico embaixo e a boca redonda acesa, por onde se entra nadando.
    pescoco: cabaça de dois bojos; enfeite: faixa trançada e janelinhas; franja: algas pendendo do bico."""
    topo, pe = y - h / 2, y + h / 2
    pre = f'<path d="M{x:.0f},{topo + 4:.0f} L{x:.0f},{topo - h * .16:.0f}" stroke="#052B38" stroke-width="{max(2, w * .05):.1f}" stroke-linecap="round" opacity="{op}"/>'
    if pescoco:      # o bojo pequeno de cima
        cw, ch, cy = w * .46, h * .4, topo - h * .1
        pre += (f'<path d="M{x:.0f},{cy - ch / 2:.0f} C{x + cw * .7:.0f},{cy - ch / 2:.0f} {x + cw * .7:.0f},{cy + ch / 2:.0f} {x:.0f},{cy + ch / 2:.0f} '
                f'C{x - cw * .7:.0f},{cy + ch / 2:.0f} {x - cw * .7:.0f},{cy - ch / 2:.0f} {x:.0f},{cy - ch / 2:.0f} Z" fill="{fill}" opacity="{op}"/>')
        if luz:
            pre += (f'<path d="M{x - cw * .5:.0f},{cy:.0f} C{x - cw * .5:.0f},{cy - ch * .4:.0f} {x - cw * .2:.0f},{cy - ch / 2 + 1:.0f} {x:.0f},{cy - ch / 2 + 1:.0f}" fill="none" '
                    f'stroke="{luz}" stroke-width="1.6" stroke-linecap="round" opacity="{.6 * op:.2f}"/>')
        pre += f'<circle cx="{x:.0f}" cy="{cy:.0f}" r="{cw * .16:.1f}" fill="url(#boca)" opacity="{op}"/>'
        LUZES.append((x, cy, cw * .5, grupo + 1))
    d = (f"M{x:.0f},{topo:.0f} C{x + w * .34:.0f},{topo:.0f} {x + w * .62:.0f},{y - h * .12:.0f} {x + w * .5:.0f},{y + h * .16:.0f} "
         f"C{x + w * .4:.0f},{y + h * .38:.0f} {x + w * .12:.0f},{pe - h * .06:.0f} {x:.0f},{pe + (h * .16 if bico else 0):.0f} "
         f"C{x - w * .12:.0f},{pe - h * .06:.0f} {x - w * .4:.0f},{y + h * .38:.0f} {x - w * .5:.0f},{y + h * .16:.0f} "
         f"C{x - w * .62:.0f},{y - h * .12:.0f} {x - w * .34:.0f},{topo:.0f} {x:.0f},{topo:.0f} Z")
    s = pre + f'<path d="{d}" fill="{fill}" opacity="{op}"/>'
    for i in range(nervuras):
        k = (i + 1) / (nervuras + 1) - .5
        s += f'<path d="M{x:.0f},{topo + 2:.0f} Q{x + w * k * 1.5:.0f},{y:.0f} {x + w * k * .3:.0f},{pe:.0f}" fill="none" stroke="#03141D" stroke-width="1.2" opacity="{.28 * op:.2f}"/>'
    if luz:     # a luz de cima pega o ombro esquerdo
        s += (f'<path d="M{x - w * .5:.0f},{y + h * .1:.0f} C{x - w * .6:.0f},{y - h * .14:.0f} {x - w * .33:.0f},{topo + 1:.0f} {x:.0f},{topo + 1:.0f}" '
              f'fill="none" stroke="{luz}" stroke-width="{max(1.2, w * .03):.1f}" stroke-linecap="round" opacity="{.6 * op:.2f}"/>')
    if op >= 1:   # casas de perto: plano de sombra na metade de baixo, para dar volume
        s += (f'<path d="M{x + w * .5:.0f},{y + h * .16:.0f} C{x + w * .4:.0f},{y + h * .38:.0f} {x + w * .12:.0f},{pe - h * .06:.0f} {x:.0f},{pe + (h * .16 if bico else 0):.0f} '
              f'C{x - w * .12:.0f},{pe - h * .06:.0f} {x - w * .4:.0f},{y + h * .38:.0f} {x - w * .5:.0f},{y + h * .16:.0f} C{x - w * .2:.0f},{y + h * .3:.0f} {x + w * .2:.0f},{y + h * .3:.0f} {x + w * .5:.0f},{y + h * .16:.0f} Z" fill="#03141D" opacity=".35"/>')
    if enfeite:      # faixa trançada, como cestaria, e duas janelinhas
        fy, meia, n = y + h * .27, w * .37, 9
        zig = " ".join(f"{x - meia + 2 * meia * i / n:.0f},{fy + (h * .035 if i % 2 else -h * .035) - abs(i - n / 2) * h * .012:.0f}" for i in range(n + 1))
        s += f'<polyline points="{zig}" fill="none" stroke="#7FE8DA" stroke-width="{max(1.2, w * .014):.1f}" stroke-linejoin="round" opacity=".42"/>'
        for dy in (-h * .075, h * .075):
            s += f'<path d="M{x - meia * 1.02:.0f},{fy + dy - h * .03:.0f} Q{x:.0f},{fy + dy + h * .03:.0f} {x + meia * 1.02:.0f},{fy + dy - h * .03:.0f}" fill="none" stroke="#7FE8DA" stroke-width="1.1" opacity=".3"/>'
        for lado in (-1, 1):
            jx, jy = x + lado * w * .3, y - h * .12
            s += f'<ellipse cx="{jx:.0f}" cy="{jy:.0f}" rx="{w * .035:.1f}" ry="{w * .05:.1f}" fill="#FFF2CF" opacity="{op}"/>'
            LUZES.append((jx, jy, w * .13, grupo + 2))
    if franja:
        for i in range(4):
            A(folha(x + (i - 1.5) * w * .06, pe + h * .08, -R.uniform(h * .18, h * .42), R.uniform(-10, 10), R.uniform(4, 7), "#12776A", .85), "algas")
    if boca:
        r = w * .2
        by = y + h * .02
        s += f'<circle cx="{x:.0f}" cy="{by:.0f}" r="{r * 1.28:.1f}" fill="#03141D" opacity="{.45 * op:.2f}"/>'
        s += f'<circle cx="{x:.0f}" cy="{by:.0f}" r="{r:.1f}" fill="url(#boca)" opacity="{op}"/>'
        if enfeite:
            s += f'<circle cx="{x:.0f}" cy="{by:.0f}" r="{r * 1.14:.1f}" fill="none" stroke="#FFE7B0" stroke-width="{max(1.2, w * .016):.1f}" opacity=".55"/>'
            # o beiço de baixo da boca, pegando a luz de dentro, e um lampião pendurado nela
            s += (f'<path d="M{x - r * 1.2:.1f},{by + r * .62:.1f} Q{x:.1f},{by + r * 1.95:.1f} {x + r * 1.2:.1f},{by + r * .62:.1f} '
                  f'Q{x:.1f},{by + r * 1.45:.1f} {x - r * 1.2:.1f},{by + r * .62:.1f} Z" fill="#FFC46B" opacity=".55"/>')
            s += f'<path d="M{x:.1f},{by - r * .98:.1f} L{x:.1f},{by - r * .5:.1f}" stroke="#8A4A1C" stroke-width="1.2"/><circle cx="{x:.1f}" cy="{by - r * .36:.1f}" r="{max(1.6, r * .16):.1f}" fill="#FFFFFF"/>'
        LUZES.append((x, by, r * 2.5, grupo))
    # tampa com nó, de onde sai a corda
    s += (f'<path d="M{x - w * .17:.0f},{topo + h * .055:.0f} Q{x:.0f},{topo - h * .05:.0f} {x + w * .17:.0f},{topo + h * .055:.0f} Q{x:.0f},{topo + h * .02:.0f} {x - w * .17:.0f},{topo + h * .055:.0f} Z" '
          f'fill="#052B38" opacity="{op}"/><circle cx="{x:.0f}" cy="{topo - h * .01:.0f}" r="{max(1.5, w * .028):.1f}" fill="#052B38" opacity="{op}"/>')
    return s


def buzio(x, y, w, h, fill, grupo, op=1.0, luz="#9FF0DD"):
    """Casa de búzio: voltas que afinam para baixo, com a boca na volta de cima."""
    topo = y - h / 2
    s = f'<path d="M{x:.0f},{topo + 6:.0f} L{x:.0f},{topo - h * .14:.0f}" stroke="#052B38" stroke-width="{max(2, w * .05):.1f}" stroke-linecap="round" opacity="{op}"/>'
    cy, cw, wh = topo + h * .2, w, h * .4
    primeira = (cy, cw, wh)
    for i in range(4):
        s += (f'<path d="M{x - cw / 2:.0f},{cy:.0f} C{x - cw / 2:.0f},{cy - wh * .68:.0f} {x + cw / 2:.0f},{cy - wh * .68:.0f} {x + cw / 2:.0f},{cy:.0f} '
              f'C{x + cw / 2:.0f},{cy + wh * .68:.0f} {x - cw / 2:.0f},{cy + wh * .68:.0f} {x - cw / 2:.0f},{cy:.0f} Z" fill="{fill}" opacity="{op}"/>')
        s += f'<path d="M{x - cw * .46:.0f},{cy + wh * .16:.0f} Q{x:.0f},{cy + wh * .5:.0f} {x + cw * .46:.0f},{cy + wh * .02:.0f}" fill="none" stroke="#03141D" stroke-width="1.3" opacity="{.32 * op:.2f}"/>'
        if luz:
            s += (f'<path d="M{x - cw * .49:.0f},{cy:.0f} C{x - cw * .49:.0f},{cy - wh * .4:.0f} {x - cw * .2:.0f},{cy - wh * .5:.0f} {x:.0f},{cy - wh * .5:.0f}" fill="none" '
                  f'stroke="{luz}" stroke-width="{max(1.2, cw * .03):.1f}" stroke-linecap="round" opacity="{.6 * op:.2f}"/>')
        cy += wh * .62
        cw *= .68
        wh *= .74
    s += f'<path d="M{x - cw * .5:.0f},{cy - wh * .3:.0f} Q{x:.0f},{cy:.0f} {x + 2:.0f},{cy + wh * .9:.0f} Q{x:.0f},{cy:.0f} {x + cw * .5:.0f},{cy - wh * .3:.0f} Z" fill="{fill}" opacity="{op}"/>'
    cy, cw, wh = primeira
    r = cw * .19
    s += f'<circle cx="{x:.0f}" cy="{cy:.0f}" r="{r * 1.28:.1f}" fill="#03141D" opacity="{.45 * op:.2f}"/><circle cx="{x:.0f}" cy="{cy:.0f}" r="{r:.1f}" fill="url(#boca)" opacity="{op}"/>'
    s += f'<circle cx="{x:.0f}" cy="{cy:.0f}" r="{r * 1.14:.1f}" fill="none" stroke="#FFE7B0" stroke-width="{max(1.2, w * .016):.1f}" opacity=".5"/>'
    LUZES.append((x, cy, r * 2.5, grupo))
    for k, (jy, jw) in enumerate([(cy + wh * .66, cw * .62), (cy + wh * 1.12, cw * .42)]):      # janelinhas nas voltas de baixo
        s += f'<ellipse cx="{x:.0f}" cy="{jy:.0f}" rx="{max(1.6, jw * .07):.1f}" ry="{max(2.2, jw * .1):.1f}" fill="#FFF2CF" opacity="{op}"/>'
        LUZES.append((x, jy, jw * .3, grupo + 1 + k))
    return s


def torre(x, base, w, h, fill, grupo, op=1.0, andares=2, luz="#9FF0DD"):
    """Torre de búzio que sobe do escuro: corpo que afina e bulbos empilhados."""
    s = f'<path d="M{x - w / 2:.0f},{base} L{x - w * .34:.0f},{base - h * .62:.0f} L{x + w * .34:.0f},{base - h * .62:.0f} L{x + w / 2:.0f},{base} Z" fill="{fill}" opacity="{op}"/>'
    y, raio = base - h * .62, w * .52
    for i in range(andares):
        alt = raio * 1.5
        s += (f'<path d="M{x - raio:.0f},{y:.0f} C{x - raio * 1.25:.0f},{y - alt * .55:.0f} {x - raio * .5:.0f},{y - alt:.0f} {x:.0f},{y - alt:.0f} '
              f'C{x + raio * .5:.0f},{y - alt:.0f} {x + raio * 1.25:.0f},{y - alt * .55:.0f} {x + raio:.0f},{y:.0f} Z" fill="{fill}" opacity="{op}"/>')
        if luz:
            s += (f'<path d="M{x - raio * 1.02:.0f},{y - alt * .3:.0f} C{x - raio * .95:.0f},{y - alt * .75:.0f} {x - raio * .4:.0f},{y - alt + 1:.0f} {x:.0f},{y - alt + 1:.0f}" '
                  f'fill="none" stroke="{luz}" stroke-width="1.8" stroke-linecap="round" opacity="{.5 * op:.2f}"/>')
        LUZES.append((x, y - alt * .45, raio * .9, grupo))
        s += f'<circle cx="{x:.0f}" cy="{y - alt * .45:.0f}" r="{raio * .24:.1f}" fill="url(#boca)" opacity="{op}"/>'
        y -= alt * .78
        raio *= .68
    s += f'<path d="M{x - 2.5:.0f},{y + 6:.0f} L{x:.0f},{y - 24:.0f} L{x + 2.5:.0f},{y + 6:.0f} Z" fill="{fill}" opacity="{op}"/>'
    # janelas subindo pelo corpo, em fileira
    n = int(h * .55 / 26)
    for i in range(n):
        jy = base - 30 - i * 26
        if jy < 760:
            jx = x + (R.random() - .5) * w * .1
            LUZES.append((jx, jy, 9, grupo + i % 2))
            s += f'<ellipse cx="{jx:.0f}" cy="{jy:.0f}" rx="2.2" ry="3.4" fill="#FFF2CF" opacity="{op}"/>'
    return s


def acende(cor_miolo="#FFF2CF", escala=1.0):
    """Desenha os halos das luzes juntadas até aqui, um <g> por ritmo de cintilar."""
    global LUZES
    grupos = {}
    for x, y, r, g in LUZES:
        grupos.setdefault(g % 4, []).append((x, y, r))
    for g, itens in sorted(grupos.items()):
        A(f'<g class="luz luz-{g}">', f"luz-{g}")
        for x, y, r in itens:
            A(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r * escala:.1f}" fill="url(#janela)"/>', f"luz-{g}")
        A('</g>', f"luz-{g}")
    LUZES = []


def peixes(cx, cy, n, espalha, cor, op, escala=1.0, vira=8):
    for i in range(n):
        fx = cx + R.uniform(-espalha, espalha * 1.2)
        fy = cy + R.uniform(-espalha * .32, espalha * .34) + (fx - cx) * .1
        s = R.uniform(.7, 1.3) * escala
        A(f'<path class="peixe" transform="translate({fx:.0f} {fy:.0f}) scale({s:.2f}) rotate({vira})" '
          f'd="M-13,0 C-7,-6 6,-6 13,0 C6,6 -7,6 -13,0 Z M13,0 L22,-6 L19,0 L22,6 Z" fill="{cor}" opacity="{op}"/>')


def folha(x, base, alt, incl, larg, cor, op=1.0, classe="planta"):
    """alt positivo cresce para cima; negativo pende para baixo (as plantas aqui pendem das raízes)."""
    tx, ty = x + incl, base - alt
    return (f'<path class="{classe}" d="M{x - larg * .5:.0f},{base:.0f} C{x - larg:.0f},{base - alt * .45:.0f} {tx - larg * .6:.0f},{ty + alt * .25:.0f} {tx:.0f},{ty:.0f} '
            f'C{tx + larg * .5:.0f},{ty + alt * .3:.0f} {x + larg + incl * .6:.0f},{base - alt * .5:.0f} {x + larg * .5:.0f},{base:.0f} Z" fill="{cor}" opacity="{op}"/>')


def corrente(pontos_ctrl, n, cor="#C9FFF6", r0=1.4, r1=3.2, halo=True):
    """Uma "rua": fileira de luzes vivas ao longo de uma curva (Bézier cúbica), maiores para perto."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pontos_ctrl
    A('<g class="corrente">')
    for i in range(n):
        t = (i + R.uniform(-.25, .25)) / (n - 1)
        t = min(1, max(0, t))
        u = 1 - t
        x = u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3 + R.uniform(-5, 5)
        y = u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3 + R.uniform(-5, 5)
        r = r0 + (r1 - r0) * t
        if halo:
            A(f'<circle class="bio" cx="{x:.0f}" cy="{y:.0f}" r="{r * 4.5:.1f}" fill="url(#bio)" opacity="{.5 + .4 * t:.2f}"/>')
        A(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r * .8:.1f}" fill="{cor}" opacity="{.6 + .4 * t:.2f}"/>')
    A('</g>')


# ------------------------------------------------------------------ camada 1: ao longe, dentro do barro alaranjado
camada("cidade-longe")
A('<g class="camada-longe">')
for x0, x1, larg, bar in [(520, 540, 20, 10), (660, 640, 30, -14), (792, 806, 22, 8), (948, 930, 36, 12), (1090, 1104, 24, -8), (1200, 1186, 18, 6)]:
    A(tronco(x0, x1, larg, "url(#troncoLonge)", .40, bar))
for x, y, w, h in [(650, 250, 46, 60), (668, 388, 36, 46), (630, 470, 30, 40), (800, 320, 34, 44), (940, 210, 58, 74), (958, 356, 44, 56),
                   (924, 474, 40, 52), (1098, 300, 40, 52), (1088, 430, 32, 42), (536, 360, 28, 36), (1194, 372, 26, 34)]:
    A(cabaca(x, y, w, h, "url(#casaLonge)", R.randrange(4), .5, luz=None, nervuras=0))
for x, w, h in [(736, 34, 250), (872, 40, 300), (1020, 30, 230)]:
    A(torre(x, 800, w, h, "url(#casaLonge)", R.randrange(4), .42, 2, luz=None))
acende(escala=.8)
A('</g>')

# cardume do fundo: passa entre o longe e o meio
camada("cardume-fundo")
A('<g class="cardume cardume-fundo">')
peixes(860, 430, 26, 150, "#5A3A2A", .55, .62, vira=186)
A('</g>')

camada("cidade-perto")
# ------------------------------------------------------------------ camada 2: o meio da cidade
A('<g class="camada-meio">')
A(tronco(596, 566, 52, "url(#casaMeio)", .92, -16, "#9FF0DD"))
A(tronco(1010, 1040, 64, "url(#casaMeio)", .94, 18, "#9FF0DD"))
A(tronco(806, 820, 40, "url(#casaMeio)", .86, 6, "#9FF0DD"))
# cipós entre os troncos, com luzes penduradas
for x0, y0, x1, y1, flecha in [(590, 112, 812, 96, 44), (812, 300, 1016, 250, 80), (584, 440, 814, 464, 60)]:
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2 + flecha
    A(f'<path class="haste" d="M{x0},{y0} Q{xm},{ym + flecha * .6:.0f} {x1},{y1}" fill="none" stroke="#0A4350" stroke-width="3" opacity=".8"/>')
    for k in range(1, 7):
        t = k / 7
        px = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * xm + t * t * x1
        py = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * (ym + flecha * .6) + t * t * y1
        A(f'<path d="M{px:.0f},{py:.0f} L{px:.0f},{py + 9:.0f}" stroke="#0A4350" stroke-width="1"/><circle cx="{px:.0f}" cy="{py + 12:.0f}" r="2" fill="#FFF2CF"/>')
        LUZES.append((px, py + 12, 8, k))
for x, y, w, h in [(560, 236, 84, 104), (626, 350, 66, 84), (548, 478, 76, 96), (604, 596, 60, 76), (1056, 196, 96, 120), (980, 330, 78, 98),
                   (1070, 452, 88, 110), (992, 580, 70, 88), (826, 222, 56, 70), (790, 372, 50, 62), (834, 520, 58, 72)]:
    if x in (548, 790, 992):
        A(buzio(x, y, w, h * 1.25, "url(#casaMeio)", R.randrange(4), .97))
    else:
        A(cabaca(x, y, w, h, "url(#casaMeio)", R.randrange(4), .97, enfeite=w > 60, pescoco=(x in (626, 980, 834)), franja=w > 80))
for x, w, h in [(700, 50, 330), (906, 58, 290)]:
    A(torre(x, 800, w, h, "url(#casaMeio)", R.randrange(4), .95, 3))
acende()
A('</g>')

# os moradores: botos pequenos rondando, e uma "rua" de luzes vivas que vem do fundo
camada("parado-moradores")
A('<g class="moradores">')
for bx, by, s, rot in [(900, 150, .17, -20), (724, 300, .13, 164), (1150, 392, .2, -8), (668, 520, .11, -34)]:
    A(f'<path class="botinho" transform="translate({bx} {by}) rotate({rot}) scale({s})" fill="#F7A3C2" opacity=".78" '
      'd="M300,0 C270,-4 250,-8 236,-14 C226,-34 200,-40 176,-36 C140,-44 100,-36 70,-22 C40,-14 10,-18 -20,-46 C-14,-20 -8,-6 0,2 C-12,14 -18,30 -22,48 C0,30 24,20 44,16 C90,30 150,36 200,24 C236,16 270,8 300,4 Z"/>')
A('</g>')
corrente([(1180, 250), (1000, 420), (760, 470), (640, 640)], 20, r0=1.0, r1=2.2)
corrente([(520, 150), (700, 250), (900, 120), (1120, 150)], 18, r0=.9, r1=1.8)
camada("cidade-perto")

# o escuro lá embaixo: a cidade continua, só as luzes aparecem
A(f'<rect class="abismo" x="0" y="430" width="{W}" height="338" fill="url(#abismo)"/>')
camada("luz-3")
A('<g class="luz luz-fundo">')
for i in range(60):
    x, y = R.uniform(330, 1250), R.uniform(640, 760)
    k = (y - 640) / 120
    A(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{(7 - 4 * k) :.1f}" fill="url(#janela)" opacity="{.75 - .5 * k:.2f}"/>')
    A(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{1.3 - .6 * k:.1f}" fill="#FFF2CF" opacity="{.9 - .5 * k:.2f}"/>')
A('</g>')

camada("cidade-perto")
# ------------------------------------------------------------------ camada 3: perto, com as casas grandes
A('<g class="camada-perto">')
A(tronco(1226, 1196, 118, "url(#casaPerto)", 1, -26, "#7FE8DA"))
for x, y, w, h, pesc in [(1164, 278, 118, 140, True), (1278, 440, 104, 150, False), (1150, 580, 126, 130, False), (1290, 168, 70, 96, False), (1236, 690, 84, 96, True)]:
    if x == 1278:
        A(buzio(x, y, w, h * 1.3, "url(#casaPerto)", R.randrange(4), 1, luz="#7FE8DA"))
    else:
        A(cabaca(x, y, w, h, "url(#casaPerto)", R.randrange(4), 1, luz="#7FE8DA", nervuras=3, pescoco=pesc, enfeite=True, franja=True))
# o canto de baixo, à esquerda: uma casa grande presa à raiz, enchendo de luz o que era só sombra
A(cabaca(262, 668, 150, 170, "url(#casaPerto)", 3, 1, luz="#7FE8DA", nervuras=3, pescoco=True, enfeite=True, franja=False))
A(cabaca(126, 560, 76, 92, "url(#casaPerto)", 1, 1, luz="#7FE8DA", nervuras=2, enfeite=True, franja=True))
A(torre(430, 830, 78, 300, "url(#casaPerto)", 2, 1, 3, luz="#7FE8DA"))
A(torre(790, 850, 64, 210, "url(#casaPerto)", 1, 1, 2, luz="#7FE8DA"))
acende(escala=.8)
A('</g>')

# cardume de perto, na luz
camada("cardume-perto")
A('<g class="cardume cardume-perto">')
peixes(960, 120, 18, 150, "#083645", .7, 1.0)
peixes(1000, 150, 7, 140, "#C9F8E6", .55, 1.0)
A('</g>')
camada("parado-moradores")
corrente([(300, 620), (520, 520), (760, 600), (1040, 690)], 16, r0=1.6, r1=3.4)

# ------------------------------------------------------------------ o Boto (sempre presente, nadando no lugar)
camada("boto-abre")
A('<g class="boto" transform="translate(96 214) rotate(-12) scale(.98)">')
A('<ellipse cx="300" cy="126" rx="400" ry="180" fill="url(#botoHalo)"/>')
# nadadeira de trás, na sombra
camada("boto")
A('<path class="nadadeira-tras" d="M396,178 C386,214 354,244 312,250 C304,244 308,234 320,222 C338,204 350,190 358,172 Z" fill="#A63B72"/>')
CORPO = ("M600,150 C565,146 530,140 502,131 C494,112 488,98 472,90 C456,80 430,76 404,80 C380,82 350,74 330,66 "
         "C310,58 290,50 268,52 C246,56 232,68 212,74 C176,86 140,102 108,112 C94,108 62,100 30,88 "
         "C44,102 56,114 66,124 C48,134 26,150 8,174 C48,168 88,154 112,142 C150,156 190,172 232,180 "
         "C290,190 370,190 424,178 C456,170 484,164 506,158 C540,158 570,157 600,156 Z")
A(f'<path class="corpo" d="{CORPO}" fill="url(#boto)"/>')
# plano de luz no dorso (a luz que vem de cima) e a barriga clara
A('<path d="M502,131 C494,112 488,98 472,90 C456,80 430,76 404,80 C380,82 350,74 330,66 C310,58 290,50 268,52 C246,56 232,68 212,74 '
  'C176,86 140,102 108,112 C150,112 200,104 250,98 C320,90 400,100 452,112 C474,118 490,126 502,131 Z" fill="url(#botoLuz)"/>')
A('<path d="M112,142 C150,156 190,172 232,180 C290,190 370,190 424,178 C456,170 484,164 506,158 C540,158 570,157 600,156 L600,153 '
  'C560,152 520,150 488,150 C420,156 330,160 250,154 C190,148 150,140 112,142 Z" fill="url(#botoBarriga)"/>')
# manchas de luz ondulando no dorso
for x, y, l, op in [(418, 92, 34, .5), (364, 84, 46, .45), (296, 70, 40, .5), (236, 80, 30, .4), (176, 98, 30, .35), (452, 104, 22, .4)]:
    A(f'<path class="mancha" d="M{x},{y} q{l / 2:.0f},-7 {l},0 q{-l / 2:.0f},5 {-l},0 Z" fill="#FFFFFF" opacity="{op}"/>')
# fio de luz no contorno de cima
A('<path d="M498,126 C492,110 486,98 471,91 C456,81 430,77 404,81 C380,83 350,75 330,67 C310,59 290,51 268,53 C246,57 232,69 212,75 C176,87 140,103 110,112" '
  'fill="none" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" opacity=".8"/>')
A('<path d="M108,112 C94,108 62,100 30,88 C44,102 56,114 66,124 C80,120 96,116 108,112 Z" fill="#A63B72" opacity=".38"/>')   # o lobo de trás, na sombra
A('<path d="M66,124 C48,134 26,150 8,174 C40,160 72,142 100,134 Z" fill="#FFD0E0" opacity=".30"/>')                       # o da frente, na luz
A('<path d="M104,111 C84,107 58,99 34,90" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity=".55"/>')
A('<path d="M598,150 C566,146 532,140 506,132" fill="none" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" opacity=".6"/>')
# sombra da nadadeira no corpo e a nadadeira da frente
A('<path d="M430,170 C400,186 360,190 330,184 C360,176 392,170 418,160 Z" fill="#A63B72" opacity=".45"/>')
A('<path class="nadadeira" d="M426,166 C422,208 392,250 338,264 C324,258 326,242 340,228 C360,208 372,188 380,164 Z" fill="url(#nadadeira)"/>')
A('<path d="M424,170 C418,206 392,242 346,258" fill="none" stroke="#FFE3EC" stroke-width="2" stroke-linecap="round" opacity=".6"/>')
# rosto: boca num sorriso leve, bochecha e o olho pequeno
A('<path d="M600,153 C562,153 530,151 502,145 C492,143 484,146 476,152" fill="none" stroke="#8E2F5C" stroke-width="2.4" stroke-linecap="round"/>')
A('<ellipse cx="474" cy="134" rx="20" ry="13" fill="#FFD0E0" opacity=".35"/>')
A('<path d="M500,128 C494,110 484,98 468,92 C478,104 484,118 486,130 Z" fill="#FFFFFF" opacity=".35"/>')                   # brilho na testa
A('<path d="M150,150 C200,168 260,178 330,180 C380,180 410,176 424,172 C380,190 300,192 232,180 C200,174 170,164 150,150 Z" fill="#8E2F5C" opacity=".30"/>')   # sombra de barriga
A('<circle cx="468" cy="118" r="5.6" fill="#35102B"/><circle cx="469.8" cy="116.2" r="1.9" fill="#FFFFFF"/>')
A('<path d="M459,111 C464,107 472,107 477,111" fill="none" stroke="#B8457A" stroke-width="1.6" stroke-linecap="round" opacity=".7"/>')
camada("parado-bolhas-do-boto")
A('</g>', "boto-fecha")
for bx, by, br in [(718, 176, 5), (732, 152, 3.2), (744, 124, 7), (726, 98, 2.6), (708, 198, 2.2), (750, 70, 4)]:
    A(f'<circle class="bolha" cx="{bx}" cy="{by}" r="{br}" fill="#DFFFF4" fill-opacity=".10" stroke="#EFFFF8" stroke-opacity=".75" stroke-width="1.2"/>')
    A(f'<circle cx="{bx - br * .3:.1f}" cy="{by - br * .3:.1f}" r="{br * .22:.1f}" fill="#FFFFFF" opacity=".8"/>')


# ------------------------------------------------------------------ moldura: raízes escuras, plantas pendentes e a superfície
def raiz(d, w, op=1.0, cor="#03202B"):
    return f'<path d="{d}" fill="none" stroke="{cor}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>'


camada("moldura")
A('<g class="camada-moldura">')
A(raiz("M-70,-30 C0,110 -6,290 46,470 C76,570 60,670 30,800", 96))
A(raiz("M10,170 C70,270 120,340 138,470 C150,570 130,690 140,800", 34))
A(raiz("M60,440 C120,480 190,540 226,650 C240,700 236,750 246,800", 22))
A(raiz("M96,310 C150,336 190,376 214,430", 11))
A(raiz("M-30,360 C-6,450 -20,570 0,710", 46))
A(raiz("M34,60 C56,170 62,300 96,440", 3, .5, "#7FE8DA"))
A(raiz("M30,190 C84,280 126,350 142,466", 2, .4, "#7FE8DA"))
A(raiz("M1440,-40 C1380,60 1390,170 1366,260", 70))
A(raiz("M-40,700 C120,690 260,730 420,800", 70))
A(raiz("M1000,800 C1120,740 1260,720 1420,700", 60))
# franjas que pendem das raízes (balançam pela ponta de cima)
for x0, y0, n, amin, amax in [(150, 470, 5, 50, 120), (214, 432, 3, 30, 70), (236, 660, 4, 40, 90), (70, 600, 4, 50, 110)]:
    for i in range(n):
        x, alt, incl = x0 + i * 11 + R.uniform(-4, 4), R.uniform(amin, amax), R.uniform(-18, 18)
        A(folha(x, y0, -alt, incl, R.uniform(6, 10), "#052735"), "franjas")
        if R.random() < .45:
            A(f'<circle class="bio" cx="{x + incl:.0f}" cy="{y0 + alt:.0f}" r="13" fill="url(#bio)"/><circle cx="{x + incl:.0f}" cy="{y0 + alt:.0f}" r="2.6" fill="#E9FFFB"/>', "franjas")
A('</g>')

camada("regias")
A('<g class="camada-superficie">')
for cx, rx in [(150, 100), (318, 60), (760, 48), (1040, 86), (1206, 64), (1310, 44)]:
    A(f'<path class="haste" d="M{cx},{24 + rx * .14:.0f} C{cx + 18},160 {cx - 26},300 {cx + 10},470" fill="none" stroke="#0E5A53" stroke-width="3.2" opacity=".6"/>')
    A(f'<ellipse class="regia" cx="{cx}" cy="22" rx="{rx}" ry="{rx * .16:.0f}" fill="#083645" opacity=".92"/>')
    A(f'<ellipse class="regia" cx="{cx}" cy="19" rx="{rx}" ry="{rx * .16:.0f}" fill="none" stroke="#C9F8E6" stroke-width="1.6" opacity=".5"/>')
# raízes de capim boiando: franjas curtas penduradas na superfície
for x0, n in [(430, 9), (880, 8), (1120, 6)]:
    for i in range(n):
        A(folha(x0 + i * 9 + R.uniform(-3, 3), 14, -R.uniform(18, 54), R.uniform(-8, 8), R.uniform(3, 5), "#0E5A53", .7, "haste"))
A('</g>')

# luzes vivas soltas, poeira do rio na luz e bolhas
camada("bio")
for i in range(80):
    x, y, r, op = R.uniform(30, W - 30), R.uniform(110, 730), R.uniform(1.1, 3.0), R.uniform(.35, 1)
    if R.random() < .18:
        A(f'<circle class="bio" cx="{x:.0f}" cy="{y:.0f}" r="{r * 6:.1f}" fill="url(#bio)" opacity="{op:.2f}"/>')
    else:
        A(f'<circle class="bio" cx="{x:.0f}" cy="{y:.0f}" r="{r * .7:.1f}" fill="#C9FFF6" opacity="{op * .7:.2f}"/>')
for i in range(70):       # poeira: o rio é turvo
    x, y = R.uniform(260, 1100), R.uniform(60, 560)
    A(f'<circle class="poeira" cx="{x:.0f}" cy="{y:.0f}" r="{R.uniform(.6, 1.6):.1f}" fill="#FFE2B0" opacity="{R.uniform(.15, .5):.2f}"/>', "poeira")
for i in range(22):
    x, y, r = R.uniform(330, 1180), R.uniform(80, 660), R.uniform(2, 7.5)
    A(f'<circle class="bolha" cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#DFFFF4" fill-opacity=".06" stroke="#EFFFF8" stroke-opacity=".5" stroke-width="1"/>', "bolhas")

A(f'<rect width="{W}" height="{H}" fill="url(#vinheta)"/>', "vinheta")

AQUI = Path(__file__).resolve().parent
REPO = AQUI.parent
PLUGIN = AQUI / "papel-vivo" / "io.github.pabloherzberg.mataviva" / "contents"
CABECA = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
DEFS = "\n".join(t for c, t in PARTES if c == "defs")
corpo = "\n".join(t for c, t in PARTES if c not in ("cabecalho", "defs"))
(REPO / "arte" / "encante-fundo.svg").write_text(
    f"{CABECA}\n<!-- Gerado por tema/gerar-encante.py; não edite à mão. -->\n{DEFS}\n{corpo}\n</svg>\n")

# ------------------------------------------------------------------ as peças da animação
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QByteArray, QRectF  # noqa: E402
from PySide6.QtGui import QGuiApplication, QImage, QPainter  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402

app = QGuiApplication.instance() or QGuiApplication([])
BOTO_CAIXA = (-30, 0, 670, 310)      # o Boto sai sozinho, deitado como foi desenhado, com folga para ondular
INTEIRAS = ("fundo", "boto", "superficie-0", "superficie-1", "superficie-2")     # não são aparadas
imagens = PLUGIN / "images" / "encante"
if imagens.exists():
    shutil.rmtree(imagens)
imagens.mkdir(parents=True)


def desenha(svg: str, w: int, h: int) -> QImage:
    render = QSvgRenderer(QByteArray(svg.encode()))
    img = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(0)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    render.render(p, QRectF(0, 0, w, h))
    p.end()
    return img


def apara(img: QImage):
    """Devolve a imagem cortada até a caixa do que tem desenho, e a caixa [x, y, largura, altura]."""
    a = img.convertToFormat(QImage.Format.Format_Alpha8)
    w, h, passo, dados = a.width(), a.height(), a.bytesPerLine(), bytes(a.constBits())
    linhas = [dados[y * passo:y * passo + w] for y in range(h)]
    cheias = [y for y, l in enumerate(linhas) if l.count(0) != w]
    if not cheias:
        return img.copy(0, 0, 1, 1), [0, 0, 1, 1]
    y0, y1 = cheias[0], cheias[-1]
    x0 = min(w - len(l.lstrip(b"\0")) for l in linhas[y0:y1 + 1] if l.count(0) != w)
    x1 = max(len(l.rstrip(b"\0")) for l in linhas[y0:y1 + 1])
    return img.copy(x0, y0, x1 - x0, y1 - y0 + 1), [x0, y0, x1 - x0, y1 - y0 + 1]


nomes = []
for c, _ in PARTES:
    if c not in nomes and c not in ("cabecalho", "defs", "boto-abre", "boto-fecha") and not c.startswith("parado-"):
        nomes.append(c)
caixas = {}
for nome in nomes:
    miolo = "\n".join(t for c, t in PARTES if c == nome)
    x, y, w, h = BOTO_CAIXA if nome == "boto" else (-200, 0, W + 400, 64) if nome.startswith("superficie-") else (0, 0, W, H)
    img = desenha(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{w}" height="{h}">\n{DEFS}\n{miolo}\n</svg>', w, h)
    if nome in INTEIRAS:
        caixas[nome] = [x, y, w, h]
    else:
        img, caixas[nome] = apara(img)
    img.save(str(imagens / f"{nome}.png"))
(PLUGIN / "ui" / "EncanteRecortes.js").write_text(
    "// Gerado por tema/gerar-encante.py; não edite à mão. Onde cada camada fica na cena: [x, y, largura, altura].\n"
    ".pragma library\nvar caixa = " + json.dumps(caixas, indent=1) + "\n")

# os programas da placa de vídeo
destino = PLUGIN / "ui" / "encante"
destino.mkdir(parents=True, exist_ok=True)
qsb = shutil.which("qsb") or "/usr/lib/qt6/bin/qsb"
fontes = sorted(list((AQUI / "papel-vivo" / "encante").glob("*.vert")) + list((AQUI / "papel-vivo" / "encante").glob("*.frag")))
for fonte in fontes:
    subprocess.run([qsb, "--glsl", "100 es,120,150", "-o", str(destino / (fonte.name + ".qsb")), str(fonte)], check=True)

# a miniatura da Toca: o desenho parado
desenha((REPO / "arte" / "encante-fundo.svg").read_text(), 400, 225).save(str(PLUGIN / "screenshot-encante.png"))

area = sum(c[2] * c[3] for c in caixas.values()) / (W * H)
print(f"Encante: {len(caixas)} camadas ({area:.1f} telas de desenho por quadro) e {len(fontes)} programas de vídeo")
