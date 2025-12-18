from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class EEGWarning:
    type: str                 # e.g. CHANNEL_DROP, FS_SANITY
    severity: str             # INFO / WARN / ERROR
    message: str
    affected: Optional[List[str]] = None