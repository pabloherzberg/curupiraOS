// Curupira: widget do painel da Curupira OS.
// No painel: um quadrado na cor do perfil. Ao clicar: o cartão rápido do mockup/Desktop.dc.html,
// com bateria e perfil, os seis seres (que acendem quando ligados), volume e brilho, e o último
// aviso automático. Lê tudo com "curupira json" e age com comandos simples.

import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.plasma.extras as PlasmaExtras
import org.kde.plasma.plasma5support as P5Support
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    property var estado: ({})
    property string mensagem: ""
    property bool mensagemErro: false

    readonly property var cores: ({
        pororoca: "#FF7A45", correnteza: "#2BB37A", remanso: "#2468B8", sereno: "#5B3A8E"
    })
    readonly property var ordem: ["pororoca", "correnteza", "remanso", "sereno"]
    readonly property string perfil: estado.perfil || ""
    readonly property color corPerfil: cores[perfil] || "#5B6A61"
    readonly property var perfisOrdenados: (estado.perfis || []).slice().sort((a, b) => {
        const ia = ordem.indexOf(a.id), ib = ordem.indexOf(b.id)
        return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib)
    })

    // cor com transparência (Qt.alpha só existe em Qt mais novo)
    function alfa(c, a) { const k = Qt.color(c); return Qt.rgba(k.r, k.g, k.b, a) }

    function nomePerfil(id) {
        const p = (estado.perfis || []).find(q => q.id === id)
        return p ? p.nome : id
    }
    function horas(h) {
        const hh = Math.floor(h), mm = Math.round((h - hh) * 60)
        return mm === 60 ? `${hh + 1}h00` : `${hh}h${mm < 10 ? "0" : ""}${mm}`
    }
    function linhaEnergia() {
        if (estado.bateria === undefined) return "sem dados do curupira"
        if (estado.fonte === "bateria" && estado.watts > 0)
            return `bateria ${estado.bateria}% · cerca de ${horas(estado.capacidade_wh * estado.bateria / 100 / estado.watts)}`
        return `na tomada · bateria ${estado.bateria}%`
    }
    function quandoFoi(t) {
        const s = Math.max(0, Date.now() / 1000 - t)
        if (s < 90) return "agora há pouco"
        if (s < 3600) return `há ${Math.round(s / 60)} min`
        if (s < 86400) return `há ${Math.round(s / 3600)} h`
        return `há ${Math.round(s / 86400)} dias`
    }

    toolTipMainText: perfil ? `Curupira: ${nomePerfil(perfil)}` : "Curupira"
    toolTipSubText: linhaEnergia()
    Plasmoid.icon: "battery-good"

    // ---------------------------------------------------------------- comandos
    P5Support.DataSource {
        id: executor
        engine: "executable"
        connectedSources: []
        property var mensagens: ({})
        onNewData: (fonte, dados) => {
            disconnectSource(fonte)
            if (fonte === "curupira json") {
                try { root.estado = JSON.parse(dados["stdout"]) } catch (e) { root.estado = ({}) }
                return
            }
            const ok = dados["exit code"] === 0
            const err = (dados["stderr"] || "").trim().split("\n").pop()
            if (mensagens[fonte] !== undefined) {
                root.mensagemErro = !ok
                root.mensagem = ok ? mensagens[fonte] : (err || "Não deu certo.")
                delete mensagens[fonte]
            }
            root.atualiza()
        }
    }
    function roda(cmd, msg) {
        if (msg !== undefined) executor.mensagens[cmd] = msg
        executor.connectSource(cmd)
    }
    function atualiza() { roda("curupira json") }

    Timer {
        interval: root.expanded ? 3000 : 20000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: root.atualiza()
    }
    onExpandedChanged: if (expanded) { mensagem = ""; atualiza() }

    // ---------------------------------------------------------------- no painel
    compactRepresentation: MouseArea {
        id: compacto
        hoverEnabled: true
        onClicked: root.expanded = !root.expanded
        Accessible.name: root.toolTipMainText
        Accessible.role: Accessible.Button

        Rectangle {
            anchors.centerIn: parent
            width: Math.round(Math.min(parent.width, parent.height) * 0.74)
            height: width
            radius: width * 0.31
            gradient: Gradient {
                GradientStop { position: 0; color: Qt.lighter(root.corPerfil, 1.35) }
                GradientStop { position: 1; color: root.corPerfil }
            }
            scale: compacto.containsMouse ? 1.08 : 1
            Behavior on scale { NumberAnimation { duration: 160; easing.type: Easing.OutCubic } }
            PlasmaComponents.Label {
                anchors.centerIn: parent
                text: root.perfil ? root.nomePerfil(root.perfil).charAt(0) : "?"
                color: "#FFFFFF"
                font.bold: true
                font.pixelSize: parent.height * 0.5
            }
        }
    }

    // ---------------------------------------------------------------- cartão rápido
    fullRepresentation: PlasmaExtras.Representation {
        Layout.minimumWidth: Kirigami.Units.gridUnit * 21
        Layout.preferredWidth: Kirigami.Units.gridUnit * 21
        Layout.preferredHeight: implicitHeight

        readonly property color neutro: root.alfa(Kirigami.Theme.textColor, 0.07)
        readonly property color suave: root.alfa(Kirigami.Theme.textColor, 0.62)

        contentItem: ColumnLayout {
            spacing: Kirigami.Units.largeSpacing

            // cabeçalho: avatar, nome, bateria e o perfil
            RowLayout {
                spacing: Kirigami.Units.largeSpacing
                Layout.fillWidth: true
                Kirigami.ShadowedImage {
                    implicitWidth: Kirigami.Units.gridUnit * 2.6
                    implicitHeight: implicitWidth
                    radius: width / 2
                    color: "#FFE6D6"
                    source: "file:///usr/local/share/curupira/toca/arte/cordel-busto.svg"
                    sourceSize: Qt.size(96, 96)
                    fillMode: Image.PreserveAspectCrop
                }
                ColumnLayout {
                    spacing: 0
                    Layout.fillWidth: true
                    PlasmaComponents.Label { text: root.estado.usuario || "curupira"; font.bold: true; Layout.fillWidth: true }
                    PlasmaComponents.Label { text: root.linhaEnergia(); color: suave; Layout.fillWidth: true; elide: Text.ElideRight }
                }
                Rectangle {
                    visible: root.perfil !== ""
                    implicitWidth: pilula.implicitWidth + Kirigami.Units.largeSpacing * 1.5
                    implicitHeight: pilula.implicitHeight + Kirigami.Units.smallSpacing * 1.5
                    radius: height / 2.4
                    color: root.alfa(root.corPerfil, 0.16)
                    PlasmaComponents.Label {
                        id: pilula
                        anchors.centerIn: parent
                        text: root.nomePerfil(root.perfil)
                        color: root.corPerfil
                        font.bold: true
                        font.pointSize: Kirigami.Theme.smallFont.pointSize
                    }
                }
            }

            // perfis: um toque troca
            RowLayout {
                spacing: Kirigami.Units.smallSpacing
                Layout.fillWidth: true
                Repeater {
                    model: root.perfisOrdenados
                    delegate: Rectangle {
                        required property var modelData
                        readonly property bool atual: modelData.id === root.perfil
                        readonly property color cor: root.cores[modelData.id] || "#5B6A61"
                        Layout.fillWidth: true
                        implicitHeight: Kirigami.Units.gridUnit * 1.9
                        radius: Kirigami.Units.cornerRadius * 2
                        color: atual ? cor : (area.containsMouse ? root.alfa(cor, 0.18) : neutro)
                        Accessible.role: Accessible.Button
                        Accessible.name: `Perfil ${modelData.nome}` + (atual ? ", ativo" : "")
                        PlasmaComponents.Label {
                            anchors.centerIn: parent
                            text: modelData.nome
                            color: parent.atual ? "#FFFFFF" : Kirigami.Theme.textColor
                            font.bold: parent.atual
                            font.pointSize: Kirigami.Theme.smallFont.pointSize
                        }
                        MouseArea {
                            id: area
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: if (!parent.atual) root.roda("curupira " + parent.modelData.id, `Perfil ${parent.modelData.nome} aplicado.`)
                        }
                    }
                }
            }

            // os seis seres
            GridLayout {
                columns: 2
                rowSpacing: Kirigami.Units.smallSpacing * 2
                columnSpacing: Kirigami.Units.smallSpacing * 2
                Layout.fillWidth: true
                Repeater {
                    model: [
                        { nome: "Iara · Wi-Fi", icone: "iara", cor: "#2468B8",
                          ligado: !!root.estado.wifi, existe: root.estado.tem_wifi !== false,
                          texto: root.estado.wifi ? (root.estado.rede || "ligado") : "desligado",
                          acao: root.estado.wifi ? "nmcli radio wifi off" : "nmcli radio wifi on",
                          msg: root.estado.wifi ? "A Iara silenciou o Wi-Fi." : "A Iara voltou a ouvir o Wi-Fi." },
                        { nome: "Bluetooth", icone: "bluetooth", cor: "#3A5EB8",
                          ligado: !!root.estado.bluetooth, existe: root.estado.tem_bluetooth !== false,
                          texto: root.estado.bluetooth ? "ligado" : "desligado",
                          acao: root.estado.bluetooth ? "bluetoothctl power off"
                                                      : "sh -c 'rfkill unblock bluetooth && sleep 1 && bluetoothctl power on'",
                          msg: root.estado.bluetooth ? "Bluetooth desligado." : "Bluetooth ligado." },
                        { nome: "Boitatá · GPU", icone: "boitata", cor: "#C2261A",
                          ligado: root.estado.boitata_dormindo === false, existe: true,
                          texto: root.estado.boitata_dormindo === false ? "acordada" : "dormindo",
                          acao: "", msg: "" },
                        { nome: "Caipora", icone: "caipora", cor: "#12935F",
                          ligado: !!(root.estado.camera_cortada && root.estado.microfone_mudo), existe: true,
                          texto: (root.estado.camera_cortada && root.estado.microfone_mudo) ? "privacidade ligada"
                                 : (root.estado.camera_cortada || root.estado.microfone_mudo) ? "em parte" : "câmera e mic liberados",
                          acao: (root.estado.camera_cortada && root.estado.microfone_mudo)
                                ? "sh -c 'wpctl set-mute @DEFAULT_AUDIO_SOURCE@ 0 && curupira camera liberar'"
                                : "sh -c 'wpctl set-mute @DEFAULT_AUDIO_SOURCE@ 1 && curupira camera cortar'",
                          msg: (root.estado.camera_cortada && root.estado.microfone_mudo) ? "Câmera e microfone liberados."
                                                                                          : "A Caipora cortou a câmera e o microfone." },
                        { nome: "Saci · turbo", icone: "saci", cor: "#C2265A",
                          ligado: !!root.estado.turbo, existe: true,
                          texto: root.estado.turbo ? "girando" : "calmo",
                          acao: "", msg: "" },
                        { nome: "Mapinguari · HD", icone: "mapinguari", cor: "#5B3A8E",
                          ligado: !!root.estado.hd_acordado, existe: true,
                          texto: root.estado.hd_acordado ? "acordado" : "hibernando",
                          acao: root.estado.hd_acordado ? "curupira hd dormir" : "curupira hd acordar",
                          msg: root.estado.hd_acordado ? "Mapinguari hibernando: motor parado."
                                                       : "O Mapinguari acordou: /data está à mão." }
                    ]
                    delegate: Rectangle {
                        required property var modelData
                        readonly property bool clicavel: modelData.acao !== "" && modelData.existe
                        Layout.fillWidth: true
                        implicitHeight: Kirigami.Units.gridUnit * 4.4
                        radius: Kirigami.Units.cornerRadius * 3
                        color: modelData.ligado ? modelData.cor : (ser.containsMouse && clicavel ? root.alfa(modelData.cor, 0.14) : neutro)
                        opacity: modelData.existe ? 1 : 0.5
                        Accessible.role: Accessible.Button
                        Accessible.name: `${modelData.nome}: ${modelData.texto}`
                        Behavior on color { ColorAnimation { duration: 180 } }
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: Kirigami.Units.largeSpacing
                            spacing: Kirigami.Units.smallSpacing / 2
                            // a arte do ser (arte/icones/seres, copiada por tema/gerar-icones.py); dormindo, fica apagada
                            Image {
                                source: Qt.resolvedUrl("../images/ser-" + modelData.icone + ".svg")
                                sourceSize: Qt.size(Kirigami.Units.iconSizes.medium * 2, Kirigami.Units.iconSizes.medium * 2)
                                Layout.preferredWidth: Kirigami.Units.iconSizes.medium
                                Layout.preferredHeight: Kirigami.Units.iconSizes.medium
                                opacity: modelData.ligado ? 1 : 0.6
                                Behavior on opacity { NumberAnimation { duration: 180 } }
                            }
                            PlasmaComponents.Label {
                                text: modelData.nome
                                font.bold: true
                                color: modelData.ligado ? "#FFFFFF" : Kirigami.Theme.textColor
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                            PlasmaComponents.Label {
                                text: modelData.texto
                                color: modelData.ligado ? Qt.rgba(1, 1, 1, 0.9) : suave
                                font.pointSize: Kirigami.Theme.smallFont.pointSize
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                        }
                        MouseArea {
                            id: ser
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: parent.clicavel ? Qt.PointingHandCursor : Qt.ArrowCursor
                            onClicked: if (parent.clicavel) root.roda(parent.modelData.acao, parent.modelData.msg)
                        }
                    }
                }
            }

            // volume e brilho
            Repeater {
                model: [
                    { icone: "som", cor: "#FF7A45", valor: root.estado.volume, nome: "Volume",
                      comando: v => `wpctl set-volume @DEFAULT_AUDIO_SINK@ ${(v / 100).toFixed(2)}` },
                    { icone: "brilho", cor: "#2BB37A", valor: root.estado.brilho, nome: "Brilho",
                      comando: v => `curupira brilho ${Math.max(5, v)}` }
                ]
                delegate: RowLayout {
                    required property var modelData
                    readonly property bool disponivel: modelData.valor !== null && modelData.valor !== undefined
                    property real arrastando: -1
                    readonly property real mostrado: arrastando >= 0 ? arrastando : (disponivel ? modelData.valor : 0)
                    visible: disponivel
                    spacing: Kirigami.Units.largeSpacing
                    Layout.fillWidth: true
                    Kirigami.Icon {
                        source: Qt.resolvedUrl("../images/" + modelData.icone + ".svg")
                        isMask: true
                        color: suave
                        implicitWidth: Kirigami.Units.iconSizes.small
                        implicitHeight: implicitWidth
                    }
                    Item {
                        Layout.fillWidth: true
                        implicitHeight: Kirigami.Units.gridUnit
                        Accessible.role: Accessible.Slider
                        Accessible.name: modelData.nome
                        Rectangle {
                            id: trilho
                            anchors.verticalCenter: parent.verticalCenter
                            width: parent.width; height: 8; radius: 4
                            color: neutro
                            Rectangle {
                                width: Math.max(8, parent.width * Math.min(100, mostrado) / 100)
                                height: 8; radius: 4
                                color: modelData.cor
                            }
                        }
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            function valorEm(x) { return Math.round(Math.max(0, Math.min(1, x / width)) * 100) }
                            onPressed: mouse => arrastando = valorEm(mouse.x)
                            onPositionChanged: mouse => { if (pressed) arrastando = valorEm(mouse.x) }
                            onReleased: {
                                root.roda(modelData.comando(arrastando))
                                arrastando = -1
                            }
                        }
                    }
                    PlasmaComponents.Label {
                        text: Math.round(mostrado) + "%"
                        color: suave
                        font.pointSize: Kirigami.Theme.smallFont.pointSize
                        Layout.preferredWidth: Kirigami.Units.gridUnit * 2
                        horizontalAlignment: Text.AlignRight
                    }
                }
            }

            // último aviso automático do Curupira
            Rectangle {
                visible: !!root.estado.ultimo_evento
                Layout.fillWidth: true
                implicitHeight: aviso.implicitHeight + Kirigami.Units.largeSpacing * 2
                radius: Kirigami.Units.cornerRadius * 3
                color: root.alfa("#FF7A45", 0.13)
                RowLayout {
                    id: aviso
                    anchors.fill: parent
                    anchors.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing
                    Kirigami.Icon {
                        source: Qt.resolvedUrl("../images/aviso.svg")
                        isMask: true
                        color: "#E2531F"
                        implicitWidth: Kirigami.Units.iconSizes.small
                        implicitHeight: implicitWidth
                        Layout.alignment: Qt.AlignTop
                    }
                    ColumnLayout {
                        spacing: 0
                        Layout.fillWidth: true
                        PlasmaComponents.Label {
                            text: root.estado.ultimo_evento ? `${root.estado.ultimo_evento.titulo} · ${root.quandoFoi(root.estado.ultimo_evento.quando)}` : ""
                            font.bold: true
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }
                        PlasmaComponents.Label {
                            text: root.estado.ultimo_evento ? root.estado.ultimo_evento.texto : ""
                            wrapMode: Text.WordWrap
                            color: suave
                            font.pointSize: Kirigami.Theme.smallFont.pointSize
                            Layout.fillWidth: true
                        }
                    }
                }
            }

            PlasmaComponents.Label {
                Layout.fillWidth: true
                visible: root.mensagem !== ""
                wrapMode: Text.WordWrap
                text: root.mensagem
                color: root.mensagemErro ? Kirigami.Theme.negativeTextColor : Kirigami.Theme.positiveTextColor
            }

            PlasmaComponents.Button {
                Layout.fillWidth: true
                icon.name: "io.github.pabloherzberg.Toca"
                text: "Abrir a Toca do Curupira"
                onClicked: {
                    root.roda("sh -c 'toca-do-curupira >/dev/null 2>&1 &'")
                    root.expanded = false
                }
            }
        }
    }
}
