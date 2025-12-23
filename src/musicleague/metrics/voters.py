"""
Voter-specific metrics for MusicLeague analysis.

Provides metrics focused on individual voters including golden ear,
hipster scores, generosity, and voting patterns.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import pandas as pd
from scipy import stats

if TYPE_CHECKING:
    from musicleague.data.loader import MusicLeagueData


class VoterMetrics:
    """Metrics focused on individual voters."""

    @staticmethod
    def get_voter_scores(
        data: "MusicLeagueData",
        voter_id: str,
        round_id: Optional[str] = None
    ) -> List[int]:
        """
        Get all scores given by a voter.
        
        Args:
            data: MusicLeagueData object
            voter_id: ID of the voter
            round_id: Optional round ID to filter by
            
        Returns:
            List of point values this voter assigned
        """
        return [
            v['points'] for v in data.votes
            if v['voter_id'] == voter_id
            and v['points'] > 0
            and (round_id is None or v['round_id'] == round_id)
        ]

    @staticmethod
    def generosity_score(
        data: "MusicLeagueData",
        voter_id: str,
        round_id: Optional[str] = None
    ) -> Tuple[float, float]:
        """
        Calculate average points given and standard deviation.
        
        Args:
            data: MusicLeagueData object
            voter_id: ID of the voter
            round_id: Optional round ID to filter by
            
        Returns:
            Tuple of (mean, std_dev)
        """
        scores = VoterMetrics.get_voter_scores(data, voter_id, round_id)
        if len(scores) == 0:
            return (0.0, 0.0)
        return (float(np.mean(scores)), float(np.std(scores)))

    @staticmethod
    def voting_range(
        data: "MusicLeagueData",
        voter_id: str,
        round_id: Optional[str] = None
    ) -> Tuple[int, int, float]:
        """
        Calculate voting range statistics.
        
        Args:
            data: MusicLeagueData object
            voter_id: ID of the voter
            round_id: Optional round ID to filter by
            
        Returns:
            Tuple of (min, max, range)
        """
        scores = VoterMetrics.get_voter_scores(data, voter_id, round_id)
        if len(scores) == 0:
            return (0, 0, 0.0)
        return (
            int(np.min(scores)),
            int(np.max(scores)),
            float(np.max(scores) - np.min(scores))
        )

    @staticmethod
    def hipster_score(
        data: "MusicLeagueData",
        voter_id: str,
        round_id: Optional[str] = None
    ) -> float:
        """
        Calculate hipster score: preference for obscure tracks.
        
        Uses top-tier votes (>= 2 points) to identify preferred tracks,
        then calculates average (100 - spotify_popularity) weighted by points.
        
        Args:
            data: MusicLeagueData object
            voter_id: ID of the voter
            round_id: Optional round ID to filter by
            
        Returns:
            Hipster score (higher = prefers more obscure tracks)
        """
        votes = [
            v for v in data.votes
            if v['voter_id'] == voter_id
            and v['points'] >= 2
            and (round_id is None or v['round_id'] == round_id)
        ]

        if len(votes) == 0:
            return 0.0

        total_obscurity = 0.0
        for vote in votes:
            spotify_data = data.get_spotify_data(vote['spotify_uri'])
            total_obscurity += (100 - spotify_data['popularity']) * vote['points']

        total_points = sum(v['points'] for v in votes)
        return total_obscurity / total_points if total_points > 0 else 0.0

    @staticmethod
    def golden_ear_score(
        data: "MusicLeagueData",
        voter_id: str,
        round_id: Optional[str] = None
    ) -> float:
        """
        Calculate correlation between voter's scores and final rankings.
        
        Higher scores indicate "tastemakers" who can predict which songs
        will be popular with the group.
        
        Args:
            data: MusicLeagueData object
            voter_id: ID of the voter
            round_id: Optional round ID to filter by
            
        Returns:
            Spearman correlation coefficient (-1 to 1)
        """
        # Get songs this voter voted for
        voter_votes = {}
        for vote in data.votes:
            if vote['voter_id'] == voter_id and vote['points'] > 0:
                if round_id is None or vote['round_id'] == round_id:
                    key = (vote['spotify_uri'], vote['round_id'])
                    voter_votes[key] = vote['points']

        if len(voter_votes) < 3:
            return 0.0

        # Calculate final rankings for each song (excluding this voter)
        voter_scores = []
        final_scores_list = []

        for (uri, rid), voter_score in voter_votes.items():
            other_votes = [
                v['points'] for v in data.votes
                if v['spotify_uri'] == uri
                and v['round_id'] == rid
                and v['voter_id'] != voter_id
            ]

            if len(other_votes) > 0:
                voter_scores.append(voter_score)
                final_scores_list.append(sum(other_votes))

        if len(voter_scores) < 3:
            return 0.0

        correlation, _ = stats.spearmanr(voter_scores, final_scores_list)
        return float(correlation) if not np.isnan(correlation) else 0.0

    @staticmethod
    def voter_similarity_matrix(
        data: "MusicLeagueData",
        round_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Calculate pairwise Spearman correlation between all voters.
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            
        Returns:
            DataFrame with voters as both rows and columns
        """
        voter_ids = list(data.competitors.keys())

        # Get all unique songs
        songs = set()
        for vote in data.votes:
            if round_id is None or vote['round_id'] == round_id:
                songs.add((vote['spotify_uri'], vote['round_id']))

        songs = sorted(list(songs))

        # Create vote matrix
        vote_matrix = []
        for song_uri, song_round in songs:
            row = []
            for voter_id in voter_ids:
                vote_val = 0
                for vote in data.votes:
                    if (vote['voter_id'] == voter_id and
                        vote['spotify_uri'] == song_uri and
                        vote['round_id'] == song_round):
                        vote_val = vote['points']
                        break
                row.append(vote_val)
            vote_matrix.append(row)

        # Transpose so voters are rows
        vote_matrix_arr = np.array(vote_matrix).T

        # Calculate correlation matrix
        correlation_matrix = np.zeros((len(voter_ids), len(voter_ids)))
        for i in range(len(voter_ids)):
            for j in range(len(voter_ids)):
                if i == j:
                    correlation_matrix[i][j] = 1.0
                else:
                    corr, _ = stats.spearmanr(vote_matrix_arr[i], vote_matrix_arr[j])
                    correlation_matrix[i][j] = corr if not np.isnan(corr) else 0.0

        voter_names = [data.competitors[vid]['name'] for vid in voter_ids]
        return pd.DataFrame(correlation_matrix, index=voter_names, columns=voter_names)

    @staticmethod
    def loyalty_index(
        data: "MusicLeagueData",
        voter_id: str,
        round_id: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate average points given to each submitter.
        
        Args:
            data: MusicLeagueData object
            voter_id: ID of the voter
            round_id: Optional round ID to filter by
            
        Returns:
            Dictionary mapping submitter names to average points given
        """
        submitter_points: Dict[str, List[int]] = defaultdict(list)

        for vote in data.votes:
            if vote['voter_id'] == voter_id and vote['points'] > 0:
                if round_id is None or vote['round_id'] == round_id:
                    submitter_id = data.get_submitter_for_song(
                        vote['spotify_uri'],
                        vote['round_id']
                    )
                    if submitter_id and submitter_id != voter_id:
                        submitter_name = data.competitors[submitter_id]['name']
                        submitter_points[submitter_name].append(vote['points'])

        return {
            submitter: float(np.mean(points))
            for submitter, points in submitter_points.items()
        }

