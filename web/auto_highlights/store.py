"""Small persistence contract for Auto Highlights.

The JSON implementation is suitable for local/dev. Production can swap this
contract for Postgres/object metadata without changing Creator Hub code.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Protocol
from .live_folder import LiveFolder

class LiveFolderStore(Protocol):
    def save(self, folder: LiveFolder) -> None: ...
    def list_for_account(self, provider: str, account_id: str) -> list[dict]: ...

class JsonLiveFolderStore:
    def __init__(self, root: str | Path):
        self.root=Path(root)

    def _path(self, provider: str, account_id: str) -> Path:
        return self.root/provider/f"{account_id}.json"

    def _load(self, provider: str, account_id: str) -> list[dict]:
        path=self._path(provider,account_id)
        if not path.is_file(): return []
        try:
            data=json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data,list) else []
        except (OSError,json.JSONDecodeError):
            return []

    def save(self, folder: LiveFolder) -> None:
        path=self._path(folder.provider,folder.account_id)
        path.parent.mkdir(parents=True,exist_ok=True)
        rows=[x for x in self._load(folder.provider,folder.account_id) if x.get("id")!=folder.id]
        rows.insert(0,folder.as_dict())
        tmp=path.with_suffix(".tmp")
        tmp.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
        tmp.replace(path)

    def list_for_account(self, provider: str, account_id: str) -> list[dict]:
        return self._load(provider,account_id)
