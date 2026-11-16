// Curupira OS: a doca flutuante do mockup/Desktop.dc.html.
// Uma barra centralizada embaixo, do tamanho do conteúdo: menu (o Cordel), apps fixados,
// o widget Curupira, a bandeja e o relógio com a data embaixo.
// Usado pelo tema global "Curupira" e por tema/aplicar-doca.sh (que guarda antes uma cópia do painel).

// recomeça do zero: sem painéis e sem widgets soltos na área de trabalho
var antigos = panels();
for (var i = 0; i < antigos.length; i++) {
    antigos[i].remove();
}
var areas = desktops();
for (var d = 0; d < areas.length; d++) {
    var soltos = areas[d].widgets();
    for (var w = 0; w < soltos.length; w++) {
        soltos[w].remove();
    }
}

var doca = new Panel;
doca.location = "bottom";
doca.floating = true;
doca.alignment = "center";
doca.lengthMode = "fit";
doca.height = 70;            // mockup: 70 px
// some quando uma janela (tela cheia ou maximizada) encosta nela; volta subindo ao tocar a borda de baixo
doca.hiding = "dodgewindows";

var menu = doca.addWidget("org.kde.plasma.kickoff");
menu.currentConfigGroup = ["General"];
menu.writeConfig("icon", "curupira-menu");   // instalado em /usr/local/share/icons/hicolor

doca.addWidget("org.kde.plasma.marginsseparator");

// Doca Curupira (sistema/doca): apps com animação ao surgir e efeito de lupa
var tarefas = doca.addWidget("io.github.pabloherzberg.doca");
tarefas.currentConfigGroup = ["General"];
tarefas.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:firefox.desktop",
    "applications:org.kde.kate.desktop",
    "applications:org.wireshark.Wireshark.desktop",
    "applications:com.anthropic.Claude.desktop",
    "applications:io.github.pabloherzberg.Toca.desktop"
]);

doca.addWidget("org.kde.plasma.marginsseparator");
doca.addWidget("io.github.pabloherzberg.curupira");
doca.addWidget("org.kde.plasma.systemtray");

var relogio = doca.addWidget("org.kde.plasma.digitalclock");
relogio.currentConfigGroup = ["Appearance"];
relogio.writeConfig("showDate", true);
relogio.writeConfig("dateDisplayFormat", 2);          // data embaixo da hora
// tamanho fixo, como no mockup (hora ~15 px em negrito, data menor), em vez de encher a altura da doca
relogio.writeConfig("autoFontAndSize", false);
relogio.writeConfig("fontSize", 11);
// o negrito é pelo peso: o relógio do Plasma 6 não olha mais para o boldText (que ficava fino e apagado)
relogio.writeConfig("fontWeight", 700);
relogio.writeConfig("fontStyleName", "Bold");
relogio.writeConfig("boldText", true);
relogio.writeConfig("dateFormat", "custom");
relogio.writeConfig("customDateFormat", "ddd, d MMM");
