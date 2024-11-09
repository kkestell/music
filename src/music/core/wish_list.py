from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path

import aiosqlite
from PySide6.QtCore import QStandardPaths, QTimer, Signal, QObject

from src.music.core.log import Log
from src.music.core.models.release_result import ReleaseResult
from src.music.core.models.wish_list_item import WishListItem


class WishList(QObject):
    itemAdded = Signal()

    def __init__(self) -> None:
        super().__init__()
        dataLocation = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
        self.dbPath = Path(dataLocation) / "wish_list.db"
        self.dbPath.parent.mkdir(parents=True, exist_ok=True)

        # Initialize the database after the event loop starts
        QTimer.singleShot(0, lambda: asyncio.create_task(self._initializeDatabase()))

    async def _initializeDatabase(self) -> None:
        async with aiosqlite.connect(self.dbPath) as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY,
                    created_at TIMESTAMP,
                    release TEXT,
                    status TEXT DEFAULT 'pending'
                )
            """)
            await conn.commit()
            Log.verbose(f"Database initialized at: {self.dbPath}")

    async def updateItemStatus(self, id: str, status: str) -> None:
        async with aiosqlite.connect(self.dbPath) as conn:
            await conn.execute("UPDATE items SET status = ? WHERE id = ?", (status, id))
            await conn.commit()

    async def addRelease(self, release: ReleaseResult) -> None:
        created_at = datetime.now().isoformat()
        release_json = release.to_json()
        async with aiosqlite.connect(self.dbPath) as conn:
            cursor = await conn.execute("""
                INSERT INTO items (created_at, release, status) VALUES (?, ?, 'pending')
            """, (created_at, release_json))
            await conn.commit()
            Log.verbose(f"Release added successfully. ID: {cursor.lastrowid}")
            self.itemAdded.emit()

    async def isEmpty(self) -> bool:
        async with aiosqlite.connect(self.dbPath) as conn:
            cursor = await conn.execute("SELECT COUNT(*) FROM items")
            count = await cursor.fetchone()
            return count[0] == 0

    async def dequeueItem(self) -> WishListItem | None:
        async with aiosqlite.connect(self.dbPath) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("""
                SELECT id, created_at, release, status FROM items 
                WHERE status = 'pending' ORDER BY created_at LIMIT 1
            """)
            row = await cursor.fetchone()
            if row:
                release = ReleaseResult.from_json(row["release"])
                await conn.execute("DELETE FROM items WHERE id = ?", (row["id"],))
                await conn.commit()
                return WishListItem(id=row["id"], createdAt=row["created_at"], release=release)
            return None

    async def enqueueItem(self, item: WishListItem) -> None:
        async with aiosqlite.connect(self.dbPath) as conn:
            release_json = item.release.to_json()
            await conn.execute("""
                INSERT INTO items (id, created_at, release, status) VALUES (?, ?, ?, 'pending')
            """, (item.id, item.createdAt, release_json))
            await conn.commit()
            Log.verbose(f"Item enqueued successfully. ID: {item.id}")
            self.itemAdded.emit()

    async def getItem(self, id: int) -> WishListItem | None:
        async with aiosqlite.connect(self.dbPath) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("SELECT id, created_at, release, status FROM items WHERE id = ?", (id,))
            row = await cursor.fetchone()
            if row:
                release = ReleaseResult.from_json(row["release"])
                return WishListItem(id=row["id"], createdAt=row["created_at"], release=release)
            return None

    async def getAllItems(self) -> list[WishListItem]:
        async with aiosqlite.connect(self.dbPath) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("SELECT id, created_at, release, status FROM items ORDER BY created_at")
            rows = await cursor.fetchall()
            return [
                WishListItem(id=row["id"], createdAt=row["created_at"], release=ReleaseResult.from_json(row["release"]), status=row["status"])
                for row in rows
            ]

    async def removeItem(self, id: int) -> None:
        async with aiosqlite.connect(self.dbPath) as conn:
            await conn.execute("DELETE FROM items WHERE id = ?", (id,))
            await conn.commit()
