#include "cover_image_provider.h"
#include <QImage>
#include <QDir>
#include <QFileInfo>

CoverImageProvider::CoverImageProvider() : QQuickImageProvider(QQuickImageProvider::Image)
{
}

QImage CoverImageProvider::requestImage(const QString &id, QSize *size, const QSize &requestedSize)
{
    int width = requestedSize.isValid() ? requestedSize.width() : 1024;
    int height = requestedSize.isValid() ? requestedSize.height() : 1024;

    QFileInfo fileInfo(id);
    QStringList coverFileNames{"cover.jpg", "folder.jpg", "cover.png", "cover.jpeg"};
    QString imagePath;

    for (const QString &fileName : coverFileNames) {
        imagePath = fileInfo.path() + "/" + fileName;
        if (QFile::exists(imagePath)) {
            break;
        }
    }

    if (m_cache.contains(imagePath)) {
        return m_cache.value(imagePath);
    }

    QImage image;
    if (QFile::exists(imagePath)) {
        image.load(imagePath);
        image = image.scaled(width, height, Qt::IgnoreAspectRatio, Qt::SmoothTransformation);
    } else {
        image = QImage(width, height, QImage::Format_RGB32);
        image.fill(Qt::black);
    }

    m_cache.insert(imagePath, image);

    return image;
}
