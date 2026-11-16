// Doca Curupira: os apps da doca da Curupira OS (mockup/Desktop.dc.html).
// - apps fixados e janelas abertas (TasksModel do Plasma), agrupados por app
// - ao surgir (a doca sobe da borda), cada ícone faz uma entrada: nasce pequeno e girado
//   abaixo da doca, sobe com balanço elástico, solta uma faísca de brasa ao chegar, e no fim
//   uma onda passa da esquerda para a direita. A ordem vai do centro para as pontas.
// - com o mouse em cima, só aquele ícone "respira": diminui e aumenta suavemente
// - clique: abre, traz para frente ou minimiza; meio: nova janela; direito: menu

import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.extras as PlasmaExtras
import org.kde.kirigami as Kirigami
import org.kde.taskmanager as TaskManager

PlasmoidItem {
    id: root

    preferredRepresentation: fullRepresentation
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

    readonly property real altura: Math.max(32, height)
    // o ícone base deixa folga para a respiração e a entrada não saírem da doca
    readonly property real icone: Math.round(altura * 0.74)
    readonly property real passo: icone + Math.round(altura * 0.14)

    Layout.minimumWidth: lista.count * passo + Math.round(altura * 0.14)
    Layout.preferredWidth: Layout.minimumWidth
    Layout.maximumWidth: Layout.minimumWidth
    Layout.fillHeight: true

    TaskManager.VirtualDesktopInfo { id: areas }
    TaskManager.ActivityInfo { id: atividades }

    TaskManager.TasksModel {
        id: tarefas
        groupMode: TaskManager.TasksModel.GroupApplications
        sortMode: TaskManager.TasksModel.SortManual
        launchInPlace: true
        separateLaunchers: false
        filterByVirtualDesktop: false
        filterByScreen: false
        filterByActivity: true
        virtualDesktop: areas.currentDesktop
        activity: atividades.currentActivity
        launcherList: Plasmoid.configuration.launchers
        onLauncherListChanged: if (launcherList.join("|") !== Plasmoid.configuration.launchers.join("|"))
                                   Plasmoid.configuration.launchers = launcherList
    }

    // ---------------------------------------------------------------- quando a doca surge
    signal surgir()
    property double saiuEm: 0
    property double surgiuEm: 0
    function anunciaSurgimento() {
        if (Date.now() - surgiuEm < 1500) return     // não repete em seguida
        surgiuEm = Date.now()
        root.surgir()
    }

    // a doca subiu da borda: o mouse entra nela depois de um tempo fora
    HoverHandler {
        id: pairar
        onHoveredChanged: {
            if (hovered) {
                if (Date.now() - root.saiuEm > 900) root.anunciaSurgimento()
            } else {
                root.saiuEm = Date.now()
            }
        }
    }
    // ou a janela do painel reaparece (doca escondida que volta, login)
    Connections {
        target: root.Window.window
        ignoreUnknownSignals: true
        function onVisibleChanged() { if (root.Window.window && root.Window.window.visible) root.anunciaSurgimento() }
    }
    Component.onCompleted: Qt.callLater(root.anunciaSurgimento)

    readonly property real meio: (lista.count - 1) / 2
    readonly property int atrasoPorPasso: 75
    readonly property int maiorAtraso: Math.ceil(meio) * atrasoPorPasso

    // ---------------------------------------------------------------- ladrilhos
    // Todo app fica num ladrilho cor da noite. Os apps do sistema têm ícone próprio no tema de ícones
    // "Curupira" (arte/icones/apps), que já vem com o ladrilho: esses aparecem inteiros. Os de terceiros
    // mantêm o ícone original, menor, sobre o mesmo ladrilho.
    readonly property color noite: "#241A4A"
    readonly property color fioDaNoite: "#3A2D6B"
    readonly property var doSistema: [
        "org.kde.dolphin", "org.kde.konsole", "org.kde.kate", "org.kde.kwrite", "systemsettings",
        "org.kde.spectacle", "org.kde.ark", "org.kde.discover", "org.kde.gwenview", "org.kde.okular",
        "org.kde.kcalc", "org.kde.plasma-systemmonitor", "org.kde.partitionmanager", "org.kde.kinfocenter",
        "org.kde.elisa", "org.kde.filelight", "org.kde.khelpcenter", "org.kde.kwalletmanager5"
    ]
    function temLadrilhoProprio(id) {
        return doSistema.indexOf(id.replace(/\.desktop$/, "")) >= 0
    }

    // ---------------------------------------------------------------- ações
    function ativa(indice, dados, delegado) {
        const idx = tarefas.makeModelIndex(indice)
        if (dados.IsLauncher) {
            tarefas.requestActivate(idx)
        } else if (dados.ChildCount > 1) {
            // grupo: vai passando pelas janelas do app
            delegado.proxima = (delegado.proxima + 1) % dados.ChildCount
            tarefas.requestActivate(tarefas.makeModelIndex(indice, delegado.proxima))
        } else if (dados.IsActive && !dados.IsMinimized) {
            tarefas.requestToggleMinimized(idx)
        } else {
            tarefas.requestActivate(idx)
        }
    }

    Row {
        id: linha
        anchors.centerIn: parent
        spacing: root.passo - root.icone
        height: root.altura

        Repeater {
            id: lista
            model: tarefas

            delegate: Item {
                id: delegado
                required property int index
                required property var model
                property int proxima: 0
                readonly property var dados: model
                readonly property bool sobMouse: dica.containsMouse

                width: root.icone
                height: root.altura

                // ------------------------------------------------ entrada (ao surgir)
                property real entradaY: 0
                property real entradaEscala: 1
                property real entradaGiro: 0
                property real entradaOpac: 1
                property real faiscaEscala: 0.3
                property real faiscaOpac: 0
                property real onda: 0
                readonly property int ordem: Math.round(Math.abs(index - root.meio))
                readonly property int atraso: ordem * root.atrasoPorPasso
                readonly property real lado: index % 2 === 0 ? -1 : 1

                SequentialAnimation {
                    id: entrada
                    // começa escondido, embaixo, pequeno e girado
                    PropertyAction { target: delegado; property: "entradaOpac"; value: 0 }
                    PropertyAction { target: delegado; property: "entradaY"; value: root.altura * 0.75 }
                    PropertyAction { target: delegado; property: "entradaEscala"; value: 0.2 }
                    PropertyAction { target: delegado; property: "entradaGiro"; value: 38 * delegado.lado }
                    PropertyAction { target: delegado; property: "onda"; value: 0 }
                    PauseAnimation { duration: delegado.atraso }
                    ParallelAnimation {
                        NumberAnimation { target: delegado; property: "entradaOpac"; to: 1; duration: 220 }
                        NumberAnimation { target: delegado; property: "entradaY"; to: 0; duration: 620; easing.type: Easing.OutBack; easing.overshoot: 1.8 }
                        NumberAnimation { target: delegado; property: "entradaGiro"; to: 0; duration: 950; easing.type: Easing.OutElastic; easing.amplitude: 1.0; easing.period: 0.45 }
                        SequentialAnimation {
                            NumberAnimation { target: delegado; property: "entradaEscala"; to: 1.22; duration: 360; easing.type: Easing.OutQuad }
                            NumberAnimation { target: delegado; property: "entradaEscala"; to: 1; duration: 420; easing.type: Easing.OutBack; easing.overshoot: 2.5 }
                        }
                        // faísca de brasa no momento em que o ícone chega
                        SequentialAnimation {
                            PauseAnimation { duration: 230 }
                            PropertyAction { target: delegado; property: "faiscaEscala"; value: 0.4 }
                            PropertyAction { target: delegado; property: "faiscaOpac"; value: 0.95 }
                            ParallelAnimation {
                                NumberAnimation { target: delegado; property: "faiscaEscala"; to: 1.55; duration: 640; easing.type: Easing.OutCubic }
                                NumberAnimation { target: delegado; property: "faiscaOpac"; to: 0; duration: 640; easing.type: Easing.InQuad }
                            }
                        }
                    }
                    // onda: depois que todos assentam, passa da esquerda para a direita
                    PauseAnimation { duration: Math.max(0, root.maiorAtraso - delegado.atraso) + 120 + delegado.index * 60 }
                    NumberAnimation { target: delegado; property: "onda"; to: -root.altura * 0.13; duration: 150; easing.type: Easing.OutQuad }
                    NumberAnimation { target: delegado; property: "onda"; to: 0; duration: 330; easing.type: Easing.OutBounce }
                }
                Connections { target: root; function onSurgir() { entrada.restart() } }
                // a lista de apps chega um pouco depois do widget: quem nasce logo após o surgimento entra também
                Component.onCompleted: if (Date.now() - root.surgiuEm < 1500) entrada.restart()

                // ------------------------------------------------ respiração (mouse em cima)
                property real pulso: 1
                SequentialAnimation {
                    id: respiracao
                    running: delegado.sobMouse
                    loops: Animation.Infinite
                    NumberAnimation { target: delegado; property: "pulso"; to: 1.16; duration: 560; easing.type: Easing.InOutSine }
                    NumberAnimation { target: delegado; property: "pulso"; to: 0.92; duration: 560; easing.type: Easing.InOutSine }
                }
                NumberAnimation {
                    id: volta
                    target: delegado; property: "pulso"; to: 1; duration: 260; easing.type: Easing.OutCubic
                }
                onSobMouseChanged: if (!sobMouse) volta.restart()

                // ------------------------------------------------ clique e abertura
                property real pulo: 0
                SequentialAnimation {
                    id: pulinho
                    NumberAnimation { target: delegado; property: "pulo"; to: -root.altura * 0.12; duration: 110; easing.type: Easing.OutQuad }
                    NumberAnimation { target: delegado; property: "pulo"; to: 0; duration: 260; easing.type: Easing.OutBounce }
                }
                SequentialAnimation on pulo {
                    running: delegado.dados.IsStartup === true
                    loops: Animation.Infinite
                    NumberAnimation { to: -root.altura * 0.14; duration: 260; easing.type: Easing.OutQuad }
                    NumberAnimation { to: 0; duration: 340; easing.type: Easing.OutBounce }
                }

                // faísca: brilho e anel dourado atrás do ícone
                Item {
                    id: faisca
                    width: root.icone; height: root.icone
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: (root.altura - root.icone) / 2
                    scale: delegado.faiscaEscala
                    opacity: delegado.faiscaOpac
                    visible: opacity > 0.01
                    Rectangle {
                        anchors.centerIn: parent
                        width: parent.width * 0.9; height: width; radius: width / 2
                        color: "#FF7A45"; opacity: 0.35
                    }
                    Rectangle {
                        anchors.centerIn: parent
                        width: parent.width; height: width; radius: width / 2
                        color: "transparent"
                        border.color: "#FFD08A"
                        border.width: Math.max(2, root.icone * 0.06)
                    }
                }

                // ladrilho cor da noite; o ícone do tema Curupira já traz o seu
                readonly property bool proprio: root.temLadrilhoProprio(String(delegado.dados.AppId || ""))
                Item {
                    id: ladrilho
                    width: root.icone
                    height: root.icone
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: (root.altura - root.icone) / 2 + delegado.entradaY + delegado.pulo + delegado.onda
                    opacity: delegado.entradaOpac * (delegado.dados.IsMinimized ? 0.7 : 1)
                    scale: delegado.entradaEscala * delegado.pulso
                    rotation: delegado.entradaGiro

                    Rectangle {
                        visible: !delegado.proprio
                        anchors.fill: parent
                        anchors.margins: parent.width * 0.03    // o mesmo respiro da arte (ladrilho de 60 em 64)
                        radius: width * 0.3
                        color: root.noite
                        border.color: root.fioDaNoite
                        border.width: 1
                    }
                    Kirigami.Icon {
                        anchors.centerIn: parent
                        source: delegado.dados.decoration
                        // sem isto o Kirigami desenha no tamanho padrão logo abaixo (32 numa caixa de 52)
                        // e o ícone com ladrilho próprio fica menor que os ladrilhos vizinhos
                        roundToIconSize: false
                        width: parent.width * (delegado.proprio ? 1 : 0.62)
                        height: width
                    }
                }

                // ponto de "aberto" (traço no app em uso), como no mockup
                Rectangle {
                    visible: !delegado.dados.IsLauncher
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: root.altura - height - Math.round(root.altura * 0.04)
                    height: Math.max(4, Math.round(root.altura * 0.08))
                    width: delegado.dados.IsActive ? height * 3 : height
                    radius: height / 2
                    opacity: delegado.entradaOpac
                    color: delegado.dados.IsDemandingAttention ? "#FF7A45" : "#12935F"
                    Behavior on width { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
                }

                PlasmaCore.ToolTipArea {
                    id: dica
                    anchors.fill: parent
                    mainText: delegado.dados.display || ""
                    subText: delegado.dados.IsLauncher ? "Clique para abrir"
                             : delegado.dados.ChildCount > 1 ? delegado.dados.ChildCount + " janelas" : ""
                    location: Plasmoid.location
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: false
                    acceptedButtons: Qt.LeftButton | Qt.MiddleButton | Qt.RightButton
                    cursorShape: Qt.PointingHandCursor
                    onClicked: mouse => {
                        if (mouse.button === Qt.MiddleButton) {
                            tarefas.requestNewInstance(tarefas.makeModelIndex(delegado.index))
                            pulinho.restart()
                        } else if (mouse.button === Qt.RightButton) {
                            menu.visualParent = delegado
                            menu.dados = delegado.dados
                            menu.indice = delegado.index
                            menu.openRelative()
                        } else {
                            pulinho.restart()
                            root.ativa(delegado.index, delegado.dados, delegado)
                        }
                    }
                }
            }
        }
    }

    PlasmaExtras.Menu {
        id: menu
        property var dados: ({})
        property int indice: -1
        readonly property bool fixado: !!dados && dados.LauncherUrlWithoutIcon !== undefined
                                       && tarefas.launcherList.indexOf(String(dados.LauncherUrlWithoutIcon)) >= 0

        PlasmaExtras.MenuItem {
            text: "Nova janela"
            icon: "window-new"
            onClicked: tarefas.requestNewInstance(tarefas.makeModelIndex(menu.indice))
        }
        PlasmaExtras.MenuItem {
            text: menu.fixado ? "Tirar da doca" : "Fixar na doca"
            icon: menu.fixado ? "window-unpin" : "window-pin"
            onClicked: {
                const url = String(menu.dados.LauncherUrlWithoutIcon)
                if (menu.fixado) tarefas.requestRemoveLauncher(url)
                else tarefas.requestAddLauncher(url)
            }
        }
        PlasmaExtras.MenuItem {
            text: menu.dados && menu.dados.ChildCount > 1 ? "Fechar todas as janelas" : "Fechar"
            icon: "window-close"
            visible: menu.dados && !menu.dados.IsLauncher
            onClicked: tarefas.requestClose(tarefas.makeModelIndex(menu.indice))
        }
    }
}
