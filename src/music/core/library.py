from __future__ import annotations
from pathlib import Path
import re
from src.music.core.config import Config
from src.music.core.library_database import LibraryDatabase
from src.music.core.models.track import Track
from src.music.core.log import Log

class Library:
    def __init__(self) -> None:
        self._database = LibraryDatabase()

    def getGenres(self) -> list[str]:
        return self._database.getGenres()

    def getArtists(self, genre: str = "") -> list[str]:
        if genre == "All Genres":
            return self._database.getArtists()
        return self._database.getArtists(genre)

    def getAlbums(self, genre: str = "", artist: str = "") -> list[str]:
        genreFilter = "" if genre == "All Genres" else genre
        artistFilter = "" if artist == "All Artists" else artist
        return self._database.getAlbums(genreFilter, artistFilter)

    def getTracks(self, genre: str = "", artist: str = "", album: str = "") -> list[Track]:
        genreFilter = "" if genre == "All Genres" else genre
        artistFilter = "" if artist == "All Artists" else artist
        albumFilter = "" if album == "All Albums" else album
        return self._database.getTracks(genreFilter, artistFilter, albumFilter)

    def importTrack(self, track: Track) -> None:
        libraryPath = Config.instance().libraryPath
        if not libraryPath:
            Log.error("Library path is not set in the configuration!")
            return

        libraryDir = Path(libraryPath)
        trackDir = self.trackDirectory(track)
        self.ensureDirectoryExists(trackDir)

        newFilePath = self.trackFile(track)
        try:
            newFilePath.write_bytes(Path(track.path).read_bytes())
            track.path = str(newFilePath)
            self._database.addTrack(track)
            Log.verbose(f"Track imported successfully: {track.name}")
        except Exception as e:
            Log.warning(f"Failed to copy file: {track.path} to {newFilePath}: {e}")

    @staticmethod
    def sanitizeForPath(name: str) -> str:
        # Remove invalid path characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        # Trim and remove trailing dots
        sanitized = sanitized.strip()
        while sanitized.endswith('.'):
            sanitized = sanitized[:-1].strip()
        return sanitized

    def trackDirectory(self, track: Track) -> Path:
        libraryPath = Config.instance().libraryPath
        artist = self.sanitizeForPath(track.artist)
        albumTitle = self.sanitizeForPath(track.album)
        year = str(track.year) if track.year > 0 else ""

        if year:
            finalPath = f"{artist}/{year} {albumTitle}"
        else:
            finalPath = f"{artist}/{albumTitle}"

        return Path(libraryPath) / finalPath

    def trackFile(self, track: Track) -> Path:
        extension = Path(track.path).suffix.lower()[1:] or "mp3"
        trackDir = self.trackDirectory(track)

        trackNumber = f"{track.trackNumber:02d}" if track.trackNumber > 0 else "00"
        trackTitle = self.sanitizeForPath(track.name) or "Unknown Title"

        return trackDir / f"{trackNumber} {trackTitle}.{extension}"

    @staticmethod
    def ensureDirectoryExists(dir: Path) -> None:
        try:
            dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            Log.warning(f"Failed to create directory: {dir}: {e}")