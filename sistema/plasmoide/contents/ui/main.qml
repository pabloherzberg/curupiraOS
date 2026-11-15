// Curupira: widget do painel da Curupira OS.
// Lê o estado com "curupira json" e troca de perfil com "curupira <perfil>".

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

    function nomePerfil(id) {
        const p = (estado.perfis || []).find(q => q.id === id)
        return p ? p.nome : id
    }

    function linhaEnergia() {
        if (estado.bateria === undefined) return "Sem dados do curupira"
        if (estado.fonte === "bateria" && estado.watts > 0) {
            const horas = estado.capacidade_wh * estado.bateria / 100 / estado.watts
            const h = Math.floor(horas), m = Math.round((horas - h) * 60)
            return `Bateria ${estado.bateria}% · ${estado.watts.toFixed(1).replace(".", ",")} W · restam ≈ ${h}h${m < 10 ? "0" : ""}${m}`
        }
        return `Na tomada · bateria ${estado.bateria}%`
    }

    toolTipMainText: perfil ? `Curupira: ${nomePerfil(perfil)}` : "Curupira"
    toolTipSubText: linhaEnergia()
    Plasmoid.icon: "battery-good"

    P5Support.DataSource {
        id: executor
        engine: "executable"
        connectedSources: []
        onNewData: (fonte, dados) => {
            disconnectSource(fonte)
            if (fonte === "curupira json") {
                try { root.estado = JSON.parse(dados["stdout"]) } catch (e) { root.estado = ({}) }
                return
            }
            if (fonte.startsWith("curupira ")) {
                const ok = dados["exit code"] === 0
                root.mensagemErro = !ok
                const err = (dados["stderr"] || "").trim().split("\n").pop()
                root.mensagem = ok ? `Perfil ${root.nomePerfil(fonte.split(" ")[1])} aplicado.` : (err || "Não consegui trocar o perfil.")
                root.atualiza()
            }
        }
    }

    function roda(cmd) { executor.connectSource(cmd) }
    function atualiza() { roda("curupira json") }

    Timer {
        interval: root.expanded ? 3000 : 20000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: root.atualiza()
    }

    onExpandedChanged: if (expanded) { mensagem = ""; atualiza() }

    compactRepresentation: MouseArea {
        id: compacto
        hoverEnabled: true
        onClicked: root.expanded = !root.expanded
        Accessible.name: root.toolTipMainText
        Accessible.role: Accessible.Button

        Rectangle {
            anchors.centerIn: parent
            width: Math.round(Math.min(parent.width, parent.height) * 0.78)
            height: width
            radius: width * 0.3
            color: root.corPerfil
            border.width: compacto.containsMouse ? 2 : 0
            border.color: Qt.lighter(root.corPerfil, 1.5)

            PlasmaComponents.Label {
                anchors.centerIn: parent
                text: root.perfil ? root.nomePerfil(root.perfil).charAt(0) : "?"
                color: "#FFFFFF"
                font.bold: true
                font.pixelSize: parent.height * 0.58
            }
        }
    }

    fullRepresentation: PlasmaExtras.Representation {
        Layout.minimumWidth: Kirigami.Units.gridUnit * 17
        Layout.preferredWidth: Kirigami.Units.gridUnit * 18
        Layout.preferredHeight: implicitHeight

        header: PlasmaExtras.PlasmoidHeading {
            ColumnLayout {
                anchors.fill: parent
                spacing: 0
                Kirigami.Heading {
                    level: 3
                    text: "Curupira"
                    Layout.fillWidth: true
                }
                PlasmaComponents.Label {
                    text: root.linhaEnergia()
                    opacity: 0.75
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
            }
        }

        contentItem: ColumnLayout {
            spacing: Kirigami.Units.smallSpacing

            Repeater {
                model: root.perfisOrdenados
                delegate: PlasmaComponents.ItemDelegate {
                    required property var modelData
                    readonly property bool atual: modelData.id === root.perfil
                    Layout.fillWidth: true
                    highlighted: atual
                    Accessible.name: `Perfil ${modelData.nome}, ${modelData.descricao}` + (atual ? ", ativo" : "")
                    onClicked: if (!atual) root.roda("curupira " + modelData.id)

                    contentItem: RowLayout {
                        spacing: Kirigami.Units.largeSpacing
                        Rectangle {
                            implicitWidth: Kirigami.Units.iconSizes.medium
                            implicitHeight: implicitWidth
                            radius: implicitWidth * 0.3
                            color: root.cores[modelData.id] || "#5B6A61"
                        }
                        ColumnLayout {
                            spacing: 0
                            Layout.fillWidth: true
                            PlasmaComponents.Label { text: modelData.nome; font.bold: true; Layout.fillWidth: true }
                            PlasmaComponents.Label { text: modelData.descricao; opacity: 0.7; Layout.fillWidth: true }
                        }
                        Kirigami.Icon {
                            source: "checkmark"
                            visible: atual
                            implicitWidth: Kirigami.Units.iconSizes.small
                            implicitHeight: implicitWidth
                        }
                    }
                }
            }

            Item { Layout.fillHeight: true }

            PlasmaComponents.Label {
                Layout.fillWidth: true
                Layout.topMargin: Kirigami.Units.smallSpacing
                wrapMode: Text.WordWrap
                opacity: 0.75
                font: Kirigami.Theme.smallFont
                text: root.estado.auto
                    ? `Troca automática ligada: tomada ${root.nomePerfil(root.estado.perfil_tomada)}, bateria ${root.nomePerfil(root.estado.perfil_bateria)}, até ${root.estado.limite_critico}% ${root.nomePerfil(root.estado.perfil_critico)}.`
                    : "Troca automática desligada: o perfil só muda quando você mandar."
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
                Layout.topMargin: Kirigami.Units.smallSpacing
                icon.name: "preferences-system-power-management"
                text: "Abrir a Toca do Curupira"
                onClicked: {
                    root.roda("sh -c 'toca-do-curupira >/dev/null 2>&1 &'")
                    root.expanded = false
                }
            }
        }
    }
}
