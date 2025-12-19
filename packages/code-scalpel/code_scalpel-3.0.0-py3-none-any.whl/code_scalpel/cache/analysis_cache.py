from __future__ import annotations

import hashlib
import logging
import mmap
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Generic, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# [20251214_PERF] Threshold for memory-mapped file reading (1MB default)
MMAP_THRESHOLD_BYTES = 1 * 1024 * 1024


# [20251214_FEATURE] Cache statistics for monitoring and evidence collection.
@dataclass
class CacheStats:
    """Statistics for cache hit/miss tracking."""

    memory_hits: int = 0
    disk_hits: int = 0
    misses: int = 0
    stores: int = 0
    invalidations: int = 0

    @property
    def total_requests(self) -> int:
        return self.memory_hits + self.disk_hits + self.misses

    @property
    def hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.memory_hits + self.disk_hits) / self.total_requests

    @property
    def memory_hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.memory_hits / self.total_requests

    @property
    def disk_hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.disk_hits / self.total_requests

    def to_dict(self) -> dict:
        return {
            "memory_hits": self.memory_hits,
            "disk_hits": self.disk_hits,
            "misses": self.misses,
            "stores": self.stores,
            "invalidations": self.invalidations,
            "total_requests": self.total_requests,
            "hit_rate": round(self.hit_rate, 4),
            "memory_hit_rate": round(self.memory_hit_rate, 4),
            "disk_hit_rate": round(self.disk_hit_rate, 4),
        }

    def reset(self) -> None:
        self.memory_hits = 0
        self.disk_hits = 0
        self.misses = 0
        self.stores = 0
        self.invalidations = 0


class AnalysisCache(Generic[T]):
    """[20251214_FEATURE] Memory+disk cache for parsed artifacts.

    Caches parsed results keyed by absolute file path and file content hash.
    - Memory cache avoids repeat parsing within a process.
    - Disk cache persists across runs; corruption triggers re-parse and rewrite.
    """

    def __init__(self, cache_dir: Path | str = ".code_scalpel_cache") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, T] = {}
        self._hash_cache: Dict[str, str] = {}
        # [20251214_FEATURE] Hit rate counters for observability
        self.stats = CacheStats()

    def get_or_parse(self, file_path: Path | str, parse_fn: Callable[[Path], T]) -> T:
        path = Path(file_path).resolve()
        key = str(path)
        file_hash = self._hash_file(path)

        # Memory cache check
        cached_hash = self._hash_cache.get(key)
        if cached_hash == file_hash and key in self._memory_cache:
            self.stats.memory_hits += 1  # [20251214_FEATURE] Track memory hit
            return self._memory_cache[key]

        # Disk cache check
        cache_path = self._cache_path_for(path)
        if cache_path.exists():
            try:
                with cache_path.open("rb") as f:
                    payload = pickle.load(f)
                if payload.get("hash") == file_hash:
                    value: T = payload["value"]
                    self._memory_cache[key] = value
                    self._hash_cache[key] = file_hash
                    self.stats.disk_hits += 1  # [20251214_FEATURE] Track disk hit
                    return value
            except Exception as exc:  # pragma: no cover - logged and falls through
                logger.warning("Cache read failed for %s: %s", cache_path, exc)

        # Parse fresh
        self.stats.misses += 1  # [20251214_FEATURE] Track miss
        value = parse_fn(path)
        self._memory_cache[key] = value
        self._hash_cache[key] = file_hash
        payload = {"hash": file_hash, "value": value}
        try:
            with cache_path.open("wb") as f:
                pickle.dump(payload, f)
        except Exception as exc:  # pragma: no cover - log but keep value
            logger.warning("Cache write failed for %s: %s", cache_path, exc)
        return value

    # [20251214_FEATURE] Peek cache without parsing; returns None on miss or corruption.
    def get_cached(self, file_path: Path | str) -> Optional[T]:
        path = Path(file_path).resolve()
        key = str(path)
        file_hash = self._hash_file(path)

        cached_hash = self._hash_cache.get(key)
        if cached_hash == file_hash and key in self._memory_cache:
            self.stats.memory_hits += 1  # [20251214_FEATURE] Track memory hit
            return self._memory_cache[key]

        cache_path = self._cache_path_for(path)
        if cache_path.exists():
            try:
                with cache_path.open("rb") as f:
                    payload = pickle.load(f)
                if payload.get("hash") == file_hash:
                    value: T = payload["value"]
                    self._memory_cache[key] = value
                    self._hash_cache[key] = file_hash
                    self.stats.disk_hits += 1  # [20251214_FEATURE] Track disk hit
                    return value
            except Exception as exc:  # pragma: no cover - logged and ignored
                logger.warning("Cache read failed for %s: %s", cache_path, exc)
        self.stats.misses += 1  # [20251214_FEATURE] Track miss
        return None

    # [20251214_FEATURE] Store a value directly (used after external parsing).
    def store(self, file_path: Path | str, value: T) -> None:
        path = Path(file_path).resolve()
        key = str(path)
        file_hash = self._hash_file(path)
        self._memory_cache[key] = value
        self._hash_cache[key] = file_hash
        self.stats.stores += 1  # [20251214_FEATURE] Track store
        payload = {"hash": file_hash, "value": value}
        cache_path = self._cache_path_for(path)
        try:
            with cache_path.open("wb") as f:
                pickle.dump(payload, f)
        except Exception as exc:  # pragma: no cover - log but keep memory entry
            logger.warning("Cache write failed for %s: %s", cache_path, exc)

    def invalidate(self, file_path: Path | str) -> None:
        path = Path(file_path).resolve()
        key = str(path)
        self._memory_cache.pop(key, None)
        self._hash_cache.pop(key, None)
        self.stats.invalidations += 1  # [20251214_FEATURE] Track invalidation
        cache_path = self._cache_path_for(path)
        cache_path.unlink(missing_ok=True)

    def _hash_file(self, path: Path) -> str:
        """Hash file contents, using memory-mapped I/O for large files."""
        file_size = path.stat().st_size
        if file_size > MMAP_THRESHOLD_BYTES:
            # [20251214_PERF] Memory-mapped reading for large files
            return self._hash_file_mmap(path)
        data = path.read_bytes()
        return hashlib.sha256(data).hexdigest()

    def _hash_file_mmap(self, path: Path) -> str:
        """[20251214_PERF] Hash large file using memory-mapped I/O."""
        hasher = hashlib.sha256()
        with path.open("rb") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                # Read in chunks to avoid memory pressure on very large files
                chunk_size = 64 * 1024  # 64KB chunks
                for i in range(0, len(mm), chunk_size):
                    hasher.update(mm[i : i + chunk_size])
        return hasher.hexdigest()

    def _cache_path_for(self, path: Path) -> Path:
        # Combine path + content hash seed to avoid collisions by filename alone
        seed = hashlib.sha256(str(path).encode("utf-8")).hexdigest()
        return self.cache_dir / f"{seed}.pkl"
