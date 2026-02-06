"""Caching system for log analysis results."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)


class AnalysisCache:
    """Cache for log analysis results."""

    def __init__(
        self,
        cache_dir: Path | str = ".cache",
        ttl_hours: int = 24,
    ) -> None:
        """Initialize analysis cache.

        Args:
            cache_dir: Directory to store cache files.
            ttl_hours: Time-to-live in hours for cache entries.
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _get_cache_key(self, log_content: str) -> str:
        """Generate cache key from log content.

        Args:
            log_content: The log content to hash.

        Returns:
            Cache key (hash).
        """
        # Normalize log content (remove extra whitespace)
        normalized = "\n".join(line.strip() for line in log_content.strip().split("\n"))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a key.

        Args:
            cache_key: Cache key.

        Returns:
            Path to cache file.
        """
        return self.cache_dir / f"{cache_key}.json"

    def get(self, log_content: str) -> str | None:
        """Get cached analysis result.

        Args:
            log_content: The log content to look up.

        Returns:
            Cached analysis result or None if not found/expired.
        """
        cache_key = self._get_cache_key(log_content)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with cache_path.open() as f:
                cache_data = json.load(f)

            # Check if expired
            cached_time = datetime.fromisoformat(cache_data["timestamp"])
            if datetime.now() - cached_time > self.ttl:
                logger.debug(f"Cache entry expired: {cache_key}")
                cache_path.unlink()  # Delete expired cache
                return None

            logger.info(f"Cache hit: {cache_key[:8]}...")
            return cache_data["analysis"]

        except Exception as e:
            logger.warning(f"Failed to read cache: {e}")
            return None

    def set(self, log_content: str, analysis: str) -> None:
        """Store analysis result in cache.

        Args:
            log_content: The log content.
            analysis: The analysis result to cache.
        """
        cache_key = self._get_cache_key(log_content)
        cache_path = self._get_cache_path(cache_key)

        try:
            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis,
                "cache_key": cache_key,
            }

            with cache_path.open("w") as f:
                json.dump(cache_data, f, indent=2)

            logger.info(f"Cached analysis: {cache_key[:8]}...")

        except Exception as e:
            logger.warning(f"Failed to write cache: {e}")

    def clear(self, older_than_hours: int | None = None) -> int:
        """Clear cache entries.

        Args:
            older_than_hours: Only clear entries older than this. If None, clear all.

        Returns:
            Number of cache files deleted.
        """
        deleted = 0
        cutoff = datetime.now() - timedelta(hours=older_than_hours) if older_than_hours else None

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                if cutoff:
                    with cache_file.open() as f:
                        cache_data = json.load(f)
                        cached_time = datetime.fromisoformat(cache_data["timestamp"])
                        if cached_time > cutoff:
                            continue

                cache_file.unlink()
                deleted += 1

            except Exception as e:
                logger.warning(f"Failed to delete cache file {cache_file}: {e}")

        logger.info(f"Cleared {deleted} cache entries")
        return deleted

    def get_stats(self) -> dict[str, int | float]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics.
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            "total_entries": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
        }


# Global cache instance
_cache: AnalysisCache | None = None


def get_cache() -> AnalysisCache:
    """Get or create global cache instance.

    Returns:
        AnalysisCache instance.
    """
    global _cache
    if _cache is None:
        _cache = AnalysisCache()
    return _cache
