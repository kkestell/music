from __future__ import annotations
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QObject
from typing import Any

from src.music.core.library import Library


class ArtistListModel(QAbstractListModel):
    def __init__(self, library: Library, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._library = library
        self._artists: list[str] = []
        self._genre = ""
        self.setGenreFilter("")

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._artists)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or index.row() >= len(self._artists) or role != Qt.ItemDataRole.DisplayRole:
            return None
        return self._artists[index.row()]

    def setGenreFilter(self, genre: str) -> None:
        self.beginResetModel()
        self._genre = genre
        self._artists = self._library.getArtists(genre)
        self._artists.insert(0, "All Artists")
        self.endResetModel()

    def getArtist(self, row: int) -> str:
        if 0 <= row < len(self._artists):
            return self._artists[row]
        return ""
