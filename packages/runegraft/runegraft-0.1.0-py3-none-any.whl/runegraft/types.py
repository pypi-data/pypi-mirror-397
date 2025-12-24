from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from urllib.parse import urlparse
import uuid
import json
from datetime import datetime, date

class TypeErrorValue(ValueError):
    pass

Converter = Callable[[str], Any]

def _bool(s: str) -> bool:
    v = s.strip().lower()
    if v in {"1","true","t","yes","y","on"}: return True
    if v in {"0","false","f","no","n","off"}: return False
    raise TypeErrorValue(f"Invalid bool: {s!r}")

def _path(s: str) -> Path:
    return Path(s).expanduser()

def _url(s: str) -> str:
    p = urlparse(s)
    if not p.scheme:
        raise TypeErrorValue("URL must include a scheme like https://")
    # allow file:// too
    if p.scheme != "file" and not p.netloc:
        raise TypeErrorValue("URL must include a host")
    return s

def _json(s: str) -> Any:
    try:
        return json.loads(s)
    except Exception as e:
        raise TypeErrorValue(f"Invalid JSON: {e}") from e

def _uuid(s: str) -> uuid.UUID:
    try:
        return uuid.UUID(s)
    except Exception as e:
        raise TypeErrorValue(f"Invalid UUID: {e}") from e

def _date(s: str) -> date:
    try:
        return date.fromisoformat(s)
    except Exception as e:
        raise TypeErrorValue(f"Invalid date (YYYY-MM-DD): {e}") from e

def _datetime(s: str) -> datetime:
    try:
        return datetime.fromisoformat(s)
    except Exception as e:
        raise TypeErrorValue(f"Invalid datetime (ISO): {e}") from e


BUILTIN_TYPES: Dict[str, Converter] = {
    "str": str,
    "string": str,
    "text": str,
    "int": int,
    "float": float,
    "bool": _bool,
    "path": _path,
    "url": _url,
    "json": _json,
    "uuid": _uuid,
    "date": _date,
    "datetime": _datetime,
}

def type_name_for_py(t: type) -> str:
    # best-effort mapping for help output
    if t is str: return "str"
    if t is int: return "int"
    if t is float: return "float"
    if t is bool: return "bool"
    try:
        from pathlib import Path as _Path
        if t is _Path: return "path"
    except Exception:
        pass
    return getattr(t, "__name__", "value")
