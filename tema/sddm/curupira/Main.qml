// Curupira OS: tela de login (SDDM). Segue o mockup mockup/Boot.dc.html.
// Só QtQuick puro, para não depender do Plasma na hora do login.
// Testar sem sair da sessão: sddm-greeter-qt6 --test-mode --theme tema/sddm/curupira

import QtQuick
import QtQuick.Controls
import QtQuick.Effects

Rectangle {
    id: raiz
    width: 1366
    height: 768
    color: "#241A4A"

    // tudo foi desenhado para 1366×768 e escala junto com a tela
    readonly property real s: Math.min(width / 1366, height / 768)
    readonly property string tinta: "#1E2A24"
    readonly property string tintaSuave: "#5B6A61"
    readonly property string verde: "#12935F"
    readonly property string areia: "#FBF4E8"
    readonly property string brasa: "#C2410C"

    property int indiceUsuario: 0
    property string usuario: ""
    property string icone: ""
    property int indiceSessao: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property string nomeSessao: ""
    property bool entrando: false
    property string erro: ""

    FontLoader { id: baloo; source: "fontes/Baloo2.ttf" }
    FontLoader { id: nunito; source: "fontes/Nunito.ttf" }

    function fonteTitulo(tamanho) {
        return { family: baloo.name, pixelSize: Math.round(tamanho * s), weight: Font.ExtraBold, variableAxes: { "wght": 800 } }
    }

    // usuários: começa pelo último que entrou
    Repeater {
        id: usuarios
        model: userModel
        delegate: Item {
            required property int index
            required property string name
            required property string icon
            Component.onCompleted: {
                if (name === userModel.lastUser || (raiz.usuario === "" && index === 0)) {
                    raiz.indiceUsuario = index
                    raiz.usuario = name
                    raiz.icone = raiz.fotoPropria(icon)
                }
            }
        }
    }
    // o rosto genérico do SDDM vira o Cordel
    function fotoPropria(caminho) {
        const c = String(caminho || "")
        return (c === "" || c.indexOf("/sddm/faces/") >= 0) ? "" : c
    }

    function trocaUsuario() {
        if (usuarios.count < 2) return
        indiceUsuario = (indiceUsuario + 1) % usuarios.count
        const item = usuarios.itemAt(indiceUsuario)
        usuario = item.name
        icone = fotoPropria(item.icon)
        senha.text = ""
        erro = ""
        senha.forceActiveFocus()
    }

    Repeater {
        id: sessoes
        model: sessionModel
        delegate: Item {
            required property int index
            required property string name
            Component.onCompleted: if (index === raiz.indiceSessao) raiz.nomeSessao = name
        }
    }

    function entra() {
        if (entrando || senha.text === "") return
        entrando = true
        erro = ""
        sddm.login(usuario, senha.text, indiceSessao)
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            raiz.entrando = false
            raiz.erro = "A mata não reconheceu essa senha. Tente de novo."
            senha.text = ""
            senha.forceActiveFocus()
            tremida.start()
        }
        function onLoginSucceeded() { raiz.entrando = false }
    }

    // fundo: o Curupira de cabelo de fogo (fica à direita; o formulário vai na mata escura, à esquerda)
    Image {
        anchors.fill: parent
        source: config.background || "fundo.png"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
    }

    // relógio
    Column {
        x: 0
        y: 56 * s
        width: 760 * s
        spacing: -30 * s   // a Baloo 2 deixa muito espaço embaixo dos números
        Text {
            id: hora
            anchors.horizontalCenter: parent.horizontalCenter
            color: "#FFFFFF"
            font: raiz.fonteTitulo(120)
            text: Qt.formatTime(new Date(), "HH:mm")
            layer.enabled: true
            layer.effect: MultiEffect { shadowEnabled: true; shadowColor: "#80140A28"; shadowBlur: 0.8; shadowVerticalOffset: 4 }
        }
        Text {
            id: data
            anchors.horizontalCenter: parent.horizontalCenter
            color: "#FFFFFF"
            font { family: nunito.name; pixelSize: Math.round(22 * s); weight: Font.Bold; variableAxes: { "wght": 700 } }
            text: Qt.locale("pt_BR").toString(new Date(), "dddd, d 'de' MMMM")
            layer.enabled: true
            layer.effect: MultiEffect { shadowEnabled: true; shadowColor: "#99140A28"; shadowBlur: 0.6; shadowVerticalOffset: 2 }
        }
        Timer {
            interval: 1000; running: true; repeat: true
            onTriggered: {
                const agora = new Date()
                hora.text = Qt.formatTime(agora, "HH:mm")
                data.text = Qt.locale("pt_BR").toString(agora, "dddd, d 'de' MMMM")
            }
        }
    }

    // sombra do cartão, à parte: o efeito recorta o que passa da borda, e o avatar passa
    Rectangle {
        x: cartao.x; y: cartao.y; width: cartao.width; height: cartao.height
        radius: cartao.radius
        color: "#FFFFFF"
        layer.enabled: true
        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: "#73140A28"; shadowBlur: 1.0; shadowVerticalOffset: 24 * s }
    }

    // cartão de login
    Rectangle {
        id: cartao
        x: 200 * s
        y: 340 * s
        width: 360 * s
        height: conteudo.implicitHeight + 50 * s
        radius: 26 * s
        color: "#FFFFFF"

        SequentialAnimation {
            id: tremida
            loops: 2
            NumberAnimation { target: cartao; property: "x"; to: 190 * s; duration: 50 }
            NumberAnimation { target: cartao; property: "x"; to: 210 * s; duration: 80 }
            NumberAnimation { target: cartao; property: "x"; to: 200 * s; duration: 50 }
        }

        Column {
            id: conteudo
            x: 28 * s
            y: 26 * s
            width: parent.width - 56 * s
            spacing: 14 * s

            // avatar: a foto do usuário, ou o Cordel
            Item {
                width: parent.width
                height: 104 * s - 78 * s
                Rectangle {
                    width: 116 * s; height: 116 * s; radius: width / 2
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: -78 * s - 6 * s
                    color: "#FFFFFF"
                    Rectangle {
                        anchors.centerIn: parent
                        width: 104 * s; height: 104 * s; radius: width / 2
                        clip: true
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0; color: "#FFD08A" }
                            GradientStop { position: 1; color: "#FF7A45" }
                        }
                        Image {
                            id: foto
                            anchors.fill: parent
                            source: raiz.icone !== "" ? raiz.icone : "avatar.svg"
                            sourceSize: Qt.size(208, 208)
                            fillMode: Image.PreserveAspectCrop
                            onStatusChanged: if (status === Image.Error) source = "avatar.svg"
                            layer.enabled: true
                            layer.effect: MultiEffect {
                                maskEnabled: true
                                maskSource: mascara
                            }
                        }
                        Rectangle { id: mascara; anchors.fill: parent; radius: width / 2; visible: false; layer.enabled: true }
                    }
                }
            }

            Column {
                width: parent.width
                spacing: 2 * s
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: raiz.usuario
                    color: raiz.tinta
                    font: raiz.fonteTitulo(26)
                    MouseArea {
                        anchors.fill: parent
                        enabled: usuarios.count > 1
                        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                        onClicked: raiz.trocaUsuario()
                    }
                }
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: usuarios.count > 1 ? "Peça licença para entrar na mata · clique no nome para trocar"
                                             : "Peça licença para entrar na mata"
                    color: raiz.tintaSuave
                    font { family: nunito.name; pixelSize: Math.round(14 * s) }
                }
            }

            Column {
                width: parent.width
                spacing: 6 * s
                Text {
                    text: "Senha"
                    color: "#3E4C44"
                    font { family: nunito.name; pixelSize: Math.round(13 * s); weight: Font.Bold; variableAxes: { "wght": 700 } }
                }
                Row {
                    width: parent.width
                    spacing: 8 * s
                    TextField {
                        id: senha
                        width: parent.width - botaoEntrar.width - parent.spacing
                        height: 46 * s
                        echoMode: TextInput.Password
                        placeholderText: "sua oferenda"
                        placeholderTextColor: "#8A968F"
                        color: raiz.tinta
                        font { family: nunito.name; pixelSize: Math.round(15 * s) }
                        leftPadding: 14 * s
                        focus: true
                        enabled: !raiz.entrando
                        Accessible.name: "Senha"
                        background: Rectangle {
                            radius: 14 * s
                            color: raiz.areia
                            border.width: 2 * s
                            border.color: raiz.erro !== "" ? raiz.brasa : (senha.activeFocus ? raiz.verde : "#E2D7C3")
                        }
                        onAccepted: raiz.entra()
                        onTextChanged: if (text !== "") raiz.erro = ""
                    }
                    Rectangle {
                        id: botaoEntrar
                        width: 46 * s; height: 46 * s; radius: 14 * s
                        color: entrarArea.pressed ? "#0F7A54" : raiz.verde
                        opacity: raiz.entrando ? 0.6 : 1
                        Accessible.role: Accessible.Button
                        Accessible.name: "Entrar"
                        Image { anchors.centerIn: parent; source: "icones/seta.svg"; width: 22 * s; height: 22 * s; sourceSize: Qt.size(44, 44) }
                        MouseArea { id: entrarArea; anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: raiz.entra() }
                    }
                }
            }

            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                text: raiz.erro !== "" ? raiz.erro
                      : keyboard.capsLock ? "Caps Lock ligado"
                      : raiz.entrando ? "Entrando na mata…"
                      : (raiz.nomeSessao !== "" ? "Sessão: " + raiz.nomeSessao : "")
                color: raiz.erro !== "" || keyboard.capsLock ? raiz.brasa : raiz.tintaSuave
                font { family: nunito.name; pixelSize: Math.round(13 * s); weight: raiz.erro !== "" ? Font.Bold : Font.Normal }
            }
        }
    }

    // canto inferior esquerdo: nome e versão
    Rectangle {
        x: 20 * s
        y: parent.height - height - 20 * s
        height: 52 * s
        width: marca.implicitWidth + 32 * s
        radius: 18 * s
        color: "#FFFFFF"
        layer.enabled: true
        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: "#66140A28"; shadowBlur: 0.8; shadowVerticalOffset: 12 * s }
        Row {
            id: marca
            anchors.centerIn: parent
            spacing: 10 * s
            Text {
                anchors.verticalCenter: parent.verticalCenter
                textFormat: Text.StyledText
                text: "Curupira<font color='#FF7A45'>OS</font>"
                color: raiz.tinta
                font: raiz.fonteTitulo(18)
            }
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: config.versao || "0.1 Pororoca"
                color: raiz.tintaSuave
                font { family: nunito.name; pixelSize: Math.round(13 * s) }
            }
        }
    }

    // canto inferior direito: suspender, reiniciar, desligar
    Rectangle {
        x: parent.width - width - 20 * s
        y: parent.height - height - 20 * s
        height: 52 * s
        width: energia.implicitWidth + 16 * s
        visible: sddm.canSuspend || sddm.canReboot || sddm.canPowerOff
        radius: 18 * s
        color: "#FFFFFF"
        layer.enabled: true
        layer.effect: MultiEffect { shadowEnabled: true; shadowColor: "#66140A28"; shadowBlur: 0.8; shadowVerticalOffset: 12 * s }
        Row {
            id: energia
            anchors.centerIn: parent
            spacing: 6 * s
            Repeater {
                model: [
                    { icone: "icones/suspender.svg", nome: "Suspender", pode: sddm.canSuspend, acao: "suspender", fundo: "#F3EEE4" },
                    { icone: "icones/reiniciar.svg", nome: "Reiniciar", pode: sddm.canReboot, acao: "reiniciar", fundo: "#F3EEE4" },
                    { icone: "icones/desligar.svg", nome: "Desligar", pode: sddm.canPowerOff, acao: "desligar", fundo: "#FFE1D6" }
                ]
                delegate: Rectangle {
                    required property var modelData
                    visible: modelData.pode
                    width: 40 * s; height: 40 * s; radius: 13 * s
                    color: area.containsMouse ? Qt.darker(modelData.fundo, 1.06) : modelData.fundo
                    Accessible.role: Accessible.Button
                    Accessible.name: modelData.nome
                    Image { anchors.centerIn: parent; source: modelData.icone; width: 20 * s; height: 20 * s; sourceSize: Qt.size(40, 40) }
                    MouseArea {
                        id: area
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (modelData.acao === "suspender") sddm.suspend()
                            else if (modelData.acao === "reiniciar") sddm.reboot()
                            else sddm.powerOff()
                        }
                    }
                    ToolTip.visible: area.containsMouse
                    ToolTip.text: modelData.nome
                }
            }
        }
    }

    Component.onCompleted: senha.forceActiveFocus()
}
