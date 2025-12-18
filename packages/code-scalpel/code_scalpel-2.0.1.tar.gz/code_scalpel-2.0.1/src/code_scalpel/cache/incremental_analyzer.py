from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Dict, Generic, Set, TypeVar

from .analysis_cache import AnalysisCache

logger = logging.getLogger(__name__)

T = TypeVar("T")


class IncrementalAnalyzer(Generic[T]):
    """[20251214_FEATURE] Dependency-aware incremental analysis."""

    def __init__(self, cache: AnalysisCache[T]) -> None:
        self.cache = cache
        self.dependency_graph: Dict[str, Set[str]] = {}

    def record_dependency(self, source: Path | str, depends_on: Path | str) -> None:
        source_key = str(Path(source).resolve())
        target_key = str(Path(depends_on).resolve())
        self.dependency_graph.setdefault(target_key, set()).add(source_key)

    def get_dependents(self, file_path: Path | str) -> Set[str]:
        return set(self.dependency_graph.get(str(Path(file_path).resolve()), set()))

    def update_file(
        self, file_path: Path | str, recompute_fn: Callable[[Path], T]
    ) -> Set[str]:
        path = Path(file_path).resolve()
        key = str(path)

        # Invalidate the changed file and recompute
        self.cache.invalidate(path)
        self.cache.get_or_parse(path, parse_fn=recompute_fn)

        affected = self.get_dependents(key)
        for dependent in affected:
            self.cache.invalidate(dependent)
        return affected
