"""
Cache management for preprocessed league data.
"""

import pickle
import json
from pathlib import Path
from typing import Any, Dict, Optional

from musicleague.config import PathConfig


class CacheManager:
    """
    Manages caching of preprocessed league data.
    
    Handles saving/loading pickle files for full data and JSON for summaries.
    """
    
    def __init__(self):
        """Initialize cache manager and ensure cache directory exists."""
        PathConfig.ensure_directories()
    
    @staticmethod
    def get_cache_path(league_name: str) -> Path:
        """Get the cache file path for a league."""
        return PathConfig.CACHE_DIR / f"{league_name}_preprocessed.pkl"
    
    @staticmethod
    def get_summary_path(league_name: str) -> Path:
        """Get the summary JSON file path for a league."""
        return PathConfig.CACHE_DIR / f"{league_name}_summary.json"
    
    def exists(self, league_name: str) -> bool:
        """Check if cache exists for a league."""
        return self.get_cache_path(league_name).exists()
    
    def load(self, league_name: str) -> Optional[Dict[str, Any]]:
        """
        Load preprocessed data from cache.
        
        Args:
            league_name: Name of the league
            
        Returns:
            Preprocessed data dictionary or None if not found
        """
        cache_path = self.get_cache_path(league_name)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading cache for {league_name}: {e}")
            return None
    
    def save(self, league_name: str, data: Dict[str, Any]) -> bool:
        """
        Save preprocessed data to cache.
        
        Args:
            league_name: Name of the league
            data: Preprocessed data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        cache_path = self.get_cache_path(league_name)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving cache for {league_name}: {e}")
            return False
    
    def save_summary(self, league_name: str, summary: Dict[str, Any]) -> bool:
        """
        Save summary data as JSON (for easy inspection).
        
        Args:
            league_name: Name of the league
            summary: Summary data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        summary_path = self.get_summary_path(league_name)
        
        try:
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving summary for {league_name}: {e}")
            return False
    
    def load_summary(self, league_name: str) -> Optional[Dict[str, Any]]:
        """
        Load summary data from JSON.
        
        Args:
            league_name: Name of the league
            
        Returns:
            Summary dictionary or None if not found
        """
        summary_path = self.get_summary_path(league_name)
        
        if not summary_path.exists():
            return None
        
        try:
            with open(summary_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading summary for {league_name}: {e}")
            return None
    
    def clear(self, league_name: str) -> bool:
        """
        Clear cache for a specific league.
        
        Args:
            league_name: Name of the league
            
        Returns:
            True if successful
        """
        cache_path = self.get_cache_path(league_name)
        summary_path = self.get_summary_path(league_name)
        
        try:
            if cache_path.exists():
                cache_path.unlink()
            if summary_path.exists():
                summary_path.unlink()
            return True
        except Exception as e:
            print(f"Error clearing cache for {league_name}: {e}")
            return False
    
    def clear_all(self) -> int:
        """
        Clear all cached data.
        
        Returns:
            Number of files removed
        """
        count = 0
        for path in PathConfig.CACHE_DIR.glob("*"):
            try:
                path.unlink()
                count += 1
            except Exception:
                pass
        return count

