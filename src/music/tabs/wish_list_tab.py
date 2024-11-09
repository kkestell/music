import asyncio
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtWidgets import QWidget, QTableView, QVBoxLayout, QHeaderView, QMenu, QPushButton
from qasync import asyncSlot

from src.music.core.models.wish_list_item import WishListItem
from src.music.core.wish_list import WishList
from src.music.view_models.wish_list_table_model import WishListTableModel


class WishListTab(QWidget):
    def __init__(self, wishList: WishList, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._wishList = wishList
        self._wishList.itemAdded.connect(self.addItem)

        # Main layout
        mainLayout = QVBoxLayout(self)

        # Refresh button
        self._refreshButton = QPushButton(self.tr("Refresh Queue"), self)
        self._refreshButton.clicked.connect(self.loadWishList)
        mainLayout.addWidget(self._refreshButton)

        # Queue table
        self._wishListTable = QTableView(self)
        self._wishListModel = WishListTableModel(self)
        self._wishListTable.setModel(self._wishListModel)

        # Configure table appearance
        header = self._wishListTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._wishListTable.verticalHeader().hide()

        # Set row selection mode
        self._wishListTable.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

        # Add context menu
        self._wishListTable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._wishListTable.customContextMenuRequested.connect(self.showContextMenu)

        mainLayout.addWidget(self._wishListTable)

        # Load initial queue items after the event loop starts
        QTimer.singleShot(0, self.loadWishList)

    @asyncSlot()
    async def loadWishList(self) -> None:
        """Load all items from the release queue into the model."""
        items = await self._wishList.getAllItems()
        self._wishListModel.setItems(items)

    def showContextMenu(self, position: QPoint) -> None:
        """Show a right-click context menu for queue actions."""
        menu = QMenu(self)
        removeAction = menu.addAction(self.tr("Remove from Queue"))
        removeAction.triggered.connect(lambda: asyncio.create_task(self.onRemoveFromQueue()))
        menu.exec(self._wishListTable.mapToGlobal(position))

    async def onRemoveFromQueue(self) -> None:
        """Remove the selected item from the queue."""
        selectedIndex = self._wishListTable.currentIndex()
        item = self._wishListModel.getItem(selectedIndex)
        if item:
            await self._wishList.removeItem(item.id)
            await self.loadWishList()

    @asyncSlot()
    async def addItem(self) -> None:
        await self.loadWishList()

    def closeEvent(self, event):
        self._wishList.itemAdded.disconnect(self.addItem)
        super().closeEvent(event)
