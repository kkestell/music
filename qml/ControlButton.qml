import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt5Compat.GraphicalEffects 6.0

Item {
    id: root

    property int buttonSize: 50
    property int iconSize: 30
    property url icon: ""
    property color iconColor: "#ffffff"
    property color buttonColor: "#ffffff"

    signal clicked()

    width: button.width
    height: button.height

    RoundButton {
        id: button

        padding: 20

        contentItem: Item {
            implicitWidth: root.iconSize
            implicitHeight: root.iconSize

            Image {
                id: iconImage
                anchors.fill: parent
                source: root.icon
                fillMode: Image.PreserveAspectFit
                sourceSize: Qt.size(root.iconSize, root.iconSize)
                visible: false
            }

            ColorOverlay {
                anchors.fill: iconImage
                source: iconImage
                color: root.iconColor
            }
        }

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
