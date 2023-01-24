import pathlib
from typing import Dict


class KradfileParser():
    def __init__(self, *paths: pathlib.Path):
        self.paths = paths
        self.kanji_dict: Dict[str, list[str]] = {}

    def parse(self):
        self.kanji_dict.clear()
        for path in self.paths:
            self._parse_kradfile(path)

    def _parse_kradfile(self, path: pathlib.Path):
        if not path.exists():
            raise Exception(f"File '{path}' does not exist!")

        with path.open(mode="r") as f:
            for line in f:
                if not line.startswith("#"):
                    split = line.split(":")
                    kanji = split[0].strip()
                    radicals = split[1].strip().split(" ")
                    self.kanji_dict[kanji] = radicals
