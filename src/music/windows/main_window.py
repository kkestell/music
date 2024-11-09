from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import QDir, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMenuBar, QFileDialog, QMessageBox, QTabWidget
)
from qasync import asyncClose

from src.music.core.config import Config
from src.music.core.downloader import Downloader
from src.music.core.library import Library
from src.music.core.log import Log
from src.music.core.models.track import Track
from src.music.core.wish_list import WishList
from src.music.core.slsk import Slsk
from src.music.tabs.library_tab import LibraryTab
from src.music.tabs.wish_list_tab import WishListTab
from src.music.tabs.search_tab import SearchTab
from src.music.widgets.player_widget import PlayerWidget
from src.music.windows.log_viewer_window import LogViewerWindow


class MainWindow(QMainWindow):
    def __init__(self, library: Library, queue: WishList, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Log startup
        Log.info("Starting up")

        # Verify FFmpeg tools
        if not self.verifyFfmpeg():
            sys.exit(1)

        # Set window icon
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        icon_path = os.path.join(base_dir, "assets", "icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Set up wish list
        self._wishList = queue

        # Initialize library
        self._library = library

        # Import task
        self._importTask = None

        # Log viewer window
        self._logViewerWindow = None

        # Set up main window properties
        self.setWindowTitle("Music")
        self.resize(1024, 768)

        # Set up central widget and layout
        centralWidget = QWidget(self)
        mainLayout = QVBoxLayout(centralWidget)

        # Configure player widget
        self._playerWidget = PlayerWidget(self)
        mainLayout.addWidget(self._playerWidget)

        # Configure tab widget with Library and Search tabs
        self._tabWidget = QTabWidget(centralWidget)
        self._libraryTab = LibraryTab(self._library, self._tabWidget)
        self._searchTab = SearchTab(self._wishList, self._tabWidget)
        self._wishListTab = WishListTab(self._wishList, self._tabWidget)
        self._tabWidget.addTab(self._libraryTab, self.tr("Library"))
        self._tabWidget.addTab(self._searchTab, self.tr("Search"))
        self._tabWidget.addTab(self._wishListTab, self.tr("Wish List"))
        mainLayout.addWidget(self._tabWidget)

        # Set central widget
        self.setCentralWidget(centralWidget)

        # Set up menu bar and actions
        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)
        fileMenu = menuBar.addMenu(self.tr("&File"))
        importAction = fileMenu.addAction(self.tr("&Import..."))
        importAction.triggered.connect(self.onImportActionTriggered)

        debugMenu = menuBar.addMenu("Debug")
        logViewerAction = debugMenu.addAction("View Logs")
        logViewerAction.triggered.connect(self.showLogViewer)

        # Set up status bar
        self.statusBar().showMessage("Ready")

        # Set up Soulseek connection manager
        self._soulSeek = Slsk("C:\\Users\\Kyle\\Downloads", self)
        loop = asyncio.get_event_loop()
        loop.create_task(self._soulSeek.start())

        # Downloader
        self._downloader = Downloader(self._soulSeek, self._wishList)
        loop.create_task(self._downloader.start())

        # Schedule the connection to start once the event loop is running
        # QTimer.singleShot(0, lambda: asyncio.create_task(self._soulseekConnectionManager.connectAndListen()))
        # QTimer.singleShot(1000, lambda: asyncio.create_task(self._search()))

    # async def _search(self):
    #     self._soulseekConnectionManager.searchComplete.connect(self._searchComplete)
    #     await self._soulseekConnectionManager.searchFiles("Nine Inch Nails")

    def _searchComplete(self, results):
        print(results)

    def verifyFfmpeg(self) -> bool:
        """
        Verify that the required FFmpeg tools exist.
        """
        config = Config.instance()
        missingTools = []

        tools = [
            ("ffmpeg", config.ffmpegPath),
            ("ffplay", config.ffplayPath),
            ("ffprobe", config.ffprobePath)
        ]

        for toolName, toolPath in tools:
            if not toolPath or not os.path.exists(toolPath):
                missingTools.append(toolPath)

        if missingTools:
            message = (
                f"The following FFmpeg tools were not found: {', '.join(missingTools)}\n\n"
                "Please ensure FFmpeg is installed or update your configuration file "
                "with the correct paths.\n\n"
                f"Configuration file location: {Config.configPath()}\n\n"
                "The application will now exit."
            )
            QMessageBox.critical(self, "Missing FFmpeg Tools", message)
            return False

        return True

    def updateStatusBar(self, message: str) -> None:
        """Slot to update the status bar text based on the connection status."""
        self.statusBar().showMessage(message)

    def onImportActionTriggered(self) -> None:
        dir = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Directory to Import"),
            QDir.homePath(),
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )

        if dir:
            if self._importTask is not None and not self._importTask.done():
                QMessageBox.information(
                    self,
                    self.tr("Import in Progress"),
                    self.tr("An import is already in progress. Please wait for it to complete.")
                )
                return

            # Start the async import task
            self._importTask = asyncio.create_task(self.importTracks(Path(dir)))

    async def importTracks(self, import_path: Path) -> None:
        """Asynchronously imports tracks from the given directory."""
        ffprobePath = Config.instance().ffprobePath
        if not ffprobePath:
            Log.error("ffprobe path is not set in the configuration!")
            return

        extensions = ["*.mp3", "*.flac"]
        imported_count = 0

        for extension in extensions:
            async for filePath in self.findFiles(import_path, extension):
                Log.verbose(f"Importing file: {filePath}")

                try:
                    newTrack = await asyncio.to_thread(Track.createTrackFromFile, filePath, ffprobePath)
                    if newTrack.name:
                        await asyncio.to_thread(self._library.importTrack, newTrack)
                        self.onTrackImported(newTrack)
                        imported_count += 1
                        Log.verbose(f"Imported track: {newTrack.name} by {newTrack.artist}")
                    else:
                        Log.warning(f"Failed to import track from file: {filePath}")
                except Exception as e:
                    Log.warning(f"Error importing track {filePath}: {e}")

        Log.verbose(f"Import complete. Total tracks imported: {imported_count}")
        self.onImportComplete()

    @staticmethod
    async def findFiles(directory: Path, pattern: str):
        """Asynchronously yields files matching a pattern within a directory, including subdirectories."""
        for filePath in await asyncio.to_thread(lambda: list(directory.rglob(pattern))):
            yield filePath

    def onTrackImported(self, track: Track) -> None:
        """Handler for library updates."""
        self.statusBar().showMessage(f"Imported {track.name} by {track.artist}")
        self._libraryTab.refreshModels()

    def onImportComplete(self) -> None:
        """Handler for import completion."""
        self._importTask = None
        self.statusBar().showMessage("Import complete")
        self._libraryTab.refreshModels()

    def showLogViewer(self):
        """Show the log viewer window."""
        self._logViewerWindow = LogViewerWindow()
        self._logViewerWindow.show()

    @asyncClose
    async def closeEvent(self, event: Any) -> None:
        """Handle cleanup on close."""
        # if self._importTask:
        #     self._importTask.cancel()

        if self._soulSeek:
            await self._soulSeek.stop()

        super().closeEvent(event)
