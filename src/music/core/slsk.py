import asyncio
import logging
import os
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from aioslsk.client import SoulSeekClient
from aioslsk.search.model import SearchRequest, SearchResult
from aioslsk.settings import (
    Settings, CredentialsSettings, NetworkSettings, ListeningSettings,
    ServerSettings, PeerSettings, UpnpSettings, NetworkLimitSettings, SharesSettings
)
from aioslsk.transfer.model import Transfer, TransferDirection

from src.music.core.config import Config
from src.music.core.log import Log
from src.music.core.models.slsk_response import SlskResponse
from src.music.core.models.slsk_file import SlskFile


class Slsk(QObject):
    connectionStatusChanged = Signal(str)
    searchComplete = Signal(list)

    def __init__(self, downloadDir: str, parent=None):
        self.QUEUE_TIMEOUT = 5  # seconds
        self.DOWNLOAD_TIMEOUT = 30  # seconds
        super().__init__(parent)
        self._downloadDir = downloadDir
        self._client: SoulSeekClient | None = None
        self._stopEvent = asyncio.Event()
        self._setupClient()

    def _setupClient(self):
        config = Config.instance()
        settings = Settings(
            credentials=CredentialsSettings(
                username=config.soulseekUsername,
                password=config.soulseekPassword
            ),
            network=NetworkSettings(
                listening=ListeningSettings(
                    port=40000,
                    obfuscatedPort=40001
                ),
                server=ServerSettings(
                    hostname='server.slsknet.org',
                    port=2416
                ),
                peer=PeerSettings(
                    obfuscate=True
                ),
                upnp=UpnpSettings(
                    enabled=True
                ),
                limits=NetworkLimitSettings(
                    uploadSpeedKbps=0,
                    downloadSpeedKbps=0
                )
            ),
            shares=SharesSettings(
                download=self._downloadDir
            )
        )
        Log.adopt(logging.getLogger('aioslsk'), logging.ERROR)
        self._client = SoulSeekClient(settings=settings)
        Log.info("Soulseek client setup completed.")

    async def start(self):
        """Connect to Soulseek and set up the client."""
        await self._connectToSoulSeek()

    async def _connectToSoulSeek(self):
        """Connect to Soulseek, emit connection status, and exit."""
        Log.info("Attempting to connect to Soulseek...")
        os.makedirs(self._downloadDir, exist_ok=True)
        self.connectionStatusChanged.emit("Connecting to Soulseek...")

        try:
            await self._client.shares.scan()
            Log.verbose("Scanned local shares for Soulseek client.")
            await self._client.start()
            Log.info("Soulseek client started.")
            await self._client.login()
            Log.info("Successfully logged into Soulseek.")
            self.connectionStatusChanged.emit("Connected to Soulseek!")
        except Exception as e:
            errorMessage = f"Connection failed: {e}"
            Log.error(errorMessage)
            self.connectionStatusChanged.emit(errorMessage)

    async def stop(self):
        """Stop the connection manager and close the client."""
        Log.info("Stopping Soulseek")
        self._stopEvent.set()
        await self._disconnectClient()

    async def _disconnectClient(self):
        """Gracefully disconnect the Soulseek client."""
        if self._client:
            Log.info("Stopping Soulseek client.")
            await self._client.stop()
            Log.info("Soulseek client stopped.")

    async def enqueueDownload(self, username: str, filename: str):
        await self._client.transfers.download(username, filename)

    async def waitForDownloads(self) -> bool:
        cancelled_users: set[str] = set()

        start_time = asyncio.get_event_loop().time()
        # loop for 1 minute
        while asyncio.get_event_loop().time() - start_time < 60:
            print(asyncio.get_event_loop().time())
            await asyncio.sleep(0.5)
            continue

            all_transfers = self._client.transfers.transfers

            # transfers_by_user: dict[str, list[Transfer]] = {}
            # for transfer in all_transfers:
            #     transfers_by_user.setdefault(transfer.username, []).append(transfer)
            #
            # for user, transfers in transfers_by_user.items():
            #     # Skip users that have already been cancelled
            #     if user in cancelled_users:
            #         continue
            #
            #     # If all transfers are complete, cancel all other transfers and return
            #     if all(transfer.complete_time for transfer in transfers):
            #         Log.info(f"finished downloading from {user}, cancelling all other transfers")
            #         for transfer in all_transfers:
            #             if transfer.username != user:
            #                 transfer.cancel_tasks()
            #         return True
            #     # If any transfer failed, cancel all transfers from that user
            #     if any(transfer.fail_reason for transfer in transfers):
            #         Log.info(f"failed to download from {user}, cancelling their transfers")
            #         for transfer in transfers:
            #             transfer.cancel_tasks()
            #         cancelled_users.add(user)
            #         continue
            #
            # # If all transfers are in a failed state, return False
            # if all(transfer.fail_reason for transfer in all_transfers):
            #     return False

            # Log transfer status
            status_counts = {}
            for transfer in all_transfers:
                state = transfer.state.__class__.__name__
                status_counts.setdefault(state, 0)
                status_counts[state] += 1
            for state, count in status_counts.items():
                Log.info(f"{count} transfers in state {state}")
            Log.info("======================================================")
        Log.info("timed out waiting for downloads")

    # async def downloadFile(self, username: str, file: str) -> Path | None:
    #     download = await self._client.transfers.download(
    #         username=username,
    #         filename=file
    #     )
    #     lastState = None
    #     queuedAt = None
    #     while True:
    #         await asyncio.sleep(0.1)
    #         if self._stopEvent.is_set():
    #             Log.info("Stop event detected, aborting download")
    #             await self._client.transfers.abort(download)
    #             return None
    #         state = download.state.__class__.__name__
    #         if state != lastState:
    #             lastState = state
    #             Log.info(f"Download state changed to: {state}")
    #             if state == "QueuedState":
    #                 queuedAt = asyncio.get_event_loop().time()
    #                 Log.info(f"Download queued at {queuedAt}. Timeout at {queuedAt + self.QUEUE_TIMEOUT}")
    #                 continue
    #             elif state == "CompleteState":
    #                 Log.info(f"Download completed: {download.local_path}")
    #                 return Path(download.local_path)
    #         else:
    #             Log.info("Current state name is the same as last state name")
    #             if state == "QueuedState":
    #                 queueDuration = asyncio.get_event_loop().time() - queuedAt
    #                 Log.info(f"Download is still queued. Timeout in {self.QUEUE_TIMEOUT - queueDuration:.1f}s")
    #                 if queueDuration > self.QUEUE_TIMEOUT:
    #                     Log.warning(f"Download queued too long ({queueDuration:.1f}s), aborting")
    #                     await self._client.transfers.abort(download)
    #                     return None
    #                 else:
    #                     Log.info(f"Download will be aborted in {self.QUEUE_TIMEOUT - queueDuration:.1f}s")



    # async def downloadFile(self, username: str, file: str) -> Path | None:
    #     try:
    #         Log.info(f"Initiating download from {username}: {file}")
    #
    #         download = await self._client.transfers.download(
    #             username=username,
    #             filename=file
    #         )
    #
    #         last_progress = -1
    #         last_state = None
    #         start_time = asyncio.get_event_loop().time()
    #         queued_start_time: float | None = None
    #
    #         while True:
    #             await asyncio.sleep(0.1)
    #             Log.info(f"Download state: {download.state.__class__.__name__}")
    #             if download.state.__class__.__name__ == "CompleteState":
    #                 Log.info(f"Download completed: {download.local_path}")
    #                 return Path(download.local_path)
    #
    #             #
    #             # if self._stopEvent.is_set():
    #             #     Log.info("Stop event detected, aborting download")
    #             #     await self._client.transfers.abort(download)
    #             #     return None
    #             #
    #             # Log.info("Stop event is not set")
    #             #
    #             # current_state_name = download.state.__class__.__name__
    #             #
    #             # Log.info(f"Current state name: {current_state_name}")
    #             #
    #             # # Log state changes
    #             # if current_state_name != last_state:
    #             #     Log.info(f"Download state changed to: {current_state_name}")
    #             #     last_state = current_state_name
    #             #
    #             #     # Handle state transitions
    #             #     if "QueuedState" in current_state_name:
    #             #         queued_start_time = asyncio.get_event_loop().time()
    #             #         Log.info(f"Download queued at {queued_start_time}. Timeout at {queued_start_time + self.QUEUE_TIMEOUT}")
    #             #     elif "CompleteState" in current_state_name:
    #             #         Log.info(f"Download completed: {download.local_path}")
    #             #         return Path(download.local_path)
    #             #     elif any(state in current_state_name for state in ["FailedState", "AbortedState"]):
    #             #         Log.warning(f"Download failed or aborted: {current_state_name}")
    #             #         return None
    #             #     elif any(state in current_state_name for state in ["InitializingState", "DownloadingState"]):
    #             #         queued_start_time = None
    #             # else:
    #             #     Log.info("Current state name is the same as last state name")
    #             #
    #             # # Check queue timeout
    #             # if "QueuedState" in current_state_name:
    #             #     queue_duration = asyncio.get_event_loop().time() - queued_start_time
    #             #     Log.info(f"Download is queued. Timeout in {self.QUEUE_TIMEOUT - queue_duration:.1f}s")
    #             #     if queue_duration > self.QUEUE_TIMEOUT:
    #             #         Log.warning(f"Download queued too long ({queue_duration:.1f}s), aborting")
    #             #         try:
    #             #             await self._client.transfers.abort(download)
    #             #         except Exception as e:
    #             #             Log.error(f"Error aborting queued download: {str(e)}")
    #             #         return None
    #             #
    #             # # Monitor download progress
    #             # if download.filesize and "DownloadingState" in current_state_name:
    #             #     progress = int((download.bytes_transfered / download.filesize) * 100)
    #             #     if progress != last_progress:
    #             #         Log.info(f"Download progress: {progress}%")
    #             #         last_progress = progress
    #             #
    #             # # Check overall timeout
    #             # elapsed_time = asyncio.get_event_loop().time() - start_time
    #             # if (elapsed_time > self.DOWNLOAD_TIMEOUT and
    #             #         any(state in current_state_name for state in ["InitializingState", "DownloadingState"])):
    #             #     Log.warning(f"Download timed out after {elapsed_time:.1f}s")
    #             #     try:
    #             #         await self._client.transfers.abort(download)
    #             #     except Exception as e:
    #             #         Log.error(f"Error aborting timed out download: {str(e)}")
    #             #     return None
    #
    #
    #     except Exception as e:
    #         Log.error(f"Error downloading {file}: {str(e)}")
    #         return None

    async def searchFiles(self, searchTerm: str) -> list[SlskResponse]:
        """Initiates a search on Soulseek and emits results when complete."""
        Log.info(f"Starting search for files with term: {searchTerm}")

        responses: list[SlskResponse] = []
        searchRequest = None

        try:
            searchRequest: SearchRequest = await self._client.searches.search(searchTerm)

            await asyncio.sleep(30)

            results: list[SearchResult] = searchRequest.results

            if not results:
                Log.info("No search results found.")
                return []

            for result in results:
                if not result.shared_items:
                    continue

                newItems = []
                for item in result.shared_items:
                    newItem = SlskFile(
                        name=item.filename,
                        size=item.filesize,
                    )
                    newItems.append(newItem)

                responses.append(SlskResponse(
                    username=result.username,
                    files=newItems
                ))
        finally:
            if searchRequest:
                self._client.searches.remove_request(searchRequest)
            return responses

    @property
    def client(self) -> SoulSeekClient | None:
        return self._client
