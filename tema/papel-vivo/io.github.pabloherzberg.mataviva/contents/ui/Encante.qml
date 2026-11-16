// Encante: a cidade dos botos, suspensa na mata alagada do rio. É a terceira cena do Mata Viva.
// Só QtQuick, para poder ser vista fora do Plasma (ferramentas/ver-papel-vivo.py --arte encante).
//
// O desenho e as camadas vêm de tema/gerar-encante.py. Todo o movimento é calculado na placa de vídeo
// (tema/papel-vivo/encante/*.vert e *.frag): daqui só sai o relógio, uma vez por quadro da tela.
// Fazer as contas de posição em QML, item por item, custava mais de meio núcleo do processador.
//
// O que o computador muda na cena:
//   perfil de energia   o quanto a cidade está acesa (Pororoca: toda; Sereno: quase apagada)
//   laboratório de rede com ele ligado, mais botos rondam as casas
//   mover = falso       tudo para onde está (bateria, Remanso/Sereno, janela por cima)

import QtQuick
import "EncanteRecortes.js" as Recortes

Item {
    id: cena
    clip: true

    property var estado: ({})       // o que "curupira json" devolve
    property bool mover: true
    property string arte: "encante" // só para ter a mesma cara da Cena.qml
    property real hora: 0

    property real t: 0              // segundos de cena em movimento; recomeça a cada duas horas, para a conta não perder precisão
    FrameAnimation { running: cena.mover; onTriggered: cena.t = (cena.t + Math.min(frameTime, 0.1)) % 7200 }

    readonly property string perfil: String(estado.perfil || "")
    readonly property bool laboratorio: !!estado.lab
    property real acesa: ({ pororoca: 1.0, correnteza: 0.88, remanso: 0.62, sereno: 0.34 })[perfil] || 0.88
    Behavior on acesa { NumberAnimation { duration: 3000; easing.type: Easing.InOutQuad } }

    // camada com imagem. Parada por padrão; os campos dizem como ela se mexe (ver camada.vert)
    component Camada: ShaderEffect {
        property string arquivo
        property variant source: Image { source: "../images/encante/" + arquivo + ".png"; visible: false }
        property real tempo: cena.t
        property real copia: 0
        property real faseVai: 0
        property vector2d anda: Qt.vector2d(0, 0)
        property vector2d emenda: Qt.vector2d(0, 0)
        property vector4d vaiVem: Qt.vector4d(0, 0, 0, 0)
        property vector4d balanco: Qt.vector4d(0, 0, 0, 0)
        property vector4d pisca: Qt.vector4d(1, 0, 0, 0)
        x: Recortes.caixa[arquivo][0]; y: Recortes.caixa[arquivo][1]
        width: Recortes.caixa[arquivo][2]; height: Recortes.caixa[arquivo][3]
        mesh: GridMesh { resolution: balanco.x !== 0 ? Qt.size(Math.max(4, Math.round(width / 34)), Math.max(4, Math.round(height / 32))) : Qt.size(1, 1) }
        vertexShader: "encante/camada.vert.qsb"
        fragmentShader: "encante/camada.frag.qsb"
    }
    component Parada: Image {
        property string arquivo
        source: "../images/encante/" + arquivo + ".png"
        x: Recortes.caixa[arquivo][0]; y: Recortes.caixa[arquivo][1]
    }
    // camada que anda sem parar e recomeça do outro lado: duas cópias emendadas
    component Esteira: Item {
        id: e
        property string arquivo
        property real vx: 0
        property real vy: 0
        property vector4d vaiVem: Qt.vector4d(0, 0, 0, 0)
        Repeater {
            model: 2
            Camada {
                required property int index
                arquivo: e.arquivo
                copia: index
                anda: Qt.vector2d(e.vx, e.vy)
                emenda: Qt.vector2d(e.vx !== 0 ? 1366 : 0, e.vy !== 0 ? 768 : 0)
                vaiVem: e.vaiVem
            }
        }
    }
    component Boto: ShaderEffect {
        property variant source: botoImg
        property real tempo: cena.t
        property real modo: 0
        property real amplitude: 15
        property real batida: 2.6
        property vector4d ciclo: Qt.vector4d(56, 0, 24, 0)
        property vector4d a
        property vector4d b
        width: botoImg.width; height: botoImg.height
        mesh: GridMesh { resolution: Qt.size(48, 2) }
        vertexShader: "encante/boto.vert.qsb"
        fragmentShader: "encante/boto.frag.qsb"
    }
    component Morador: Boto {       // boto pequeno rondando: centro, raios, período, atraso, escala
        modo: 1; batida: 1.9; opacity: 0.85
    }
    component Rua: ShaderEffect {
        property real tempo: cena.t
        property real n: 18
        property real dura: 46
        property vector2d origem: Qt.vector2d(x, y)
        property vector2d tamanho: Qt.vector2d(width, height)
        property vector2d raios: Qt.vector2d(5, 10)
        property vector2d p0; property vector2d p1; property vector2d p2; property vector2d p3
        fragmentShader: "encante/rua.frag.qsb"
    }

    // a cena foi desenhada em 1366×768: cobre a tela inteira, cortando o que sobrar
    Item {
        id: palco
        width: 1366; height: 768
        anchors.centerIn: parent
        scale: Math.max(cena.width / 1366, cena.height / 768)

        Image { id: botoImg; source: "../images/encante/boto.png"; visible: false }

        Parada { arquivo: "fundo" }

        // a superfície vista de baixo: três faixas de brilho indo e vindo em tempos diferentes
        Camada { arquivo: "superficie-0"; vaiVem: Qt.vector4d(90, 1.5, 20.7, 5.4); pisca: Qt.vector4d(0.82, 0.18, 4.05, 1.0) }
        Camada { arquivo: "superficie-1"; vaiVem: Qt.vector4d(-70, 1.5, 15.0, 3.9); faseVai: 2.0; pisca: Qt.vector4d(0.82, 0.18, 2.9, 3.0) }
        Camada { arquivo: "superficie-2"; vaiVem: Qt.vector4d(46, 1.5, 9.9, 2.6); faseVai: 4.1; pisca: Qt.vector4d(0.82, 0.18, 1.9, 5.1) }

        // a luz que desce da superfície
        ShaderEffect {
            width: 1366; height: 768
            property real tempo: cena.t
            property real largura: width
            property real altura: height
            property real forca: 0.45
            fragmentShader: "encante/raios.frag.qsb"
        }

        Parada { arquivo: "cidade-longe" }
        Esteira { arquivo: "cardume-fundo"; vx: 16; vaiVem: Qt.vector4d(0, 5, 0, 13) }

        Morador { a: Qt.vector4d(860, 330, 250, 60); b: Qt.vector4d(47, 1.0, 0.12, 0); opacity: 0.7 }
        Morador { a: Qt.vector4d(760, 520, 200, 40); b: Qt.vector4d(39, 3.6, 0.10, 0); opacity: 0.65; visible: cena.laboratorio }

        // O Boto dá a volta na cidade: aqui ele volta ao longe, entre as casas de trás e as da frente
        Boto { ciclo: Qt.vector4d(56, 24, 28, 0); a: Qt.vector4d(1496, 300, -130, 390); b: Qt.vector4d(16, 4, 0.34, -1); batida: 3.2; opacity: 0.82 }

        Parada { arquivo: "cidade-perto" }
        Camada { arquivo: "algas"; balanco: Qt.vector4d(2.2, 6.1, 0, 0) }

        // luzes da cidade: quatro grupos, cada um cintilando no seu ritmo; o perfil de energia diz o quanto acendem
        Camada { arquivo: "luz-0"; pisca: Qt.vector4d(0.74 * cena.acesa, 0.20 * cena.acesa, 3.1, 0.0) }
        Camada { arquivo: "luz-1"; pisca: Qt.vector4d(0.74 * cena.acesa, 0.20 * cena.acesa, 4.3, 1.7) }
        Camada { arquivo: "luz-2"; pisca: Qt.vector4d(0.74 * cena.acesa, 0.20 * cena.acesa, 5.9, 3.3) }
        Camada { arquivo: "luz-3"; pisca: Qt.vector4d(0.74 * cena.acesa, 0.20 * cena.acesa, 7.3, 5.0) }

        Morador { a: Qt.vector4d(1000, 200, 230, 70); b: Qt.vector4d(34, 0.4, 0.19, 0) }
        Morador { a: Qt.vector4d(640, 470, 260, 90); b: Qt.vector4d(43, 2.4, 0.16, 0); visible: cena.laboratorio }

        // as "ruas": luzes vivas correndo por três curvas
        Rua { x: 600; y: 210; width: 620; height: 470; n: 20; dura: 46; raios: Qt.vector2d(4.5, 10)
              p0: Qt.vector2d(1180, 250); p1: Qt.vector2d(1000, 420); p2: Qt.vector2d(760, 470); p3: Qt.vector2d(640, 640) }
        Rua { x: 480; y: 90; width: 680; height: 200; n: 18; dura: 58; raios: Qt.vector2d(4, 8)
              p0: Qt.vector2d(520, 150); p1: Qt.vector2d(700, 250); p2: Qt.vector2d(900, 120); p3: Qt.vector2d(1120, 150) }
        Rua { x: 250; y: 480; width: 840; height: 260; n: 16; dura: 38; raios: Qt.vector2d(7, 15)
              p0: Qt.vector2d(300, 620); p1: Qt.vector2d(520, 520); p2: Qt.vector2d(760, 600); p3: Qt.vector2d(1040, 690) }

        Esteira { arquivo: "cardume-perto"; vx: -26; vaiVem: Qt.vector4d(0, 7, 0, 13) }

        // …e aqui passa de perto, da esquerda para a direita
        Boto { ciclo: Qt.vector4d(56, 0, 24, 0); a: Qt.vector4d(-360, 400, 1726, 250); b: Qt.vector4d(24, 3, 0.98, 1) }

        Parada { arquivo: "moldura" }
        Camada { arquivo: "franjas"; balanco: Qt.vector4d(2.6, 7.4, 0, 1.3) }
        Camada { arquivo: "regias"; balanco: Qt.vector4d(7, 8.6, 1, 0) }

        // luzes vivas soltas piscam e boiam; a poeira do rio deriva; as bolhas sobem
        Camada { arquivo: "bio"; vaiVem: Qt.vector4d(5, 7, 17, 12); pisca: Qt.vector4d(0.72, 0.28, 4.7, 0.5) }
        Esteira { arquivo: "poeira"; vx: 7; vaiVem: Qt.vector4d(0, 5, 0, 13) }
        Esteira { arquivo: "bolhas"; vy: -22; vaiVem: Qt.vector4d(6, 0, 5, 0) }
        Parada { arquivo: "vinheta" }
    }
}
