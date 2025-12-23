"""
Helper functions for the Soundwave Smackdown dashboard.
Provides data loading, processing, and utility functions.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any

from musicleague.config import PathConfig, get_available_leagues
from musicleague.data.loader import MusicLeagueData
from musicleague.data.cache import CacheManager
from musicleague.metrics.songs import SongMetrics
from musicleague.metrics.voters import VoterMetrics
from musicleague.metrics.submitters import SubmitterMetrics
from musicleague.metrics.network import NetworkMetrics


@st.cache_data
def load_preprocessed_data(league_name: str) -> Dict[str, Any]:
    """
    Load preprocessed league data from cache.

    Args:
        league_name: Name of the league directory

    Returns:
        Dictionary containing all preprocessed data
    """
    cache_manager = CacheManager()
    data = cache_manager.load(league_name)
    
    if data is None:
        st.error(f"""
        ❌ **Preprocessed data not found for {league_name}**

        Please run the preprocessing script first:

        ```bash
        python -m musicleague.scripts.preprocess {league_name}
        ```

        Or preprocess all leagues:

        ```bash
        python -m musicleague.scripts.preprocess --all
        ```
        """)
        st.stop()
    
    return data


@st.cache_data
def load_league_data(league_name: str) -> MusicLeagueData:
    """
    Load league data from preprocessed cache.
    Reconstructs a MusicLeagueData-like object from cached data.

    Args:
        league_name: Name of the league directory

    Returns:
        MusicLeagueData object (reconstructed from cache)
    """
    preprocessed = load_preprocessed_data(league_name)

    # Create a minimal MusicLeagueData object from cached data
    data = MusicLeagueData.__new__(MusicLeagueData)
    data.league_name = league_name
    data.competitors = preprocessed['raw_data']['competitors']
    data.submissions = preprocessed['raw_data']['submissions']
    data.votes = preprocessed['raw_data']['votes']
    data.rounds = preprocessed['raw_data']['rounds']
    data.spotify_data = preprocessed['raw_data']['spotify_data']
    data._spotify = None  # Don't fetch new data

    return data


def get_league_summary_stats(data: MusicLeagueData) -> Dict[str, Any]:
    """
    Get high-level summary statistics for a league.

    Args:
        data: MusicLeagueData object

    Returns:
        Dictionary of summary statistics
    """
    song_df = SongMetrics.get_all_song_metrics(data)

    return {
        'total_competitors': len(data.competitors),
        'total_submissions': len(data.submissions),
        'total_votes': len([v for v in data.votes if v['points'] > 0]),
        'total_rounds': len(data.rounds),
        'avg_controversy': song_df['controversy_score'].mean() if len(song_df) > 0 else 0,
        'avg_spotify_popularity': song_df['spotify_popularity'].mean() if len(song_df) > 0 else 0,
        'avg_points_per_song': song_df['total_points'].mean() if len(song_df) > 0 else 0,
        'top_song': song_df.iloc[0] if len(song_df) > 0 else None,
    }


def get_top_songs(data: MusicLeagueData, n: int = 20) -> pd.DataFrame:
    """
    Get top N songs formatted for display.

    Args:
        data: MusicLeagueData object
        n: Number of top songs to return

    Returns:
        DataFrame with top songs
    """
    song_df = SongMetrics.get_all_song_metrics(data)

    if len(song_df) == 0:
        return pd.DataFrame()

    display_df = song_df.head(n)[[
        'song_name', 'artist', 'submitter', 'total_points',
        'controversy_score', 'spotify_popularity'
    ]].copy()
    display_df.columns = ['Song', 'Artist', 'Submitted By', 'Points', 'Controversy', 'Spotify Pop']
    display_df['Rank'] = range(1, len(display_df) + 1)
    display_df = display_df[['Rank', 'Song', 'Artist', 'Submitted By', 'Points', 'Controversy', 'Spotify Pop']]

    return display_df


def get_most_controversial_songs(data: MusicLeagueData, n: int = 10) -> pd.DataFrame:
    """
    Get most controversial songs formatted for display.

    Args:
        data: MusicLeagueData object
        n: Number of songs to return

    Returns:
        DataFrame with most controversial songs
    """
    song_df = SongMetrics.get_all_song_metrics(data)

    if len(song_df) == 0:
        return pd.DataFrame()

    controversial = song_df.nlargest(n, 'controversy_score')
    display_df = controversial[['song_name', 'artist', 'submitter', 'total_points', 'controversy_score']].copy()
    display_df.columns = ['Song', 'Artist', 'Submitted By', 'Points', 'Controversy σ']

    return display_df


def get_hidden_gems(data: MusicLeagueData, n: int = 10) -> pd.DataFrame:
    """
    Get hidden gems (high obscurity score) formatted for display.

    Args:
        data: MusicLeagueData object
        n: Number of songs to return

    Returns:
        DataFrame with hidden gems
    """
    song_df = SongMetrics.get_all_song_metrics(data)

    if len(song_df) == 0:
        return pd.DataFrame()

    gems = song_df.nlargest(n, 'obscurity_score')
    display_df = gems[[
        'song_name', 'artist', 'submitter', 'total_points',
        'spotify_popularity', 'obscurity_score'
    ]].copy()
    display_df.columns = ['Song', 'Artist', 'Submitted By', 'Points', 'Spotify Pop', 'Deep Cut Cred']

    return display_df


def get_submitter_rankings(data: MusicLeagueData) -> pd.DataFrame:
    """
    Get submitter rankings formatted for display.

    Args:
        data: MusicLeagueData object

    Returns:
        DataFrame with submitter rankings
    """
    submitter_stats = []

    for submitter_id, submitter_data in data.competitors.items():
        avg_points = SubmitterMetrics.average_points_per_submission(data, submitter_id)
        if avg_points > 0:
            avg, std = SubmitterMetrics.consistency_score(data, submitter_id)
            underdog = SubmitterMetrics.underdog_factor(data, submitter_id)

            submitter_stats.append({
                'Submitter': submitter_data['name'],
                'A&R Score': round(avg_points, 2),
                'Consistency': round(std, 2),
                'Deep Cut Cred': round(underdog, 2),
            })

    df = pd.DataFrame(submitter_stats)
    if len(df) > 0:
        df = df.sort_values('A&R Score', ascending=False)
        df['Rank'] = range(1, len(df) + 1)
        df = df[['Rank', 'Submitter', 'A&R Score', 'Consistency', 'Deep Cut Cred']]

    return df


def get_voter_rankings(data: MusicLeagueData) -> pd.DataFrame:
    """
    Get voter rankings formatted for display.

    Args:
        data: MusicLeagueData object

    Returns:
        DataFrame with voter rankings
    """
    voter_stats = []

    for voter_id, voter_data in data.competitors.items():
        golden_ear = VoterMetrics.golden_ear_score(data, voter_id)
        hipster = VoterMetrics.hipster_score(data, voter_id)
        generosity, _ = VoterMetrics.generosity_score(data, voter_id)

        voter_stats.append({
            'Voter': voter_data['name'],
            'Trendsetter': round(golden_ear, 3),
            'Obscurity Cred': round(hipster, 2),
            'Generosity': round(generosity, 2),
        })

    df = pd.DataFrame(voter_stats)
    if len(df) > 0:
        df = df.sort_values('Trendsetter', ascending=False)

    return df


def get_influence_rankings(data: MusicLeagueData, n: int = 15) -> pd.DataFrame:
    """
    Get influence (PageRank) rankings formatted for display.

    Args:
        data: MusicLeagueData object
        n: Number of top influencers to return

    Returns:
        DataFrame with influence rankings
    """
    influence = NetworkMetrics.influence_score(data)

    influence_list = [
        {'Voter': name, 'Clout Score': round(score, 4)}
        for name, score in influence.items()
    ]

    df = pd.DataFrame(influence_list)
    if len(df) > 0:
        df = df.sort_values('Clout Score', ascending=False).head(n)
        df['Rank'] = range(1, len(df) + 1)
        df = df[['Rank', 'Voter', 'Clout Score']]

    return df


def create_comparison_metrics(data1: MusicLeagueData, data2: MusicLeagueData) -> pd.DataFrame:
    """
    Create a comparison table of key metrics between two leagues.

    Args:
        data1: First league data
        data2: Second league data

    Returns:
        DataFrame comparing key metrics
    """
    stats1 = get_league_summary_stats(data1)
    stats2 = get_league_summary_stats(data2)

    comparison = []

    metrics_to_compare = [
        ('total_competitors', 'Roster Size'),
        ('total_submissions', 'Tracks Dropped'),
        ('total_votes', 'Fan Fervor'),
        ('total_rounds', 'Rounds Fought'),
        ('avg_controversy', 'Avg Controversy'),
        ('avg_spotify_popularity', 'Avg Spotify Pop'),
        ('avg_points_per_song', 'Avg Points/Song'),
    ]

    for key, display_name in metrics_to_compare:
        val1 = stats1[key]
        val2 = stats2[key]
        delta = val2 - val1
        delta_pct = (delta / val1 * 100) if val1 != 0 else 0

        comparison.append({
            'Metric': display_name,
            'League 1': round(val1, 2) if isinstance(val1, float) else val1,
            'League 2': round(val2, 2) if isinstance(val2, float) else val2,
            'Δ': f"{delta:+.2f}" if isinstance(delta, float) else f"{delta:+d}",
            'Δ %': f"{delta_pct:+.1f}%" if delta_pct != 0 else "-",
        })

    return pd.DataFrame(comparison)


def calculate_weighted_score(data: MusicLeagueData, weights: Dict[str, float]) -> float:
    """
    Calculate a weighted final score for a league based on user preferences.

    Args:
        data: MusicLeagueData object
        weights: Dictionary of metric weights (0-100)

    Returns:
        Weighted score (0-100 scale)
    """
    import numpy as np
    from musicleague.metrics.voters import VoterMetrics
    from musicleague.metrics.network import NetworkMetrics

    stats = get_league_summary_stats(data)

    # Calculate real taste score (avg golden ear)
    golden_ears = [
        VoterMetrics.golden_ear_score(data, vid)
        for vid in data.competitors.keys()
    ]
    avg_golden_ear = np.mean(golden_ears) if golden_ears else 0
    taste_score = (avg_golden_ear + 1) / 2 * 100  # Normalize -1 to 1 → 0 to 100

    # Calculate real clout score (network balance)
    influence = NetworkMetrics.influence_score(data)
    var_influence = np.var(list(influence.values())) if influence else 0
    clout_score = max(0, 100 - var_influence * 10000)

    normalized_metrics = {
        'mainstream_hits': min(stats['avg_points_per_song'] / 15 * 100, 100),
        'deep_cuts': 100 - min(stats['avg_spotify_popularity'], 100),  # Inverse of popularity
        'taste': taste_score,
        'controversy': min(stats['avg_controversy'] / 2 * 100, 100),
        'clout': clout_score,
    }

    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0

    score = 0
    for metric, weight in weights.items():
        if metric in normalized_metrics:
            score += normalized_metrics[metric] * (weight / total_weight)

    return score


def get_league_champion(data: MusicLeagueData) -> Optional[Dict]:
    """
    Get the top song (champion) of a league.

    Args:
        data: MusicLeagueData object

    Returns:
        Dictionary with champion info or None
    """
    song_df = SongMetrics.get_all_song_metrics(data)

    if len(song_df) == 0:
        return None

    champion = song_df.iloc[0]
    return {
        'song': champion['song_name'],
        'artist': champion['artist'],
        'points': champion['total_points'],
        'submitter': champion['submitter'],
        'controversy': champion['controversy_score'],
        'popularity': champion['spotify_popularity'],
    }


def get_player_champion(data: MusicLeagueData) -> Optional[Dict]:
    """
    Get the winning player (most total points) of a league.

    Args:
        data: MusicLeagueData object

    Returns:
        Dictionary with player champion info or None
    """
    from musicleague.metrics.comparisons import CrossRoundMetrics

    song_df = SongMetrics.get_all_song_metrics(data)

    if len(song_df) == 0:
        return None

    # Calculate total points per submitter
    submitter_points = song_df.groupby('submitter').agg({
        'total_points': 'sum',
        'song_name': 'count'  # number of submissions
    }).reset_index()
    submitter_points.columns = ['submitter', 'total_points', 'submissions']
    submitter_points = submitter_points.sort_values('total_points', ascending=False)

    if len(submitter_points) == 0:
        return None

    champion = submitter_points.iloc[0]

    # Count round wins for this player
    rankings_df = CrossRoundMetrics.round_rankings(data)
    round_wins = 0
    if len(rankings_df) > 0:
        wins = rankings_df[(rankings_df['submitter'] == champion['submitter']) & (rankings_df['rank'] == 1)]
        round_wins = len(wins)

    avg_points = champion['total_points'] / champion['submissions'] if champion['submissions'] > 0 else 0

    return {
        'name': champion['submitter'],
        'total_points': int(champion['total_points']),
        'submissions': int(champion['submissions']),
        'round_wins': round_wins,
        'avg_points': round(avg_points, 1),
    }


# Comment-related helpers

def get_wordsmith_rankings(data: MusicLeagueData) -> pd.DataFrame:
    """
    Get submitters ranked by comment engagement.

    Args:
        data: MusicLeagueData object

    Returns:
        DataFrame with submitter comment stats
    """
    from musicleague.metrics.comments import CommentMetrics

    stats_df = CommentMetrics.get_all_submitter_comment_stats(data)

    if len(stats_df) == 0:
        return pd.DataFrame()

    display_df = stats_df[[
        'submitter_name', 'avg_length', 'comment_rate', 'total_comments'
    ]].copy()
    display_df.columns = ['Submitter', 'Avg Length', 'Comment Rate %', 'Total Comments']
    display_df['Rank'] = range(1, len(display_df) + 1)
    display_df = display_df[['Rank', 'Submitter', 'Avg Length', 'Comment Rate %', 'Total Comments']]

    return display_df


def get_critic_rankings(data: MusicLeagueData) -> pd.DataFrame:
    """
    Get voters ranked by comment engagement.

    Args:
        data: MusicLeagueData object

    Returns:
        DataFrame with voter comment stats
    """
    from musicleague.metrics.comments import CommentMetrics

    stats_df = CommentMetrics.get_all_voter_comment_stats(data)

    if len(stats_df) == 0:
        return pd.DataFrame()

    display_df = stats_df[[
        'voter_name', 'avg_length', 'comment_rate', 'total_comments'
    ]].copy()
    display_df.columns = ['Voter', 'Avg Length', 'Comment Rate %', 'Total Comments']
    display_df['Rank'] = range(1, len(display_df) + 1)
    display_df = display_df[['Rank', 'Voter', 'Avg Length', 'Comment Rate %', 'Total Comments']]

    return display_df


def get_best_comments(data: MusicLeagueData, n: int = 10) -> pd.DataFrame:
    """
    Get top N most notable comments.

    Args:
        data: MusicLeagueData object
        n: Number of comments to return

    Returns:
        DataFrame with notable comments
    """
    from musicleague.metrics.comments import CommentMetrics

    return CommentMetrics.get_notable_comments(data, min_length=20, top_n=n)


# Trends-related helpers

def get_round_by_round_performance(data: MusicLeagueData) -> pd.DataFrame:
    """
    Get performance data formatted for trend charts.

    Args:
        data: MusicLeagueData object

    Returns:
        DataFrame with columns: round_id, round_index, submitter, cumulative_points
    """
    from musicleague.metrics.comparisons import CrossRoundMetrics

    rows = []

    for submitter_id, submitter_info in data.competitors.items():
        cumulative = CrossRoundMetrics.cumulative_points_by_round(data, submitter_id)

        for i, round_id in enumerate(data.rounds):
            rows.append({
                'round_id': round_id,
                'round_index': i + 1,
                'submitter_id': submitter_id,
                'submitter': submitter_info['name'],
                'cumulative_points': cumulative.get(round_id, 0),
            })

    return pd.DataFrame(rows)


def get_momentum_rankings(data: MusicLeagueData) -> pd.DataFrame:
    """
    Get players ranked by momentum (improving vs declining).

    Args:
        data: MusicLeagueData object

    Returns:
        DataFrame with momentum rankings
    """
    from musicleague.metrics.comparisons import CrossRoundMetrics

    momentum_df = CrossRoundMetrics.get_all_momentum_scores(data)

    if len(momentum_df) == 0:
        return pd.DataFrame()

    display_df = momentum_df[[
        'submitter', 'momentum', 'trend', 'current_streak', 'max_streak'
    ]].copy()
    display_df.columns = ['Player', 'Momentum', 'Trend', 'Current Streak', 'Best Streak']
    display_df['Rank'] = range(1, len(display_df) + 1)
    display_df = display_df[['Rank', 'Player', 'Momentum', 'Trend', 'Current Streak', 'Best Streak']]

    return display_df


def get_player_round_scores(data: MusicLeagueData, player_name: str) -> pd.DataFrame:
    """
    Get round-by-round scores for a specific player.

    Args:
        data: MusicLeagueData object
        player_name: Name of the player

    Returns:
        DataFrame with columns: round_num, points, cumulative_points
    """
    from musicleague.metrics.songs import SongMetrics

    # Find submitter_id by name
    submitter_id = None
    for sid, info in data.competitors.items():
        if info['name'] == player_name:
            submitter_id = sid
            break

    if submitter_id is None:
        return pd.DataFrame()

    rows = []
    cumulative = 0

    for i, round_id in enumerate(data.rounds):
        submissions = [
            s for s in data.submissions
            if s['submitter_id'] == submitter_id and s['round_id'] == round_id
        ]

        if submissions:
            points = sum(
                SongMetrics.total_points(data, s['spotify_uri'], round_id)
                for s in submissions
            )
            cumulative += points
            rows.append({
                'round_num': i + 1,
                'round_id': round_id,
                'points': points,
                'cumulative_points': cumulative,
            })

    df = pd.DataFrame(rows)

    if len(df) > 0:
        # Add first/second half markers
        midpoint = len(df) // 2
        df['half'] = ['First Half' if i < midpoint else 'Second Half' for i in range(len(df))]

    return df


def get_player_arcs(data: MusicLeagueData) -> pd.DataFrame:
    """
    Get player arc data formatted for display.

    Each player is assigned a music-themed arc type based on their
    performance trajectory:
    - Headliner: Top performer with consistent results
    - Opening Act: Started strong but faded
    - Encore: Weak start but strong finish
    - Crowd Favorite: Steady, reliable
    - One-Hit Wonder: One standout round
    - Wild Card: High variance, unpredictable

    Args:
        data: MusicLeagueData object

    Returns:
        DataFrame with player arc data
    """
    from musicleague.metrics.comparisons import CrossRoundMetrics

    arcs_df = CrossRoundMetrics.get_all_player_arcs(data)

    if len(arcs_df) == 0:
        return pd.DataFrame()

    display_df = arcs_df[[
        'submitter', 'arc_type', 'avg_points', 'consistency',
        'finishing_strength', 'peak_round', 'peak_points'
    ]].copy()
    display_df.columns = [
        'Player', 'Arc', 'Avg Points', 'Consistency',
        'Finish Strength', 'Peak Round', 'Peak Points'
    ]

    return display_df


def get_round_champions(data: MusicLeagueData) -> pd.DataFrame:
    """
    Get the winner of each round.

    Args:
        data: MusicLeagueData object

    Returns:
        DataFrame with round winners
    """
    from musicleague.metrics.comparisons import CrossRoundMetrics

    rankings_df = CrossRoundMetrics.round_rankings(data)

    if len(rankings_df) == 0:
        return pd.DataFrame()

    # Filter to rank 1 only
    winners = rankings_df[rankings_df['rank'] == 1].copy()
    winners['Round'] = range(1, len(winners) + 1)
    winners = winners[['Round', 'submitter', 'song', 'artist', 'points']]
    winners.columns = ['Round', 'Winner', 'Song', 'Artist', 'Points']

    return winners


# Re-export get_available_leagues for convenience
__all__ = [
    "load_preprocessed_data",
    "load_league_data",
    "get_available_leagues",
    "get_league_summary_stats",
    "get_top_songs",
    "get_most_controversial_songs",
    "get_hidden_gems",
    "get_submitter_rankings",
    "get_voter_rankings",
    "get_influence_rankings",
    "create_comparison_metrics",
    "calculate_weighted_score",
    "get_league_champion",
    "get_player_champion",
    # Comment helpers
    "get_wordsmith_rankings",
    "get_critic_rankings",
    "get_best_comments",
    # Trends helpers
    "get_round_by_round_performance",
    "get_momentum_rankings",
    "get_player_arcs",
    "get_player_round_scores",
    "get_round_champions",
]

