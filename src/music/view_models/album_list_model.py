from __future__ import annotations
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QObject
from typing import Any

from src.music.core.library import Library


class AlbumListModel(QAbstractListModel):
    def __init__(self, library: Library, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._library = library
        self._albums: list[str] = []
        self._genreFilter = ""
        self._artistFilter = ""
        self.setFilters("", "")

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._albums)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or index.row() >= len(self._albums) or role != Qt.ItemDataRole.DisplayRole:
            return None
        return self._albums[index.row()]

    def setFilters(self, genre: str, artist: str) -> None:
        self.beginResetModel()
        self._genreFilter = genre
        self._artistFilter = artist
        self._albums = self._library.getAlbums(genre, artist)
        self._albums.insert(0, "All Albums")
        self.endResetModel()

    def getAlbum(self, row: int) -> str:
        if 0 <= row < len(self._albums):
            return self._albums[row]
        return ""
