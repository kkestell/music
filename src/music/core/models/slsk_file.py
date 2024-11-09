from dataclasses import dataclass


@dataclass(frozen=True)
class SlskFile:
    name: str
    size: int
