#ifndef SONG_H
#define SONG_H

#include <QString>
#include <QMetaType>

struct Song {
    Q_GADGET

    Q_PROPERTY(QString title  MEMBER title)
    Q_PROPERTY(QString artist MEMBER artist)
    Q_PROPERTY(QString album  MEMBER album)
    Q_PROPERTY(QString path   MEMBER path)

public:
    QString title  = "";
    QString artist = "";
    QString album  = "";
    QString path   = "";

    bool operator==(const Song& other) const {
        return title == other.title && artist == other.artist &&
               album == other.album && path == other.path;
    }
};

Q_DECLARE_METATYPE(Song)

#endif // SONG_H
