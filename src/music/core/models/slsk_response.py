from dataclasses import dataclass, field

from src.music.core.models.slsk_file import SlskFile


@dataclass
class SlskResponse:
    username: str
    files: list[SlskFile] = field(default_factory=list)

