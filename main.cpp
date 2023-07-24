#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QIcon>

#include "app_state.h"
#include "cover_image_provider.h"
#include "playlist_model.h"

int main(int argc, char **argv)
{
    QGuiApplication app(argc, argv);

    QGuiApplication::setWindowIcon(QIcon(":/icons/app_dark.svg"));

    qRegisterMetaType<Song>("Song");

    QQmlApplicationEngine engine;

    auto *coverProvider = new CoverImageProvider();
    engine.addImageProvider(QLatin1String("cover"), coverProvider);

    auto *playlistModel = new PlaylistModel();
    engine.rootContext()->setContextProperty("playlistModel", playlistModel);

    auto *appState = new AppState(playlistModel);
    engine.rootContext()->setContextProperty("appState", appState);

    engine.load(QUrl(QStringLiteral("qrc:/qml/AppWindow.qml")));

    if (engine.rootObjects().isEmpty()) {
        return -1;
    }

    return app.exec();
}
