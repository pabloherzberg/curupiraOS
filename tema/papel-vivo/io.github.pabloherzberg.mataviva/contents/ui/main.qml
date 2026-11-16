// Mata Viva: papel de parede animado da Curupira OS. A cena fica em Cena.qml; aqui só se lê o estado
// do sistema com "curupira json" (o mesmo que alimenta a Toca e o widget) e se decide se a mata se mexe.

import QtQuick
import QtQuick.Window
import org.kde.plasma.plasmoid
import org.kde.plasma.plasma5support as P5Support
import org.kde.taskmanager as TaskManager

WallpaperItem {
    id: raiz

    property var estado: ({})
    // 0: só na tomada; 1: sempre; 2: nunca
    readonly property int movimento: raiz.configuration.Movimento || 0
    readonly property string arte: ["brasa", "iara"][raiz.configuration.Cena || 0] || "brasa"
    // animação contínua mantém a placa de vídeo acordada: na bateria, e nos perfis de economia, a mata fica parada
    readonly property bool economia: estado.perfil === "remanso" || estado.perfil === "sereno"
    // com uma janela maximizada ou em tela cheia por cima ninguém vê a mata: ela para até a janela sair
    property bool coberta: false
    readonly property bool mover: !coberta && !economia && (movimento === 1 || (movimento === 0 && estado.fonte === "tomada"))

    TaskManager.VirtualDesktopInfo { id: areas }
    TaskManager.ActivityInfo { id: atividades }
    TaskManager.TasksModel {
        id: janelas
        groupMode: TaskManager.TasksModel.GroupDisabled
        sortMode: TaskManager.TasksModel.SortDisabled
        filterByVirtualDesktop: true
        filterByActivity: true
        filterByScreen: true
        virtualDesktop: areas.currentDesktop
        activity: atividades.currentActivity
        screenGeometry: Qt.rect(raiz.Screen.virtualX, raiz.Screen.virtualY, raiz.Screen.width, raiz.Screen.height)
        onDataChanged: confere.restart()
        onCountChanged: confere.restart()
        onModelReset: confere.restart()
    }
    Timer {     // junta as várias mudanças de uma vez só (abrir uma janela muda vários campos)
        id: confere
        interval: 250
        running: true
        onTriggered: {
            const P = TaskManager.AbstractTasksModel
            let tapada = false
            for (let i = 0; i < janelas.count && !tapada; i++) {
                const j = janelas.index(i, 0)
                if (!janelas.data(j, P.IsWindow) || janelas.data(j, P.IsMinimized)) continue
                // maximizada, em tela cheia, ou só arrastada até ocupar quase a tela toda
                const g = janelas.data(j, P.Geometry), t = janelas.screenGeometry
                const larg = Math.min(g.x + g.width, t.x + t.width) - Math.max(g.x, t.x)
                const alt = Math.min(g.y + g.height, t.y + t.height) - Math.max(g.y, t.y)
                if (janelas.data(j, P.IsMaximized) || janelas.data(j, P.IsFullScreen)
                        || (larg > 0 && alt > 0 && larg * alt >= 0.9 * t.width * t.height))
                    tapada = true
            }
            raiz.coberta = tapada
        }
    }

    P5Support.DataSource {
        id: leitor
        engine: "executable"
        connectedSources: []
        onNewData: (fonte, dados) => {
            try { raiz.estado = JSON.parse(dados["stdout"]) } catch (e) { /* fica com o estado anterior */ }
            disconnectSource(fonte)
        }
    }
    Timer {
        // com a mata coberta ou parada não há pressa: o estado só muda o que aparece na cena
        interval: raiz.mover ? 20000 : 60000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: leitor.connectSource("curupira json")
    }
    Timer {     // a lua da Cuca anda devagar
        interval: 300000
        running: true
        repeat: true
        onTriggered: { const d = new Date(); cena.hora = d.getHours() + d.getMinutes() / 60 }
    }

    Rectangle { anchors.fill: parent; color: "#0B0717" }
    Cena {
        id: cena
        anchors.fill: parent
        estado: raiz.estado
        arte: raiz.arte
        mover: raiz.mover
    }
}
