import json
from pathlib import Path

data_path = Path("data/alias")
if not data_path.exists():
    data_path.mkdir(parents=True)


class AliasList:
    def __init__(self, path: Path):
        self.path = path
        self.list = self._load_alias()

    def _load_alias(self) -> dict:
        if self.path.exists():
            return json.load(self.path.open("r", encoding="utf-8"))
        else:
            return {}

    def _dump_alias(self) -> bool:
        json.dump(
            self.list,
            self.path.open("w", encoding="utf-8"),
            indent=4,
            separators=(",", ": "),
            ensure_ascii=False,
        )
        return True

    def add_alias(self, id: str, name: str, command: str) -> bool:
        if id not in self.list:
            self.list[id] = {}
        self.list[id][name] = command
        return self._dump_alias()

    def del_alias(self, id: str, name: str) -> bool:
        if id not in self.list:
            return False
        self.list[id].pop(name, "")
        if not self.list[id]:
            self.list.pop(id, {})
        return self._dump_alias()

    def del_alias_all(self, id: str) -> bool:
        self.list.pop(id, {})
        return self._dump_alias()

    def get_alias(self, id: str, name: str) -> str:
        if id not in self.list:
            return ""
        if name not in self.list[id]:
            return ""
        return self.list[id][name]

    def get_alias_all(self, id: str) -> dict:
        if id not in self.list:
            return {}
        return self.list[id].copy()


aliases = AliasList(data_path / "aliases.json")