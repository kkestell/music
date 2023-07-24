import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root

    property int buttonSize: 50
    property int iconSize: 30
    property alias icon: button.icon.source
    property color iconColor: "#000000"
    property color buttonColor: "#ffffff"

    signal clicked()

    width: button.width
    height: button.height

    RoundButton {
        id: button

        icon.width: root.iconSize
        icon.height: root.iconSize
        icon.color: iconColor
        padding: 20

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onEntered: {
                button.background.color = root.buttonColor;
            }
            onExited: {
                button.background.color = "transparent";
            }
            onClicked: {
                root.clicked();
            }
        }

        background: Rectangle {
            color: "transparent"
            implicitHeight: root.buttonSize
            implicitWidth: root.buttonSize
            radius: root.buttonSize
        }

    }

}
