from dataclasses import dataclass


@dataclass
class ReleaseGroupResult:
    mbid: str
    artist: str
    title: str
    release_date: str
    type: str
    disambiguation: str
