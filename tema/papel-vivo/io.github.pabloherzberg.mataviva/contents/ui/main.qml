// Mata Viva: papel de parede animado da Curupira OS. A cena fica em Cena.qml; aqui só se lê o estado
// do sistema com "curupira json" (o mesmo que alimenta a Toca e o widget) e se decide se a mata se mexe.

import QtQuick
import org.kde.plasma.plasmoid
import org.kde.plasma.plasma5support as P5Support

WallpaperItem {
    id: raiz

    property var estado: ({})
    // 0: só na tomada; 1: sempre; 2: nunca
    readonly property int movimento: raiz.configuration.Movimento || 0
    readonly property string arte: ["brasa", "iara"][raiz.configuration.Cena || 0] || "brasa"
    // animação contínua mantém a placa de vídeo acordada: na bateria, e nos perfis de economia, a mata fica parada
    readonly property bool economia: estado.perfil === "remanso" || estado.perfil === "sereno"
    readonly property bool mover: !economia && (movimento === 1 || (movimento === 0 && estado.fonte === "tomada"))

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
        interval: 20000
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
