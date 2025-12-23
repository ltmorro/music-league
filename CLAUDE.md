# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MusicLeague Analysis Suite is a Python toolkit for analyzing MusicLeague competitions. It provides:

- **Metrics calculation** for songs, voters, submitters, and network relationships
- **Interactive visualizations** using Plotly and Matplotlib
- **Streamlit dashboard** ("The Soundwave Smackdown") for comparing leagues
- **CLI tools** for preprocessing data and running analyses

## Project Structure

```
musicleague/
├── src/musicleague/           # Main package
│   ├── data/                  # Data loading and caching
│   │   ├── loader.py          # MusicLeagueData class
│   │   ├── spotify.py         # Spotify API client
│   │   └── cache.py           # CacheManager for preprocessed data
│   ├── metrics/               # Metric calculations
│   │   ├── songs.py           # SongMetrics (controversy, obscurity, etc.)
│   │   ├── voters.py          # VoterMetrics (golden ear, hipster, etc.)
│   │   ├── submitters.py      # SubmitterMetrics (consistency, fans, etc.)
│   │   ├── network.py         # NetworkMetrics (influence, reciprocity)
│   │   ├── comments.py        # CommentMetrics (wordsmith, critic scores)
│   │   └── comparisons.py     # CrossRoundMetrics, CrossLeagueMetrics
│   ├── visualizations/        # Chart generation
│   │   ├── songs.py           # Song visualizations
│   │   ├── voters.py          # Voter visualizations
│   │   ├── submitters.py      # Submitter visualizations
│   │   └── network.py         # Network visualizations
│   ├── dashboard/             # Streamlit dashboard helpers
│   │   ├── helpers.py         # Data loading for dashboard
│   │   ├── theme.py           # Colors and styling
│   │   └── narrative.py       # Dynamic commentary generation
│   ├── scripts/               # CLI entry points
│   │   ├── preprocess.py      # Data preprocessing script
│   │   └── analyze.py         # Analysis CLI script
│   └── config.py              # Path configuration
├── pages/                     # Streamlit dashboard pages
│   ├── 1_🎵_Songs.py           # Top tracks, controversy, hidden gems
│   ├── 2_🌟_Players.py         # Submitter & voter stats
│   ├── 3_💬_Commentary_Booth.py # Comment analysis, wordsmith rankings
│   ├── 4_📈_Trends.py          # Round-by-round performance, momentum
│   ├── 5_🕸️_Connections.py     # Network graph, loyalty, reciprocity
│   └── 6_⚖️_Final_Scorecard.py  # Weighted scoring, crown a winner
├── streamlit_app.py           # Main dashboard entry point
├── data/                      # League data (CSV files)
├── cache/                     # Preprocessed data cache
└── outputs/                   # Generated visualizations
```

## Common Commands

```bash
# Install dependencies
uv sync

# Install package in editable mode
uv pip install -e .

# Preprocess league data (required before dashboard)
musicleague-preprocess metalicactopus_1 metalicactopus_2
musicleague-preprocess --all  # Process all leagues in data/

# Run analysis CLI
musicleague-analyze metalicactopus_1
musicleague-analyze metalicactopus_1 --visualize
musicleague-analyze --compare-leagues=metalicactopus_1,metalicactopus_2

# Run the Streamlit dashboard
streamlit run streamlit_app.py
```

## Data Format

League data lives in `data/<league_name>/` with these CSV files:

- `rounds.csv` - Round IDs
- `competitors.csv` - Competitor IDs and names
- `submissions.csv` - Round ID, Submitter ID, Spotify URI
- `votes.csv` - Round ID, Voter ID, Spotify URI, Points Assigned

## Key Metrics

### Song Metrics
- **Controversy Score**: Standard deviation of votes (higher = more polarizing)
- **Obscurity Score**: `total_points / (spotify_popularity + 1)` (hidden gems)
- **Total Points**: Sum of all votes received

### Voter Metrics
- **Golden Ear Score**: Correlation with final rankings (tastemakers)
- **Hipster Score**: Preference for low-popularity tracks
- **Generosity Score**: Average points given per vote

### Submitter Metrics
- **Consistency Score**: Standard deviation of points across submissions
- **Underdog Factor**: Success with obscure songs
- **Biggest Fan/Nemesis**: Who votes highest/lowest for them

### Network Metrics
- **Influence Score**: PageRank-based voting influence
- **Voting Reciprocity**: Mutual voting relationships

### Comment Metrics
- **Wordsmith Score**: Average comment length for submitters
- **Critic Score**: Average comment length for voters
- **Comment Rate**: Percentage of submissions/votes with comments

### Trends Metrics
- **Cumulative Points**: Running total of points by round
- **Momentum Score**: Linear regression slope of performance (rising/falling)
- **Hot Streak**: Consecutive top-3 finishes

## Environment Setup

Spotify API credentials are required. Set in `.env`:

```bash
SPOTIPY_CLIENT_ID=your-client-id
SPOTIPY_CLIENT_SECRET=your-client-secret
```

## Code Conventions

- Use the `musicleague` package imports (not path hacks)
- Metrics classes use static methods: `SongMetrics.controversy_score(data, uri)`
- Visualization classes return Plotly figures for `interactive=True`, Matplotlib for `False`
- Dashboard uses cached preprocessed data to avoid Spotify API rate limits