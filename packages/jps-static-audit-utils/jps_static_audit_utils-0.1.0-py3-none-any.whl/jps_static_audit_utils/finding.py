from dataclasses import dataclass, asdict


@dataclass
class Finding:
    file: str
    line: int
    path: str
    path_type: str
    context: str

