import asyncio
from PySide6.QtWidgets import QWidget, QLineEdit, QPushButton, QTableView, QVBoxLayout, QHBoxLayout, QHeaderView, QMenu
from PySide6.QtCore import Qt, QPoint

from src.music.core.models.release_result import ReleaseResult
from src.music.core.musicbrainz import MusicBrainz
from src.music.core.wish_list import WishList
from src.music.view_models.search_results_table_model import SearchResultsTableModel


class SearchTab(QWidget):
    def __init__(self, queue: WishList, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._wishList = queue

        # UI elements
        self._artistEdit: QLineEdit
        self._albumEdit: QLineEdit
        self._searchButton: QPushButton
        self._resultsTable: QTableView
        self._resultsModel: SearchResultsTableModel

        # MusicBrainz API handler
        self._musicbrainz = MusicBrainz()

        # Main layout
        mainLayout = QVBoxLayout(self)

        # Search controls
        searchLayout = QHBoxLayout()

        self._artistEdit = QLineEdit(self)
        self._artistEdit.setPlaceholderText(self.tr("Artist name"))
        searchLayout.addWidget(self._artistEdit)

        self._albumEdit = QLineEdit(self)
        self._albumEdit.setPlaceholderText(self.tr("Album title"))
        searchLayout.addWidget(self._albumEdit)

        self._searchButton = QPushButton(self.tr("Search"), self)
        self._searchButton.clicked.connect(self.onSearchClicked)
        searchLayout.addWidget(self._searchButton)

        mainLayout.addLayout(searchLayout)

        # Results table
        self._resultsTable = QTableView(self)
        self._resultsModel = SearchResultsTableModel(self)
        self._resultsTable.setModel(self._resultsModel)

        # Configure table appearance
        header = self._resultsTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._resultsTable.verticalHeader().hide()

        # Set row selection mode
        self._resultsTable.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

        # Add context menu
        self._resultsTable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._resultsTable.customContextMenuRequested.connect(self.showContextMenu)

        mainLayout.addWidget(self._resultsTable)

        # Connect return/enter in text fields to search
        self._artistEdit.returnPressed.connect(self.onSearchClicked)
        self._albumEdit.returnPressed.connect(self.onSearchClicked)

    def setControlsEnabled(self, enabled: bool) -> None:
        """Enable or disable all input controls."""
        self._artistEdit.setEnabled(enabled)
        self._albumEdit.setEnabled(enabled)
        self._searchButton.setEnabled(enabled)

    def onSearchClicked(self) -> None:
        artist = self._artistEdit.text().strip()
        album = self._albumEdit.text().strip()

        # Clear current results and disable controls
        self._resultsModel.clearResults()
        self.setControlsEnabled(False)

        # Start async search task
        asyncio.create_task(self.performSearch(artist, album))

    async def performSearch(self, artist: str, album: str) -> None:
        """Asynchronously perform a search and update the UI with results."""
        async for result in self._musicbrainz.searchReleases(artist, album):
            self.onSearchResultAvailable(result)
        self.onSearchComplete()

    def onSearchResultAvailable(self, result: ReleaseResult) -> None:
        """Handle a single search result."""
        self._resultsModel.addResult(result)

    def onSearchComplete(self) -> None:
        """Handle search results from the async search."""
        self.setControlsEnabled(True)

    def showContextMenu(self, position: QPoint) -> None:
        """Show a right-click context menu."""
        menu = QMenu(self)
        addToQueueAction = menu.addAction(self.tr("Add to Wish List"))
        addToQueueAction.triggered.connect(lambda: asyncio.create_task(self.addToWishList()))
        menu.exec(self._resultsTable.mapToGlobal(position))

    async def addToWishList(self) -> None:
        release = self._resultsModel.getResult(self._resultsTable.currentIndex())
        await self._wishList.addRelease(release)
