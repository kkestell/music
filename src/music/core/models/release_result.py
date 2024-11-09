from __future__ import annotations

import json
from dataclasses import dataclass, asdict


@dataclass
class ReleaseResult:
    mbid: str
    artist: str
    title: str
    release_date: str
    country: str
    format: str
    tracks: list[str]

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(json_str: str) -> ReleaseResult:
        data = json.loads(json_str)
        return ReleaseResult(**data)
