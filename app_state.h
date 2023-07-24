#ifndef APP_STATE_H
#define APP_STATE_H

#include <QObject>
#include <QUrl>
#include <QDir>
#include "audio_player.h"
#include "playlist_model.h"
#include "metadata_loader.h"
#include "song.h"

class AppState : public QObject
{
    Q_OBJECT
    Q_PROPERTY(int     currentSongIndex READ currentSongIndex WRITE setCurrentSongIndex NOTIFY currentSongIndexChanged)
    Q_PROPERTY(Song    currentSong      READ currentSong                                NOTIFY currentSongChanged)
    Q_PROPERTY(bool    empty            READ empty                                      NOTIFY emptyChanged)
    Q_PROPERTY(qint64  duration         READ duration                                   NOTIFY durationChanged)
    Q_PROPERTY(qint64  position         READ position                                   NOTIFY positionChanged)
    Q_PROPERTY(QString playbackState    READ playbackState                              NOTIFY playbackStateChanged)
    Q_PROPERTY(int     volume           READ volume           WRITE setVolume           NOTIFY volumeChanged)
    Q_PROPERTY(bool    sidebarVisible   READ sidebarVisible   WRITE setSidebarVisible   NOTIFY sidebarVisibleChanged)

public:
    explicit AppState(PlaylistModel *playlistModel, QObject *parent = nullptr);

    int currentSongIndex() const;
    void setCurrentSongIndex(int index);

    int volume() const;
    void setVolume(int volume);

    bool sidebarVisible() const;
    void setSidebarVisible(bool visible);

    Song currentSong() const;
    bool empty() const;
    qint64 duration() const;
    qint64 position() const;
    QString playbackState() const;

    Q_INVOKABLE void togglePlayback();
    Q_INVOKABLE void nextSong();
    Q_INVOKABLE void previousSong();
    Q_INVOKABLE void addUrl(const QUrl &url);
    Q_INVOKABLE void clearPlaylist();

signals:
    void currentSongIndexChanged(int index);
    void currentSongChanged(const Song &song);
    void emptyChanged(bool empty);
    void durationChanged(qint64 duration);
    void positionChanged(qint64 position);
    void playbackStateChanged(QMediaPlayer::State state);
    void volumeChanged(int volume);
    void sidebarVisibleChanged(bool visible);

private:
    void addDirectory(const QDir &dir);
    void addFile(const QString &filePath);

    static bool isAudioFile(const QString &filePath);
    static const QStringList audioExtensions;

    AudioPlayer *m_audioPlayer;
    MetadataLoader *m_metadataLoader;
    PlaylistModel *m_playlistModel;

    int m_currentSongIndex;
    bool m_sidebarVisible;
};

#endif // APP_STATE_H
