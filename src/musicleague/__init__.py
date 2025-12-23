"""
MusicLeague Analysis Package

A comprehensive toolkit for analyzing MusicLeague competition data,
including metrics calculation, visualization, and comparison tools.
"""

__version__ = "2.0.0"

# Core data loading
from musicleague.data.loader import MusicLeagueData

# Metrics
from musicleague.metrics.songs import SongMetrics
from musicleague.metrics.voters import VoterMetrics
from musicleague.metrics.submitters import SubmitterMetrics
from musicleague.metrics.network import NetworkMetrics
from musicleague.metrics.comparisons import CrossRoundMetrics, CrossLeagueMetrics

__all__ = [
    "MusicLeagueData",
    "SongMetrics",
    "VoterMetrics",
    "SubmitterMetrics",
    "NetworkMetrics",
    "CrossRoundMetrics",
    "CrossLeagueMetrics",
]

