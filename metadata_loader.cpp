#include "metadata_loader.h"

MetadataLoader::MetadataLoader(QObject *parent)
        : QObject(parent)
{
}

Song MetadataLoader::load(const QString &path)
{
    QFileInfo fileInfo(path);
    if (!fileInfo.exists())
        return {};

    TagLib::FileRef file(path.toStdString().c_str());

    if (file.isNull() || !file.tag())
        return {};

    TagLib::Tag *tag = file.tag();

    Song song;
    song.path = path;
    song.artist = tag->artist().isEmpty() ? QString("Unknown Artist") : QString::fromStdString(tag->artist().to8Bit(true));
    song.album = tag->album().isEmpty() ? QString("Unknown Album") : QString::fromStdString(tag->album().to8Bit(true));
    song.title = tag->title().isEmpty() ? QString("Unknown Title") : QString::fromStdString(tag->title().to8Bit(true));

    return song;
}
