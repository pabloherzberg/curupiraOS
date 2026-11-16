# Folha de estudo do tema de cores "Encante": paleta + uma janela e um terminal de exemplo.
o=[]; A=o.append
P = {  # nome, cor, papel
 "fundo":   ("Fundo do rio", "#062A38", "fundo das janelas"),
 "vista":   ("Água funda",   "#0B3A48", "listas e campos"),
 "botao":   ("Petróleo",     "#125565", "botões"),
 "agua":    ("Correnteza",   "#1C8C8C", "bordas, foco suave"),
 "bio":     ("Luz viva",     "#5FE3D9", "links, seleção de texto"),
 "boto":    ("Rosa do boto", "#F08FB5", "destaque e seleção"),
 "boto2":   ("Boto fundo",   "#B8457A", "destaque pressionado"),
 "ambar":   ("Luz da cidade","#FFC46B", "título da janela, avisos"),
 "espuma":  ("Espuma",       "#E9F7F3", "texto"),
 "nevoa":   ("Névoa",        "#9CC8C6", "texto suave"),
 "abismo":  ("Abismo",       "#031822", "barra de título, doca"),
}
A('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1366 768" width="1366" height="768" font-family="Nunito, sans-serif">')
A('<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0E5562"/><stop offset="1" stop-color="#041C28"/></linearGradient></defs>')
A('<rect width="1366" height="768" fill="url(#bg)"/>')
A('<text x="48" y="70" font-family="\'Baloo 2\', Nunito, sans-serif" font-weight="800" font-size="40" fill="#FFC46B">Encante</text>')
A('<text x="48" y="100" font-size="17" fill="#9CC8C6">tema de cores · a cidade dos botos no fundo do rio</text>')
# amostras
x0, y0 = 48, 136
for i, (k, (nome, cor, papel)) in enumerate(P.items()):
    col, lin = i % 2, i // 2
    x, y = x0 + col*250, y0 + lin*98
    A(f'<rect x="{x}" y="{y}" width="64" height="64" rx="16" fill="{cor}" stroke="#1C8C8C" stroke-opacity=".5"/>')
    A(f'<text x="{x+78}" y="{y+22}" font-weight="800" font-size="16" fill="#E9F7F3">{nome}</text>')
    A(f'<text x="{x+78}" y="{y+41}" font-size="13" fill="#5FE3D9" font-family="JetBrains Mono, monospace">{cor}</text>')
    A(f'<text x="{x+78}" y="{y+59}" font-size="12.5" fill="#9CC8C6">{papel}</text>')
# janela de exemplo
wx, wy, ww, wh = 580, 70, 738, 400
A(f'<rect x="{wx}" y="{wy+8}" width="{ww}" height="{wh}" rx="14" fill="#000" opacity=".35"/>')
A(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="14" fill="#062A38"/>')
A(f'<path d="M{wx},{wy+36} v-22 a14,14 0 0 1 14,-14 h{ww-28} a14,14 0 0 1 14,14 v22 Z" fill="#031822"/>')
A(f'<text x="{wx+ww/2}" y="{wy+24}" text-anchor="middle" font-weight="700" font-size="14" fill="#FFC46B">Documentos · Dolphin</text>')
for i, c in enumerate(["#9CC8C6"]*3):
    A(f'<circle cx="{wx+ww-70+i*22}" cy="{wy+18}" r="5" fill="none" stroke="{c}" stroke-width="1.6"/>')
# barra lateral
A(f'<path d="M{wx},{wy+36} h190 v{wh-36} h-176 a14,14 0 0 1 -14,-14 Z" fill="#052230"/>')
for i, (t, sel) in enumerate([("Pasta pessoal", False), ("Documentos", True), ("Downloads", False), ("Imagens", False), ("Músicas", False), ("/data · Mapinguari", False)]):
    y = wy + 58 + i*38
    if sel:
        A(f'<rect x="{wx+10}" y="{y-6}" width="170" height="32" rx="9" fill="#F08FB5"/>')
    A(f'<rect x="{wx+22}" y="{y+2}" width="16" height="14" rx="3" fill="{"#062A38" if sel else "#1C8C8C"}"/>')
    A(f'<text x="{wx+48}" y="{y+15}" font-size="14" font-weight="{800 if sel else 600}" fill="{"#062A38" if sel else "#E9F7F3"}">{t}</text>')
# conteúdo: lista
lx = wx + 190
A(f'<rect x="{lx+16}" y="{wy+52}" width="{ww-190-32}" height="34" rx="9" fill="#0B3A48" stroke="#125565"/>')
A(f'<text x="{lx+30}" y="{wy+74}" font-size="13.5" fill="#9CC8C6">Pesquisar…</text>')
linhas = [("notas-da-toca.md", "12 KiB", "hoje, 17:32"), ("encante-estudo.svg", "48 KiB", "hoje, 18:09"), ("orçamento.ods", "31 KiB", "ontem"),
          ("fotos-do-rio", "pasta", "12 de nov"), ("curupiraOS", "pasta", "16 de nov"), ("lenda-do-boto.pdf", "2,1 MiB", "3 de nov")]
for i, (n, t, d) in enumerate(linhas):
    y = wy + 104 + i*36
    if i % 2 == 0: A(f'<rect x="{lx+16}" y="{y-4}" width="{ww-190-32}" height="36" fill="#0B3A48" opacity=".55"/>')
    if i == 1:
        A(f'<rect x="{lx+16}" y="{y-4}" width="{ww-190-32}" height="36" rx="8" fill="#F08FB5"/>')
    cor = "#062A38" if i == 1 else "#E9F7F3"; sub = "#3A1030" if i == 1 else "#9CC8C6"
    A(f'<rect x="{lx+30}" y="{y+5}" width="18" height="18" rx="4" fill="{"#B8457A" if i==1 else ("#FFC46B" if t=="pasta" else "#1C8C8C")}"/>')
    A(f'<text x="{lx+60}" y="{y+19}" font-size="14" font-weight="700" fill="{cor}">{n}</text>')
    A(f'<text x="{lx+330}" y="{y+19}" font-size="13" fill="{sub}">{t}</text><text x="{lx+420}" y="{y+19}" font-size="13" fill="{sub}">{d}</text>')
# botões e chave
by = wy + wh - 58
A(f'<rect x="{lx+16}" y="{by}" width="118" height="36" rx="10" fill="#F08FB5"/><text x="{lx+75}" y="{by+23}" text-anchor="middle" font-weight="800" font-size="14" fill="#062A38">Abrir</text>')
A(f'<rect x="{lx+146}" y="{by}" width="118" height="36" rx="10" fill="#125565" stroke="#1C8C8C"/><text x="{lx+205}" y="{by+23}" text-anchor="middle" font-weight="700" font-size="14" fill="#E9F7F3">Cancelar</text>')
A(f'<text x="{lx+290}" y="{by+23}" font-size="14" fill="#5FE3D9" text-decoration="underline">um link assim</text>')
A(f'<rect x="{lx+430}" y="{by+6}" width="46" height="24" rx="12" fill="#F08FB5"/><circle cx="{lx+464}" cy="{by+18}" r="9" fill="#FFFFFF"/>')
A(f'<rect x="{lx+486}" y="{by+6}" width="46" height="24" rx="12" fill="#125565"/><circle cx="{lx+498}" cy="{by+18}" r="9" fill="#E9F7F3"/>')
# terminal
tx, ty, tw, th = 580, 500, 738, 222
A(f'<rect x="{tx}" y="{ty+8}" width="{tw}" height="{th}" rx="14" fill="#000" opacity=".35"/>')
A(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="14" fill="#041C28"/>')
A(f'<path d="M{tx},{ty+32} v-18 a14,14 0 0 1 14,-14 h{tw-28} a14,14 0 0 1 14,14 v18 Z" fill="#031822"/>')
A(f'<text x="{tx+tw/2}" y="{ty+22}" text-anchor="middle" font-weight="700" font-size="13" fill="#FFC46B">Konsole</text>')
m = 'font-family="JetBrains Mono, monospace" font-size="14"'
def L(i, partes):
    x = tx + 20; s = f'<text x="{x}" y="{ty+60+i*24}" {m} xml:space="preserve">'
    for cor, t in partes: s += f'<tspan fill="{cor}">{t}</tspan>'
    A(s + '</text>')
L(0, [("#F08FB5", "pablo"), ("#9CC8C6", "@"), ("#5FE3D9", "curupira"), ("#E9F7F3", " ~/curupiraOS "), ("#FFC46B", "main"), ("#E9F7F3", " $ curupira hd")])
L(1, [("#E9F7F3", "Mapinguari hibernando: motor parado.")])
L(2, [("#F08FB5", "pablo"), ("#9CC8C6", "@"), ("#5FE3D9", "curupira"), ("#E9F7F3", " ~/curupiraOS "), ("#FFC46B", "main"), ("#E9F7F3", " $ git status -sb")])
L(3, [("#7FE3B0", "## main"), ("#9CC8C6", "..."), ("#FF8A70", "origin/main")])
L(4, [("#FF8A70", " M "), ("#E9F7F3", "tema/gerar-cores.py   "), ("#7FE3B0", "?? "), ("#E9F7F3", "arte/encante-fundo.svg")])
cores = ["#0B3A48","#FF8A70","#7FE3B0","#FFC46B","#6FB6F2","#F08FB5","#5FE3D9","#E9F7F3"]
for i, c in enumerate(cores):
    A(f'<rect x="{tx+20+i*34}" y="{ty+th-40}" width="26" height="18" rx="5" fill="{c}"/>')
A('</svg>')
open("encante-paleta.svg","w").write("\n".join(o))
