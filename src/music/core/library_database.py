from __future__ import annotations
from PySide6.QtCore import QStandardPaths
from pathlib import Path
import threading
from src.music.core.models.track import Track
from src.music.core.log import Log
import sqlite3
from typing import Any


class LibraryDatabase:
    def __init__(self) -> None:
        dataLocation = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
        self.dbPath = Path(dataLocation) / "library.db"
        self.dbPath.parent.mkdir(parents=True, exist_ok=True)

        self._local = threading.local()
        self._initializeDatabase()

    def _initializeDatabase(self) -> None:
        with self._getConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY,
                    artist TEXT,
                    album_artist TEXT,
                    album TEXT,
                    track_number INTEGER,
                    track_total INTEGER,
                    name TEXT,
                    duration INTEGER,
                    year INTEGER,
                    genre TEXT,
                    musicbrainz_album_id TEXT,
                    musicbrainz_artist_id TEXT,
                    musicbrainz_track_id TEXT,
                    path TEXT,
                    format TEXT
                )
            """)
            conn.commit()
            Log.verbose(f"Database initialized at: {self.dbPath}")

    def _getConnection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(self.dbPath)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def getGenres(self) -> list[str]:
        with self._getConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT genre FROM tracks ORDER BY genre")
            return [row[0] for row in cursor.fetchall() if row[0]]

    def getArtists(self, genre: str = "") -> list[str]:
        with self._getConnection() as conn:
            cursor = conn.cursor()
            if not genre:
                cursor.execute("SELECT DISTINCT album_artist FROM tracks ORDER BY album_artist")
            else:
                cursor.execute("SELECT DISTINCT album_artist FROM tracks WHERE genre = ? ORDER BY album_artist",
                               (genre,))
            return [row[0] for row in cursor.fetchall() if row[0]]

    def getAlbums(self, genre: str = "", artist: str = "") -> list[str]:
        with self._getConnection() as conn:
            cursor = conn.cursor()
            query = "SELECT DISTINCT album FROM tracks"
            params: list[Any] = []
            conditions = []

            if genre:
                conditions.append("genre = ?")
                params.append(genre)
            if artist:
                conditions.append("album_artist = ?")
                params.append(artist)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY album"

            cursor.execute(query, params)
            return [row[0] for row in cursor.fetchall() if row[0]]

    def getTracks(self, genre: str = "", artist: str = "", album: str = "") -> list[Track]:
        with self._getConnection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT id, artist, album_artist, album, track_number, track_total, name,
                       duration, year, genre, musicbrainz_album_id, musicbrainz_artist_id,
                       musicbrainz_track_id, path, format
                FROM tracks
            """
            params: list[Any] = []
            conditions = []

            if genre:
                conditions.append("genre = ?")
                params.append(genre)
            if artist:
                conditions.append("album_artist = ?")
                params.append(artist)
            if album:
                conditions.append("album = ?")
                params.append(album)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY album_artist, album, track_number"

            cursor.execute(query, params)

            return [Track(
                id=row[0],
                name=row[6],
                trackNumber=row[4],
                trackTotal=row[5],
                duration=row[7],
                artist=row[1],
                albumArtist=row[2],
                album=row[3],
                year=row[8],
                genre=row[9],
                format=row[14],
                musicbrainzAlbumId=row[10],
                musicbrainzArtistId=row[11],
                musicbrainzTrackId=row[12],
                path=row[13]
            ) for row in cursor.fetchall()]

    def addTrack(self, track: Track) -> None:
        with self._getConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tracks (
                    artist, album_artist, album, track_number, track_total, name,
                    duration, year, genre, musicbrainz_album_id, musicbrainz_artist_id,
                    musicbrainz_track_id, path, format
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                track.artist, track.albumArtist, track.album, track.trackNumber,
                track.trackTotal, track.name, track.duration, track.year,
                track.genre, track.musicbrainzAlbumId, track.musicbrainzArtistId,
                track.musicbrainzTrackId, track.path, track.format
            ))
            conn.commit()
            Log.verbose(f"Track added successfully. ID: {cursor.lastrowid}")

    def removeTrack(self, trackId: int) -> None:
        with self._getConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tracks WHERE id = ?", (trackId,))
            conn.commit()

    def updateTrack(self, track: Track) -> None:
        with self._getConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tracks SET
                    artist = ?, album_artist = ?, album = ?,
                    track_number = ?, track_total = ?, name = ?,
                    duration = ?, year = ?, genre = ?,
                    musicbrainz_album_id = ?, musicbrainz_artist_id = ?,
                    musicbrainz_track_id = ?, path = ?, format = ?
                WHERE id = ?
            """, (
                track.artist, track.albumArtist, track.album,
                track.trackNumber, track.trackTotal, track.name,
                track.duration, track.year, track.genre,
                track.musicbrainzAlbumId, track.musicbrainzArtistId,
                track.musicbrainzTrackId, track.path, track.format,
                track.id
            ))
            conn.commit()