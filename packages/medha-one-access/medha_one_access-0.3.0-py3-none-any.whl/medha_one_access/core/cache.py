"""
Performance Caching Module for MedhaOne Access Control

Provides global caching functionality to improve performance across
multiple sessions and requests.

All cache parameters are configurable via LibraryConfig.
"""

import time
from typing import Any, Dict, Optional, Set, TYPE_CHECKING
from functools import wraps
from threading import RLock

if TYPE_CHECKING:
    from .config import LibraryConfig


class PerformanceCache:
    """
    High-performance LRU cache with TTL support for access control operations.

    This cache is designed to store:
    - Resolved expression results
    - User access resolutions
    - Frequently accessed database entities

    All parameters are configurable:
    - max_size: Maximum number of items to cache (default: 10000)
    - default_ttl: Default time-to-live in seconds (default: 300)
    """

    def __init__(self, max_size: int = 10000, default_ttl: int = 300):
        """
        Initialize the performance cache.

        Args:
            max_size: Maximum number of items to cache
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = RLock()
        self._hits = 0
        self._misses = 0
        self._total_requests = 0

    def get(self, key: str) -> Optional[Any]:
        """Get an item from the cache."""
        with self._lock:
            self._total_requests += 1

            if key not in self._cache:
                self._misses += 1
                return None

            item = self._cache[key]
            current_time = time.time()

            # Check if item has expired
            if current_time > item['expires_at']:
                self._remove(key)
                self._misses += 1
                return None

            # Update access time for LRU
            self._access_times[key] = current_time
            self._hits += 1
            return item['value']

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set an item in the cache."""
        with self._lock:
            if ttl is None:
                ttl = self.default_ttl

            current_time = time.time()

            # If cache is full, remove LRU item
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()

            # Store the item
            self._cache[key] = {
                'value': value,
                'created_at': current_time,
                'expires_at': current_time + ttl
            }
            self._access_times[key] = current_time

    def delete(self, key: str) -> bool:
        """Delete an item from the cache."""
        with self._lock:
            if key in self._cache:
                self._remove(key)
                return True
            return False

    def clear(self) -> None:
        """Clear all items from the cache."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self._hits = 0
            self._misses = 0
            self._total_requests = 0

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache keys matching a pattern.

        Args:
            pattern: String pattern to match against keys

        Returns:
            Number of items invalidated
        """
        with self._lock:
            keys_to_remove = [key for key in self._cache.keys() if pattern in key]
            for key in keys_to_remove:
                self._remove(key)
            return len(keys_to_remove)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            current_time = time.time()
            expired_count = sum(
                1 for item in self._cache.values()
                if current_time > item['expires_at']
            )

            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'default_ttl': self.default_ttl,
                'expired_items': expired_count,
                'hits': self._hits,
                'misses': self._misses,
                'total_requests': self._total_requests,
                'hit_rate': self._hits / max(self._total_requests, 1)
            }

    def reconfigure(self, max_size: Optional[int] = None, default_ttl: Optional[int] = None) -> None:
        """
        Reconfigure cache parameters at runtime.

        Args:
            max_size: New maximum cache size (if provided)
            default_ttl: New default TTL (if provided)
        """
        with self._lock:
            if max_size is not None:
                self.max_size = max_size
                # Evict items if we're over the new limit
                while len(self._cache) > self.max_size:
                    self._evict_lru()
            if default_ttl is not None:
                self.default_ttl = default_ttl

    def _remove(self, key: str) -> None:
        """Remove an item from internal structures."""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)

    def _evict_lru(self) -> None:
        """Evict the least recently used item."""
        if not self._access_times:
            return

        # Find the key with the oldest access time
        lru_key = min(self._access_times, key=self._access_times.get)
        self._remove(lru_key)


class CacheManager:
    """
    Manages multiple cache instances with configuration support.

    This class allows creating configured cache instances and
    provides centralized cache management.
    """

    def __init__(self):
        self._caches: Dict[str, PerformanceCache] = {}
        self._lock = RLock()
        self._config: Optional["LibraryConfig"] = None

    def configure(self, config: "LibraryConfig") -> None:
        """
        Configure all caches based on LibraryConfig.

        Args:
            config: LibraryConfig instance with cache parameters
        """
        with self._lock:
            self._config = config

            # Reconfigure global cache
            if "global" in self._caches:
                self._caches["global"].reconfigure(
                    max_size=config.global_cache_max_size,
                    default_ttl=config.global_cache_ttl
                )

            # Reconfigure expression cache
            if "expression" in self._caches:
                self._caches["expression"].reconfigure(
                    max_size=config.expression_cache_max_size,
                    default_ttl=config.expression_cache_ttl
                )

            # Reconfigure user access cache
            if "user_access" in self._caches:
                self._caches["user_access"].reconfigure(
                    max_size=config.user_access_cache_max_size,
                    default_ttl=config.user_access_cache_ttl
                )

    def get_global_cache(self) -> PerformanceCache:
        """Get or create the global cache instance."""
        with self._lock:
            if "global" not in self._caches:
                if self._config:
                    self._caches["global"] = PerformanceCache(
                        max_size=self._config.global_cache_max_size,
                        default_ttl=self._config.global_cache_ttl
                    )
                else:
                    # Default values for backward compatibility
                    self._caches["global"] = PerformanceCache(
                        max_size=50000,
                        default_ttl=600
                    )
            return self._caches["global"]

    def get_expression_cache(self) -> PerformanceCache:
        """Get or create the expression cache instance."""
        with self._lock:
            if "expression" not in self._caches:
                if self._config:
                    self._caches["expression"] = PerformanceCache(
                        max_size=self._config.expression_cache_max_size,
                        default_ttl=self._config.expression_cache_ttl
                    )
                else:
                    # Default values for backward compatibility
                    self._caches["expression"] = PerformanceCache(
                        max_size=10000,
                        default_ttl=300
                    )
            return self._caches["expression"]

    def get_user_access_cache(self) -> PerformanceCache:
        """Get or create the user access cache instance."""
        with self._lock:
            if "user_access" not in self._caches:
                if self._config:
                    self._caches["user_access"] = PerformanceCache(
                        max_size=self._config.user_access_cache_max_size,
                        default_ttl=self._config.user_access_cache_ttl
                    )
                else:
                    # Default values for backward compatibility
                    self._caches["user_access"] = PerformanceCache(
                        max_size=10000,
                        default_ttl=300
                    )
            return self._caches["user_access"]

    def get_custom_cache(self, name: str, max_size: int = 10000, default_ttl: int = 300) -> PerformanceCache:
        """
        Get or create a custom named cache.

        Args:
            name: Unique name for the cache
            max_size: Maximum cache size
            default_ttl: Default TTL in seconds

        Returns:
            PerformanceCache instance
        """
        with self._lock:
            if name not in self._caches:
                self._caches[name] = PerformanceCache(
                    max_size=max_size,
                    default_ttl=default_ttl
                )
            return self._caches[name]

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches."""
        with self._lock:
            return {
                name: cache.get_stats()
                for name, cache in self._caches.items()
            }

    def clear_all(self) -> None:
        """Clear all caches."""
        with self._lock:
            for cache in self._caches.values():
                cache.clear()


# Global cache manager instance
_cache_manager = CacheManager()

# Global cache instance (for backward compatibility)
# This is lazily initialized via the cache manager
_global_cache: Optional[PerformanceCache] = None


def _get_global_cache() -> PerformanceCache:
    """Get the global cache instance (lazy initialization)."""
    global _global_cache
    if _global_cache is None:
        _global_cache = _cache_manager.get_global_cache()
    return _global_cache


def configure_caches(config: "LibraryConfig") -> None:
    """
    Configure all caches based on LibraryConfig.

    Call this function during application startup to configure
    cache parameters from your configuration.

    Args:
        config: LibraryConfig instance

    Example:
        from medha_one_access import LibraryConfig
        from medha_one_access.core.cache import configure_caches

        config = LibraryConfig(
            database_url="...",
            secret_key="...",
            global_cache_max_size=100000,
            global_cache_ttl=1200,
        )
        configure_caches(config)
    """
    global _global_cache
    _cache_manager.configure(config)
    # Reset global cache reference to pick up new config
    _global_cache = _cache_manager.get_global_cache()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return _cache_manager


def cached_expression_resolution(cache_key_func):
    """
    Decorator for caching expression resolution results.

    Args:
        cache_key_func: Function that generates cache key from method arguments
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = _cache_manager.get_expression_cache()

            # Generate cache key
            cache_key = cache_key_func(*args, **kwargs)

            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)

            return result
        return wrapper
    return decorator


def cache_user_access_resolution(user_id: str, app_name: Optional[str] = None, ttl: Optional[int] = None):
    """
    Cache user access resolution results.

    Args:
        user_id: User ID being resolved
        app_name: Application name filter
        ttl: Time to live in seconds (uses config default if not specified)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = _cache_manager.get_user_access_cache()

            # Generate cache key
            cache_key = f"user_access:{user_id}:{app_name or 'all'}:{kwargs.get('evaluation_time', 'current')}"

            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)

            return result
        return wrapper
    return decorator


def invalidate_user_cache(user_id: str) -> int:
    """
    Invalidate all cached data for a specific user.

    Args:
        user_id: User ID to invalidate

    Returns:
        Number of cache entries invalidated
    """
    global_cache = _get_global_cache()
    user_access_cache = _cache_manager.get_user_access_cache()

    count = global_cache.invalidate_pattern(f"user:{user_id}")
    count += global_cache.invalidate_pattern(f"user_access:{user_id}")
    count += user_access_cache.invalidate_pattern(f"user_access:{user_id}")

    return count


def invalidate_resource_cache(resource_id: str) -> int:
    """
    Invalidate all cached data for a specific resource.

    Args:
        resource_id: Resource ID to invalidate

    Returns:
        Number of cache entries invalidated
    """
    global_cache = _get_global_cache()
    return global_cache.invalidate_pattern(f"resource:{resource_id}")


def get_cache_stats() -> Dict[str, Any]:
    """Get global cache statistics."""
    return _cache_manager.get_all_stats()


def clear_all_caches() -> None:
    """Clear all global caches."""
    _cache_manager.clear_all()


# Export cache utilities
__all__ = [
    "PerformanceCache",
    "CacheManager",
    "configure_caches",
    "get_cache_manager",
    "cached_expression_resolution",
    "cache_user_access_resolution",
    "invalidate_user_cache",
    "invalidate_resource_cache",
    "get_cache_stats",
    "clear_all_caches",
]
