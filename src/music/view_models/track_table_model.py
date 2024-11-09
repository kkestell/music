from __future__ import annotations
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QObject, QTime
from typing import Any

from src.music.core.library import Library
from src.music.core.models.track import Track
from src.music.core.log import Log


class TrackTableModel(QAbstractTableModel):
    def __init__(self, library: Library, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._library = library
        self._tracks: list[Track] = []
        self._genreFilter = ""
        self._artistFilter = ""
        self._albumFilter = ""

        self._tracks = self._library.getTracks()
        Log.verbose(f"TrackModel initialized with {len(self._tracks)} tracks")
        # for track in self._tracks:
        #     Log.verbose(f"Track: {track.name} Artist: {track.artist} Album: {track.album}")
        # if not self._tracks:
        #     Log.verbose("Warning: TrackModel initialized with no tracks")

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._tracks)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 5

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or index.row() >= len(self._tracks) or role != Qt.ItemDataRole.DisplayRole:
            return None

        track = self._tracks[index.row()]
        match index.column():
            case 0:
                return f"{track.trackNumber} of {track.trackTotal}"
            case 1:
                return track.name
            case 2:
                time = QTime(0, 0, 0).addMSecs(track.duration)
                return time.toString("mm:ss")
            case 3:
                return track.artist
            case 4:
                return track.album
            case _:
                return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if role != Qt.ItemDataRole.DisplayRole or orientation != Qt.Orientation.Horizontal:
            return None

        match section:
            case 0:
                return "#"
            case 1:
                return "Name"
            case 2:
                return "Time"
            case 3:
                return "Artist"
            case 4:
                return "Album"
            case _:
                return None

    def setFilters(self, genre: str, artist: str, album: str) -> None:
        self.beginResetModel()
        self._genreFilter = "" if genre == "All Genres" else genre
        self._artistFilter = "" if artist == "All Artists" else artist
        self._albumFilter = "" if album == "All Albums" else album
        self._tracks = self._library.getTracks(self._genreFilter, self._artistFilter, self._albumFilter)
        self.endResetModel()
