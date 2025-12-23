"""
Configuration management for MusicLeague.

Handles environment variables, paths, and application settings.
Credentials should NEVER be hardcoded - use environment variables or .env file.
"""

import os
from pathlib import Path
from typing import List, Optional

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class SpotifyConfig:
    """Spotify API configuration."""
    
    @staticmethod
    def get_client_id() -> str:
        """Get Spotify client ID from environment."""
        client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        if not client_id:
            raise ValueError(
                "SPOTIFY_CLIENT_ID environment variable not set. "
                "Please set it or create a .env file."
            )
        return client_id
    
    @staticmethod
    def get_client_secret() -> str:
        """Get Spotify client secret from environment."""
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        if not client_secret:
            raise ValueError(
                "SPOTIFY_CLIENT_SECRET environment variable not set. "
                "Please set it or create a .env file."
            )
        return client_secret


class PathConfig:
    """Path configuration for data directories."""

    # Base paths - relative to cwd (user runs from project root)
    # Can be overridden via environment variables for flexibility
    PROJECT_ROOT = Path(os.environ.get("MUSICLEAGUE_ROOT", Path.cwd()))
    DATA_DIR = Path(os.environ.get("MUSICLEAGUE_DATA_DIR", PROJECT_ROOT / "data"))
    CACHE_DIR = Path(os.environ.get("MUSICLEAGUE_CACHE_DIR", PROJECT_ROOT / "cache"))
    OUTPUT_DIR = Path(os.environ.get("MUSICLEAGUE_OUTPUT_DIR", PROJECT_ROOT / "outputs"))
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create required directories if they don't exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_league_data_path(cls, league_name: str) -> Path:
        """Get the data directory path for a specific league."""
        return cls.DATA_DIR / league_name
    
    @classmethod
    def get_cache_file(cls, league_name: str, suffix: str = "preprocessed.pkl") -> Path:
        """Get the cache file path for a specific league."""
        return cls.CACHE_DIR / f"{league_name}_{suffix}"


class VisualizationConfig:
    """Visualization and theming configuration."""

    # Primary color palette
    COLORS = [
        '#2980b9',  # Blue
        '#c0392b',  # Red
        '#16a085',  # Green
        '#8e44ad',  # Purple
        '#d35400',  # Orange
        '#7f8c8d',  # Gray
        '#ecf0f1',  # White
        '#FFC864',  # Gold
    ]

    COLORS_DICT = {
        'blue': '#2980b9',
        'red': '#c0392b',
        'green': '#16a085',
        'purple': '#8e44ad',
        'orange': '#d35400',
        'gray': '#7f8c8d',
        'white': '#ecf0f1',
        'gold': '#FFC864',
    }

    # Dark variants for gradients (derived from primary colors)
    COLORS_DARK = {
        'blue': '#1a5276',
        'red': '#922b21',
        'green': '#0e6655',
        'purple': '#6c3483',
        'orange': '#a04000',
        'gray': '#566573',
    }

    # Background colors for dark theme
    BG_COLORS = {
        'dark': '#1f1f1f',
        'card': '#2a2a2a',
        'sidebar': '#121212',
    }

    # Semantic colors (map semantic meaning to palette colors)
    SEMANTIC = {
        'positive': '#16a085',   # green - for gains, rising trends
        'negative': '#c0392b',   # red - for losses, falling trends
        'neutral': '#7f8c8d',    # gray - for steady/unchanged
        'highlight': '#FFC864',  # gold - for emphasis, winners
        'accent': '#8e44ad',     # purple - for special elements
        'info': '#2980b9',       # blue - for informational
        'warning': '#d35400',    # orange - for controversy, caution
    }

    # League-specific colors
    LEAGUE_COLORS = {
        'metalicactopus_1': '#2980b9',
        'metalicactopus_2': '#c0392b',
    }
    
    # Metric display names (branded)
    METRIC_NAMES = {
        'total_votes': '💥 Total Fan Fervor',
        'total_competitors': '🏟️ The Roster Size',
        'total_submissions': '🎸 Tracks Dropped',
        'total_rounds': '🎯 Rounds Fought',
        'avg_points_per_submission': '🎯 The A&R Score',
        'controversy_score': '🔥 Love-it-or-Hate-it Index',
        'obscurity_score': '💎 Deep Cut Cred',
        'golden_ear_score': '🔮 Trendsetter Rating',
        'hipster_score': '🕵️ Obscurity Cred',
        'influence_score': '👑 League Clout',
        'generosity_score': '🎁 Generosity Rating',
        'consistency_score': '📊 Consistency Factor',
    }


# Default leagues for the dashboard
DEFAULT_LEAGUES = ('metalicactopus_1', 'metalicactopus_2')


def format_league_name(league_name: str) -> str:
    """
    Format a league name for display.

    Splits by underscore and capitalizes each part.
    Example: "metalicactopus_1" -> "Metalicactopus 1"
    """
    parts = league_name.split('_')
    return ' '.join(part.capitalize() for part in parts)


# Convenience functions
def get_available_leagues() -> List[str]:
    """Get list of available league directories."""
    if not PathConfig.DATA_DIR.exists():
        return []

    leagues = [
        d.name for d in PathConfig.DATA_DIR.iterdir()
        if d.is_dir() and not d.name.startswith('.')
    ]
    return sorted(leagues)

