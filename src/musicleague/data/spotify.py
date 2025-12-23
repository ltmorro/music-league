"""
Spotify API client wrapper.

Handles authentication and API calls to Spotify.
"""

from typing import Dict, Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from musicleague.config import SpotifyConfig


class SpotifyClient:
    """
    Wrapper for Spotify API client.

    Handles authentication using environment variables and provides
    methods for fetching track data.
    """
    
    _instance: Optional["SpotifyClient"] = None
    
    def __init__(self):
        """Initialize Spotify client with credentials from environment."""
        try:
            client_id = SpotifyConfig.get_client_id()
            client_secret = SpotifyConfig.get_client_secret()
            
            credentials_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            self._client = spotipy.Spotify(client_credentials_manager=credentials_manager)
        except ValueError as e:
            # Re-raise with helpful message
            raise ValueError(
                f"Failed to initialize Spotify client: {e}\n"
                "Make sure SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET are set."
            ) from e
    
    @classmethod
    def get_instance(cls) -> "SpotifyClient":
        """Get singleton instance of SpotifyClient."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def client(self) -> spotipy.Spotify:
        """Get the underlying spotipy client."""
        return self._client
    
    def get_track(self, uri: str) -> Dict:
        """
        Fetch track metadata from Spotify.

        Args:
            uri: Spotify URI (e.g., 'spotify:track:...' or just the track ID)

        Returns:
            Track metadata dictionary
        """
        return self._client.track(uri)

