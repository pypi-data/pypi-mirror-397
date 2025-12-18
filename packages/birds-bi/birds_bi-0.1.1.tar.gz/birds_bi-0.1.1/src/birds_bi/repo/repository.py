from pathlib import Path
from typing import Literal, get_args

from .component import Component, Category

_CATEGORY_VALUES = set(get_args(Category))


class Repository:
    def __init__(self, path: str | Path) -> None:
        self.path: Path = Path(str(path).strip()).expanduser().resolve(strict=False)
        self.content_path: Path = self.path / "content"
        self.tabular_path: Path = self.path / "tabular"

    def _get_directories(self, path: Path) -> list[Path]:
        if not path.is_dir():
            return []
        return [p for p in path.iterdir() if p.is_dir()]

    @property
    def components(self) -> list[Component]:
        return [
            Component(
                repo=self, category=category_dir.name, component=component_dir.name
            )
            for category_dir in sorted(
                self._get_directories(self.content_path), key=lambda p: p.name
            )
            if category_dir.name in _CATEGORY_VALUES
            for component_dir in sorted(
                self._get_directories(category_dir), key=lambda p: p.name
            )
        ]

    def get_components_from_category(
        self, category: Literal[Category]
    ) -> list[Component]:
        category_path = self.content_path / category
        if not category_path.is_dir():
            raise ValueError(f"Category does not exist: {category}")

        return [
            Component(repo=self, category=category, component=component_dir.name)
            for component_dir in self._get_directories(category_path)
        ]
