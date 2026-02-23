#ifndef METADATA_LOADER_H
#define METADATA_LOADER_H

#include <taglib/fileref.h>
#include <taglib/tag.h>
#include <QString>
#include <QFileInfo>
#include "song.h"

class MetadataLoader : public QObject
{
Q_OBJECT
public:
    explicit MetadataLoader(QObject *parent = nullptr);
    static Song load(const QString &path);
};

#endif // METADATA_LOADER_H
