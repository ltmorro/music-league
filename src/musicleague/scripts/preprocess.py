#!/usr/bin/env python3
"""
Preprocess MusicLeague data for the Soundwave Smackdown dashboard.

This script:
1. Loads league data and fetches all Spotify metadata
2. Calculates all metrics for songs, voters, and submitters
3. Saves preprocessed data to pickle/JSON files
4. Avoids hitting Spotify API rate limits during dashboard usage

Usage:
    python -m musicleague.scripts.preprocess metalicactopus_1 metalicactopus_2
    python -m musicleague.scripts.preprocess --all  # Process all leagues in data/
"""

import sys
import argparse

from musicleague.config import PathConfig, get_available_leagues
from musicleague.data.loader import MusicLeagueData
from musicleague.data.cache import CacheManager
from musicleague.metrics.songs import SongMetrics
from musicleague.metrics.voters import VoterMetrics
from musicleague.metrics.submitters import SubmitterMetrics
from musicleague.metrics.network import NetworkMetrics


def preprocess_league(league_name: str, force: bool = False) -> bool:
    """
    Preprocess a single league: fetch Spotify data and calculate all metrics.

    Args:
        league_name: Name of the league to preprocess
        force: If True, reprocess even if cache exists
        
    Returns:
        True if successful, False otherwise
    """
    cache_manager = CacheManager()
    
    # Check if already cached
    if cache_manager.exists(league_name) and not force:
        print(f"✓ {league_name} already preprocessed (use --force to reprocess)")
        return True

    print(f"\n{'='*80}")
    print(f"Preprocessing: {league_name}")
    print(f"{'='*80}")

    # Load data
    print("Loading league data...")
    try:
        data = MusicLeagueData(league_name)
    except Exception as e:
        print(f"✗ Error loading {league_name}: {e}")
        return False

    print(f"✓ Loaded {len(data.competitors)} competitors")
    print(f"✓ Loaded {len(data.submissions)} submissions")
    print(f"✓ Loaded {len(data.votes)} votes")
    print(f"✓ Rounds: {', '.join(data.rounds)}")

    # Fetch all Spotify data upfront
    print("\nFetching Spotify metadata...")
    unique_uris = list(set(sub['spotify_uri'] for sub in data.submissions))
    total_tracks = len(unique_uris)

    for i, uri in enumerate(unique_uris, 1):
        if i % 10 == 0 or i == total_tracks:
            print(f"  Progress: {i}/{total_tracks} tracks", end='\r')
        data.get_spotify_data(uri)

    print(f"\n✓ Fetched metadata for {total_tracks} tracks")

    # Calculate all song metrics
    print("\nCalculating song metrics...")
    song_df = SongMetrics.get_all_song_metrics(data)
    print(f"✓ Processed {len(song_df)} songs")

    # Calculate voter metrics
    print("\nCalculating voter metrics...")
    voter_metrics = {}
    for voter_id, voter_data in data.competitors.items():
        voter_metrics[voter_id] = {
            'name': voter_data['name'],
            'golden_ear': VoterMetrics.golden_ear_score(data, voter_id),
            'hipster': VoterMetrics.hipster_score(data, voter_id),
            'generosity': VoterMetrics.generosity_score(data, voter_id),
            'voting_range': VoterMetrics.voting_range(data, voter_id),
            'loyalty_index': VoterMetrics.loyalty_index(data, voter_id),
        }
    print(f"✓ Processed {len(voter_metrics)} voters")

    # Calculate submitter metrics
    print("\nCalculating submitter metrics...")
    submitter_metrics = {}
    for submitter_id, submitter_data in data.competitors.items():
        avg_points = SubmitterMetrics.average_points_per_submission(data, submitter_id)
        if avg_points > 0:
            avg, std = SubmitterMetrics.consistency_score(data, submitter_id)
            fan, nemesis = SubmitterMetrics.biggest_fan_and_nemesis(data, submitter_id)

            submitter_metrics[submitter_id] = {
                'name': submitter_data['name'],
                'avg_points': avg_points,
                'consistency_avg': avg,
                'consistency_std': std,
                'underdog_factor': SubmitterMetrics.underdog_factor(data, submitter_id),
                'biggest_fan': fan,
                'nemesis': nemesis,
            }
    print(f"✓ Processed {len(submitter_metrics)} submitters")

    # Calculate network metrics
    print("\nCalculating network metrics...")
    try:
        influence_scores = NetworkMetrics.influence_score(data)
        voting_graph = NetworkMetrics.build_voting_graph(data)
        reciprocity_df = NetworkMetrics.voting_reciprocity(data)
        voter_similarity = VoterMetrics.voter_similarity_matrix(data)

        network_metrics = {
            'influence_scores': influence_scores,
            'num_nodes': len(voting_graph.nodes()),
            'num_edges': len(voting_graph.edges()),
            'reciprocity_df': reciprocity_df,
            'voter_similarity': voter_similarity,
        }
        print(f"✓ Built network with {len(voting_graph.nodes())} nodes, {len(voting_graph.edges())} edges")
    except Exception as e:
        print(f"⚠ Warning: Could not calculate network metrics: {e}")
        network_metrics = {}

    # Calculate summary stats
    print("\nCalculating summary statistics...")
    summary_stats = {
        'total_competitors': len(data.competitors),
        'total_submissions': len(data.submissions),
        'total_votes': len([v for v in data.votes if v['points'] > 0]),
        'total_rounds': len(data.rounds),
        'avg_controversy': song_df['controversy_score'].mean() if len(song_df) > 0 else 0,
        'avg_spotify_popularity': song_df['spotify_popularity'].mean() if len(song_df) > 0 else 0,
        'avg_points_per_song': song_df['total_points'].mean() if len(song_df) > 0 else 0,
    }

    # Package everything
    preprocessed_data = {
        'league_name': league_name,
        'raw_data': {
            'competitors': data.competitors,
            'submissions': data.submissions,
            'votes': data.votes,
            'rounds': data.rounds,
            'spotify_data': data.spotify_data,
        },
        'song_metrics': song_df,
        'voter_metrics': voter_metrics,
        'submitter_metrics': submitter_metrics,
        'network_metrics': network_metrics,
        'summary_stats': summary_stats,
    }

    # Save to cache
    print(f"\nSaving preprocessed data...")
    if cache_manager.save(league_name, preprocessed_data):
        cache_path = cache_manager.get_cache_path(league_name)
        print(f"✓ Successfully preprocessed {league_name}")
        print(f"  Cache file: {cache_path}")
        print(f"  Size: {cache_path.stat().st_size / 1024:.1f} KB")
    else:
        print(f"✗ Failed to save cache for {league_name}")
        return False

    # Save JSON summary
    json_summary = {
        'league_name': league_name,
        'summary_stats': summary_stats,
        'top_songs': song_df.head(10)[['song_name', 'artist', 'total_points']].to_dict('records'),
        'top_submitters': sorted(
            [(v['name'], v['avg_points']) for v in submitter_metrics.values()],
            key=lambda x: x[1],
            reverse=True
        )[:10],
    }

    if cache_manager.save_summary(league_name, json_summary):
        print(f"✓ Summary saved to {cache_manager.get_summary_path(league_name)}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Preprocess MusicLeague data for the Soundwave Smackdown dashboard'
    )
    parser.add_argument(
        'leagues',
        nargs='*',
        help='League names to preprocess (e.g., metalicactopus_1 metalicactopus_2)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Preprocess all leagues found in data/ directory'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force reprocessing even if cache exists'
    )

    args = parser.parse_args()

    # Determine which leagues to process
    if args.all:
        leagues_to_process = get_available_leagues()
        if not leagues_to_process:
            print("No leagues found in data/ directory")
            sys.exit(1)
        print(f"Found {len(leagues_to_process)} leagues: {', '.join(leagues_to_process)}")
    elif args.leagues:
        leagues_to_process = args.leagues
    else:
        print("Error: Specify league names or use --all flag")
        parser.print_help()
        sys.exit(1)

    # Process each league
    print(f"\n🎧 Soundwave Smackdown - Data Preprocessing 🎧")
    print(f"{'='*80}\n")

    success_count = 0
    for league in leagues_to_process:
        try:
            if preprocess_league(league, force=args.force):
                success_count += 1
        except Exception as e:
            print(f"✗ Error preprocessing {league}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*80}")
    print(f"✓ Preprocessing complete! ({success_count}/{len(leagues_to_process)} leagues)")
    print(f"{'='*80}")
    print(f"\nCached data saved to: {PathConfig.CACHE_DIR}/")
    print("\nYou can now run the dashboard with:")
    print("  streamlit run streamlit_app.py")


if __name__ == "__main__":
    main()

