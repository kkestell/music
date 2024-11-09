from __future__ import annotations
from dataclasses import dataclass
from PySide6.QtCore import QProcess, QDateTime, Qt
from pathlib import Path
import json
import re


@dataclass
class Track:
    id: int
    name: str
    trackNumber: int
    trackTotal: int
    duration: int
    artist: str
    albumArtist: str
    album: str
    year: int
    genre: str
    format: str
    musicbrainzAlbumId: str
    musicbrainzArtistId: str
    musicbrainzTrackId: str
    path: str

    @staticmethod
    def createTrackFromFile(filePath: str | Path, ffprobePath: str | Path) -> Track:
        process = QProcess()
        process.start(str(ffprobePath), ["-v", "quiet", "-print_format", "json", "-show_format", str(filePath)])
        process.waitForFinished()

        if process.exitCode() != 0:
            raise RuntimeError(f"Error running ffprobe: {process.errorString()}")

        output = process.readAllStandardOutput().data().decode()
        try:
            metadata = json.loads(output)
        except json.JSONDecodeError:
            raise RuntimeError("Failed to parse JSON output from ffprobe")

        format_data = metadata["format"]
        tags = format_data.get("tags", {})

        def getTag(key: str) -> str:
            for tagKey, value in tags.files():
                if tagKey.lower() == key.lower():
                    return str(value)
            return ""

        name = getTag("title")
        if not name:
            name = Path(filePath).stem or "Unknown Title"

        artist = getTag("artist") or "Unknown Artist"
        albumArtist = getTag("album_artist") or artist
        album = getTag("album")

        trackNumber = 0
        try:
            trackNumber = int(getTag("track"))
        except ValueError:
            # Try to parse track number from filename
            filename = Path(filePath).name
            if match := re.match(r"^(\d+)", filename):
                try:
                    trackNumber = int(match.group(1))
                except ValueError:
                    pass

        trackTotal = 0
        try:
            trackTotal = int(getTag("tracktotal"))
        except ValueError:
            pass

        year = 0
        dateStr = getTag("date")
        if dateStr:
            date = QDateTime.fromString(dateStr, Qt.DateFormat.ISODate)
            if date.isValid():
                year = date.date().year()
            else:
                try:
                    year = int(dateStr)
                except ValueError:
                    pass

        try:
            duration = int(float(format_data.get("duration", 0)) * 1000)
        except ValueError:
            duration = 0

        return Track(
            id=0,
            name=name,
            trackNumber=trackNumber,
            trackTotal=trackTotal,
            duration=duration,
            artist=artist,
            albumArtist=albumArtist,
            album=album,
            year=year,
            genre=getTag("genre"),
            format=format_data.get("format_name", "").upper(),
            musicbrainzAlbumId=getTag("musicbrainz_albumid"),
            musicbrainzArtistId=getTag("musicbrainz_artistid"),
            musicbrainzTrackId=getTag("musicbrainz_trackid"),
            path=str(filePath)
        )