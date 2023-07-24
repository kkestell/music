#ifndef AUDIO_PLAYER_H
#define AUDIO_PLAYER_H

#include <QObject>
#include <QMediaPlayer>

class AudioPlayer : public QObject
{
    Q_OBJECT
    Q_PROPERTY(qint64              position READ position                 NOTIFY positionChanged)
    Q_PROPERTY(qint64              duration READ duration                 NOTIFY durationChanged)
    Q_PROPERTY(QMediaPlayer::State state    READ state                    NOTIFY stateChanged)

public:
    explicit AudioPlayer(QObject *parent = nullptr);

    Q_INVOKABLE int volume() const;
    Q_INVOKABLE void setVolume(int volume);

    qint64 position() const;
    qint64 duration() const;
    QMediaPlayer::State state() const;

public slots:
    void play(const QString &filePath);
    void stop();
    void togglePlayback();

signals:
    void trackFinished();
    void stateChanged(QMediaPlayer::State state);
    void durationChanged(qint64);
    void positionChanged(qint64);

private slots:
    void onStateChanged(QMediaPlayer::State state);
    void onMediaStatusChanged(QMediaPlayer::MediaStatus state);
    void onPositionChanged(qint64 position);
    void onDurationChanged(qint64 duration);

private:
    QMediaPlayer* m_player;
};

#endif // AUDIO_PLAYER_H
