#!/usr/bin/env python3
"""Gera as imagens do papel de parede animado "Mata Viva" (tema/papel-vivo/), com duas cenas:
"brasa" (arte/brasa-fundo.svg, com os seres da mata) e "iara" (arte/iara-fundo.svg).

Cada arte já descreve, em CSS, como cada parte se mexe (as mechas do cabelo de fogo,
as pálpebras, o halo, as faíscas e os vaga-lumes). O Plasma não roda CSS dentro de SVG, então este
gerador desmonta a arte na ordem em que ela é pintada:

  - cada parte animada (classes f, breath, lid, halo, sp, ff, vai) vira um recorte PNG próprio, com a
    animação anotada (origem, quadros, duração, atraso);
  - o que fica parado entre duas partes animadas vira uma camada PNG;
  - em três pontos abre uma vaga para os seres entrarem na mata: "ceu" (atrás de todas as árvores),
    "longe" (atrás dos troncos do meio) e "perto" (na frente da mata, atrás do Curupira e das folhas escuras).

Também desenha os seres de arte/papel-vivo/*.svg em PNG. O resultado vai para
contents/images/ do pacote e a lista, na ordem de pintura, para contents/ui/Camadas.js.

    python3 tema/gerar-papel-vivo.py
"""

import copy
import json
import os
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QByteArray, QRect, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QGuiApplication, QImage, QPainter  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402

AQUI = Path(__file__).resolve().parent
ARTE = AQUI.parent / "arte"
PACOTE = AQUI / "papel-vivo" / "io.github.pabloherzberg.mataviva"
IMAGENS = PACOTE / "contents" / "images"
LARGURA, ALTURA = 1366, 768          # tamanho da arte
ESCALA = 1920 / LARGURA              # os PNG saem em 1920×1080
MARGEM = 90                          # a arte passa da borda (o cabelo); os recortes levam essa sobra para poder balançar
SVG = "http://www.w3.org/2000/svg"
ANIMADAS = {"f", "breath", "lid", "halo", "sp", "ff", "vai"}
# cada cena do papel de parede animado sai de uma arte
CENAS = {"brasa": ARTE / "brasa-fundo.svg", "iara": ARTE / "iara-fundo.svg"}
ET.register_namespace("", SVG)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")


def nome(el) -> str:
    return el.tag.split("}")[-1]


def tem_animada(el) -> bool:
    return any(d.get("class") in ANIMADAS for d in el.iter())


def quadros_css(estilo: str) -> dict:
    """@keyframes do <style> -> {nome: [(fração, giro, escala x, escala y, opacidade)]}"""
    quadros = {}
    for nome_q, corpo in re.findall(r"@keyframes (\w+)\{((?:[^{}]*\{[^{}]*\})+)\}", estilo):
        pontos = []
        for seletores, props in re.findall(r"([\d.,%\s]+)\{([^}]*)\}", corpo):
            giro = re.search(r"rotate\(([-\d.]+)deg\)", props)
            escala = re.search(r"scale\(([-\d.]+),([-\d.]+)\)", props)
            opac = re.search(r"opacity:([\d.]+)", props)
            valor = (float(giro.group(1)) if giro else 0.0,
                     float(escala.group(1)) if escala else 1.0, float(escala.group(2)) if escala else 1.0,
                     float(opac.group(1)) if opac else None)
            for s in seletores.split(","):
                pontos.append((float(s.strip().rstrip("%")) / 100,) + valor)
        quadros[nome_q] = sorted(pontos)
    return quadros


def desmonta(raiz):
    """Percorre a arte na ordem de pintura e devolve as unidades: paradas, animadas e vagas."""
    unidades, parada = [], []

    def fecha():
        if parada:
            unidades.append(("parada", list(parada)))
            parada.clear()

    def anda(el, cadeia):
        for filho in el:
            if nome(filho) in ("defs", "style"):
                continue
            if el is raiz and filho.get("id") is None and nome(filho) == "g" and filho.find(f".//{{{SVG}}}g[@id='head']") is not None:
                fecha()
                unidades.append(("vaga", "perto"))      # logo antes do Curupira
            if filho.get("class") in ANIMADAS:
                fecha()
                unidades.append(("animada", cadeia, filho))
            elif nome(filho) == "g" and tem_animada(filho):
                anda(filho, cadeia + [filho])
            else:
                parada.append((cadeia, filho))
            if el is raiz and filho.get("fill") == "url(#mist)":
                fecha()
                unidades.append(("vaga", "longe"))      # logo depois da névoa do fundo
            if el is raiz and filho.get("fill") == "url(#moon)":
                fecha()
                unidades.append(("vaga", "ceu"))        # logo depois do céu, atrás de todas as árvores
    anda(raiz, [])
    fecha()
    return unidades


def monta_svg(defs, itens) -> bytes:
    """SVG só com estes itens, cada um dentro de cópias dos grupos que o continham (sem classe nem estilo)."""
    svg = ET.Element(f"{{{SVG}}}svg", {"viewBox": f"{-MARGEM} {-MARGEM} {LARGURA + 2 * MARGEM} {ALTURA + 2 * MARGEM}"})
    if defs is not None:
        svg.append(defs)
    for cadeia, el in itens:
        pai = svg
        for g in cadeia:
            pai = ET.SubElement(pai, f"{{{SVG}}}g", {k: v for k, v in g.attrib.items() if k not in ("class", "style", "id")})
        limpo = copy.deepcopy(el)
        for d in limpo.iter():
            if d.get("class") in ANIMADAS:
                d.attrib.pop("class", None)
                d.attrib.pop("style", None)
        pai.append(limpo)
    return ET.tostring(svg)


def desenha(svg: bytes) -> QImage:
    largura, altura = round((LARGURA + 2 * MARGEM) * ESCALA), round((ALTURA + 2 * MARGEM) * ESCALA)
    render = QSvgRenderer(QByteArray(svg))
    img = QImage(largura, altura, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    render.render(p, QRectF(0, 0, largura, altura))
    p.end()
    return img


def caixa(img: QImage) -> QRect:
    """Menor retângulo com algo desenhado (olha só o canal alfa)."""
    dados, passo, w, h = bytes(img.constBits()), img.bytesPerLine(), img.width(), img.height()
    topo = fundo = None
    esq, dir_ = w, -1
    for y in range(h):
        alfa = dados[y * passo + 3:y * passo + 4 * w:4]
        cheio = alfa.lstrip(b"\0")
        if not cheio:
            continue
        topo = y if topo is None else topo
        fundo = y
        esq = min(esq, w - len(cheio))
        dir_ = max(dir_, len(alfa.rstrip(b"\0")) - 1)
    if topo is None:
        return QRect()
    return QRect(esq, topo, dir_ - esq + 1, fundo - topo + 1).adjusted(-1, -1, 1, 1).intersected(img.rect())


def grava(img: QImage, arquivo: str) -> dict | None:
    r = caixa(img)
    if r.isEmpty():
        return None
    img.copy(r).save(str(IMAGENS / arquivo), "PNG")
    return {"img": arquivo, "x": round(r.x() / ESCALA - MARGEM, 2), "y": round(r.y() / ESCALA - MARGEM, 2),
            "w": round(r.width() / ESCALA, 2), "h": round(r.height() / ESCALA, 2)}


def estilo_de(el) -> dict:
    return dict(p.split(":", 1) for p in (el.get("style") or "").split(";") if ":" in p)


def segundos(texto: str | None, padrao: float) -> float:
    return float(texto.rstrip("s")) if texto else padrao


def desmonta_arte(nome_cena: str, arquivo: Path) -> dict:
    """Uma arte -> PNG em images/<cena>/ e a lista de camadas com as animações anotadas."""
    pasta = IMAGENS / nome_cena
    pasta.mkdir(parents=True, exist_ok=True)
    raiz = ET.parse(arquivo).getroot()
    defs = raiz.find(f"{{{SVG}}}defs")
    quadros = quadros_css(raiz.find(f"{{{SVG}}}style").text)
    camadas, n = [], 0
    for unidade in desmonta(raiz):
        if unidade[0] == "vaga":
            camadas.append({"tipo": "vaga", "nome": unidade[1]})
            continue
        n += 1
        if unidade[0] == "parada":
            dado = grava(desenha(monta_svg(defs, unidade[1])), f"{nome_cena}/c{n:02d}.png")
            if dado:
                camadas.append({"tipo": "parada", **dado})
            continue
        _, cadeia, el = unidade
        classe, estilo = el.get("class"), estilo_de(el)
        dado = grava(desenha(monta_svg(defs, [(cadeia, el)])), f"{nome_cena}/c{n:02d}-{classe}.png")
        if not dado:
            continue
        dado["tipo"] = classe
        if classe == "f":       # mecha do cabelo: balança em torno da raiz
            ox, oy = (float(v.rstrip("%")) / 100 for v in estilo["transform-origin"].split())
            dado.update(ox=ox, oy=oy, quadros=estilo["animation-name"])
        if classe == "vai":     # vai e volta devagar (o que boia, a correnteza)
            dado.update(dx=float(estilo["--dx"].rstrip("px")), dy=float(estilo["--dy"].rstrip("px")))
        if classe == "sp":      # faísca: sobe e some
            dado.update(dx=float(estilo["--dx"].rstrip("px")), dy=float(estilo["--dy"].rstrip("px")))
        if classe == "halo":
            dado["opacidade"] = float(el.get("opacity", "1"))
        dado["duracao"] = segundos(estilo.get("animation-duration"), {"breath": 2.6667, "lid": 8, "halo": 4, "sp": 4, "ff": 8, "vai": 6}.get(classe, 4))
        dado["atraso"] = segundos(estilo.get("animation-delay"), 0)
        camadas.append(dado)
    tipos = {}
    for c in camadas:
        tipos[c["tipo"]] = tipos.get(c["tipo"], 0) + 1
    print(f"  {nome_cena}: {len(camadas)} camadas {tipos}")
    return {"camadas": camadas, "quadros": quadros}


def main():
    app = QGuiApplication([])  # noqa: F841 - o QPainter precisa de uma aplicação
    if IMAGENS.exists():
        shutil.rmtree(IMAGENS)
    IMAGENS.mkdir(parents=True)
    cenas = {nome_cena: desmonta_arte(nome_cena, arquivo) for nome_cena, arquivo in CENAS.items()}

    seres = {}
    for svg in sorted((ARTE / "papel-vivo").glob("*.svg")):
        r = QSvgRenderer(str(svg))
        tam = r.defaultSize()
        w, h = round(tam.width() * ESCALA), round(tam.height() * ESCALA)
        img = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(Qt.GlobalColor.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r.render(p, QRectF(0, 0, w, h))
        p.end()
        img.save(str(IMAGENS / f"ser-{svg.stem}.png"), "PNG")
        seres[svg.stem] = {"img": f"ser-{svg.stem}.png", "w": tam.width(), "h": tam.height()}

    js = ("// Gerado por tema/gerar-papel-vivo.py a partir de arte/brasa-fundo.svg, arte/iara-fundo.svg e arte/papel-vivo/.\n"
          "// Não edite à mão.\n"
          ".pragma library\n"
          f"var cenas = {json.dumps(cenas, ensure_ascii=False, separators=(',', ':'))}\n"
          f"var seres = {json.dumps(seres, separators=(',', ':'))}\n")
    (PACOTE / "contents" / "ui").mkdir(parents=True, exist_ok=True)
    (PACOTE / "contents" / "ui" / "Camadas.js").write_text(js, encoding="utf-8")
    pesos = sum(a.stat().st_size for a in IMAGENS.rglob("*.png")) / 1e6
    print(f"papel-vivo: {len(cenas)} cenas, {len(seres)} seres, {pesos:.1f} MB em PNG")


if __name__ == "__main__":
    main()
