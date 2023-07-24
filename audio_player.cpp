#include "audio_player.h"

AudioPlayer::AudioPlayer(QObject *parent) : QObject(parent)
{
    m_player = new QMediaPlayer(this);

    connect(m_player, &QMediaPlayer::stateChanged,       this, &AudioPlayer::onStateChanged);
    connect(m_player, &QMediaPlayer::mediaStatusChanged, this, &AudioPlayer::onMediaStatusChanged);
    connect(m_player, &QMediaPlayer::positionChanged,    this, &AudioPlayer::onPositionChanged);
    connect(m_player, &QMediaPlayer::durationChanged,    this, &AudioPlayer::onDurationChanged);
}

qint64 AudioPlayer::position() const
{
    return m_player->position();
}

qint64 AudioPlayer::duration() const
{
    return m_player->duration();
}

QMediaPlayer::State AudioPlayer::state() const
{
    return m_player->state();
}

void AudioPlayer::play(const QString &filePath)
{
    m_player->setMedia(QUrl::fromLocalFile(filePath));
    m_player->play();
}

void AudioPlayer::stop()
{
    m_player->stop();
}

void AudioPlayer::togglePlayback()
{
    if(m_player->state() == QMediaPlayer::PlayingState)\
    {
        m_player->pause();
    }
    else {
        m_player->play();
    }
}

void AudioPlayer::onStateChanged(QMediaPlayer::State state)
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
    return m_player->volume();
}

void AudioPlayer::setVolume(int volume)
{
    m_player->setVolume(volume);
}
