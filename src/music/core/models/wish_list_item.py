from dataclasses import dataclass

from src.music.core.models.release_result import ReleaseResult


@dataclass
class WishListItem:
    id: str
    createdAt: str
    release: ReleaseResult
    status: str
