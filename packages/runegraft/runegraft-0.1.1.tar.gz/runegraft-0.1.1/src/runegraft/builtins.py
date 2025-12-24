from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Optional, List

@dataclass
class AliasStore:
    mapping: Dict[str, str]

def expand_alias(aliases: AliasStore, line: str) -> str:
    # simple: if first token matches alias, replace it
    stripped = line.strip()
    if not stripped:
        return line
    head = stripped.split(None, 1)[0]
    rest = stripped[len(head):].lstrip()
    if head in aliases.mapping:
        repl = aliases.mapping[head]
        return (repl + (" " + rest if rest else "")).strip()
    return line

def clear_screen() -> None:
    # best-effort portable clear
    os.system("cls" if os.name == "nt" else "clear")
