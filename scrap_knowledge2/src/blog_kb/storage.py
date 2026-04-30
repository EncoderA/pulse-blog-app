from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat()


def _base_data_dir() -> Path:
    root = Path(__file__).resolve().parents[2]
    path = root / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def processed_json_path(dt: datetime | None = None) -> Path:
    current = dt or utc_now()
    path = _base_data_dir() / "processed" / f"{current:%Y}" / f"{current:%m}" / f"{current:%d}"
    path.mkdir(parents=True, exist_ok=True)
    return path / "cleaned_articles.json"


def write_json_file(path: Path, payload: list[dict] | dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
