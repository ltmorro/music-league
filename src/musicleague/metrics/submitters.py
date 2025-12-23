"""
Submitter-specific metrics for MusicLeague analysis.

Provides metrics focused on song submitters including average performance,
consistency, underdog factor, and fan/nemesis analysis.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from musicleague.data.loader import MusicLeagueData

from musicleague.metrics.songs import SongMetrics


class SubmitterMetrics:
    """Metrics focused on song submitters."""

    @staticmethod
    def average_points_per_submission(
        data: "MusicLeagueData",
        submitter_id: str,
        round_id: Optional[str] = None
    ) -> float:
        """
        Calculate average points per submission for a submitter.
        
        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter
            round_id: Optional round ID to filter by
            
        Returns:
            Average points across all submissions
        """
        submissions = [
            s for s in data.submissions
            if s['submitter_id'] == submitter_id
            and (round_id is None or s['round_id'] == round_id)
        ]

        if len(submissions) == 0:
            return 0.0

        total_points = sum(
            SongMetrics.total_points(data, sub['spotify_uri'], sub['round_id'])
            for sub in submissions
        )

        return total_points / len(submissions)

    @staticmethod
    def consistency_score(
        data: "MusicLeagueData",
        submitter_id: str,
        round_id: Optional[str] = None
    ) -> Tuple[float, float]:
        """
        Calculate consistency metrics for a submitter.
        
        Low standard deviation indicates consistent performance across submissions.
        
        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter
            round_id: Optional round ID to filter by
            
        Returns:
            Tuple of (average_points, std_dev)
        """
        submissions = [
            s for s in data.submissions
            if s['submitter_id'] == submitter_id
            and (round_id is None or s['round_id'] == round_id)
        ]

        if len(submissions) == 0:
            return (0.0, 0.0)

        points = [
            SongMetrics.total_points(data, sub['spotify_uri'], sub['round_id'])
            for sub in submissions
        ]

        return (float(np.mean(points)), float(np.std(points)))

    @staticmethod
    def underdog_factor(
        data: "MusicLeagueData",
        submitter_id: str,
        round_id: Optional[str] = None
    ) -> float:
        """
        Calculate underdog factor: total_points / (avg_spotify_popularity + 1).
        
        Higher scores indicate success with obscure songs - the submitter
        knows how to find hidden gems that resonate with voters.
        
        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter
            round_id: Optional round ID to filter by
            
        Returns:
            Underdog factor score
        """
        submissions = [
            s for s in data.submissions
            if s['submitter_id'] == submitter_id
            and (round_id is None or s['round_id'] == round_id)
        ]

        if len(submissions) == 0:
            return 0.0

        total_points = 0
        total_popularity = 0

        for sub in submissions:
            total_points += SongMetrics.total_points(
                data, sub['spotify_uri'], sub['round_id']
            )
            spotify_data = data.get_spotify_data(sub['spotify_uri'])
            total_popularity += spotify_data['popularity']

        avg_popularity = total_popularity / len(submissions)
        return total_points / (avg_popularity + 1)

    @staticmethod
    def biggest_fan_and_nemesis(
        data: "MusicLeagueData",
        submitter_id: str,
        round_id: Optional[str] = None
    ) -> Tuple[Dict, Dict]:
        """
        Find who votes most and least for this submitter.
        
        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter
            round_id: Optional round ID to filter by
            
        Returns:
            Tuple of (biggest_fan_dict, nemesis_dict) with format:
            {'name': voter_name, 'avg_points': float, 'total_points': int, 'num_votes': int}
        """
        submissions = [
            s for s in data.submissions
            if s['submitter_id'] == submitter_id
            and (round_id is None or s['round_id'] == round_id)
        ]

        if len(submissions) == 0:
            return ({}, {})

        voter_points: Dict[str, List[int]] = defaultdict(list)

        for sub in submissions:
            for vote in data.votes:
                if (vote['spotify_uri'] == sub['spotify_uri'] and
                    vote['round_id'] == sub['round_id'] and
                    vote['voter_id'] != submitter_id):
                    voter_name = data.competitors[vote['voter_id']]['name']
                    voter_points[voter_name].append(vote['points'])

        if len(voter_points) == 0:
            return ({}, {})

        # Calculate averages and build voter stats
        voter_averages = {
            voter: {
                'name': voter,
                'avg_points': float(np.mean(points)),
                'total_points': sum(points),
                'num_votes': len(points)
            }
            for voter, points in voter_points.items()
        }

        # Sort by average points
        sorted_voters = sorted(
            voter_averages.values(),
            key=lambda x: x['avg_points']
        )

        biggest_fan = sorted_voters[-1] if sorted_voters else {}
        nemesis = sorted_voters[0] if sorted_voters else {}

        return (biggest_fan, nemesis)

