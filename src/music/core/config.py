from __future__ import annotations
from PySide6.QtCore import QObject, QStandardPaths, QFileInfo
import json
import sys
from pathlib import Path

from src.music.core.log import Log


class Config(QObject):
    _instance: Config | None = None

    @classmethod
    def instance(cls) -> Config:
        if cls._instance is None:
            cls._instance = Config()
        return cls._instance

    def __init__(self, parent: QObject | None = None) -> None:
        if Config._instance is not None:
            raise RuntimeError("Config instance already exists - use Config.instance() instead")
        super().__init__(parent)
        self._config: dict = {}
        self.load()

    def load(self) -> None:
        path = self.configPath()

        if not path.exists():
            self.createDefaultConfig()
            return

        try:
            with open(path, 'r') as file:
                self._config = json.load(file)
        except json.JSONDecodeError:
            Log.error(f"Failed to parse config file: {path}")
        except IOError:
            Log.error(f"Couldn't open config file: {path}")

    def createDefaultConfig(self) -> None:
        self._config = {
            "libraryPath": self.getDefaultLibraryPath(),
            "ffmpegPath": self.getDefaultFfmpegPath(),
            "ffplayPath": self.getDefaultFfplayPath(),
            "ffprobePath": self.getDefaultFfprobePath(),
            "soulseekUsername": "",
            "soulseekPassword": ""
        }

        self.save()
        Log.info(f"Created default config at {self.configPath()}")

    def configPath(self) -> Path:
        if sys.platform == 'win32':
            base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
        elif sys.platform == 'darwin':
            base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
        else:
            base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.ConfigLocation)
        return Path(base) / "config.json"

    def getDefaultLibraryPath(self) -> str:
        return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.MusicLocation)

    def getDefaultFfmpegPath(self) -> str:
        if sys.platform == 'win32':
            return r"C:/Program Files/ffmpeg/bin/ffmpeg.exe"
        elif sys.platform == 'darwin':
            return "/usr/local/bin/ffmpeg"
        return "/usr/bin/ffmpeg"

    def getDefaultFfplayPath(self) -> str:
        if sys.platform == 'win32':
            return r"C:/Program Files/ffmpeg/bin/ffplay.exe"
        elif sys.platform == 'darwin':
            return "/usr/local/bin/ffplay"
        return "/usr/bin/ffplay"

    def getDefaultFfprobePath(self) -> str:
        if sys.platform == 'win32':
            return r"C:/Program Files/ffmpeg/bin/ffprobe.exe"
        elif sys.platform == 'darwin':
            return "/usr/local/bin/ffprobe"
        return "/usr/bin/ffprobe"

    @property
    def libraryPath(self) -> str:
        return self._config.get("libraryPath", "")

    @libraryPath.setter
    def libraryPath(self, path: str) -> None:
        self._config["libraryPath"] = path

    @property
    def ffmpegPath(self) -> str:
        return self._config.get("ffmpegPath", "")

    @ffmpegPath.setter
    def ffmpegPath(self, path: str) -> None:
        self._config["ffmpegPath"] = path

    @property
    def ffplayPath(self) -> str:
        return self._config.get("ffplayPath", "")

    @ffplayPath.setter
    def ffplayPath(self, path: str) -> None:
        self._config["ffplayPath"] = path

    @property
    def ffprobePath(self) -> str:
        return self._config.get("ffprobePath", "")

    @ffprobePath.setter
    def ffprobePath(self, path: str) -> None:
        self._config["ffprobePath"] = path

    @property
    def soulseekUsername(self) -> str:
        return self._config.get("soulseekUsername", "")

    @soulseekUsername.setter
    def soulseekUsername(self, username: str) -> None:
        self._config["soulseekUsername"] = username

    @property
    def soulseekPassword(self) -> str:
        return self._config.get("soulseekPassword", "")

    @soulseekPassword.setter
    def soulseekPassword(self, password: str) -> None:
        self._config["soulseekPassword"] = password

    def save(self) -> None:
        path = self.configPath()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as file:
                json.dump(self._config, file, indent=4)
        except IOError:
            Log.error(f"Couldn't open config file for writing: {path}")
