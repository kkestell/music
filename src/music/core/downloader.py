import asyncio
import shutil
import tempfile
from pathlib import Path

from PySide6.QtCore import QObject
from fuzzywuzzy import fuzz

from src.music.core.log import Log
from src.music.core.models.release_result import ReleaseResult
from src.music.core.models.slsk_response import SlskResponse
from src.music.core.models.slsk_match import SlskMatch
from src.music.core.models.slsk_file import SlskFile
from src.music.core.slsk import Slsk
from src.music.core.wish_list import WishList


class Downloader(QObject):
    def __init__(self, soulSeek: Slsk, wishList: WishList, parent=None):
        super().__init__(parent)
        self._soulSeek = soulSeek
        self._wishList = wishList
        self._stopEvent = asyncio.Event()
        self._task: asyncio.Task | None = None

    async def start(self):
        """Start the downloader process"""
        self._task = asyncio.create_task(self._processWishListItems())

    async def _processWishListItems(self):
        Log.info("Downloader waiting 10 seconds before starting")
        await asyncio.sleep(10)

        while True:
            if self._stopEvent.is_set():
                break

            if not await self._wishList.isEmpty():
                wishListItems = await self._wishList.getAllItems()
                for item in wishListItems:
                    if self._stopEvent.is_set():
                        break

                    if item.status == "pending":
                        Log.info(f"Downloading {item.release.title} by {item.release.artist}")
                        responses = await self._soulSeek.searchFiles(f"{item.release.artist} {item.release.title}")
                        if responses:
                            matches = self._findMatches(responses, item.release)
                            tempDir = await self._downloadMatch(matches)
                            if tempDir:
                                Log.info(f"Successfully downloaded {item.release.title} by {item.release.artist} to {tempDir}")
                                item.status = "downloaded"
                                await self._wishList.updateItemStatus(item.id, "downloaded")
                            else:
                                Log.warning(f"Failed to download {item.release.title} by {item.release.artist}")
                        else:
                            Log.info(f"No results found for {item.release.title} by {item.release.artist}")
                        await asyncio.sleep(5)
            else:
                await asyncio.sleep(5)

    async def _downloadMatch(self, matches: list[SlskMatch]) -> Path | None:
        for match in matches:
            for track, file in match.files.items():
                await self._soulSeek.enqueueDownload(match.username, file.name)
        await self._soulSeek.waitForDownloads()

        # """
        # Loops through the matches and attempts to download all files for each match.
        # Creates a temp directory for each match attempt. If successful, returns the
        # temp directory Path. If failed, cleans up and returns None.
        # """
        # for match in matches:
        #     Log.info(f"Attempting download from user {match.username}")
        #     temp_dir = Path(tempfile.mkdtemp())
        #
        #     successful_downloads = []
        #     failed = False
        #
        #     for track, file in match.files.items():
        #         if self._stopEvent.is_set():
        #             Log.info("Stop event detected during download, breaking")
        #             shutil.rmtree(temp_dir)
        #             return None
        #
        #         downloaded_path = await self._soulSeek.downloadFile(match.username, file.name)
        #
        #         if downloaded_path:
        #             # Copy to temp dir and delete original
        #             temp_path = temp_dir / downloaded_path.name
        #             shutil.copy2(downloaded_path, temp_path)
        #             downloaded_path.unlink()
        #             successful_downloads.append(temp_path)
        #         else:
        #             failed = True
        #             Log.warning(f"Failed to download {file.name} from {match.username}")
        #             # Clean up any successful downloads
        #             for path in successful_downloads:
        #                 path.unlink(missing_ok=True)
        #             shutil.rmtree(temp_dir)
        #             break
        #
        #         await asyncio.sleep(1)
        #
        #     if not failed:
        #         Log.info(f"Successfully downloaded all files from {match.username}")
        #         return temp_dir
        #
        #     Log.info(f"Moving to next match after failure from {match.username}")
        #     await asyncio.sleep(2)
        #
        # Log.warning("All download matches failed")
        # return None

    def _findMatches(self, responses: list[SlskResponse], release: ReleaseResult) -> list[
        SlskMatch]:
        MATCH_THRESHOLD = 85
        matches = []

        for response in responses:
            # Skip if we don't have enough files for all tracks
            if len(response.files) < len(release.tracks):
                continue

            # Try to find matches for all tracks
            track_to_file_mapping: dict[str, SlskFile] = {}
            used_files = set()  # Keep track of which files we've matched

            for track in release.tracks:
                best_match_score = MATCH_THRESHOLD
                best_match_file = None

                # Find the best matching file for this track
                for file in response.files:
                    if file in used_files:
                        continue

                    # Calculate similarity score
                    score = fuzz.partial_ratio(track.lower(), file.name.lower())

                    if score > best_match_score:
                        best_match_score = score
                        best_match_file = file

                # If we found a match for this track
                if best_match_file:
                    track_to_file_mapping[track] = best_match_file
                    used_files.add(best_match_file)

            # If we found matches for all tracks, this is a valid match
            if len(track_to_file_mapping) == len(release.tracks):
                matches.append(SlskMatch(
                    username=response.username,
                    files=track_to_file_mapping
                ))

        return matches

    async def stop(self):
        """Stop the downloader process"""
        Log.info("Stopping downloader")
        self._stopEvent.set()
        if self._task:
            await self._task
