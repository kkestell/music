from typing import Any
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QWidget
from src.music.core.models.wish_list_item import WishListItem


class WishListTableModel(QAbstractTableModel):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._items: list[WishListItem] = []
        self._headers = ["Id", "Created", "Title", "Artist", "Status"]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._items)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            item = self._items[index.row()]
            column = index.column()

            if column == 0:
                return item.id
            elif column == 1:
                return item.createdAt
            elif column == 2:
                return item.release.title
            elif column == 3:
                return item.release.artist
            elif column == 4:
                return item.status.title()

        return None

    def getItem(self, index: QModelIndex) -> WishListItem | None:
        """Returns the ReleaseQueueItem at the given index."""
        if not index.isValid():
            return None

        return self._items[index.row()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        return None

    def addItem(self, item: WishListItem) -> None:
        """Adds a single ReleaseQueueItem object to the table."""
        self.beginInsertRows(QModelIndex(), len(self._items), len(self._items))
        self._items.append(item)
        self.endInsertRows()

    def setItems(self, items: list[WishListItem]) -> None:
        """Sets the list of ReleaseQueueItem objects to display in the table."""
        self.beginResetModel()
        self._items = items
        self.endResetModel()

    def clearItems(self) -> None:
        """Clears all items from the model."""
        self.beginResetModel()
        self._items = []
        self.endResetModel()
