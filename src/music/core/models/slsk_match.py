from dataclasses import dataclass, field

from src.music.core.models.slsk_file import SlskFile


@dataclass
class SlskMatch:
    username: str
    files: dict[str, SlskFile] = field(default_factory=dict)
