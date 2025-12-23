#!/usr/bin/env python3
"""
CLI script for analyzing MusicLeague data using the metrics system.

Usage:
    musicleague-analyze <league_name> [round_id] [options]
    python -m musicleague.scripts.analyze <league_name> [round_id] [options]

Options:
    --visualize              Generate interactive visualizations
    --compare=round1,round2  Compare two rounds within a league
    --compare-leagues=l1,l2  Compare multiple leagues/competitions

Examples:
    musicleague-analyze metalicactopus_1
    musicleague-analyze metalicactopus_1 --visualize
    musicleague-analyze metalicactopus_1 round_123
    musicleague-analyze metalicactopus --compare=round1_id,round2_id
    musicleague-analyze --compare-leagues=metalicactopus_1,metalicactopus_2
"""

import sys
import os

from musicleague.data import MusicLeagueData
from musicleague.metrics import (
    SongMetrics,
    VoterMetrics,
    SubmitterMetrics,
    CrossRoundMetrics,
    CrossLeagueMetrics,
    NetworkMetrics,
)
from musicleague.visualizations import (
    SongVisualizations,
    VoterVisualizations,
    SubmitterVisualizations,
    NetworkVisualizations,
)


def analyze_single_round(league_name: str, round_id: str = None):
    """
    Perform comprehensive analysis of a single round or entire league.
    """
    print(f"\n{'='*80}")
    print(f"MusicLeague Analysis: {league_name}")
    if round_id:
        print(f"Round: {round_id}")
    else:
        print("Analyzing all rounds combined")
    print(f"{'='*80}\n")

    # Load data
    print("Loading data...")
    data = MusicLeagueData(league_name)
    print(f"✓ Loaded {len(data.competitors)} competitors")
    print(f"✓ Loaded {len(data.submissions)} submissions")
    print(f"✓ Loaded {len(data.votes)} votes")
    print(f"✓ Rounds: {', '.join(data.rounds)}\n")

    # ========================================
    # SONG METRICS
    # ========================================
    print("\n" + "="*80)
    print("SONG METRICS")
    print("="*80)

    song_df = SongMetrics.get_all_song_metrics(data, round_id)
    print(f"\n{len(song_df)} songs analyzed\n")

    print("Top 20 Songs by Total Points:")
    print("-" * 80)
    for idx, row in song_df.head(20).iterrows():
        print(f"{row['song_name'][:40]:40} - {row['artist'][:220]:220} | {row['total_points']:3.0f} pts")

    print("\nTop 20 Most Controversial Songs:")
    print("-" * 80)
    top_controversial = song_df.nlargest(20, 'controversy_score')
    for idx, row in top_controversial.iterrows():
        print(f"{row['song_name'][:40]:40} - {row['artist'][:220]:220} | σ={row['controversy_score']:.2f}")

    print("\nTop 20 Hidden Gems (Obscurity Score):")
    print("-" * 80)
    top_obscure = song_df.nlargest(20, 'obscurity_score')
    for idx, row in top_obscure.iterrows():
        print(f"{row['song_name'][:40]:40} - {row['artist'][:220]:220} | Score={row['obscurity_score']:.2f} (Pop={row['spotify_popularity']})")

    # ========================================
    # VOTER METRICS
    # ========================================
    print("\n" + "="*80)
    print("VOTER METRICS")
    print("="*80)

    print("\nGolden Ear Scores (Tastemakers):")
    print("-" * 80)
    golden_ear_scores = []
    for voter_id, voter_data in data.competitors.items():
        score = VoterMetrics.golden_ear_score(data, voter_id, round_id)
        golden_ear_scores.append((voter_data['name'], score))

    golden_ear_scores.sort(key=lambda x: x[1], reverse=True)
    for name, score in golden_ear_scores:
        print(f"{name:30} | Correlation: {score:.3f}")

    print("\nHipster Scores (Obscure Track Preference):")
    print("-" * 80)
    hipster_scores = []
    for voter_id, voter_data in data.competitors.items():
        score = VoterMetrics.hipster_score(data, voter_id, round_id)
        hipster_scores.append((voter_data['name'], score))

    hipster_scores.sort(key=lambda x: x[1], reverse=True)
    for name, score in hipster_scores:
        print(f"{name:30} | Score: {score:.2f}")

    print("\nGenerosity Scores (Average Points Given):")
    print("-" * 80)
    generosity_scores = []
    for voter_id, voter_data in data.competitors.items():
        mean, std = VoterMetrics.generosity_score(data, voter_id, round_id)
        generosity_scores.append((voter_data['name'], mean, std))

    generosity_scores.sort(key=lambda x: x[1], reverse=True)
    for name, mean, std in generosity_scores:
        print(f"{name:30} | Avg: {mean:.2f} ± {std:.2f}")

    # ========================================
    # SUBMITTER METRICS
    # ========================================
    print("\n" + "="*80)
    print("SUBMITTER METRICS")
    print("="*80)

    print("\nAverage Points Per Submission:")
    print("-" * 80)
    submitter_avgs = []
    for submitter_id, submitter_data in data.competitors.items():
        avg = SubmitterMetrics.average_points_per_submission(data, submitter_id, round_id)
        if avg > 0:
            submitter_avgs.append((submitter_data['name'], avg))

    submitter_avgs.sort(key=lambda x: x[1], reverse=True)
    for name, avg in submitter_avgs:
        print(f"{name:30} | Avg: {avg:.2f} pts")

    print("\nSubmitter Consistency (Avg ± StdDev):")
    print("-" * 80)
    consistency_scores = []
    for submitter_id, submitter_data in data.competitors.items():
        avg, std = SubmitterMetrics.consistency_score(data, submitter_id, round_id)
        if avg > 0:
            consistency_scores.append((submitter_data['name'], avg, std))

    consistency_scores.sort(key=lambda x: x[2])  # Sort by std (lower = more consistent)
    for name, avg, std in consistency_scores:
        print(f"{name:30} | {avg:.2f} ± {std:.2f} pts")

    print("\nUnderdog Factor (Success with Obscure Songs):")
    print("-" * 80)
    underdog_scores = []
    for submitter_id, submitter_data in data.competitors.items():
        score = SubmitterMetrics.underdog_factor(data, submitter_id, round_id)
        if score > 0:
            underdog_scores.append((submitter_data['name'], score))

    underdog_scores.sort(key=lambda x: x[1], reverse=True)
    for name, score in underdog_scores:
        print(f"{name:30} | Score: {score:.2f}")

    print("\nBiggest Fans & Nemeses (Top 3 Submitters):")
    print("-" * 80)
    for submitter_id, submitter_data in submitter_avgs[:3]:
        # Find submitter_id from name
        sub_id = None
        for sid, sdata in data.competitors.items():
            if sdata['name'] == submitter_data:
                sub_id = sid
                break

        if sub_id:
            fan, nemesis = SubmitterMetrics.biggest_fan_and_nemesis(data, sub_id, round_id)
            print(f"\n{submitter_data}:")
            if fan:
                print(f"  Biggest Fan: {fan['name']} ({fan['avg_points']:.1f} avg pts)")
            if nemesis:
                print(f"  Nemesis: {nemesis['name']} ({nemesis['avg_points']:.1f} avg pts)")

    # ========================================
    # NETWORK METRICS
    # ========================================
    print("\n" + "="*80)
    print("NETWORK METRICS")
    print("="*80)

    print("\nInfluence Scores (PageRank):")
    print("-" * 80)
    influence = NetworkMetrics.influence_score(data, round_id)
    sorted_influence = sorted(influence.items(), key=lambda x: x[1], reverse=True)
    for name, score in sorted_influence:
        print(f"{name:30} | Influence: {score:.4f}")

    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)


def compare_leagues(league_names: list):
    """
    Compare metrics across multiple leagues/competitions.
    """
    print(f"\n{'='*80}")
    print(f"Cross-League Comparison")
    print(f"Leagues: {', '.join(league_names)}")
    print(f"{'='*80}\n")

    # ========================================
    # LEAGUE CHARACTERISTICS
    # ========================================
    print("League Characteristics:")
    print("=" * 80)
    characteristics = CrossLeagueMetrics.league_characteristics(league_names)

    for _, league in characteristics.iterrows():
        print(f"\n{league['league_name']}:")
        print(f"  Total Songs: {league['total_songs']}")
        print(f"  Total Votes: {league['total_votes']}")
        print(f"  Competitors: {league['num_competitors']}")
        print(f"  Rounds: {league['num_rounds']}")
        print(f"  Avg Controversy: {league['avg_controversy']:.2f}")
        print(f"  Avg Spotify Popularity: {league['avg_spotify_popularity']:.1f}")
        print(f"  Avg Voter Similarity: {league['avg_voter_similarity']:.3f}")
        print(f"  Avg Competitiveness: {league['avg_competitiveness']:.2f}")

    # ========================================
    # SUBMITTER PERFORMANCE COMPARISON
    # ========================================
    print("\n\n" + "="*80)
    print("Submitter Performance Comparison")
    print("="*80)

    submitter_df = CrossLeagueMetrics.submitter_performance_comparison(league_names)

    # Filter to only those who participated in both leagues
    if len(league_names) == 2:
        submitter_df_both = submitter_df[
            (submitter_df[f'{league_names[0]}_avg'] > 0) &
            (submitter_df[f'{league_names[1]}_avg'] > 0)
        ]

        if len(submitter_df_both) > 0:
            submitter_df_both = submitter_df_both.sort_values('change', ascending=False)

            print(f"\nTop Improvers ({league_names[0]} → {league_names[1]}):")
            print("-" * 80)
            for _, row in submitter_df_both.head(20).iterrows():
                print(f"{row['submitter_name']:30} | {row[f'{league_names[0]}_avg']:6.2f} → {row[f'{league_names[1]}_avg']:6.2f} ({row['change']:+.2f})")

            print(f"\nBiggest Declines ({league_names[0]} → {league_names[1]}):")
            print("-" * 80)
            for _, row in submitter_df_both.tail(20).iterrows():
                print(f"{row['submitter_name']:30} | {row[f'{league_names[0]}_avg']:6.2f} → {row[f'{league_names[1]}_avg']:6.2f} ({row['change']:+.2f})")

    # ========================================
    # VOTER BEHAVIOR COMPARISON
    # ========================================
    print("\n\n" + "="*80)
    print("Voter Behavior Comparison")
    print("="*80)

    voter_df = CrossLeagueMetrics.voter_behavior_comparison(league_names)

    # Filter to only those who participated in both leagues
    if len(league_names) == 2:
        voter_df_both = voter_df[
            (voter_df[f'{league_names[0]}_generosity'] > 0) &
            (voter_df[f'{league_names[1]}_generosity'] > 0)
        ]

        if len(voter_df_both) > 0:
            print(f"\nGolden Ear Score Changes:")
            print("-" * 80)
            voter_df_both['ge_change'] = voter_df_both[f'{league_names[1]}_golden_ear'] - voter_df_both[f'{league_names[0]}_golden_ear']
            voter_df_both_sorted = voter_df_both.sort_values('ge_change', ascending=False)

            for _, row in voter_df_both_sorted.head(20).iterrows():
                print(f"{row['voter_name']:30} | {row[f'{league_names[0]}_golden_ear']:6.3f} → {row[f'{league_names[1]}_golden_ear']:6.3f} ({row['ge_change']:+.3f})")

            print(f"\nHipster Score Changes:")
            print("-" * 80)
            voter_df_both['hipster_change'] = voter_df_both[f'{league_names[1]}_hipster'] - voter_df_both[f'{league_names[0]}_hipster']
            voter_df_both_sorted = voter_df_both.sort_values('hipster_change', ascending=False)

            for _, row in voter_df_both_sorted.head(20).iterrows():
                print(f"{row['voter_name']:30} | {row[f'{league_names[0]}_hipster']:6.2f} → {row[f'{league_names[1]}_hipster']:6.2f} ({row['hipster_change']:+.2f})")

    # ========================================
    # SONG OVERLAP ANALYSIS
    # ========================================
    print("\n\n" + "="*80)
    print("Song Overlap Analysis")
    print("="*80)

    overlap_df = CrossLeagueMetrics.song_overlap_analysis(league_names)

    if len(overlap_df) > 0:
        print(f"\n{len(overlap_df)} songs appeared in multiple leagues\n")
        print("Songs that appeared in most leagues:")
        print("-" * 80)

        for _, row in overlap_df.head(10).iterrows():
            print(f"\n{row['song_name'][:200]} - {row['artist'][:30]}")
            print(f"  Appeared in {row['num_leagues']} leagues")
            for league_name in league_names:
                if f'{league_name}_points' in row and row[f'{league_name}_points'] > 0:
                    print(f"    {league_name}: {row[f'{league_name}_points']:.0f} pts (submitted by {row[f'{league_name}_submitter']})")
    else:
        print("\nNo songs appeared in multiple leagues")

    print("\n" + "="*80)
    print("Comparison complete!")
    print("="*80)


def compare_rounds(league_name: str, round_ids: list):
    """
    Compare metrics across multiple rounds.
    """
    print(f"\n{'='*80}")
    print(f"Cross-Round Comparison: {league_name}")
    print(f"Rounds: {', '.join(round_ids)}")
    print(f"{'='*80}\n")

    # Load data
    data = MusicLeagueData(league_name)

    print("Round Competitiveness:")
    print("-" * 80)
    for round_id in round_ids:
        stats = CrossRoundMetrics.round_competitiveness(data, round_id)
        print(f"\n{round_id}:")
        print(f"  Vote Std Dev: {stats['vote_std']:.2f}")
        print(f"  Score Std Dev: {stats['score_std']:.2f}")
        print(f"  Avg Score: {stats['avg_score']:.2f}")

    print("\n\nSubmitter Performance Trajectories:")
    print("-" * 80)
    trajectories = []
    for submitter_id, submitter_data in data.competitors.items():
        traj = CrossRoundMetrics.submitter_performance_trajectory(data, submitter_id, round_ids)
        if len(traj) >= 2:
            change = list(traj.values())[1] - list(traj.values())[0]
            trajectories.append((submitter_data['name'], list(traj.values()), change))

    trajectories.sort(key=lambda x: x[2], reverse=True)

    print("\nTop Improvers:")
    for name, scores, change in trajectories:
        if change > 0:
            print(f"{name:30} | {scores[0]:.1f} → {scores[1]:.1f} (+{change:.1f})")

    print("\nBiggest Declines:")
    for name, scores, change in reversed(trajectories[-20:]):
        if change < 0:
            print(f"{name:30} | {scores[0]:.1f} → {scores[1]:.1f} ({change:.1f})")


def generate_visualizations(league_name: str, round_id: str = None, output_dir: str = None):
    """
    Generate all visualizations and save to files.
    """
    print(f"\n{'='*80}")
    print(f"Generating Visualizations: {league_name}")
    print(f"{'='*80}\n")

    # Create output directory based on league name if not specified
    if output_dir is None:
        output_dir = f"outputs/{league_name}"

    os.makedirs(output_dir, exist_ok=True)

    # Load data
    data = MusicLeagueData(league_name)

    print("Generating song visualizations...")
    try:
        fig = SongVisualizations.controversy_chart(data, round_id, interactive=True)
        if fig:
            fig.write_html(f"{output_dir}/controversy_chart.html")
            print("✓ Controversy chart saved")
    except Exception as e:
        print(f"✗ Error generating controversy chart: {e}")

    try:
        fig = SongVisualizations.mainstream_vs_underground_scatter(data, round_id, interactive=True)
        if fig:
            fig.write_html(f"{output_dir}/mainstream_vs_underground.html")
            print("✓ Mainstream vs Underground scatter saved")
    except Exception as e:
        print(f"✗ Error generating scatter plot: {e}")

    try:
        fig = SongVisualizations.obscurity_score_chart(data, round_id, interactive=True)
        if fig:
            fig.write_html(f"{output_dir}/obscurity_scores.html")
            print("✓ Obscurity score chart saved")
    except Exception as e:
        print(f"✗ Error generating obscurity chart: {e}")

    print("\nGenerating voter visualizations...")
    try:
        fig = VoterVisualizations.similarity_heatmap(data, round_id, interactive=True)
        if fig:
            fig.write_html(f"{output_dir}/voter_similarity.html")
            print("✓ Voter similarity heatmap saved")
    except Exception as e:
        print(f"✗ Error generating similarity heatmap: {e}")

    try:
        fig = VoterVisualizations.golden_ear_chart(data, round_id, interactive=True)
        if fig:
            fig.write_html(f"{output_dir}/golden_ear_scores.html")
            print("✓ Golden ear chart saved")
    except Exception as e:
        print(f"✗ Error generating golden ear chart: {e}")

    try:
        fig = VoterVisualizations.hipster_score_chart(data, round_id, interactive=True)
        if fig:
            fig.write_html(f"{output_dir}/hipster_scores.html")
            print("✓ Hipster score chart saved")
    except Exception as e:
        print(f"✗ Error generating hipster chart: {e}")

    try:
        fig = VoterVisualizations.generosity_chart(data, round_id, interactive=True)
        if fig:
            fig.write_html(f"{output_dir}/generosity_scores.html")
            print("✓ Generosity chart saved")
    except Exception as e:
        print(f"✗ Error generating generosity chart: {e}")

    try:
        fig = VoterVisualizations.loyalty_heatmap(data, round_id, interactive=True)
        if fig:
            fig.write_html(f"{output_dir}/loyalty_heatmap.html")
            print("✓ Loyalty heatmap saved")
    except Exception as e:
        print(f"✗ Error generating loyalty heatmap: {e}")

    print("\nGenerating submitter visualizations...")
    try:
        fig = SubmitterVisualizations.average_points_chart(data, round_id, interactive=True)
        if fig:
            fig.write_html(f"{output_dir}/avg_points_per_submission.html")
            print("✓ Average points chart saved")
    except Exception as e:
        print(f"✗ Error generating avg points chart: {e}")

    try:
        fig = SubmitterVisualizations.consistency_scatter(data, round_id, interactive=True)
        if fig:
            fig.write_html(f"{output_dir}/submitter_consistency.html")
            print("✓ Consistency scatter saved")
    except Exception as e:
        print(f"✗ Error generating consistency scatter: {e}")

    print("\nGenerating network visualizations...")
    try:
        fig = NetworkVisualizations.influence_score_chart(data, round_id, interactive=True)
        if fig:
            fig.write_html(f"{output_dir}/influence_scores.html")
            print("✓ Influence score chart saved")
    except Exception as e:
        print(f"✗ Error generating influence chart: {e}")

    try:
        fig = NetworkVisualizations.voting_network(data, round_id, interactive=True)
        if fig:
            fig.write_html(f"{output_dir}/voting_network.html")
            print("✓ Voting network saved")
    except Exception as e:
        print(f"✗ Error generating voting network: {e}")

    print(f"\n✓ All visualizations saved to {output_dir}/")


def main():
    if len(sys.argv) < 2:
        print("Usage: musicleague-analyze <league_name> [round_id] [options]")
        print("\nOptions:")
        print("  --visualize              Generate interactive visualizations")
        print("  --compare=round1,round2  Compare two rounds within a league")
        print("  --compare-leagues=l1,l2  Compare multiple leagues/competitions")
        print("\nExamples:")
        print("  musicleague-analyze metalicactopus_1")
        print("  musicleague-analyze metalicactopus_1 --visualize")
        print("  musicleague-analyze metalicactopus_1 round_123")
        print("\nCompare rounds within a league:")
        print("  musicleague-analyze metalicactopus --compare=round1_id,round2_id")
        print("\nCompare multiple leagues:")
        print("  musicleague-analyze --compare-leagues=metalicactopus_1,metalicactopus_2")
        sys.exit(1)

    league_name = None
    round_id = None
    visualize = False
    compare = False
    compare_leagues_mode = False
    round_ids = []
    league_names = []

    # Parse arguments
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]
        if arg == '--visualize':
            visualize = True
        elif arg.startswith('--compare='):
            compare = True
            round_ids = arg.split('=')[1].split(',')
        elif arg.startswith('--compare-leagues='):
            compare_leagues_mode = True
            league_names = arg.split('=')[1].split(',')
        elif not league_name and not arg.startswith('--'):
            league_name = arg
        elif league_name and not round_id and not arg.startswith('--'):
            round_id = arg

    # Run analysis
    if compare_leagues_mode and len(league_names) >= 2:
        compare_leagues(league_names)
    elif compare and len(round_ids) >= 2 and league_name:
        compare_rounds(league_name, round_ids)
    elif league_name:
        analyze_single_round(league_name, round_id)

        # Generate visualizations if requested
        if visualize:
            generate_visualizations(league_name, round_id)
    else:
        print("Error: Must specify either a league name or --compare-leagues option")
        sys.exit(1)


if __name__ == "__main__":
    main()