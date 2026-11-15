// Mata Viva: ajustes do papel de parede (botão direito na área de trabalho → Configurar área de trabalho).

import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Kirigami.FormLayout {
    property alias cfg_Movimento: movimento.currentIndex
    property int cfg_MovimentoDefault: 0

    QQC2.ComboBox {
        id: movimento
        Kirigami.FormData.label: "Movimento:"
        model: ["Só na tomada (poupa a bateria)", "Sempre", "Nunca: os seres aparecem, mas parados"]
    }
    QQC2.Label {
        Layout.fillWidth: true
        wrapMode: Text.WordWrap
        text: "No Remanso e no Sereno a mata fica sempre parada."
        opacity: 0.7
    }
}
