// Curupira OS: tela de abertura do Plasma (KSplash), logo depois do login.
// Continua a tela de boot: o mesmo retrato e as mesmas pegadas (images/ vem de
// tema/plymouth/curupira, copiado pelo instalar.sh). Aqui cada pegada fica acesa
// conforme o Plasma avança: são 6 etapas (stage), e da 2 à 6 acende uma pegada.
// Testar numa janela: ksplashqml --test --window <pasta do tema global>

import QtQuick

Rectangle {
    id: root
    property int stage

    gradient: Gradient {
        GradientStop { position: 0; color: "#100b21" }
        GradientStop { position: 1; color: "#0b0717" }
    }

    // a arte tem 800×1000; tudo escala junto com o retrato
    readonly property real escala: Math.min(height / 1000, width / 800)
    readonly property real rx: (width - 800 * escala) / 2
    readonly property real ry: (height - 1000 * escala) / 2
    // centro de cada pegada na arte (tema/plymouth/curupira/posicoes.txt)
    readonly property var pegadas: [[297, 919], [349, 937], [401, 919], [453, 937], [505, 919]]

    FontLoader { id: nunito; source: "images/Nunito.ttf" }

    Item {
        id: cena
        anchors.fill: parent
        opacity: 0
        Behavior on opacity { NumberAnimation { duration: 600; easing.type: Easing.OutCubic } }

        Image {
            x: root.rx; y: root.ry
            width: 800 * root.escala; height: 1000 * root.escala
            source: "images/retrato.png"
            asynchronous: true
            smooth: true
            mipmap: true
        }

        Repeater {
            model: root.pegadas.length
            delegate: Image {
                required property int index
                readonly property bool acesa: root.stage >= index + 2
                readonly property bool ultima: root.stage === index + 2
                x: root.rx + (root.pegadas[index][0] - 44) * root.escala
                y: root.ry + (root.pegadas[index][1] - 30) * root.escala
                width: 88 * root.escala; height: 60 * root.escala
                source: "images/pegada" + index + ".png"
                smooth: true
                opacity: acesa ? 1 : 0.12
                Behavior on opacity { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
                // a pegada mais nova pulsa, como brasa
                SequentialAnimation on scale {
                    running: ultima
                    loops: Animation.Infinite
                    NumberAnimation { to: 1.12; duration: 450; easing.type: Easing.InOutSine }
                    NumberAnimation { to: 1.0; duration: 450; easing.type: Easing.InOutSine }
                }
            }
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            y: root.ry + 988 * root.escala - height / 2
            text: root.stage >= 6 ? "Pronto. Bem-vindo à mata!" : "Entrando na mata…"
            color: "#F3EEE4"
            opacity: 0.85
            font { family: nunito.name; pixelSize: Math.max(13, Math.round(17 * root.escala)); weight: Font.Bold }
            Accessible.role: Accessible.StaticText
            Accessible.name: text
        }
    }

    onStageChanged: if (stage >= 1) cena.opacity = 1
    Component.onCompleted: if (stage >= 1) cena.opacity = 1
}
