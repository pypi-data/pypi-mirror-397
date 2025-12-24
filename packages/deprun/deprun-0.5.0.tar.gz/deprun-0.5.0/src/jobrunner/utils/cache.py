"""Caching utilities for job-runner.

Provides caching for configuration, dependency resolution,
and execution results to improve performance.
"""

import json
import hashlib
from pathlib import Path
from typing import Any, Optional, Dict
from datetime import datetime, timedelta


class CacheManager:
    """Manage caching for various job-runner operations."""
    
    CACHE_DIR = Path.home() / ".cache" / "job-runner"
    DEFAULT_TTL = timedelta(hours=24)
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache manager.
        
        Args:
            cache_dir: Optional custom cache directory
        """
        self.cache_dir = cache_dir or self.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, namespace: str, key: str) -> str:
        """Generate cache key hash.
        
        Args:
            namespace: Cache namespace (e.g., 'config', 'deps')
            key: Unique identifier within namespace
            
        Returns:
            Hashed cache key
        """
        full_key = f"{namespace}:{key}"
        return hashlib.sha256(full_key.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get path for cache file.
        
        Args:
            cache_key: Hashed cache key
            
        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, namespace: str, key: str, 
            ttl: Optional[timedelta] = None) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            ttl: Time-to-live (use default if None)
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_key = self._get_cache_key(namespace, key)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)
            
            # Check expiration
            cached_time = datetime.fromisoformat(cached['timestamp'])
            ttl = ttl or self.DEFAULT_TTL
            if datetime.now() - cached_time > ttl:
                cache_path.unlink()  # Delete expired cache
                return None
            
            return cached['value']
        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid cache file
            if cache_path.exists():
                cache_path.unlink()
            return None
    
    def set(self, namespace: str, key: str, value: Any) -> None:
        """Set value in cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache (must be JSON-serializable)
        """
        cache_key = self._get_cache_key(namespace, key)
        cache_path = self._get_cache_path(cache_key)
        
        cached = {
            'timestamp': datetime.now().isoformat(),
            'namespace': namespace,
            'key': key,
            'value': value,
        }
        
        with open(cache_path, 'w') as f:
            json.dump(cached, f, indent=2)
    
    def invalidate(self, namespace: str, key: str) -> bool:
        """Invalidate a cache entry.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            
        Returns:
            True if entry was deleted, False if not found
        """
        cache_key = self._get_cache_key(namespace, key)
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            cache_path.unlink()
            return True
        return False
    
    def clear_namespace(self, namespace: str) -> int:
        """Clear all entries in a namespace.
        
        Args:
            namespace: Cache namespace to clear
            
        Returns:
            Number of entries cleared
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                if cached.get('namespace') == namespace:
                    cache_file.unlink()
                    count += 1
            except (json.JSONDecodeError, KeyError):
                continue
        return count
    
    def clear_all(self) -> int:
        """Clear all cache entries.
        
        Returns:
            Number of entries cleared
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_files = len(list(self.cache_dir.glob("*.json")))
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))
        
        namespaces: Dict[str, int] = {}
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                namespace = cached.get('namespace', 'unknown')
                namespaces[namespace] = namespaces.get(namespace, 0) + 1
            except (json.JSONDecodeError, KeyError):
                continue
        
        return {
            'total_entries': total_files,
            'total_size_bytes': total_size,
            'namespaces': namespaces,
            'cache_dir': str(self.cache_dir),
        }
