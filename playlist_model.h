#ifndef PLAYLIST_MODEL_H
#define PLAYLIST_MODEL_H

#include <QAbstractListModel>
#include "song.h"

class PlaylistModel : public QAbstractListModel
{
Q_OBJECT

public:
    enum Roles {
        TitleRole = Qt::UserRole + 1,
        ArtistRole,
        AlbumRole,
        PathRole
    };
    Q_ENUM(Roles)

    explicit PlaylistModel(QObject* parent = nullptr);

    QVariant data(const QModelIndex &index, int role = Qt::DisplayRole) const override;
    QHash<int, QByteArray> roleNames() const override;
    int rowCount(const QModelIndex &parent = QModelIndex()) const override;

    void addSong(const Song& song);
    Song getSong(int index) const;
    int indexOf(const Song& song) const;
    int length() const;
    void clear();

private:
    QList<Song> m_songList;
    Song m_currentSong;
};

#endif // PLAYLIST_MODEL_H
