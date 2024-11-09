from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListView,
    QTableView, QSplitter, QHeaderView
)
from PySide6.QtCore import Qt, QModelIndex

from src.music.core.library import Library
from src.music.view_models.album_list_model import AlbumListModel
from src.music.view_models.artist_list_model import ArtistListModel
from src.music.view_models.genre_list_model import GenreListModel
from src.music.view_models.track_table_model import TrackTableModel


class LibraryTab(QWidget):
    def __init__(self, library: Library, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._library = library

        # UI elements
        self._genreListView: QListView
        self._artistListView: QListView
        self._albumListView: QListView
        self._trackTableView: QTableView

        # Models
        self._genreModel: GenreListModel
        self._artistModel: ArtistListModel
        self._albumModel: AlbumListModel
        self._trackModel: TrackTableModel

        # Selection state
        self._selectedGenre = ""
        self._selectedArtist = ""
        self._selectedAlbum = ""

        self.setupUi()
        self.setupModels()

    def setupUi(self) -> None:
        mainLayout = QVBoxLayout(self)
        # mainLayout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Vertical, self)
        mainLayout.addWidget(splitter)

        # Top half
        topWidget = QWidget(splitter)
        topLayout = QHBoxLayout(topWidget)
        topLayout.setContentsMargins(0, 0, 0, 0)

        self._genreListView = QListView(topWidget)
        self._artistListView = QListView(topWidget)
        self._albumListView = QListView(topWidget)

        topLayout.addWidget(self._genreListView)
        topLayout.addWidget(self._artistListView)
        topLayout.addWidget(self._albumListView)

        splitter.addWidget(topWidget)

        # Bottom half
        self._trackTableView = QTableView(splitter)
        splitter.addWidget(self._trackTableView)

    def setupModels(self) -> None:
        self._genreModel = GenreListModel(self._library)
        self._genreListView.setModel(self._genreModel)
        self._genreListView.selectionModel().currentChanged.connect(self.onGenreSelected)

        self._artistModel = ArtistListModel(self._library)
        self._artistListView.setModel(self._artistModel)
        self._artistListView.selectionModel().currentChanged.connect(self.onArtistSelected)

        self._albumModel = AlbumListModel(self._library)
        self._albumListView.setModel(self._albumModel)
        self._albumListView.selectionModel().currentChanged.connect(self.onAlbumSelected)

        self._trackModel = TrackTableModel(self._library)
        self._trackTableView.setModel(self._trackModel)

        header = self._trackTableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._trackTableView.verticalHeader().hide()

        self.updateFilters()

    def onGenreSelected(self, index: QModelIndex) -> None:
        self._selectedGenre = self._genreModel.getGenre(index.row())
        self._selectedArtist = ""
        self._selectedAlbum = ""
        self.updateFilters()

    def onArtistSelected(self, index: QModelIndex) -> None:
        self._selectedArtist = self._artistModel.getArtist(index.row())
        self._selectedAlbum = ""
        self.updateFilters()

    def onAlbumSelected(self, index: QModelIndex) -> None:
        self._selectedAlbum = self._albumModel.getAlbum(index.row())
        self.updateFilters()

    def updateFilters(self) -> None:
        self._artistModel.setGenreFilter(self._selectedGenre)
        self._albumModel.setFilters(self._selectedGenre, self._selectedArtist)
        self._trackModel.setFilters(self._selectedGenre, self._selectedArtist, self._selectedAlbum)

    def refreshModels(self) -> None:
        self.setupModels()