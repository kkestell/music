from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QSlider
)
from PySide6.QtCore import Qt

class PlayerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._previousButton: QPushButton
        self._playButton: QPushButton
        self._nextButton: QPushButton
        self._trackTitleLabel: QLabel
        self._artistNameLabel: QLabel
        self._progressSlider: QSlider
        self.setupUi()

    def setupUi(self) -> None:
        mainLayout = QHBoxLayout(self)

        # Left
        buttonWidget = QWidget(self)
        buttonWidget.setFixedWidth(250)
        buttonLayout = QHBoxLayout(buttonWidget)
        self._previousButton = QPushButton("Previous", buttonWidget)
        self._playButton = QPushButton("Play", buttonWidget)
        self._nextButton = QPushButton("Next", buttonWidget)
        buttonLayout.addWidget(self._previousButton)
        buttonLayout.addWidget(self._playButton)
        buttonLayout.addWidget(self._nextButton)
        mainLayout.addWidget(buttonWidget)

        # Middle
        infoWidget = QWidget(self)
        infoLayout = QVBoxLayout(infoWidget)
        self._trackTitleLabel = QLabel("Track Title", infoWidget)
        self._artistNameLabel = QLabel("Artist Name", infoWidget)
        self._progressSlider = QSlider(Qt.Orientation.Horizontal, infoWidget)

        self._trackTitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._artistNameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titleFont = self._trackTitleLabel.font()
        titleFont.setBold(True)
        self._trackTitleLabel.setFont(titleFont)

        infoLayout.addWidget(self._trackTitleLabel)
        infoLayout.addWidget(self._artistNameLabel)
        infoLayout.addWidget(self._progressSlider)
        mainLayout.addWidget(infoWidget, 1)

        # Right
        emptyWidget = QWidget(self)
        emptyWidget.setFixedWidth(250)
        mainLayout.addWidget(emptyWidget)

        self.setLayout(mainLayout)
