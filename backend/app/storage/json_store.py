from __future__ import annotations

import json
import os
from pathlib import Path
from threading import RLock
from typing import Any, Callable


APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("THISPOT_DATA_DIR", APP_DIR / "data"))
_LOCKS: dict[Path, RLock] = {}


def data_path(filename: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / filename


class JsonStore:
    def __init__(self, filename: str, default: dict[str, Any]) -> None:
        self.path = data_path(filename)
        self.default = default
        self.lock = _LOCKS.setdefault(self.path, RLock())

    def read(self) -> dict[str, Any]:
        with self.lock:
            if not self.path.exists():
                return self._copy_default()
            try:
                payload = json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return self._copy_default()
            return payload if isinstance(payload, dict) else self._copy_default()

    def write(self, payload: dict[str, Any]) -> None:
        with self.lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
            tmp_path.write_text(
                json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            os.replace(tmp_path, self.path)

    def update(self, mutator: Callable[[dict[str, Any]], Any]) -> Any:
        with self.lock:
            payload = self.read()
            result = mutator(payload)
            self.write(payload)
            return result

    def _copy_default(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.default))
