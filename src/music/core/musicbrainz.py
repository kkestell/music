import asyncio
from typing import AsyncGenerator

import musicbrainzngs

from src.music.core.models.release_result import ReleaseResult


class MusicBrainz:
    """Encapsulates MusicBrainz API interactions."""

    def __init__(self) -> None:
        # Set up musicbrainzngs
        musicbrainzngs.set_useragent(
            "Music",
            "0.1",
            "https://github.com/kkestell/music"
        )

    async def searchReleases(self, artist: str, album: str, limit: int = 25) -> AsyncGenerator[ReleaseResult, None]:
        """Searches for releases directly, based on artist and album, yielding each ReleaseResult as it’s available."""
        query_parts = []
        if artist:
            query_parts.append(f"artist:{artist}")
        if album:
            query_parts.append(f"release:{album}")

        if not query_parts:
            return

        query = ' AND '.join(query_parts)

        # Run the blocking musicbrainzngs.search_releases in a separate thread
        result = await asyncio.to_thread(musicbrainzngs.search_releases, query, limit=limit)

        # Process and yield each release result as it's available
        for release_data in result['release-list']:
            release_mbid = release_data["id"]
            title = release_data.get("title", "Unknown Title")
            release_date = release_data.get("date", "")
            country = release_data.get("country", "")
            format = release_data.get("medium-list", [{}])[0].get("format", "")
            artist_name = self._getArtistName(release_data)

            # Fetch track information
            tracks = await self._getTracksForRelease(release_mbid)

            # Yield each result as a ReleaseResult
            yield ReleaseResult(
                mbid=release_mbid,
                artist=artist_name,
                title=title,
                release_date=release_date,
                country=country,
                format=format,
                tracks=tracks
            )

    async def _getTracksForRelease(self, release_mbid: str) -> list[str]:
        """Retrieves track titles for a specific release by mbid."""
        result = await asyncio.to_thread(musicbrainzngs.get_release_by_id, release_mbid, includes=["recordings"])
        tracks = [
            track["recording"]["title"]
            for medium in result.get("release", {}).get("medium-list", [])
            for track in medium.get("track-list", [])
        ]
        return tracks

    def _getArtistName(self, release_data: dict) -> str:
        """Extracts artist name from the release data."""
        artist_name = "Unknown"
        if 'artist-credit' in release_data:
            artist_credit = release_data['artist-credit']
            if artist_credit:
                artist_parts = []
                for credit in artist_credit:
                    if isinstance(credit, dict):
                        name = credit.get('artist', {}).get('name', '')
                        join_phrase = credit.get('joinphrase', '')
                        if name:
                            artist_parts.append(name + join_phrase)
                if artist_parts:
                    artist_name = ''.join(artist_parts)
        return artist_name
