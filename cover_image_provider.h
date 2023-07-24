#ifndef COVER_IMAGE_PROVIDER_H
#define COVER_IMAGE_PROVIDER_H

#include <QQuickImageProvider>
#include <QMap>

class CoverImageProvider : public QQuickImageProvider
{
public:
    CoverImageProvider();

    QImage requestImage(const QString &id, QSize *size, const QSize& requestedSize) override;

private:
    QMap<QString, QImage> m_cache;
};

#endif // COVER_IMAGE_PROVIDER_H
