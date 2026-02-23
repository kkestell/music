#include "audio_player.h"
#include <QTimer>
#include <QAudioOutput>

AudioPlayer::AudioPlayer(QObject* parent) : QObject(parent)
{
    m_player = new QMediaPlayer(this);
    m_audioOutput = new QAudioOutput(this);
    m_player->setAudioOutput(m_audioOutput);

    connect(m_player, &QMediaPlayer::playbackStateChanged, this, &AudioPlayer::onStateChanged);
    connect(m_player, &QMediaPlayer::mediaStatusChanged, this, &AudioPlayer::onMediaStatusChanged);
    connect(m_player, &QMediaPlayer::positionChanged, this, &AudioPlayer::onPositionChanged);
    connect(m_player, &QMediaPlayer::durationChanged, this, &AudioPlayer::onDurationChanged);
}

void AudioPlayer::setPosition(qint64 position)
{
    m_player->setPosition(position);
}

qint64 AudioPlayer::position() const
{
    return m_player->position();
}

qint64 AudioPlayer::duration() const
{
    return m_player->duration();
}

QMediaPlayer::PlaybackState AudioPlayer::state() const
{
    return m_player->playbackState();
}

void AudioPlayer::play(const QString &filePath)
{
    m_player->setSource(QUrl::fromLocalFile(filePath));
    m_player->play();
}

void AudioPlayer::stop()
{
    m_player->stop();
}

void AudioPlayer::togglePlayback()
{
    if(m_player->playbackState() == QMediaPlayer::PlayingState)
    {
        m_player->pause();
    }
    else {
        m_player->play();
    }
}

void AudioPlayer::onStateChanged(QMediaPlayer::PlaybackState state)
{
    emit stateChanged(state);
}

void AudioPlayer::onMediaStatusChanged(QMediaPlayer::MediaStatus state)
{
    if(state == QMediaPlayer::EndOfMedia)
    {
        emit trackFinished();
    }
}

void AudioPlayer::onPositionChanged(qint64 position)
{
    emit positionChanged(position);
}

void AudioPlayer::onDurationChanged(qint64 duration)
{
    emit durationChanged(duration);
}

int AudioPlayer::volume() const
{
    return m_audioOutput->volume() * 100;
}

void AudioPlayer::setVolume(int volume)
{
    m_audioOutput->setVolume(volume / 100.0);
}
