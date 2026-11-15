// Mata Viva: a cena do papel de parede animado. Só QtQuick, para poder ser vista fora do Plasma
// (ferramentas/ver-papel-vivo.py). Quem entrega o estado do sistema é o main.qml.
//
// A arte é a do papel de parede Brasa, desmontada em camadas por tema/gerar-papel-vivo.py (Camadas.js).
// Cada ser da mata aparece conforme o que o computador está fazendo:
//   Curupira    perfil de energia e uso do processador: o vigor do cabelo de fogo, as faíscas e o halo;
//               os olhos fecham no Sereno. Os vaga-lumes acesos são a carga da bateria.
//   Boitatá     a cobra de fogo passa atrás dos troncos quando a placa NVIDIA está acordada
//   Mapinguari  o gigante abre o olho quando o HD está acordado
//   Saci        o redemoinho gira quando o turbo do processador está ligado
//   Iara        sobe na lagoa com o Wi-Fi ligado (as ondas são o sinal); os fogos azuis são o Bluetooth
//   Boto        salta na lagoa quando a rede de laboratório existe
//   Caipora     com câmera e microfone cortados, a névoa cobre a mata e os olhos dela vigiam
//   Cuca        a lua atravessa o céu marcando as horas

import QtQuick
import "Camadas.js" as Camadas

Item {
    id: cena

    property var estado: ({})       // o que "curupira json" devolve
    property bool mover: true       // falso: tudo parado (bateria, ou movimento desligado)
    property real hora: new Date().getHours() + new Date().getMinutes() / 60

    clip: true

    // ---------------------------------------------------------------- leitura do estado
    readonly property string perfil: String(estado.perfil || "")
    readonly property real carga: Math.max(0, Math.min(100, Number(estado.carga) || 0))
    readonly property real bateria: estado.bateria === undefined || estado.bateria === null ? 100 : Number(estado.bateria)
    readonly property bool boitata: estado.boitata_dormindo === false
    readonly property bool mapinguari: !!estado.hd_acordado
    readonly property bool saci: !!estado.turbo
    readonly property bool iara: !!estado.wifi
    readonly property bool fogoAzul: !!estado.bluetooth
    readonly property bool boto: !!estado.lab
    readonly property real caipora: (estado.camera_cortada ? 0.5 : 0) + (estado.microfone_mudo ? 0.5 : 0)
    readonly property bool sereno: perfil === "sereno"

    // vigor do fogo: o perfil dá a base, o uso do processador soma
    readonly property real vigorAlvo: Math.min(1.9, ({ pororoca: 1.2, correnteza: 0.85, remanso: 0.55, sereno: 0.3 }[perfil] || 0.8) + carga * 0.006)
    property real vigor: vigorAlvo
    Behavior on vigor { NumberAnimation { duration: 2500; easing.type: Easing.InOutSine } }
    readonly property int faiscas: Math.round(Camadas.camadas.filter(c => c.tipo === "sp").length * Math.min(1, vigor / 1.3))
    readonly property int vagaLumes: Math.max(1, Math.ceil(Camadas.camadas.filter(c => c.tipo === "ff").length * bateria / 100))
    readonly property real forcaDoHalo: 0.45 + 0.55 * Math.min(1, bateria / 60)     // bateria baixa: a brasa esmorece

    // ---------------------------------------------------------------- ajudas
    function vaga(nome) {
        for (let i = 0; i < Camadas.camadas.length; i++)
            if (Camadas.camadas[i].tipo === "vaga" && Camadas.camadas[i].nome === nome) return i + 0.5
        return 0
    }
    function ordem(indice, tipo) {     // este é o enésimo recorte do seu tipo
        let n = 0
        for (let i = 0; i < indice; i++) if (Camadas.camadas[i].tipo === tipo) n++
        return n
    }
    function suave(u) { return u * u * (3 - 2 * u) }
    // quadros de animação tirados do CSS da arte: [fração, giro, escala x, escala y, opacidade]
    function quadro(nome, t) {
        const q = Camadas.quadros[nome]
        for (let i = 1; i < q.length; i++) {
            if (t <= q[i][0]) {
                const a = q[i - 1], b = q[i], u = suave((t - a[0]) / (b[0] - a[0]))
                const oa = a[4] === null ? 1 : a[4], ob = b[4] === null ? 1 : b[4]
                return [a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u, a[3] + (b[3] - a[3]) * u, oa + (ob - oa) * u]
            }
        }
        return [0, 1, 1, 1]
    }
    function entre(pontos, t) {        // interpolação suave numa tabela [[fração, valor…], …]
        for (let i = 1; i < pontos.length; i++) {
            if (t <= pontos[i][0]) {
                const a = pontos[i - 1], b = pontos[i], u = suave((t - a[0]) / (b[0] - a[0]))
                return a.map((v, k) => v + (b[k] - v) * u)
            }
        }
        return pontos[0]
    }
    readonly property var vooDoVagaLume: [[0, 0.08, 0, 0], [0.3, 0.75, 7, -5], [0.55, 0.25, 12, 2], [0.78, 0.7, 4, 6], [1, 0.08, 0, 0]]
    readonly property var pulsoDoHalo: [[0, 1], [0.23, 0.55], [0.47, 0.9], [0.71, 0.45], [1, 1]]

    // ---------------------------------------------------------------- o palco, do tamanho da arte
    Item {
        id: palco
        width: 1366; height: 768
        anchors.centerIn: parent
        scale: Math.max(cena.width / width, cena.height / height)     // cobre a tela inteira

        // ---- a arte do Brasa, camada por camada, na ordem de pintura
        Repeater {
            model: Camadas.camadas
            Image {
                id: peca
                required property var modelData
                required property int index
                readonly property string tipo: modelData.tipo
                readonly property int n: cena.ordem(index, tipo)
                readonly property real duracao: modelData.duracao || 4
                readonly property real fase0: (((-(modelData.atraso || 0) / duracao) % 1) + 1) % 1
                readonly property bool animada: tipo !== "parada" && tipo !== "vaga"
                property real fase: 0
                readonly property real t: (fase + fase0) % 1
                readonly property var q: tipo === "f" ? cena.quadro(modelData.quadros, t)
                                       : tipo === "breath" ? cena.quadro("breath", t) : null
                readonly property var voo: tipo === "ff" ? cena.entre(cena.vooDoVagaLume, t) : null

                z: index
                source: tipo === "vaga" ? "" : "../images/" + modelData.img
                asynchronous: false
                smooth: true
                x: (modelData.x || 0) + (tipo === "sp" ? modelData.dx * t : voo ? voo[2] : 0)
                y: (modelData.y || 0) + (tipo === "sp" ? modelData.dy * t : voo ? voo[3] : 0)
                width: modelData.w || 0
                height: modelData.h || 0
                visible: tipo === "sp" ? n < cena.faiscas && cena.mover
                       : tipo === "ff" ? n < cena.vagaLumes
                       : tipo !== "vaga"
                opacity: {
                    switch (tipo) {
                    case "f": return 1 - (1 - q[3]) * Math.min(1, cena.vigor)
                    case "breath": return q[3]
                    case "halo": return modelData.opacidade * cena.forcaDoHalo * cena.entre(cena.pulsoDoHalo, t)[1]
                    case "sp": return t < 0.1 ? t * 10 : t < 0.7 ? 1 - (t - 0.1) / 3 : 0.8 * (1 - (t - 0.7) / 0.3)
                    case "ff": return cena.mover ? voo[1] : 0.6
                    case "lid": return palpebra > 0 ? 1 : 0
                    }
                    return 1
                }
                // pálpebras: fechadas no Sereno; senão piscam uma vez a cada ciclo
                readonly property real palpebra: tipo !== "lid" ? 0
                    : cena.sereno ? 1
                    : !cena.mover ? 0
                    : t < 0.606 || t > 0.651 ? 0
                    : t < 0.619 ? 0.05 + 0.95 * (t - 0.606) / 0.013
                    : t < 0.627 ? 1
                    : 0.05 + 0.95 * (0.651 - t) / 0.024
                transform: [
                    Scale {
                        origin.x: peca.tipo === "f" ? peca.modelData.ox * peca.width : peca.width / 2
                        origin.y: peca.tipo === "f" ? peca.modelData.oy * peca.height : 0
                        xScale: peca.tipo === "f" ? 1 + (peca.q[1] - 1) * cena.vigor : peca.tipo === "sp" ? 1 - 0.7 * peca.t : 1
                        yScale: peca.tipo === "f" ? 1 + (peca.q[2] - 1) * cena.vigor
                              : peca.tipo === "sp" ? 1 - 0.7 * peca.t
                              : peca.tipo === "lid" ? Math.max(0.001, peca.palpebra) : 1
                    },
                    Rotation {
                        origin.x: peca.tipo === "f" ? peca.modelData.ox * peca.width : 0
                        origin.y: peca.tipo === "f" ? peca.modelData.oy * peca.height : 0
                        angle: peca.tipo === "f" ? peca.q[0] * cena.vigor : 0
                    }
                ]
                NumberAnimation on fase {
                    from: 0; to: 1
                    duration: peca.duracao * 1000
                    loops: Animation.Infinite
                    running: cena.mover && peca.animada
                }
            }
        }

        // ---- Cuca: a lua atravessa o céu ao longo do dia (meia-noite no alto)
        Image {
            id: lua
            readonly property real u: ((cena.hora + 12) % 24) / 24
            z: cena.vaga("ceu")
            source: "../images/" + Camadas.seres.lua.img
            width: Camadas.seres.lua.w; height: Camadas.seres.lua.h
            x: 20 + u * 520 - width / 2
            y: 190 - Math.sin(Math.PI * u) * 130 - height / 2
            opacity: 0.35 + 0.65 * Math.sin(Math.PI * u)
        }

        // ---- Mapinguari: o vulto está sempre lá; o olho abre quando o HD acorda
        Item {
            id: mapinguari
            z: cena.vaga("longe")
            x: 455; y: 200
            width: Camadas.seres.mapinguari.w; height: Camadas.seres.mapinguari.h
            Image {
                anchors.fill: parent
                source: "../images/" + Camadas.seres.mapinguari.img
                opacity: cena.mapinguari ? 1 : 0.6
                Behavior on opacity { NumberAnimation { duration: 1500 } }
            }
            Image {
                id: olho
                property real aberto: cena.mapinguari ? 1 : 0.07
                property real pisca: 1
                source: "../images/" + Camadas.seres.olho.img
                width: Camadas.seres.olho.w; height: Camadas.seres.olho.h
                x: 160 - width / 2; y: 52 - height / 2
                opacity: cena.mapinguari ? 1 : 0.28
                transform: Scale { origin.x: olho.width / 2; origin.y: olho.height / 2; yScale: olho.aberto * olho.pisca }
                Behavior on aberto { NumberAnimation { duration: 900; easing.type: Easing.OutCubic } }
                Behavior on opacity { NumberAnimation { duration: 900 } }
                SequentialAnimation on pisca {
                    running: cena.mover && cena.mapinguari
                    loops: Animation.Infinite
                    PauseAnimation { duration: 6200 }
                    NumberAnimation { to: 0.06; duration: 130 }
                    NumberAnimation { to: 1; duration: 190 }
                }
            }
        }

        // ---- Boitatá: a cobra de fogo desliza atrás dos troncos do meio
        Item {
            id: boitata
            property real passeio: 0
            property real tremor: 1
            z: cena.vaga("longe") + 0.1
            width: Camadas.seres.boitata.w; height: Camadas.seres.boitata.h
            x: 30 + passeio * 46
            y: 372 + Math.sin(passeio * Math.PI) * 10
            opacity: cena.boitata ? 1 : 0
            visible: opacity > 0.01
            Behavior on opacity { NumberAnimation { duration: 1800 } }
            Image {
                anchors.fill: parent
                source: "../images/" + Camadas.seres.boitata.img
                opacity: boitata.tremor
            }
            SequentialAnimation on passeio {
                running: cena.mover && cena.boitata
                loops: Animation.Infinite
                NumberAnimation { to: 1; duration: 5200; easing.type: Easing.InOutSine }
                NumberAnimation { to: -1; duration: 10400; easing.type: Easing.InOutSine }
                NumberAnimation { to: 0; duration: 5200; easing.type: Easing.InOutSine }
            }
            SequentialAnimation on tremor {
                running: cena.mover && cena.boitata
                loops: Animation.Infinite
                NumberAnimation { to: 0.84; duration: 420; easing.type: Easing.InOutSine }
                NumberAnimation { to: 1; duration: 610; easing.type: Easing.InOutSine }
            }
        }

        // ---- Iara: a lagoa, as ondas do Wi-Fi, os fogos azuis do Bluetooth e o salto do Boto
        Item {
            id: lagoa
            z: cena.vaga("perto")
            x: 236; y: 632
            width: Camadas.seres.lagoa.w; height: Camadas.seres.lagoa.h
            Image {
                anchors.fill: parent
                source: "../images/" + Camadas.seres.lagoa.img
                opacity: cena.iara ? 1 : 0.5
                Behavior on opacity { NumberAnimation { duration: 1500 } }
            }
            Repeater {      // as ondas saem de onde a Iara está
                model: 3
                Image {
                    id: onda
                    required property int index
                    property real cresce: cena.mover ? 0 : 0.35 + index * 0.25
                    source: "../images/" + Camadas.seres.onda.img
                    width: Camadas.seres.onda.w; height: Camadas.seres.onda.h
                    x: 118 - width / 2; y: 70 - height / 2
                    scale: 0.15 + cresce * 1.25
                    opacity: cena.iara ? 0.75 * (1 - cresce) : 0
                    SequentialAnimation on cresce {
                        running: cena.mover && cena.iara
                        loops: Animation.Infinite
                        PauseAnimation { duration: onda.index * 1300 }
                        NumberAnimation { from: 0; to: 1; duration: 3900; easing.type: Easing.OutQuad }
                    }
                }
            }
            Item {          // a Iara sobe da água
                x: 118 - width / 2; y: 70 - height
                width: Camadas.seres.iara.w; height: Camadas.seres.iara.h
                clip: true
                Image {
                    property real mergulho: cena.iara ? 0 : 1
                    source: "../images/" + Camadas.seres.iara.img
                    width: parent.width; height: parent.height
                    y: height * mergulho
                    Behavior on mergulho { NumberAnimation { duration: 2400; easing.type: Easing.InOutCubic } }
                }
            }
            Repeater {      // fogos azuis
                model: [{ x: 250, y: 6, t: 3100 }, { x: 318, y: 26, t: 4300 }, { x: 200, y: -22, t: 3700 }]
                Image {
                    id: fogo
                    required property var modelData
                    property real sobe: 0
                    source: "../images/" + Camadas.seres["fogo-azul"].img
                    width: Camadas.seres["fogo-azul"].w; height: Camadas.seres["fogo-azul"].h
                    x: modelData.x; y: modelData.y - sobe * 10
                    opacity: cena.fogoAzul ? 0.65 + 0.35 * sobe : 0
                    Behavior on opacity { NumberAnimation { duration: 1200 } }
                    SequentialAnimation on sobe {
                        running: cena.mover && cena.fogoAzul
                        loops: Animation.Infinite
                        NumberAnimation { to: 1; duration: fogo.modelData.t; easing.type: Easing.InOutSine }
                        NumberAnimation { to: 0; duration: fogo.modelData.t; easing.type: Easing.InOutSine }
                    }
                }
            }
            Image {         // o Boto
                id: boto
                property real salto: cena.mover ? 0 : 0.5
                source: "../images/" + Camadas.seres.boto.img
                width: Camadas.seres.boto.w; height: Camadas.seres.boto.h
                x: 150 + salto * 140          // salta da esquerda para a direita, de focinho para a frente
                y: 62 - height - Math.sin(salto * Math.PI) * 54
                rotation: (salto - 0.5) * 100
                opacity: cena.boto ? Math.min(1, Math.sin(salto * Math.PI) * 3) : 0
                SequentialAnimation on salto {
                    running: cena.mover && cena.boto
                    loops: Animation.Infinite
                    PauseAnimation { duration: 7000 }
                    NumberAnimation { from: 0; to: 1; duration: 1500; easing.type: Easing.InOutSine }
                }
            }
        }

        // ---- Saci: pulando dentro do redemoinho, com as folhas girando em volta
        Item {
            id: saci
            property real giro: 0
            property real pulo: 0
            z: cena.vaga("perto") + 0.1
            x: 36; y: 392
            width: Camadas.seres.redemoinho.w; height: Camadas.seres.redemoinho.h
            opacity: cena.saci ? 1 : 0
            visible: opacity > 0.01
            Behavior on opacity { NumberAnimation { duration: 1400 } }
            NumberAnimation on giro {
                running: cena.mover && cena.saci
                from: 0; to: Math.PI * 2; duration: 2600; loops: Animation.Infinite
            }
            SequentialAnimation on pulo {
                running: cena.mover && cena.saci
                loops: Animation.Infinite
                NumberAnimation { to: 1; duration: 330; easing.type: Easing.OutQuad }
                NumberAnimation { to: 0; duration: 330; easing.type: Easing.InQuad }
                PauseAnimation { duration: 500 }
            }
            Image {
                z: 1
                source: "../images/" + Camadas.seres.redemoinho.img
                anchors.fill: parent
                opacity: 0.9
                transform: Rotation { origin.x: saci.width / 2; origin.y: saci.height; angle: Math.sin(saci.giro) * 2.5 }
            }
            Image {
                z: 2
                source: "../images/" + Camadas.seres.saci.img
                width: Camadas.seres.saci.w; height: Camadas.seres.saci.h
                x: saci.width / 2 - width / 2 - 4
                y: saci.height - height - 4 - saci.pulo * 16
            }
            Repeater {      // folhas em órbita: mais largas no alto do funil
                model: 11
                Rectangle {
                    required property int index
                    readonly property real nivel: (index * 0.37) % 1
                    readonly property real angulo: saci.giro * (1 + (index % 3) * 0.5) + index * 1.9
                    readonly property real raio: 16 + 80 * nivel
                    z: Math.sin(angulo) > 0 ? 3 : 0
                    width: 11; height: 5; radius: 2.5
                    color: index % 3 === 0 ? "#C2513A" : index % 3 === 1 ? "#7A2E3A" : "#2B2466"
                    x: saci.width / 2 + raio * Math.cos(angulo) - width / 2
                    y: saci.height - 16 - 226 * nivel + raio * 0.28 * Math.sin(angulo)
                    rotation: angulo * 57.3 * 2
                }
            }
        }

        // ---- Caipora: a névoa cobre a mata e os olhos dela vigiam do mato
        Image {
            id: nevoa
            property real vento: 0
            z: cena.vaga("perto") + 0.2
            source: "../images/" + Camadas.seres.nevoa.img
            width: Camadas.seres.nevoa.w; height: Camadas.seres.nevoa.h
            x: -120 + vento * 60; y: 400
            opacity: cena.caipora
            visible: opacity > 0.01
            Behavior on opacity { NumberAnimation { duration: 2600 } }
            SequentialAnimation on vento {
                running: cena.mover && cena.caipora > 0
                loops: Animation.Infinite
                NumberAnimation { to: 1; duration: 16000; easing.type: Easing.InOutSine }
                NumberAnimation { to: 0; duration: 16000; easing.type: Easing.InOutSine }
            }
        }
        Image {
            id: olhosDaCaipora
            property real pisca: 1
            z: 1000
            source: "../images/" + Camadas.seres["olhos-caipora"].img
            width: Camadas.seres["olhos-caipora"].w * 0.62; height: Camadas.seres["olhos-caipora"].h * 0.62
            x: 150; y: 628
            opacity: cena.caipora >= 1 ? 1 : 0
            Behavior on opacity { NumberAnimation { duration: 1800 } }
            transform: Scale { origin.y: olhosDaCaipora.height / 2; yScale: olhosDaCaipora.pisca }
            SequentialAnimation on pisca {
                running: cena.mover && cena.caipora >= 1
                loops: Animation.Infinite
                PauseAnimation { duration: 4700 }
                NumberAnimation { to: 0.08; duration: 110 }
                NumberAnimation { to: 1; duration: 160 }
            }
        }

        // ---- o perfil tinge a mata: brasa na Pororoca, rio no Remanso, noite funda no Sereno
        Rectangle {
            z: 1001
            anchors.fill: parent
            color: ({ pororoca: "#FF7A45", remanso: "#2468B8", sereno: "#0B0717" }[cena.perfil] || "#000000")
            opacity: ({ pororoca: 0.07, remanso: 0.09, sereno: 0.3 }[cena.perfil] || 0)
            Behavior on opacity { NumberAnimation { duration: 2500 } }
            Behavior on color { ColorAnimation { duration: 2500 } }
        }
    }
}
