"""
Comment metrics for MusicLeague analysis.

Provides metrics based on submission and vote comments,
including wordiness, engagement, and notable quotes.
"""

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from musicleague.data.loader import MusicLeagueData


class CommentMetrics:
    """Metrics based on submission and vote comments."""

    @staticmethod
    def submitter_wordsmith_score(
        data: "MusicLeagueData",
        submitter_id: str,
        round_id: Optional[str] = None
    ) -> Tuple[float, float]:
        """
        Calculate comment engagement metrics for a submitter.

        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter
            round_id: Optional round ID to filter by

        Returns:
            Tuple of (avg_comment_length, comment_rate)
            - avg_comment_length: Average character count of non-empty comments
            - comment_rate: Percentage of submissions with comments (0-100)
        """
        submissions = [
            s for s in data.submissions
            if s['submitter_id'] == submitter_id
            and (round_id is None or s['round_id'] == round_id)
        ]

        if not submissions:
            return (0.0, 0.0)

        comments = [s.get('comment', '') for s in submissions]
        non_empty = [c for c in comments if c and c.strip()]

        if not non_empty:
            return (0.0, 0.0)

        avg_length = sum(len(c) for c in non_empty) / len(non_empty)
        comment_rate = (len(non_empty) / len(submissions)) * 100

        return (avg_length, comment_rate)

    @staticmethod
    def voter_critic_score(
        data: "MusicLeagueData",
        voter_id: str,
        round_id: Optional[str] = None
    ) -> Tuple[float, float]:
        """
        Calculate comment engagement metrics for a voter.

        Args:
            data: MusicLeagueData object
            voter_id: ID of the voter
            round_id: Optional round ID to filter by

        Returns:
            Tuple of (avg_comment_length, comment_rate)
            - avg_comment_length: Average character count of non-empty comments
            - comment_rate: Percentage of votes with comments (0-100)
        """
        votes = [
            v for v in data.votes
            if v['voter_id'] == voter_id
            and v['points'] > 0
            and (round_id is None or v['round_id'] == round_id)
        ]

        if not votes:
            return (0.0, 0.0)

        comments = [v.get('comment', '') for v in votes]
        non_empty = [c for c in comments if c and c.strip()]

        if not non_empty:
            return (0.0, 0.0)

        avg_length = sum(len(c) for c in non_empty) / len(non_empty)
        comment_rate = (len(non_empty) / len(votes)) * 100

        return (avg_length, comment_rate)

    @staticmethod
    def song_discussion_score(
        data: "MusicLeagueData",
        spotify_uri: str,
        round_id: Optional[str] = None
    ) -> Tuple[int, float]:
        """
        Calculate how much discussion a song generated.

        Args:
            data: MusicLeagueData object
            spotify_uri: Spotify URI of the song
            round_id: Optional round ID to filter by

        Returns:
            Tuple of (comment_count, avg_comment_length)
        """
        votes = [
            v for v in data.votes
            if v['spotify_uri'] == spotify_uri
            and (round_id is None or v['round_id'] == round_id)
        ]

        comments = [v.get('comment', '') for v in votes if v.get('comment', '').strip()]

        if not comments:
            return (0, 0.0)

        return (len(comments), sum(len(c) for c in comments) / len(comments))

    @staticmethod
    def get_all_submitter_comment_stats(data: "MusicLeagueData") -> pd.DataFrame:
        """
        Get comment statistics for all submitters.

        Args:
            data: MusicLeagueData object

        Returns:
            DataFrame with columns: submitter_name, avg_length, comment_rate, total_comments
        """
        stats = []

        for submitter_id, submitter_info in data.competitors.items():
            submissions = [s for s in data.submissions if s['submitter_id'] == submitter_id]
            comments = [s.get('comment', '') for s in submissions]
            non_empty = [c for c in comments if c and c.strip()]

            avg_length, comment_rate = CommentMetrics.submitter_wordsmith_score(
                data, submitter_id
            )

            stats.append({
                'submitter_id': submitter_id,
                'submitter_name': submitter_info['name'],
                'avg_length': round(avg_length, 1),
                'comment_rate': round(comment_rate, 1),
                'total_comments': len(non_empty),
                'total_submissions': len(submissions),
            })

        df = pd.DataFrame(stats)
        if len(df) > 0:
            df = df.sort_values('avg_length', ascending=False)
        return df

    @staticmethod
    def get_all_voter_comment_stats(data: "MusicLeagueData") -> pd.DataFrame:
        """
        Get comment statistics for all voters.

        Args:
            data: MusicLeagueData object

        Returns:
            DataFrame with columns: voter_name, avg_length, comment_rate, total_comments
        """
        stats = []

        for voter_id, voter_info in data.competitors.items():
            votes = [v for v in data.votes if v['voter_id'] == voter_id and v['points'] > 0]
            comments = [v.get('comment', '') for v in votes]
            non_empty = [c for c in comments if c and c.strip()]

            avg_length, comment_rate = CommentMetrics.voter_critic_score(data, voter_id)

            stats.append({
                'voter_id': voter_id,
                'voter_name': voter_info['name'],
                'avg_length': round(avg_length, 1),
                'comment_rate': round(comment_rate, 1),
                'total_comments': len(non_empty),
                'total_votes': len(votes),
            })

        df = pd.DataFrame(stats)
        if len(df) > 0:
            df = df.sort_values('avg_length', ascending=False)
        return df

    @staticmethod
    def get_notable_comments(
        data: "MusicLeagueData",
        min_length: int = 50,
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        Find the longest/most notable comments for display.

        Args:
            data: MusicLeagueData object
            min_length: Minimum comment length to include
            top_n: Number of top comments to return

        Returns:
            DataFrame with columns: type, person, song, artist, comment, length
        """
        notable = []

        # Submission comments
        for sub in data.submissions:
            comment = sub.get('comment', '')
            if comment and len(comment.strip()) >= min_length:
                submitter = data.competitors.get(
                    sub['submitter_id'], {'name': 'Unknown'}
                )
                spotify_data = data.get_spotify_data(sub['spotify_uri'])
                notable.append({
                    'type': 'submission',
                    'person': submitter['name'],
                    'song': spotify_data['name'],
                    'artist': spotify_data['artist'],
                    'comment': comment.strip(),
                    'length': len(comment.strip()),
                    'round_id': sub['round_id'],
                })

        # Vote comments
        for vote in data.votes:
            comment = vote.get('comment', '')
            if comment and len(comment.strip()) >= min_length:
                voter = data.competitors.get(
                    vote['voter_id'], {'name': 'Unknown'}
                )
                spotify_data = data.get_spotify_data(vote['spotify_uri'])
                notable.append({
                    'type': 'vote',
                    'person': voter['name'],
                    'song': spotify_data['name'],
                    'artist': spotify_data['artist'],
                    'comment': comment.strip(),
                    'length': len(comment.strip()),
                    'points': vote['points'],
                    'round_id': vote['round_id'],
                })

        df = pd.DataFrame(notable)
        if len(df) > 0:
            df = df.sort_values('length', ascending=False).head(top_n)
        return df

    @staticmethod
    def comment_engagement_by_points(data: "MusicLeagueData") -> pd.DataFrame:
        """
        Analyze correlation between points given and comment engagement.

        Args:
            data: MusicLeagueData object

        Returns:
            DataFrame with columns: points, avg_comment_length, comment_rate, count
        """
        # Group votes by points
        from collections import defaultdict
        point_groups: Dict[int, List[str]] = defaultdict(list)

        for vote in data.votes:
            if vote['points'] > 0:
                comment = vote.get('comment', '')
                point_groups[vote['points']].append(comment)

        stats = []
        for points, comments in sorted(point_groups.items()):
            non_empty = [c for c in comments if c and c.strip()]
            avg_length = (
                sum(len(c) for c in non_empty) / len(non_empty)
                if non_empty else 0
            )
            comment_rate = (len(non_empty) / len(comments) * 100) if comments else 0

            stats.append({
                'points': points,
                'avg_comment_length': round(avg_length, 1),
                'comment_rate': round(comment_rate, 1),
                'count': len(comments),
            })

        return pd.DataFrame(stats)

    @staticmethod
    def submission_comment_vs_points(data: "MusicLeagueData") -> pd.DataFrame:
        """
        Analyze relationship between submission comment length and points received.

        Do songs with longer explanatory comments get more votes?

        Args:
            data: MusicLeagueData object

        Returns:
            DataFrame with columns: song, artist, submitter, comment_length,
                                   total_points, has_comment
        """
        from musicleague.metrics.songs import SongMetrics

        results = []

        for sub in data.submissions:
            comment = sub.get('comment', '')
            comment_length = len(comment.strip()) if comment else 0

            # Get total points for this submission
            total_points = SongMetrics.total_points(
                data, sub['spotify_uri'], sub['round_id']
            )

            spotify_data = data.get_spotify_data(sub['spotify_uri'])
            submitter = data.competitors.get(
                sub['submitter_id'], {'name': 'Unknown'}
            )

            results.append({
                'song': spotify_data['name'],
                'artist': spotify_data['artist'],
                'submitter': submitter['name'],
                'comment_length': comment_length,
                'total_points': total_points,
                'has_comment': comment_length > 0,
                'round_id': sub['round_id'],
            })

        return pd.DataFrame(results)

    @staticmethod
    def comment_length_correlation(data: "MusicLeagueData") -> Dict[str, float]:
        """
        Calculate correlation between submission comment length and points.

        Args:
            data: MusicLeagueData object

        Returns:
            Dictionary with correlation stats
        """
        import numpy as np

        df = CommentMetrics.submission_comment_vs_points(data)

        if len(df) < 3:
            return {'correlation': 0.0, 'avg_points_with_comment': 0.0,
                    'avg_points_without_comment': 0.0, 'difference': 0.0}

        # Calculate correlation
        correlation = np.corrcoef(
            df['comment_length'], df['total_points']
        )[0, 1] if len(df) > 1 else 0.0

        # Compare averages
        with_comment = df[df['has_comment']]
        without_comment = df[~df['has_comment']]

        avg_with = with_comment['total_points'].mean() if len(with_comment) > 0 else 0
        avg_without = without_comment['total_points'].mean() if len(without_comment) > 0 else 0

        return {
            'correlation': float(correlation) if not np.isnan(correlation) else 0.0,
            'avg_points_with_comment': round(avg_with, 2),
            'avg_points_without_comment': round(avg_without, 2),
            'difference': round(avg_with - avg_without, 2),
            'pct_with_comment': round(len(with_comment) / len(df) * 100, 1) if len(df) > 0 else 0,
        }
