import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtMultimedia 5.15
import QtGraphicalEffects 1.0
import QtQuick.Controls.Styles 1.4
import "."

Window {
    id: appWindow

    width: 850
    height: 750
    minimumWidth: 450
    minimumHeight: 600
    visible: true
    title: "Music"
    color: themeManager.currentTheme.backgroundColor

    Item {
        anchors.fill: parent
        opacity: themeManager.currentTheme.backgroundOpacity

        Image {
            id: background
            opacity: 0.5
            source: "image://cover/" + appState.currentSong.path
            sourceSize: Qt.size(parent.width, parent.height)
            anchors.fill: parent
            fillMode: Image.PreserveAspectCrop
            smooth: true
            visible: false
            mirror: true
        }

        GaussianBlur {
            anchors.fill: background
            source: background
            radius: 100
            samples: 128
        }

    }

    Text {
        visible: appState.empty
        anchors.centerIn: parent
        text: "Nothing Loaded"
        color: themeManager.currentTheme.textColor
        opacity: 0.5
    }

    ThemeManager {
        id: themeManager
    }

    Item {
        focus: true
        Keys.onPressed: function(event) {
            if (event.key === Qt.Key_Space) {
                appState.togglePlayback();
                event.accepted = true;
            }
        }

        Shortcut {
            sequence: "Shift+Backspace"
            onActivated: appState.clearPlaylist()
        }

    }

    DropArea {
        id: dropArea

        anchors.fill: parent
        onDropped: function(drop) {
            for (var i = 0; i < drop.urls.length; i++) {
                appState.addUrl(drop.urls[i]);
            }
        }
    }

    Rectangle {
        id: sidebar

        color: themeManager.currentTheme.sidebarColor
        height: parent.height
        width: 300
        states: [
            State {
                name: "visible"
                when: appState.sidebarVisible

                PropertyChanges {
                    target: sidebar
                    x: 0
                }

            },
            State {
                name: "hidden"
                when: !appState.sidebarVisible

                PropertyChanges {
                    target: sidebar
                    x: -sidebar.width
                }

            }
        ]
        transitions: [
            Transition {
                NumberAnimation {
                    properties: "x"
                    duration: 300 // adjust as needed
                    easing.type: Easing.InOutQuad
                }

            }
        ]

        ListView {
            id: playlistView

            width: parent.width
            height: parent.height
            model: playlistModel
            highlightFollowsCurrentItem: true
            highlightMoveDuration: 0
            highlightMoveVelocity: 1000
            currentIndex: appState.currentSongIndex
            delegate: playlistViewDelegate
            boundsBehavior: Flickable.StopAtBounds

            Component {
                id: playlistViewDelegate

                Item {
                    id: wrapper

                    width: ListView.view.width
                    height: 70

                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: 10
                        color: "transparent"

                        RowLayout {
                            spacing: 10
                            Layout.fillWidth: true

                            Rectangle {
                                id: smallCoverWrapper

                                Layout.alignment: Qt.AlignVCenter
                                Layout.preferredWidth: 50
                                Layout.preferredHeight: 50
                                color: "transparent"

                                Image {
                                    id: smallCover

                                    anchors.fill: parent
                                    fillMode: Image.PreserveAspectFit
                                    source: "image://cover/" + path
                                    layer.enabled: true

                                    layer.effect: OpacityMask {

                                        maskSource: Item {
                                            width: smallCover.width
                                            height: smallCover.height

                                            Rectangle {
                                                anchors.centerIn: parent
                                                width: smallCover.width
                                                height: smallCover.height
                                                radius: 5
                                            }

                                        }

                                    }

                                }

                            }

                            ColumnLayout {
                                Layout.alignment: Qt.AlignVCenter
                                Layout.fillWidth: true

                                Text {
                                    Layout.preferredWidth: 210
                                    text: model.title
                                    color: wrapper.ListView.isCurrentItem ? themeManager.currentTheme.sidebarHighlightTextColor : themeManager.currentTheme.sidebarTextColor
                                    elide: Text.ElideRight
                                    clip: true
                                }

                                Text {
                                    Layout.preferredWidth: 210
                                    text: model.album
                                    color: wrapper.ListView.isCurrentItem ? themeManager.currentTheme.sidebarHighlightTextColor : themeManager.currentTheme.sidebarTextColor
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                    clip: true
                                    opacity: 0.8
                                }

                            }

                        }

                    }

                    MouseArea {
                        width: parent.width
                        height: parent.height
                        onClicked: {
                            appState.currentSongIndex = index;
                        }
                    }

                }

            }

            highlight: Rectangle {
                color: themeManager.currentTheme.sidebarHighlight
            }

        }

    }

    Loader {
        id: nowPlayingLoader
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: sidebar.right
        anchors.right: parent.right
        active: !appState.empty
        sourceComponent: nowPlaying

        Behavior on anchors.left {
            AnchorAnimation {
                duration: 300
                easing.type: Easing.InOutQuad
            }

        }

    }

    Component {
        id: nowPlaying

        ColumnLayout {
            spacing: 40
            Layout.fillWidth: appState.sidebarVisible ? false : true
            Layout.fillHeight: true

            CoverImage {
                image: appState.currentSong ? "image://cover/" + appState.currentSong.path : ""
                Layout.alignment: Qt.AlignCenter
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.topMargin: 40
                Layout.leftMargin: 40
                Layout.rightMargin: 40
                Layout.maximumWidth: 350
                Layout.maximumHeight: 350
            }

            ColumnLayout {
                Layout.alignment: Qt.AlignCenter

                Text {
                    Layout.alignment: Qt.AlignCenter
                    Layout.maximumWidth: 350
                    Layout.preferredWidth: 350
                    Layout.bottomMargin: 10
                    elide: Text.ElideRight
                    horizontalAlignment: Text.AlignHCenter
                    text: appState.currentSong.title
                    font.bold: true
                    font.pixelSize: 18
                    color: themeManager.currentTheme.textColor
                }

                Text {
                    Layout.alignment: Qt.AlignCenter
                    Layout.maximumWidth: 350
                    Layout.preferredWidth: 350
                    horizontalAlignment: Text.AlignHCenter
                    text: appState.currentSong.artist
                    color: themeManager.currentTheme.textColorDim
                }

                Text {
                    Layout.alignment: Qt.AlignCenter
                    Layout.maximumWidth: 350
                    Layout.preferredWidth: 350
                    horizontalAlignment: Text.AlignHCenter
                    text: appState.currentSong.album
                    color: themeManager.currentTheme.textColorDim
                }

            }

            Rectangle {
                id: progressBar

                Layout.alignment: Qt.AlignCenter
                Layout.preferredWidth: 350
                height: 3
                color: themeManager.currentTheme.progressBackground

                Rectangle {
                    color: themeManager.currentTheme.progressForeground
                    height: parent.height
                    width: Math.max(0, Math.min(parent.width, (parent.width * (appState.position / appState.duration))))
                }

                MouseArea {
                    id: mouseArea

                    anchors.fill: parent
                    onClicked: {
                        var clickPosition = mouse.x;
                        var progressBarWidth = progressBar.width;
                        var newProgress = (clickPosition / progressBarWidth) * appState.duration;
                        appState.position = newProgress;
                    }
                }
            }

            // Slider {
            //     id: positionSlider
            //     Layout.alignment: Qt.AlignCenter
            //     Layout.preferredWidth: 350
            //     Layout.fillWidth: true
            //     Layout.fillHeight: false
            //     Layout.leftMargin: 40
            //     Layout.rightMargin: 40
            //     Layout.maximumWidth: 350
            //     Layout.maximumHeight: 350
            //     to: appState.duration
            //     value: appState.position
            //     stepSize: 1
            //     live: false
            //     onMoved: appState.position = value
            //
            //     background: Rectangle {
            //         x: positionSlider.leftPadding
            //         y: positionSlider.topPadding + positionSlider.availableHeight / 2 - height / 2
            //         implicitWidth: 350
            //         implicitHeight: 5
            //         width: positionSlider.availableWidth
            //         height: implicitHeight
            //         radius: 2
            //         color: themeManager.currentTheme.buttonColor
            //
            //         Rectangle {
            //             width: positionSlider.visualPosition * parent.width
            //             height: 5
            //             color: themeManager.currentTheme.textColor
            //             radius: 2
            //         }
            //
            //     }
            //
            //     handle: Rectangle {
            //     }
            // }

            RowLayout {
                spacing: 15
                Layout.alignment: Qt.AlignCenter
                Layout.bottomMargin: 35
                Layout.leftMargin: 35
                Layout.rightMargin: 35

                ControlButton {
                    icon: "qrc:/icons/menu.svg"
                    buttonSize: 40
                    buttonColor: themeManager.currentTheme.buttonColor
                    iconSize: 20
                    iconColor: themeManager.currentTheme.textColor
                    onClicked: {
                        appState.sidebarVisible = !appState.sidebarVisible;
                    }
                }

                ControlButton {
                    icon: "qrc:/icons/previous.svg"
                    buttonSize: 40
                    buttonColor: themeManager.currentTheme.buttonColor
                    iconSize: 20
                    iconColor: themeManager.currentTheme.textColor
                    onClicked: {
                        appState.previousSong();
                    }
                }

                ControlButton {
                    icon: appState.playbackState === "PlayingState" ? "qrc:/icons/pause.svg" : "qrc:/icons/play.svg"
                    buttonSize: 40
                    buttonColor: themeManager.currentTheme.buttonColor
                    iconSize: 40
                    iconColor: themeManager.currentTheme.textColor
                    onClicked: appState.togglePlayback()
                }

                ControlButton {
                    icon: "qrc:/icons/next.svg"
                    buttonSize: 40
                    buttonColor: themeManager.currentTheme.buttonColor
                    iconSize: 20
                    iconColor: themeManager.currentTheme.textColor
                    onClicked: {
                        appState.nextSong();
                    }
                }

                VolumeButton {
                    id: volumeButton

                    volume: appState.volume

                    Binding {
                        target: appState
                        property: "volume"
                        value: volumeButton.volume
                    }

                }

            }

        }

    }

}
