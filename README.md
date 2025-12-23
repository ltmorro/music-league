# MusicLeague Analysis Suite

A comprehensive Python toolkit for analyzing MusicLeague data with advanced metrics and visualizations.

## Overview

This analysis suite provides deep insights into:
- **Song performance** (controversy, obscurity, vote distribution)
- **Voter behavior** (similarity, golden ear score, hipster score, generosity)
- **Submitter performance** (consistency, underdog factor, biggest fans)
- **Cross-round comparisons** (performance trajectories, competitiveness)
- **Network relationships** (voting reciprocity, influence scores, cliques)

## Installation

1. Install with uv:
```bash
uv sync
uv pip install -e .
```

2. Set up Spotify API credentials (required for fetching track metadata):
   - Create a Spotify Developer app at https://developer.spotify.com/
   - Create a `.env` file:
     ```bash
     SPOTIPY_CLIENT_ID='your-client-id'
     SPOTIPY_CLIENT_SECRET='your-client-secret'
     ```

## Quick Start

### Preprocess Data (Required First)

Before running analysis or the dashboard, preprocess your league data:
```bash
# Preprocess specific leagues
musicleague-preprocess metalicactopus_1 metalicactopus_2

# Or preprocess all leagues in data/
musicleague-preprocess --all
```

This fetches Spotify metadata, calculates all metrics, and caches the results.

### Run the Dashboard

```bash
streamlit run streamlit_app.py
```

### CLI Analysis

Analyze a single league:
```bash
musicleague-analyze metalicactopus_1
```

Generate visualizations:
```bash
musicleague-analyze metalicactopus_1 --visualize
```

Compare leagues:
```bash
musicleague-analyze --compare-leagues=metalicactopus_1,metalicactopus_2
```

## Programmatic Usage

### Loading Data

```python
from musicleague.data import MusicLeagueData

# Load league data
data = MusicLeagueData('metalicactopus_1')

print(f"Competitors: {len(data.competitors)}")
print(f"Submissions: {len(data.submissions)}")
print(f"Votes: {len(data.votes)}")
print(f"Rounds: {data.rounds}")
```

### Song Metrics

```python
from musicleague.data import MusicLeagueData
from musicleague.metrics import SongMetrics

data = MusicLeagueData('metalicactopus_1')

# Get comprehensive metrics for all songs
song_df = SongMetrics.get_all_song_metrics(data)

# Get metrics for a specific song
uri = "spotify:track:xyz123"
controversy = SongMetrics.controversy_score(data, uri)
total_points = SongMetrics.total_points(data, uri)
obscurity = SongMetrics.obscurity_score(data, uri)

print(f"Controversy Score: {controversy:.2f}")
print(f"Total Points: {total_points}")
print(f"Obscurity Score: {obscurity:.2f}")
```

### Voter Metrics

```python
from musicleague.metrics import VoterMetrics

voter_id = "voter_xyz123"

# Golden Ear Score (correlation with winners)
golden_ear = VoterMetrics.golden_ear_score(data, voter_id)

# Hipster Score (preference for obscure tracks)
hipster = VoterMetrics.hipster_score(data, voter_id)

# Generosity Score (average points given)
mean, std = VoterMetrics.generosity_score(data, voter_id)

# Voter Similarity Matrix
similarity_matrix = VoterMetrics.voter_similarity_matrix(data)
```

### Submitter Metrics

```python
from musicleague.metrics import SubmitterMetrics

submitter_id = "submitter_xyz123"

# Average points per submission
avg_points = SubmitterMetrics.average_points_per_submission(data, submitter_id)

# Consistency (avg, std dev)
avg, std = SubmitterMetrics.consistency_score(data, submitter_id)

# Underdog Factor (success with obscure songs)
underdog = SubmitterMetrics.underdog_factor(data, submitter_id)

# Biggest Fan & Nemesis
fan, nemesis = SubmitterMetrics.biggest_fan_and_nemesis(data, submitter_id)
print(f"Biggest Fan: {fan['name']} ({fan['avg_points']:.1f} pts)")
print(f"Nemesis: {nemesis['name']} ({nemesis['avg_points']:.1f} pts)")
```

### Network Analysis

```python
from musicleague.metrics import NetworkMetrics

# Build voting graph
G = NetworkMetrics.build_voting_graph(data)

# Calculate influence scores (PageRank)
influence = NetworkMetrics.influence_score(data)
for voter, score in sorted(influence.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"{voter}: {score:.4f}")

# Voting reciprocity analysis
reciprocity_df = NetworkMetrics.voting_reciprocity(data)

# Detect voting cliques/communities
cliques = NetworkMetrics.detect_cliques(data)
```

### Cross-League Comparisons

```python
from musicleague.metrics import CrossLeagueMetrics

league_names = ['metalicactopus_1', 'metalicactopus_2']

# Compare league characteristics
characteristics = CrossLeagueMetrics.league_characteristics(league_names)
print(characteristics)

# Compare submitter performance across leagues
submitter_comparison = CrossLeagueMetrics.submitter_performance_comparison(league_names)
top_improvers = submitter_comparison.nlargest(5, 'change')

# Find songs that appeared in multiple leagues
song_overlap = CrossLeagueMetrics.song_overlap_analysis(league_names)
print(f"Found {len(song_overlap)} songs in multiple leagues")
```

## Visualizations

```python
from musicleague.data import MusicLeagueData
from musicleague.visualizations import (
    SongVisualizations,
    VoterVisualizations,
    SubmitterVisualizations,
    NetworkVisualizations
)

data = MusicLeagueData('metalicactopus_1')

# Song visualizations
fig = SongVisualizations.controversy_chart(data, top_n=10, interactive=True)
fig.write_html('controversy_chart.html')

fig = SongVisualizations.mainstream_vs_underground_scatter(data, interactive=True)
fig.write_html('mainstream_vs_underground.html')

# Voter visualizations
fig = VoterVisualizations.similarity_heatmap(data, interactive=True)
fig.write_html('voter_similarity.html')

# Network visualizations
fig = NetworkVisualizations.voting_network(data, interactive=True)
fig.write_html('voting_network.html')
```

## Project Structure

```
musicleague/
├── src/musicleague/           # Main package
│   ├── data/                  # Data loading and caching
│   ├── metrics/               # Metric calculations
│   ├── visualizations/        # Chart generation
│   ├── dashboard/             # Streamlit helpers
│   ├── scripts/               # CLI entry points
│   └── config.py              # Configuration
├── pages/                     # Streamlit dashboard pages
├── streamlit_app.py           # Dashboard entry point
├── data/                      # League data (CSV files)
├── cache/                     # Preprocessed data cache
└── outputs/                   # Generated visualizations
```

## Data Format

The analysis suite expects the following CSV files in `data/<league_name>/`:

### `rounds.csv`
```csv
ID
round_xyz123
round_abc456
```

### `competitors.csv`
```csv
ID,Name
competitor1_id,Alice
competitor2_id,Bob
```

### `submissions.csv`
```csv
Round ID,Submitter ID,Spotify URI
round_xyz123,competitor1_id,spotify:track:abc123
```

### `votes.csv`
```csv
Round ID,Voter ID,Spotify URI,Points Assigned
round_xyz123,competitor2_id,spotify:track:abc123,5
```

## Metric Descriptions

### Song Metrics
- **Controversy Score**: Standard deviation of votes (higher = more polarizing)
- **Vote Distribution**: Count of each point value (1s, 2s, 3s, etc.)
- **Total Points**: Sum of all votes received
- **Obscurity Score**: `total_points / (spotify_popularity + 1)` (rewards hidden gems)

### Voter Metrics
- **Golden Ear Score**: Spearman correlation between voter's scores and final rankings
- **Hipster Score**: Weighted average of (100 - spotify_popularity) for highly-voted songs
- **Generosity Score**: Average points given per vote
- **Voter Similarity**: Pairwise Spearman correlation between all voters

### Submitter Metrics
- **Average Points Per Submission**: Total points / number of submissions
- **Consistency Score**: Standard deviation of points across submissions
- **Underdog Factor**: `total_points / (avg_spotify_popularity + 1)`
- **Biggest Fan**: Voter who gives highest average points
- **Nemesis**: Voter who gives lowest average points

### Network Metrics
- **Voting Graph**: Directed graph with edge weights = points given
- **Influence Score**: PageRank-based measure of voting influence
- **Voting Reciprocity**: How much people vote for those who vote for them
- **Clique Detection**: Community/group detection in voting patterns

## License

MIT