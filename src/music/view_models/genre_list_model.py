from __future__ import annotations
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QObject
from typing import Any

from src.music.core.library import Library


class GenreListModel(QAbstractListModel):
    def __init__(self, library: Library, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._library = library
        self._genres = self._library.getGenres()
        self._genres.insert(0, "All Genres")

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._genres)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or index.row() >= len(self._genres) or role != Qt.ItemDataRole.DisplayRole:
            return None
        return self._genres[index.row()]

    def getGenre(self, row: int) -> str:
        if 0 <= row < len(self._genres):
            return self._genres[row]
        return ""
