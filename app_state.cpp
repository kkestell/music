#include "app_state.h"
#include <QDebug>

const QStringList AppState::audioExtensions = QStringList() << "mp3"  << "m4a"  << "ogg"  << "wav" << "flac" << "aac"
                                                            << "wma"  << "alac" << "opus" << "mpc" << "ape"  << "tta"
                                                            << "ac3"  << "dts";

AppState::AppState(PlaylistModel *playlistModel, QObject *parent)
        : QObject(parent),
          m_audioPlayer(new AudioPlayer(this)),
          m_metadataLoader(new MetadataLoader(this)),
          m_playlistModel(playlistModel),
          m_currentSongIndex(-1),
          m_sidebarVisible(true)
{
    connect(m_audioPlayer, &AudioPlayer::stateChanged,    this, &AppState::playbackStateChanged);
    connect(m_audioPlayer, &AudioPlayer::durationChanged, this, &AppState::durationChanged);
    connect(m_audioPlayer, &AudioPlayer::positionChanged, this, &AppState::positionChanged);
    connect(m_audioPlayer, &AudioPlayer::trackFinished,   this, &AppState::nextSong);
}

int AppState::currentSongIndex() const
{
    return m_currentSongIndex;
}

void AppState::setCurrentSongIndex(int index)
{
    if (index < 0 || index >= m_playlistModel->length())
        return;

    if (index == m_currentSongIndex)
    {
        togglePlayback();
        return;
    }

    m_currentSongIndex = index;
    emit currentSongIndexChanged(m_currentSongIndex);
    emit currentSongChanged(currentSong());

    m_audioPlayer->play(m_playlistModel->getSong(m_currentSongIndex).path);
}

void AppState::togglePlayback()
{
    m_audioPlayer->togglePlayback();
}

void AppState::nextSong()
{
    if (m_currentSongIndex + 1 < m_playlistModel->length())
    {
        setCurrentSongIndex(m_currentSongIndex + 1);
    }
    else
    {
        setCurrentSongIndex(0);
    }
}

void AppState::previousSong()
{
    if (m_currentSongIndex - 1 >= 0)
    {
        setCurrentSongIndex(m_currentSongIndex - 1);
    }
    else
    {
        setCurrentSongIndex(m_playlistModel->length() - 1);
    }
}

void AppState::clearPlaylist()
{
    m_audioPlayer->stop();
    m_playlistModel->clear();
    m_currentSongIndex = -1;
    emit currentSongIndexChanged(m_currentSongIndex);
    emit currentSongChanged(currentSong());
    emit emptyChanged(empty());
    emit sidebarVisibleChanged(sidebarVisible());
}

int AppState::volume() const
{
    return m_audioPlayer->volume();
}

void AppState::setVolume(int volume)
{
    if (m_audioPlayer->volume() != volume)
    {
        m_audioPlayer->setVolume(volume);
        emit volumeChanged(volume);
    }
}

bool AppState::sidebarVisible() const
{
    return !empty() && m_sidebarVisible;
}

void AppState::setSidebarVisible(bool visible)
{
    m_sidebarVisible = visible;
    emit sidebarVisibleChanged(m_sidebarVisible);
}

void AppState::addUrl(const QUrl &url)
{
    auto localFile = url.toLocalFile();
    QFileInfo fileInfo(localFile);

    if (fileInfo.isDir())
    {
        addDirectory(QDir(localFile));
    }
    else if (isAudioFile(localFile))
    {
        addFile(localFile);
    }
}

void AppState::addDirectory(const QDir &dir)
{
    auto files = dir.entryList(QDir::Files | QDir::NoDotAndDotDot | QDir::Hidden | QDir::AllDirs | QDir::Readable, QDir::Name);

    for (const QString &file : files)
    {
        QFileInfo fileInfo(dir, file);

        if (fileInfo.isDir())
        {
            addDirectory(QDir(fileInfo.absoluteFilePath()));
        }
        else if (isAudioFile(fileInfo.absoluteFilePath()))
        {
            addFile(fileInfo.absoluteFilePath());
        }
    }
}

void AppState::addFile(const QString &filePath)
{
    auto song = m_metadataLoader->load(filePath);
    m_playlistModel->addSong(song);

    if (m_currentSongIndex == -1)
    {
        setCurrentSongIndex(0);
        emit emptyChanged(empty());
        emit sidebarVisibleChanged(sidebarVisible());
    }
}

Song AppState::currentSong() const
{
    if (m_currentSongIndex == -1)
        return {};

    auto song = m_playlistModel->getSong(m_currentSongIndex);

    return song;
}

bool AppState::empty() const
{
    return m_currentSongIndex == -1;
}

qint64 AppState::duration() const
{
    return m_audioPlayer->duration();
}

qint64 AppState::position() const
{
    return m_audioPlayer->position();
}

QString AppState::playbackState() const
{
    switch(m_audioPlayer->state()) {
        case QMediaPlayer::StoppedState:
            return "StoppedState";
        case QMediaPlayer::PlayingState:
            return "PlayingState";
        case QMediaPlayer::PausedState:
            return "PausedState";
        default:
            return "UnknownState";
    }
}

bool AppState::isAudioFile(const QString &filePath)
{
    return audioExtensions.contains(QFileInfo(filePath).suffix().toLower());
}
