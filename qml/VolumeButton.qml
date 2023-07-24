import QtQuick 2.15
import QtQuick.Controls 2.15

ControlButton {
    id: volumeButton

    property int volume: 50

    onVolumeChanged: {
        if (!handle.dragging)
            handle.y = (1 - volume / slider.maximumValue) * (groove.height - handle.height);

    }
    icon: volume < 25 ? 'qrc:/icons/volume0.svg' : volume < 50 ? 'qrc:/icons/volume1.svg' : volume < 75 ? 'qrc:/icons/volume2.svg' : 'qrc:/icons/volume3.svg'
    buttonSize: 40
    buttonColor: themeManager.currentTheme.buttonColor
    iconSize: 20
    iconColor: themeManager.currentTheme.textColor
    onClicked: {
        volumePopup.open();
    }

    Popup {
        id: volumePopup

        x: volumeButton.width / 2 - width / 2
        y: volumeButton.height / 2 - height / 2
        width: 50
        height: 80
        modal: false
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        onAboutToShow: {
            volumeButton.opacity = 0;
        }
        onClosed: {
            volumeButton.opacity = 1;
        }

        MouseArea {
            anchors.fill: parent
            onWheel: {
                var delta = wheel.angleDelta.y / 120;
                var change = delta * 10;
                volume = Math.min(Math.max(volume + change, 0), slider.maximumValue);
            }
        }

        Rectangle {
            id: slider

            property int maximumValue: 100
            property int minimumValue: 0

            width: 50
            height: 80
            color: "transparent"
            anchors.centerIn: parent

            Rectangle {
                id: groove

                width: 20
                anchors.horizontalCenter: parent.horizontalCenter
                height: parent.height
                color: "transparent"

                Rectangle {
                    id: visibleGroove

                    width: 3
                    anchors.horizontalCenter: parent.horizontalCenter
                    height: parent.height
                    color: themeManager.currentTheme.progressBackground
                    radius: 1.5
                }

                MouseArea {
                    id: grooveMouseArea

                    anchors.fill: parent
                    acceptedButtons: Qt.LeftButton
                    onClicked: {
                        var newY = grooveMouseArea.mouseY - handle.height / 2;
                        handle.y = Math.min(Math.max(newY, 0), visibleGroove.height - handle.height);
                        volume = Math.round((visibleGroove.height - handle.y - handle.height / 2) / visibleGroove.height * (slider.maximumValue));
                        mouse.accepted = true;
                    }
                }

            }

            Rectangle {
                id: handle

                property bool dragging: false

                width: 20
                height: width
                color: mouseArea.pressed ? Qt.rgba(1, 1, 1, 1) : Qt.rgba(1, 1, 1, 0.9)
                radius: width / 2
                anchors.horizontalCenter: parent.horizontalCenter

                MouseArea {
                    id: mouseArea

                    anchors.fill: parent
                    drag.target: parent
                    drag.axis: Drag.YAxis
                    drag.minimumY: 0 - handle.height / 2
                    drag.maximumY: groove.height - handle.height / 2
                    onPressed: {
                        handle.dragging = true;
                    }
                    onReleased: {
                        handle.dragging = false;
                    }
                    onPositionChanged: {
                        volume = Math.round((groove.height - handle.y - handle.height / 2) / groove.height * (slider.maximumValue));
                    }
                }

            }

        }

        background: Rectangle {
            color: "transparent"
            border.width: 0
        }

    }

}
