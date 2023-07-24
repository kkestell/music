#include "playlist_model.h"

PlaylistModel::PlaylistModel(QObject* parent)
        : QAbstractListModel(parent)
{
}

QVariant PlaylistModel::data(const QModelIndex &index, int role) const
{
    if (index.row() < 0 || index.row() >= m_songList.count())
        return {};

    const Song &song = m_songList[index.row()];
    if (role == TitleRole)
        return song.title;
    else if (role == ArtistRole)
        return song.artist;
    else if (role == AlbumRole)
        return song.album;
    else if (role == PathRole)
        return song.path;

    return {};
}

QHash<int, QByteArray> PlaylistModel::roleNames() const
{
    QHash<int, QByteArray> roles;
    roles[TitleRole] = "title";
    roles[ArtistRole] = "artist";
    roles[AlbumRole] = "album";
    roles[PathRole] = "path";
    return roles;
}

int PlaylistModel::rowCount(const QModelIndex &parent) const
{
    Q_UNUSED(parent);
    return m_songList.count();
}

void PlaylistModel::addSong(const Song& song)
{
    beginInsertRows(QModelIndex(), rowCount(), rowCount());
    m_songList << song;
    endInsertRows();

    if (m_currentSong.title.isEmpty() && m_currentSong.artist.isEmpty() &&
        m_currentSong.album.isEmpty() && m_currentSong.path.isEmpty())
        m_currentSong = song;
}

Song PlaylistModel::getSong(int index) const
{
    return m_songList.at(index);
}

int PlaylistModel::indexOf(const Song& song) const
{
    return m_songList.indexOf(song);
}

int PlaylistModel::length() const
{
    return rowCount();
}

void PlaylistModel::clear()
{
    beginRemoveRows(QModelIndex(), 0, m_songList.count() - 1);
    m_songList.clear();
    endRemoveRows();
}