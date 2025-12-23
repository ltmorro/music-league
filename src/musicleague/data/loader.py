"""
MusicLeague data loader.

Loads and manages MusicLeague data from CSV files.
"""

import csv
from typing import Dict, List, Optional

from musicleague.config import PathConfig
from musicleague.data.spotify import SpotifyClient


class MusicLeagueData:
    """
    Loads and manages MusicLeague data from CSV files.
    
    This class handles loading competition data (rounds, competitors,
    submissions, votes) and fetching Spotify metadata for tracks.
    
    Attributes:
        league_name: Name of the league (matches data directory name)
        rounds: List of round IDs
        competitors: Dict mapping competitor ID to competitor info
        submissions: List of submission records
        votes: List of vote records
        spotify_data: Cache of Spotify metadata by URI
    """

    def __init__(self, league_name: str, fetch_spotify: bool = True):
        """
        Initialize and load league data.
        
        Args:
            league_name: Name of the league directory in data/
            fetch_spotify: Whether to initialize Spotify client for fetching metadata
        """
        self.league_name = league_name
        self.rounds: List[str] = []
        self.competitors: Dict[str, Dict] = {}
        self.submissions: List[Dict] = []
        self.votes: List[Dict] = []
        self.spotify_data: Dict[str, Dict] = {}
        
        # Initialize Spotify client if needed
        self._spotify: Optional[SpotifyClient] = None
        if fetch_spotify:
            try:
                self._spotify = SpotifyClient.get_instance()
            except ValueError as e:
                print(f"Warning: Could not initialize Spotify client: {e}")
                print("Spotify metadata will not be available.")
        
        self._load_data()

    @property
    def sp(self):
        """Get underlying spotipy client for backwards compatibility."""
        return self._spotify.client if self._spotify else None

    def _load_data(self) -> None:
        """Load all CSV data files for the league."""
        data_path = PathConfig.get_league_data_path(self.league_name)
        
        # Load rounds
        rounds_file = data_path / "rounds.csv"
        if rounds_file.exists():
            with open(rounds_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.rounds.append(row['ID'])
        
        # Load competitors
        competitors_file = data_path / "competitors.csv"
        if competitors_file.exists():
            with open(competitors_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.competitors[row['ID']] = {
                        'id': row['ID'],
                        'name': row['Name']
                    }
        
        # Load submissions
        submissions_file = data_path / "submissions.csv"
        if submissions_file.exists():
            with open(submissions_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.submissions.append({
                        'round_id': row['Round ID'],
                        'submitter_id': row['Submitter ID'],
                        'spotify_uri': row['Spotify URI'],
                        'comment': row.get('Comment', ''),
                    })
        
        # Load votes
        votes_file = data_path / "votes.csv"
        if votes_file.exists():
            with open(votes_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.votes.append({
                        'round_id': row['Round ID'],
                        'voter_id': row['Voter ID'],
                        'spotify_uri': row['Spotify URI'],
                        'points': int(row['Points Assigned']),
                        'comment': row.get('Comment', ''),
                    })

    def get_spotify_data(self, uri: str) -> Dict:
        """
        Fetch Spotify metadata for a track (with caching).
        
        Args:
            uri: Spotify URI for the track
            
        Returns:
            Dictionary with track metadata
        """
        if uri not in self.spotify_data:
            if self._spotify is None:
                # Return placeholder if no Spotify client
                self.spotify_data[uri] = {
                    'popularity': 0,
                    'name': 'Unknown',
                    'artist': 'Unknown',
                    'release_date': '1900-01-01',
                    'uri': uri
                }
            else:
                try:
                    track = self._spotify.get_track(uri)
                    self.spotify_data[uri] = {
                        'popularity': track['popularity'],
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'release_date': track['album']['release_date'],
                        'uri': uri
                    }
                except Exception as e:
                    print(f"Error fetching Spotify data for {uri}: {e}")
                    self.spotify_data[uri] = {
                        'popularity': 0,
                        'name': 'Unknown',
                        'artist': 'Unknown',
                        'release_date': '1900-01-01',
                        'uri': uri
                    }
        
        return self.spotify_data[uri]

    def get_votes_for_song(self, spotify_uri: str, round_id: Optional[str] = None) -> List[int]:
        """
        Get all vote values for a specific song.
        
        Args:
            spotify_uri: Spotify URI of the song
            round_id: Optional round ID to filter by
            
        Returns:
            List of point values for votes on this song
        """
        return [
            v['points'] for v in self.votes
            if v['spotify_uri'] == spotify_uri
            and (round_id is None or v['round_id'] == round_id)
        ]

    def get_submitter_for_song(self, spotify_uri: str, round_id: str) -> Optional[str]:
        """
        Get the submitter ID for a song in a round.
        
        Args:
            spotify_uri: Spotify URI of the song
            round_id: Round ID
            
        Returns:
            Submitter ID or None if not found
        """
        for sub in self.submissions:
            if sub['spotify_uri'] == spotify_uri and sub['round_id'] == round_id:
                return sub['submitter_id']
        return None

    def __repr__(self) -> str:
        """String representation of the data object."""
        return (
            f"MusicLeagueData(league='{self.league_name}', "
            f"rounds={len(self.rounds)}, "
            f"competitors={len(self.competitors)}, "
            f"submissions={len(self.submissions)}, "
            f"votes={len(self.votes)})"
        )

