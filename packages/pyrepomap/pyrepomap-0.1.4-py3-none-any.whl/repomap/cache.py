"""Caching layer for repomap using diskcache with SQLite fallback."""

import shutil
import sqlite3
from pathlib import Path

from diskcache import Cache


SQLITE_ERRORS = (sqlite3.OperationalError, sqlite3.DatabaseError, OSError)


class TagsCache:
    """Disk-based cache for parsed tags with fallback to in-memory dict."""
    
    def __init__(self, root: str, cache_version: int = 4, verbose: bool = False):
        self.root = root
        self.verbose = verbose
        self.cache_dir = f".repomap.tags.cache.v{cache_version}"
        self._cache = None
        self._load_cache()
    
    def _load_cache(self):
        """Initialize the disk cache, falling back to dict on errors."""
        path = Path(self.root) / self.cache_dir
        try:
            self._cache = Cache(path)
        except SQLITE_ERRORS as e:
            self._handle_error(e)
    
    def _handle_error(self, original_error=None):
        """Handle SQLite errors by trying to recreate cache, falling back to dict."""
        if self.verbose and original_error:
            print(f"Tags cache error: {str(original_error)}")
        
        if isinstance(self._cache, dict):
            return
        
        path = Path(self.root) / self.cache_dir
        
        # Try to recreate the cache
        try:
            if path.exists():
                shutil.rmtree(path)
            
            new_cache = Cache(path)
            
            # Test that it works
            test_key = "test"
            new_cache[test_key] = "test"
            _ = new_cache[test_key]
            del new_cache[test_key]
            
            self._cache = new_cache
            return
        except SQLITE_ERRORS as e:
            if self.verbose:
                print(f"Cache recreation error: {str(e)}")
        
        # Fall back to dict
        self._cache = dict()
    
    def get(self, key):
        """Get a value from cache."""
        try:
            return self._cache.get(key)
        except SQLITE_ERRORS as e:
            self._handle_error(e)
            return self._cache.get(key)
    
    def set(self, key, value):
        """Set a value in cache."""
        try:
            self._cache[key] = value
        except SQLITE_ERRORS as e:
            self._handle_error(e)
            self._cache[key] = value
    
    def __len__(self):
        """Return cache size."""
        try:
            return len(self._cache)
        except SQLITE_ERRORS as e:
            self._handle_error(e)
            return len(self._cache)
    
    def __contains__(self, key):
        """Check if key is in cache."""
        try:
            return key in self._cache
        except SQLITE_ERRORS:
            return False
