import QtQuick 2.15

QtObject {
    property QtObject currentTheme: appTheme === "light" ? lightTheme : darkTheme
    property string appTheme: "dark" // appState.theme
    property QtObject lightTheme
    property QtObject darkTheme

    lightTheme: QtObject {
        property color backgroundColor:           Qt.rgba(0.980, 0.980, 0.980, 1.000)
        property color borderColor:               Qt.rgba(0.000, 0.000, 0.000, 0.200)
        property color textColor:                 Qt.rgba(0.000, 0.000, 0.000, 0.800)
        property color textColorDim:              Qt.rgba(0.000, 0.000, 0.000, 0.500)
        property color sidebarColor:              Qt.rgba(0.941, 0.941, 0.941, 0.500)
        property color sidebarTextColor:          Qt.rgba(0.000, 0.000, 0.000, 0.800)
        property color sidebarHighlight:          Qt.rgba(1.000, 1.000, 1.000, 0.800)
        property color sidebarHighlightTextColor: Qt.rgba(0.000, 0.000, 0.000, 1.000)
        property color buttonColor:               Qt.rgba(0.000, 0.000, 0.000, 0.100)
        property color progressBackground:        Qt.rgba(0.000, 0.000, 0.000, 0.100)
        property color progressForeground:        Qt.rgba(0.000, 0.000, 0.000, 0.500)
        property color shadowColor:               Qt.rgba(0.000, 0.000, 0.000, 0.200)

        property real  backgroundOpacity:         0.500
    }

    darkTheme: QtObject {
        property color backgroundColor:           Qt.rgba(0.140, 0.140, 0.140, 1.000)
        property color borderColor:               Qt.rgba(1.000, 1.000, 1.000, 0.200)
        property color textColor:                 Qt.rgba(1.000, 1.000, 1.000, 0.800)
        property color textColorDim:              Qt.rgba(1.000, 1.000, 1.000, 0.500)
        property color sidebarColor:              Qt.rgba(0.118, 0.118, 0.118, 0.500)
        property color sidebarTextColor:          Qt.rgba(1.000, 1.000, 1.000, 0.800)
        property color sidebarHighlight:          Qt.rgba(0.000, 0.000, 0.000, 0.500)
        property color sidebarHighlightTextColor: Qt.rgba(1.000, 1.000, 1.000, 1.000)
        property color buttonColor:               Qt.rgba(1.000, 1.000, 1.000, 0.100)
        property color progressBackground:        Qt.rgba(1.000, 1.000, 1.000, 0.100)
        property color progressForeground:        Qt.rgba(1.000, 1.000, 1.000, 0.500)
        property color shadowColor:               Qt.rgba(0.000, 0.000, 0.000, 0.200)

        property real  backgroundOpacity:         0.500
    }
}
