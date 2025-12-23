"""
Cross-round and cross-league comparison metrics.

Provides metrics for comparing performance across multiple rounds
within a league or across different leagues.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from musicleague.data.loader import MusicLeagueData

from musicleague.metrics.songs import SongMetrics
from musicleague.metrics.voters import VoterMetrics
from musicleague.metrics.submitters import SubmitterMetrics


class CrossRoundMetrics:
    """Metrics comparing performance across multiple rounds."""

    @staticmethod
    def submitter_performance_trajectory(
        data: "MusicLeagueData",
        submitter_id: str,
        round_ids: List[str]
    ) -> Dict[str, float]:
        """
        Calculate average points per round for a submitter.
        
        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter
            round_ids: List of round IDs to analyze
            
        Returns:
            Dictionary mapping round_id to average points
        """
        trajectory = {}
        for round_id in round_ids:
            avg_points = SubmitterMetrics.average_points_per_submission(
                data, submitter_id, round_id
            )
            trajectory[round_id] = avg_points
        return trajectory

    @staticmethod
    def voter_consistency_across_rounds(
        data: "MusicLeagueData",
        voter_id: str,
        round_ids: List[str]
    ) -> Dict[str, Tuple[float, float]]:
        """
        Calculate voter generosity stats per round.
        
        Args:
            data: MusicLeagueData object
            voter_id: ID of the voter
            round_ids: List of round IDs to analyze
            
        Returns:
            Dictionary mapping round_id to (mean, std_dev)
        """
        consistency = {}
        for round_id in round_ids:
            stats = VoterMetrics.generosity_score(data, voter_id, round_id)
            consistency[round_id] = stats
        return consistency

    @staticmethod
    def round_competitiveness(
        data: "MusicLeagueData",
        round_id: str
    ) -> Dict[str, float]:
        """
        Calculate competitiveness metrics for a round.

        Higher variance indicates more competitive rounds where
        scores were spread out rather than clustered.

        Args:
            data: MusicLeagueData object
            round_id: ID of the round

        Returns:
            Dictionary with variance, std dev, and average stats
        """
        votes = [
            v['points'] for v in data.votes
            if v['round_id'] == round_id and v['points'] > 0
        ]

        song_uris = set(
            s['spotify_uri'] for s in data.submissions
            if s['round_id'] == round_id
        )
        song_scores = [
            SongMetrics.total_points(data, uri, round_id)
            for uri in song_uris
        ]

        return {
            'vote_variance': float(np.var(votes)) if votes else 0.0,
            'vote_std': float(np.std(votes)) if votes else 0.0,
            'score_variance': float(np.var(song_scores)) if song_scores else 0.0,
            'score_std': float(np.std(song_scores)) if song_scores else 0.0,
            'avg_score': float(np.mean(song_scores)) if song_scores else 0.0
        }

    @staticmethod
    def cumulative_points_by_round(
        data: "MusicLeagueData",
        submitter_id: str
    ) -> Dict[str, int]:
        """
        Calculate cumulative points per round for a submitter.

        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter

        Returns:
            Dictionary mapping round_id to cumulative points
        """
        cumulative = {}
        running_total = 0

        for round_id in data.rounds:
            # Get submissions for this submitter in this round
            submissions = [
                s for s in data.submissions
                if s['submitter_id'] == submitter_id and s['round_id'] == round_id
            ]

            round_points = 0
            for sub in submissions:
                round_points += SongMetrics.total_points(
                    data, sub['spotify_uri'], round_id
                )

            running_total += round_points
            cumulative[round_id] = running_total

        return cumulative

    @staticmethod
    def round_rankings(data: "MusicLeagueData") -> pd.DataFrame:
        """
        Get rankings for each round - who won and placement.

        Args:
            data: MusicLeagueData object

        Returns:
            DataFrame with columns: round_id, submitter, song, artist, points, rank
        """
        rankings = []

        for round_id in data.rounds:
            round_submissions = [
                s for s in data.submissions if s['round_id'] == round_id
            ]

            round_scores = []
            for sub in round_submissions:
                points = SongMetrics.total_points(data, sub['spotify_uri'], round_id)
                spotify_data = data.get_spotify_data(sub['spotify_uri'])
                submitter = data.competitors.get(
                    sub['submitter_id'], {'name': 'Unknown'}
                )
                round_scores.append({
                    'round_id': round_id,
                    'submitter_id': sub['submitter_id'],
                    'submitter': submitter['name'],
                    'song': spotify_data['name'],
                    'artist': spotify_data['artist'],
                    'points': points,
                })

            # Sort by points and assign ranks
            round_scores.sort(key=lambda x: x['points'], reverse=True)
            for i, score in enumerate(round_scores):
                score['rank'] = i + 1
                rankings.append(score)

        return pd.DataFrame(rankings)

    @staticmethod
    def momentum_score(
        data: "MusicLeagueData",
        submitter_id: str
    ) -> float:
        """
        Calculate momentum (trend indicator) for a submitter.

        Positive = improving over time, negative = declining.
        Uses linear regression slope of normalized round scores.

        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter

        Returns:
            Momentum score (positive = improving, negative = declining)
        """
        round_scores = []

        for i, round_id in enumerate(data.rounds):
            submissions = [
                s for s in data.submissions
                if s['submitter_id'] == submitter_id and s['round_id'] == round_id
            ]

            if submissions:
                total = sum(
                    SongMetrics.total_points(data, s['spotify_uri'], round_id)
                    for s in submissions
                )
                round_scores.append((i, total))

        if len(round_scores) < 2:
            return 0.0

        # Calculate linear regression slope
        x = np.array([s[0] for s in round_scores])
        y = np.array([s[1] for s in round_scores])

        # Normalize y to 0-1 range for comparable momentum across players
        y_range = y.max() - y.min()
        if y_range > 0:
            y_norm = (y - y.min()) / y_range
        else:
            return 0.0

        # Simple linear regression: slope = cov(x,y) / var(x)
        if np.var(x) == 0:
            return 0.0

        slope = np.cov(x, y_norm)[0, 1] / np.var(x)
        return float(slope)

    @staticmethod
    def hot_streak_detection(
        data: "MusicLeagueData",
        submitter_id: str,
        top_n: int = 3
    ) -> Dict:
        """
        Detect hot streaks (consecutive top-N finishes).

        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter
            top_n: What counts as a "top" finish (default: top 3)

        Returns:
            Dictionary with streak info: current_streak, max_streak, total_top_finishes
        """
        rankings_df = CrossRoundMetrics.round_rankings(data)

        if len(rankings_df) == 0:
            return {'current_streak': 0, 'max_streak': 0, 'total_top_finishes': 0}

        # Filter to this submitter
        submitter_ranks = rankings_df[
            rankings_df['submitter_id'] == submitter_id
        ].sort_values('round_id')

        if len(submitter_ranks) == 0:
            return {'current_streak': 0, 'max_streak': 0, 'total_top_finishes': 0}

        # Check if each round was a top-N finish
        top_finishes = (submitter_ranks['rank'] <= top_n).tolist()

        # Calculate streaks
        current_streak = 0
        max_streak = 0
        temp_streak = 0

        for is_top in top_finishes:
            if is_top:
                temp_streak += 1
                max_streak = max(max_streak, temp_streak)
            else:
                temp_streak = 0

        # Current streak is the last consecutive run
        for is_top in reversed(top_finishes):
            if is_top:
                current_streak += 1
            else:
                break

        return {
            'current_streak': current_streak,
            'max_streak': max_streak,
            'total_top_finishes': sum(top_finishes),
        }

    @staticmethod
    def get_all_momentum_scores(data: "MusicLeagueData") -> pd.DataFrame:
        """
        Get momentum scores for all submitters.

        Args:
            data: MusicLeagueData object

        Returns:
            DataFrame with columns: submitter, momentum, trend
        """
        scores = []

        for submitter_id, submitter_info in data.competitors.items():
            momentum = CrossRoundMetrics.momentum_score(data, submitter_id)
            streak_info = CrossRoundMetrics.hot_streak_detection(data, submitter_id)

            if momentum > 0.1:
                trend = "Rising"
            elif momentum < -0.1:
                trend = "Falling"
            else:
                trend = "Steady"

            scores.append({
                'submitter_id': submitter_id,
                'submitter': submitter_info['name'],
                'momentum': round(momentum, 3),
                'trend': trend,
                'current_streak': streak_info['current_streak'],
                'max_streak': streak_info['max_streak'],
            })

        df = pd.DataFrame(scores)
        if len(df) > 0:
            df = df.sort_values('momentum', ascending=False)
        return df

    # =========================================================================
    # Player Arc Metrics (retrospective analysis for completed leagues)
    # =========================================================================

    @staticmethod
    def _get_round_scores(
        data: "MusicLeagueData",
        submitter_id: str
    ) -> List[Tuple[int, str, int]]:
        """
        Get list of (round_index, round_id, points) for a submitter.

        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter

        Returns:
            List of tuples (round_index, round_id, points)
        """
        round_scores = []

        for i, round_id in enumerate(data.rounds):
            submissions = [
                s for s in data.submissions
                if s['submitter_id'] == submitter_id and s['round_id'] == round_id
            ]

            if submissions:
                total = sum(
                    SongMetrics.total_points(data, s['spotify_uri'], round_id)
                    for s in submissions
                )
                round_scores.append((i, round_id, total))

        return round_scores

    @staticmethod
    def finishing_strength(
        data: "MusicLeagueData",
        submitter_id: str
    ) -> float:
        """
        Calculate finishing strength: second half avg minus first half avg.

        Positive = finished stronger than started.
        Negative = started stronger than finished.

        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter

        Returns:
            Finishing strength score (positive = strong finish)
        """
        round_scores = CrossRoundMetrics._get_round_scores(data, submitter_id)

        if len(round_scores) < 2:
            return 0.0

        midpoint = len(round_scores) // 2
        first_half = [s[2] for s in round_scores[:midpoint]]
        second_half = [s[2] for s in round_scores[midpoint:]]

        first_avg = np.mean(first_half) if first_half else 0
        second_avg = np.mean(second_half) if second_half else 0

        return float(second_avg - first_avg)

    @staticmethod
    def peak_round(
        data: "MusicLeagueData",
        submitter_id: str
    ) -> Dict:
        """
        Find the player's best single round.

        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter

        Returns:
            Dict with round_num (1-indexed), round_id, and points
        """
        round_scores = CrossRoundMetrics._get_round_scores(data, submitter_id)

        if not round_scores:
            return {'round_num': 0, 'round_id': None, 'points': 0}

        best = max(round_scores, key=lambda x: x[2])
        return {
            'round_num': best[0] + 1,  # 1-indexed for display
            'round_id': best[1],
            'points': best[2]
        }

    @staticmethod
    def best_stretch(
        data: "MusicLeagueData",
        submitter_id: str,
        window: int = 3
    ) -> Dict:
        """
        Find the best consecutive N-round stretch.

        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter
            window: Number of consecutive rounds (default 3)

        Returns:
            Dict with start_round (1-indexed), avg_points, total_points
        """
        round_scores = CrossRoundMetrics._get_round_scores(data, submitter_id)

        if len(round_scores) < window:
            if round_scores:
                total = sum(s[2] for s in round_scores)
                return {
                    'start_round': 1,
                    'avg_points': total / len(round_scores),
                    'total_points': total
                }
            return {'start_round': 0, 'avg_points': 0, 'total_points': 0}

        best_start = 0
        best_total = 0

        for i in range(len(round_scores) - window + 1):
            stretch_total = sum(s[2] for s in round_scores[i:i + window])
            if stretch_total > best_total:
                best_total = stretch_total
                best_start = i

        return {
            'start_round': best_start + 1,  # 1-indexed
            'avg_points': best_total / window,
            'total_points': best_total
        }

    @staticmethod
    def player_arc_type(
        data: "MusicLeagueData",
        submitter_id: str,
        all_stats: Optional[Dict] = None
    ) -> str:
        """
        Categorize the player's journey with a music-themed arc type.

        Arc types:
        - Headliner: Top performer with consistent results
        - Opening Act: Started strong but faded
        - Encore: Weak start but strong finish
        - Crowd Favorite: Steady, reliable (low variance)
        - One-Hit Wonder: One standout round
        - Wild Card: High variance, unpredictable

        Args:
            data: MusicLeagueData object
            submitter_id: ID of the submitter
            all_stats: Optional pre-computed stats dict with 'avg_points',
                      'consistency', 'finishing_strength', 'peak_points'

        Returns:
            Arc type string
        """
        # Get player stats
        if all_stats:
            avg_points = all_stats.get('avg_points', 0)
            consistency = all_stats.get('consistency', 0)
            finish_strength = all_stats.get('finishing_strength', 0)
            peak_points = all_stats.get('peak_points', 0)
        else:
            avg_points, consistency = SubmitterMetrics.consistency_score(
                data, submitter_id
            )
            finish_strength = CrossRoundMetrics.finishing_strength(
                data, submitter_id
            )
            peak_info = CrossRoundMetrics.peak_round(data, submitter_id)
            peak_points = peak_info['points']

        # Need league-wide context for percentile calculations
        all_avgs = []
        all_consistencies = []
        for sid in data.competitors.keys():
            avg, std = SubmitterMetrics.consistency_score(data, sid)
            if avg > 0:  # Only count active players
                all_avgs.append(avg)
                all_consistencies.append(std)

        if not all_avgs:
            return "Wild Card"

        avg_percentile = (
            sum(1 for a in all_avgs if a < avg_points) / len(all_avgs)
        )
        consistency_percentile = (
            sum(1 for c in all_consistencies if c < consistency)
            / len(all_consistencies)
        )

        # Classification logic
        # Headliner: Top 25% avg AND low variance (consistency below median)
        if avg_percentile >= 0.75 and consistency_percentile < 0.5:
            return "Headliner"

        # One-Hit Wonder: Peak round > 2x their average
        if avg_points > 0 and peak_points > avg_points * 2:
            return "One-Hit Wonder"

        # Opening Act: First half significantly better (negative finish strength)
        if finish_strength < -avg_points * 0.3:
            return "Opening Act"

        # Encore: Second half significantly better (positive finish strength)
        if finish_strength > avg_points * 0.3:
            return "Encore"

        # Crowd Favorite: Low variance (bottom 25%) but not a headliner
        if consistency_percentile < 0.25:
            return "Crowd Favorite"

        # Wild Card: High variance (top 25%)
        if consistency_percentile >= 0.75:
            return "Wild Card"

        # Default to Crowd Favorite for middle-of-the-road players
        return "Crowd Favorite"

    @staticmethod
    def get_all_player_arcs(data: "MusicLeagueData") -> pd.DataFrame:
        """
        Get player arc data for all submitters.

        Args:
            data: MusicLeagueData object

        Returns:
            DataFrame with columns: submitter, arc_type, avg_points,
            consistency, finishing_strength, peak_round, peak_points,
            best_stretch_start, best_stretch_avg
        """
        arcs = []

        for submitter_id, submitter_info in data.competitors.items():
            avg_points, consistency = SubmitterMetrics.consistency_score(
                data, submitter_id
            )

            if avg_points == 0:
                continue  # Skip players with no submissions

            finish_strength = CrossRoundMetrics.finishing_strength(
                data, submitter_id
            )
            peak_info = CrossRoundMetrics.peak_round(data, submitter_id)
            stretch_info = CrossRoundMetrics.best_stretch(data, submitter_id)

            # Pre-compute stats for arc type calculation
            stats = {
                'avg_points': avg_points,
                'consistency': consistency,
                'finishing_strength': finish_strength,
                'peak_points': peak_info['points']
            }
            arc_type = CrossRoundMetrics.player_arc_type(
                data, submitter_id, all_stats=stats
            )

            arcs.append({
                'submitter_id': submitter_id,
                'submitter': submitter_info['name'],
                'arc_type': arc_type,
                'avg_points': round(avg_points, 1),
                'consistency': round(consistency, 1),
                'finishing_strength': round(finish_strength, 1),
                'peak_round': peak_info['round_num'],
                'peak_points': peak_info['points'],
                'best_stretch_start': stretch_info['start_round'],
                'best_stretch_avg': round(stretch_info['avg_points'], 1),
            })

        df = pd.DataFrame(arcs)
        if len(df) > 0:
            # Sort by avg_points descending
            df = df.sort_values('avg_points', ascending=False)
        return df


class CrossLeagueMetrics:
    """Metrics comparing performance across different leagues."""

    @staticmethod
    def submitter_performance_comparison(league_names: List[str]) -> pd.DataFrame:
        """
        Compare submitter performance across multiple leagues.
        
        Args:
            league_names: List of league names to compare
            
        Returns:
            DataFrame with submitter metrics per league
        """
        # Import here to avoid circular imports
        from musicleague.data.loader import MusicLeagueData
        
        league_data = {}
        all_submitters = set()

        for league_name in league_names:
            data = MusicLeagueData(league_name)
            league_data[league_name] = data
            for submitter_id, submitter_info in data.competitors.items():
                all_submitters.add((submitter_id, submitter_info['name']))

        results = []
        for submitter_id, submitter_name in all_submitters:
            row = {'submitter_name': submitter_name, 'submitter_id': submitter_id}

            for league_name in league_names:
                data = league_data[league_name]
                if submitter_id in data.competitors:
                    avg_points = SubmitterMetrics.average_points_per_submission(
                        data, submitter_id
                    )
                    _, std_dev = SubmitterMetrics.consistency_score(data, submitter_id)
                    underdog = SubmitterMetrics.underdog_factor(data, submitter_id)

                    row[f'{league_name}_avg'] = avg_points
                    row[f'{league_name}_std'] = std_dev
                    row[f'{league_name}_underdog'] = underdog
                else:
                    row[f'{league_name}_avg'] = 0
                    row[f'{league_name}_std'] = 0
                    row[f'{league_name}_underdog'] = 0

            results.append(row)

        df = pd.DataFrame(results)

        if len(league_names) >= 2:
            df['change'] = df[f'{league_names[-1]}_avg'] - df[f'{league_names[0]}_avg']
            df['improved'] = df['change'] > 0

        return df

    @staticmethod
    def voter_behavior_comparison(league_names: List[str]) -> pd.DataFrame:
        """
        Compare voter behavior across multiple leagues.
        
        Args:
            league_names: List of league names to compare
            
        Returns:
            DataFrame with voter metrics per league
        """
        from musicleague.data.loader import MusicLeagueData
        
        league_data = {}
        all_voters = set()

        for league_name in league_names:
            data = MusicLeagueData(league_name)
            league_data[league_name] = data
            for voter_id, voter_info in data.competitors.items():
                all_voters.add((voter_id, voter_info['name']))

        results = []
        for voter_id, voter_name in all_voters:
            row = {'voter_name': voter_name, 'voter_id': voter_id}

            for league_name in league_names:
                data = league_data[league_name]
                if voter_id in data.competitors:
                    golden_ear = VoterMetrics.golden_ear_score(data, voter_id)
                    hipster = VoterMetrics.hipster_score(data, voter_id)
                    generosity_mean, _ = VoterMetrics.generosity_score(data, voter_id)

                    row[f'{league_name}_golden_ear'] = golden_ear
                    row[f'{league_name}_hipster'] = hipster
                    row[f'{league_name}_generosity'] = generosity_mean
                else:
                    row[f'{league_name}_golden_ear'] = 0
                    row[f'{league_name}_hipster'] = 0
                    row[f'{league_name}_generosity'] = 0

            results.append(row)

        return pd.DataFrame(results)

    @staticmethod
    def league_characteristics(league_names: List[str]) -> pd.DataFrame:
        """
        Compare overall characteristics of different leagues.
        
        Args:
            league_names: List of league names to compare
            
        Returns:
            DataFrame with league-level metrics
        """
        from musicleague.data.loader import MusicLeagueData
        
        results = []

        for league_name in league_names:
            data = MusicLeagueData(league_name)
            song_df = SongMetrics.get_all_song_metrics(data)

            avg_controversy = (
                song_df['controversy_score'].mean() if len(song_df) > 0 else 0
            )
            avg_obscurity = (
                song_df['obscurity_score'].mean() if len(song_df) > 0 else 0
            )
            avg_spotify_popularity = (
                song_df['spotify_popularity'].mean() if len(song_df) > 0 else 0
            )
            total_songs = len(song_df)
            total_votes = len([v for v in data.votes if v['points'] > 0])

            # Calculate voter similarity
            sim_matrix = VoterMetrics.voter_similarity_matrix(data)
            avg_similarity = 0
            if len(sim_matrix) > 0:
                mask = np.triu(np.ones_like(sim_matrix, dtype=bool), k=1)
                avg_similarity = sim_matrix.values[mask].mean()

            # Calculate average competitiveness
            all_competitiveness = []
            for round_id in data.rounds:
                comp = CrossRoundMetrics.round_competitiveness(data, round_id)
                all_competitiveness.append(comp['score_std'])
            avg_competitiveness = (
                np.mean(all_competitiveness) if all_competitiveness else 0
            )

            results.append({
                'league_name': league_name,
                'total_songs': total_songs,
                'total_votes': total_votes,
                'num_competitors': len(data.competitors),
                'num_rounds': len(data.rounds),
                'avg_controversy': avg_controversy,
                'avg_obscurity': avg_obscurity,
                'avg_spotify_popularity': avg_spotify_popularity,
                'avg_voter_similarity': avg_similarity,
                'avg_competitiveness': avg_competitiveness
            })

        return pd.DataFrame(results)

    @staticmethod
    def song_overlap_analysis(league_names: List[str]) -> pd.DataFrame:
        """
        Find songs that appear in multiple leagues and compare performance.
        
        Args:
            league_names: List of league names to compare
            
        Returns:
            DataFrame with songs appearing in multiple leagues
        """
        from musicleague.data.loader import MusicLeagueData
        
        song_performances: Dict[str, Dict] = defaultdict(dict)

        for league_name in league_names:
            data = MusicLeagueData(league_name)
            song_df = SongMetrics.get_all_song_metrics(data)

            for _, song in song_df.iterrows():
                uri = song['spotify_uri']
                song_performances[uri][league_name] = {
                    'song_name': song['song_name'],
                    'artist': song['artist'],
                    'total_points': song['total_points'],
                    'controversy': song['controversy_score'],
                    'submitter': song['submitter']
                }

        # Filter to songs in multiple leagues
        results = []
        for uri, performances in song_performances.items():
            if len(performances) >= 2:
                first_perf = list(performances.values())[0]
                row = {
                    'spotify_uri': uri,
                    'song_name': first_perf['song_name'],
                    'artist': first_perf['artist'],
                    'num_leagues': len(performances)
                }

                for league_name in league_names:
                    if league_name in performances:
                        perf = performances[league_name]
                        row[f'{league_name}_points'] = perf['total_points']
                        row[f'{league_name}_controversy'] = perf['controversy']
                        row[f'{league_name}_submitter'] = perf['submitter']
                    else:
                        row[f'{league_name}_points'] = 0
                        row[f'{league_name}_controversy'] = 0
                        row[f'{league_name}_submitter'] = None

                results.append(row)

        df = pd.DataFrame(results)
        if len(df) > 0:
            df = df.sort_values('num_leagues', ascending=False)
        return df

