from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QWidget

from src.music.core.models.release_result import ReleaseResult


class SearchResultsTableModel(QAbstractTableModel):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._results: list[ReleaseResult] = []
        self._headers = ["Artist", "Title", "Date", "Country", "Format", "Tracks"]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._results)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            result = self._results[index.row()]
            column = index.column()

            if column == 0:
                return result.artist
            elif column == 1:
                return result.title
            elif column == 2:
                return result.release_date
            elif column == 3:
                return result.country
            elif column == 4:
                return result.format
            elif column == 5:
                return len(result.tracks) if result.tracks else 0

        return None

    def getResult(self, index: QModelIndex) -> ReleaseResult | None:
        """Returns the MBID of the release at the given index."""
        if not index.isValid():
            return None

        return self._results[index.row()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        return None

    def addResult(self, result: ReleaseResult) -> None:
        """Adds a single ReleaseResult object to the table."""
        self.beginInsertRows(QModelIndex(), len(self._results), len(self._results))
        self._results.append(result)
        self.endInsertRows()

    def setResults(self, results: list[ReleaseResult]) -> None:
        """Sets the list of ReleaseResult objects to display in the table."""
        self.beginResetModel()
        self._results = results
        self.endResetModel()

    def clearResults(self) -> None:
        """Clears all results from the model."""
        self.beginResetModel()
        self._results = []
        self.endResetModel()
