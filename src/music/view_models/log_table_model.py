from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex

from src.music.core.log import Log
from src.music.core.models.log_entry import LogEntry


class LogTableModel(QAbstractTableModel):
    def __init__(self, log_entries=None):
        super().__init__()
        self.log_entries = log_entries or []
        self.headers = ["Timestamp", "Source", "Level", "Message"]

    def rowCount(self, parent=None):
        return len(self.log_entries)

    def columnCount(self, parent=None):
        return 4

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        try:
            if role == Qt.ItemDataRole.DisplayRole:
                entry = self.log_entries[index.row()]
                if index.column() == 0:
                    return entry.timestamp
                elif index.column() == 1:
                    return entry.source
                elif index.column() == 2:
                    return entry.level
                elif index.column() == 3:
                    return entry.message
            return None
        except Exception as e:
            print(f"Error getting log entry data: {e}")
            return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

    def appendLogEntry(self, entry):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.log_entries.append(entry)
        self.endInsertRows()
