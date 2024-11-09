import asyncio
from pathlib import Path
from datetime import datetime
import os
import re
from PySide6.QtWidgets import (
    QMainWindow, QTableView, QHeaderView, QCheckBox, QLabel, QWidget,
    QVBoxLayout, QHBoxLayout
)
from src.music.core.fonts import getMonospacedFont
from src.music.core.log import Log
from src.music.view_models.log_table_model import LogTableModel
from src.music.core.models.log_entry import LogEntry


class LogViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Log Viewer")
        self.resize(1200, 600)

        self.logFilePath = Log.getLogFilePath()

        # Create the table view widget for displaying log content
        self.tableView = QTableView(self)
        self.logModel = LogTableModel()
        self.tableView.setModel(self.logModel)

        # Set preferred monospaced fonts
        font = getMonospacedFont()
        self.tableView.setFont(font)

        # Set up columns
        header = self.tableView.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)

        # Create the 'Follow' checkbox
        self.followCheckBox = QCheckBox("Follow", self)
        self.followCheckBox.setChecked(True)  # Default to checked

        # Create a label to display the log file path
        self.pathLabel = QLabel(self)
        self.pathLabel.setText(f"Log file: {self.logFilePath}")

        # Set up the central widget and layout
        centralWidget = QWidget()
        mainLayout = QVBoxLayout(centralWidget)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # Add the table view to the layout
        mainLayout.addWidget(self.tableView)

        # Add the checkbox and path label to the layout
        bottomLayout = QHBoxLayout()
        bottomLayout.setContentsMargins(5, 5, 5, 5)
        bottomLayout.addWidget(self.pathLabel)
        bottomLayout.addStretch()
        bottomLayout.addWidget(self.followCheckBox)

        mainLayout.addLayout(bottomLayout)

        self.setCentralWidget(centralWidget)

        # Start async log loader
        asyncio.create_task(self.load_log_content_async())

        # Connect to the log message signal for real-time updates
        self.logSignalEmitter = Log.getLogSignalEmitter()
        self.logSignalEmitter.messageLogged.connect(self.appendLogMessage)

    async def load_log_content_async(self):
        """Asynchronously load the last 1000 lines from the log file."""
        lines = await asyncio.to_thread(self.tail, self.logFilePath, 1000)
        log_entries = [self.parse_log_line(line) for line in lines]
        self.update_log_model(log_entries)

    def update_log_model(self, log_entries: list[LogEntry]):
        """Update the model with the loaded log entries."""
        self.logModel = LogTableModel(log_entries)
        self.tableView.setModel(self.logModel)
        self.tableView.resizeRowsToContents()

        if self.followCheckBox.isChecked():
            self.tableView.scrollToBottom()

    def appendLogMessage(self, logEntry: dict):
        """Add a new log entry in real-time."""
        self.logModel.appendLogEntry(LogEntry(
            logEntry["timestamp"], logEntry["source"],
            logEntry["level"], logEntry["message"]
        ))
        self.tableView.resizeRowsToContents()

        if self.followCheckBox.isChecked():
            self.tableView.scrollToBottom()

    def closeEvent(self, event):
        self.logSignalEmitter.messageLogged.disconnect(self.appendLogMessage)
        super().closeEvent(event)

    @staticmethod
    def tail(filename: Path, n: int) -> list[str]:
        """Read the last n lines from a file efficiently."""
        with open(filename, "rb") as f:
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            block_size = 1024
            blocks = []
            linesFound = 0
            position = file_size

            while position > 0 and linesFound < n:
                if position - block_size > 0:
                    position -= block_size
                else:
                    block_size = position
                    position = 0

                f.seek(position)
                block = f.read(block_size)
                blocks.insert(0, block)
                linesFound += block.count(b"\n")

            content = b"".join(blocks)
            lines = content.splitlines()[-n:]
            return [line.decode("utf-8", errors="replace") + "\n" for line in lines]

    @staticmethod
    def parse_log_line(line: str) -> LogEntry:
        """Parse a single line of log text into a LogEntry."""
        pattern = r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}) - (\w+) - (\w+) - (.+)"
        match = re.match(pattern, line)
        if match:
            timestamp, source, level, message = match.groups()
            return LogEntry(timestamp, source, level, message)
        return LogEntry(str(datetime.now()), "MUSIC", "ERROR", f"Failed to parse log line: {line}")
