import QtQuick 2.15
import QtGraphicalEffects 1.0

Item {
    id: coverWrapper
    property alias image: image.source

    Rectangle {
        id: shadow

        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height)
        height: Math.min(parent.width, parent.height)
        color: themeManager.currentTheme.shadowColor
        radius: 10
        layer.enabled: true

        layer.effect: GaussianBlur {
            radius: 40
            samples: 64
            transparentBorder: true
        }

    }

    Rectangle {
        id: cover

        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) - 20
        height: Math.min(parent.width, parent.height) - 20
        color: "transparent"

        Image {
            id: image

            anchors.fill: parent
            layer.enabled: true

            layer.effect: OpacityMask {

                maskSource: Item {
                    width: image.width
                    height: image.height

                    Rectangle {
                        anchors.centerIn: parent
                        width: image.width
                        height: image.height
                        radius: 10
                    }

                }

            }

        }

    }

}
