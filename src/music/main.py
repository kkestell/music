from __future__ import annotations
import signal
import sys
from typing import Any

import asyncio
from PySide6.QtWidgets import QApplication, QStyleFactory
from qasync import QEventLoop
from src.music.core.library import Library
from src.music.core.wish_list import WishList
from src.music.windows.main_window import MainWindow


def signalHandler(signum: int, frame: Any) -> None:
    print(f"Interrupt signal ({signum}) received.")
    sys.exit(signum)


def main() -> int:
    signal.signal(signal.SIGSEGV, signalHandler)

    app = QApplication(sys.argv)
    app.setApplicationName("Music")
    app.setStyle(QStyleFactory.create("Fusion"))

    # Set up the asyncio event loop with qasync
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    library = Library()
    wishList = WishList()
    window = MainWindow(library, wishList)
    window.show()

    # Run the application within the qasync event loop
    with loop:
        return loop.run_forever()


if __name__ == "__main__":
    sys.exit(main())
