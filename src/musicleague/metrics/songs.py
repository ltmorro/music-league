"""
Song-specific metrics for MusicLeague analysis.

Provides metrics focused on individual songs including controversy,
vote distribution, and obscurity scores.
"""

from collections import defaultdict
from typing import Dict, List, Optional, TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from musicleague.data.loader import MusicLeagueData


class SongMetrics:
    """Metrics focused on individual songs."""

    @staticmethod
    def controversy_score(
        data: "MusicLeagueData",
        spotify_uri: str,
        round_id: Optional[str] = None
    ) -> float:
        """
        Calculate controversy score (standard deviation of votes).
        
        Higher scores indicate more polarizing songs where voters disagreed
        significantly on the song's quality.
        
        Args:
            data: MusicLeagueData object
            spotify_uri: Spotify URI of the song
            round_id: Optional round ID to filter by
            
        Returns:
            Standard deviation of votes (0.0 if < 2 votes)
        """
        votes = data.get_votes_for_song(spotify_uri, round_id)
        if len(votes) < 2:
            return 0.0
        return float(np.std(votes))

    @staticmethod
    def vote_distribution(
        data: "MusicLeagueData",
        spotify_uri: str,
        round_id: Optional[str] = None
    ) -> Dict[int, int]:
        """
        Get distribution of vote values.
        
        Args:
            data: MusicLeagueData object
            spotify_uri: Spotify URI of the song
            round_id: Optional round ID to filter by
            
        Returns:
            Dictionary mapping point values to counts (e.g., {1: 2, 2: 3, 3: 5})
        """
        votes = data.get_votes_for_song(spotify_uri, round_id)
        distribution: Dict[int, int] = defaultdict(int)
        for vote in votes:
            distribution[vote] += 1
        return dict(distribution)

    @staticmethod
    def total_points(
        data: "MusicLeagueData",
        spotify_uri: str,
        round_id: Optional[str] = None
    ) -> int:
        """
        Calculate total points received by a song.
        
        Args:
            data: MusicLeagueData object
            spotify_uri: Spotify URI of the song
            round_id: Optional round ID to filter by
            
        Returns:
            Sum of all votes for this song
        """
        votes = data.get_votes_for_song(spotify_uri, round_id)
        return sum(votes)

    @staticmethod
    def obscurity_score(
        data: "MusicLeagueData",
        spotify_uri: str,
        round_id: Optional[str] = None
    ) -> float:
        """
        Calculate obscurity score: votes / (spotify_popularity + 1).
        
        Higher scores indicate "hidden gems" - songs that performed well
        despite low Spotify popularity.
        
        Args:
            data: MusicLeagueData object
            spotify_uri: Spotify URI of the song
            round_id: Optional round ID to filter by
            
        Returns:
            Obscurity score (higher = more impressive for an obscure song)
        """
        total_votes = SongMetrics.total_points(data, spotify_uri, round_id)
        spotify_data = data.get_spotify_data(spotify_uri)
        popularity = spotify_data['popularity']
        return total_votes / (popularity + 1)

    @staticmethod
    def get_all_song_metrics(
        data: "MusicLeagueData",
        round_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get comprehensive metrics for all songs.
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            
        Returns:
            DataFrame with one row per song, sorted by total_points descending
        """
        metrics = []

        submissions = data.submissions
        if round_id:
            submissions = [s for s in submissions if s['round_id'] == round_id]

        for submission in submissions:
            uri = submission['spotify_uri']
            rid = submission['round_id']
            spotify_data = data.get_spotify_data(uri)
            submitter = data.competitors.get(submission['submitter_id'], {'name': 'Unknown', 'id': ''})

            metrics.append({
                'spotify_uri': uri,
                'round_id': rid,
                'song_name': spotify_data['name'],
                'artist': spotify_data['artist'],
                'submitter': submitter['name'],
                'submitter_id': submitter.get('id', ''),
                'spotify_popularity': spotify_data['popularity'],
                'total_points': SongMetrics.total_points(data, uri, rid),
                'controversy_score': SongMetrics.controversy_score(data, uri, rid),
                'obscurity_score': SongMetrics.obscurity_score(data, uri, rid),
                'vote_distribution': SongMetrics.vote_distribution(data, uri, rid),
                'release_date': spotify_data['release_date']
            })

        df = pd.DataFrame(metrics)
        if len(df) > 0:
            df = df.sort_values('total_points', ascending=False)
        return df

