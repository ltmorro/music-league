"""
Song-specific visualizations for MusicLeague analysis.
"""

from typing import Optional, TYPE_CHECKING

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

if TYPE_CHECKING:
    from musicleague.data.loader import MusicLeagueData

from musicleague.metrics.songs import SongMetrics
from musicleague.visualizations.base import (
    COLORS_DICT, configure_axes, apply_plotly_theme, PLOTLY_FONT_SIZES
)


class SongVisualizations:
    """Visualizations for song-specific metrics."""

    @staticmethod
    def controversy_chart(
        data: "MusicLeagueData",
        round_id: Optional[str] = None,
        top_n: int = 10,
        interactive: bool = True
    ):
        """
        Horizontal bar chart of most controversial songs.
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            top_n: Number of top songs to show
            interactive: If True, return Plotly figure; else Matplotlib
            
        Returns:
            Plotly or Matplotlib figure
        """
        song_df = SongMetrics.get_all_song_metrics(data, round_id)

        if len(song_df) == 0:
            print("No songs found")
            return None

        top_songs = song_df.nlargest(top_n, 'controversy_score')

        if interactive:
            fig = go.Figure(go.Bar(
                x=top_songs['controversy_score'],
                y=top_songs['song_name'] + ' - ' + top_songs['artist'],
                orientation='h',
                marker=dict(color=COLORS_DICT['orange'])
            ))

            apply_plotly_theme(
                fig,
                title=f"Top {top_n} Most Controversial Songs",
                xaxis_title="Controversy Score (Std Dev of Votes)",
                yaxis_title="Song",
                height=500,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )

            return fig
        else:
            fig, ax = plt.subplots(figsize=(16, 9), dpi=200)
            y_pos = np.arange(len(top_songs))
            ax.barh(y_pos, top_songs['controversy_score'], color=COLORS_DICT['orange'])
            ax.set_yticks(y_pos)
            ax.set_yticklabels(top_songs['song_name'] + ' - ' + top_songs['artist'])
            configure_axes(ax, f'Top {top_n} Most Controversial Songs',
                         'Controversy Score (Std Dev)', 'Song')
            plt.tight_layout()
            return fig

    @staticmethod
    def vote_distribution_heatmap(
        data: "MusicLeagueData",
        round_id: Optional[str] = None,
        top_n: int = 15,
        interactive: bool = True
    ):
        """
        Heatmap showing vote distribution (count of each point value per song).
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            top_n: Number of top songs to show
            interactive: If True, return Plotly figure; else Matplotlib
            
        Returns:
            Plotly or Matplotlib figure
        """
        song_df = SongMetrics.get_all_song_metrics(data, round_id)

        if len(song_df) == 0:
            print("No songs found")
            return None

        top_songs = song_df.nlargest(top_n, 'total_points')
        vote_values = range(1, 6)
        
        matrix_data = []
        song_labels = []

        for _, song in top_songs.iterrows():
            dist = song['vote_distribution']
            row = [dist.get(val, 0) for val in vote_values]
            matrix_data.append(row)
            song_labels.append(f"{song['song_name'][:30]}...")

        matrix = np.array(matrix_data)

        if interactive:
            fig = go.Figure(data=go.Heatmap(
                z=matrix,
                x=[f"{v} points" for v in vote_values],
                y=song_labels,
                colorscale='Blues',
                text=matrix,
                texttemplate='%{text}',
                textfont={"size": PLOTLY_FONT_SIZES['heatmap_text']}
            ))

            apply_plotly_theme(
                fig,
                title=f"Vote Distribution - Top {top_n} Songs",
                xaxis_title="Points Awarded",
                yaxis_title="Song",
                height=600
            )

            return fig
        else:
            fig, ax = plt.subplots(figsize=(10, 12))
            sns.heatmap(
                matrix, annot=True, fmt='d', cmap='Blues',
                xticklabels=[f"{v}pts" for v in vote_values],
                yticklabels=song_labels, ax=ax
            )
            ax.set_title(f'Vote Distribution - Top {top_n} Songs')
            plt.tight_layout()
            return fig

    @staticmethod
    def mainstream_vs_underground_scatter(
        data: "MusicLeagueData",
        round_id: Optional[str] = None,
        interactive: bool = True
    ):
        """
        Scatter plot showing Spotify popularity vs total votes.
        
        Quadrants show: Popular hits, Popular flops, Obscure bangers, Obscure flops.
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            interactive: If True, return Plotly figure; else Matplotlib
            
        Returns:
            Plotly or Matplotlib figure
        """
        song_df = SongMetrics.get_all_song_metrics(data, round_id)

        if len(song_df) == 0:
            print("No songs found")
            return None

        median_pop = song_df['spotify_popularity'].median()
        median_votes = song_df['total_points'].median()

        if interactive:
            fig = px.scatter(
                song_df,
                x='spotify_popularity',
                y='total_points',
                hover_name='song_name',
                hover_data=['artist', 'submitter'],
                color='total_points',
                color_continuous_scale='Viridis',
                size='total_points',
                labels={
                    'spotify_popularity': 'Spotify Popularity',
                    'total_points': 'Total Votes'
                }
            )

            fig.add_hline(y=median_votes, line_dash="dash", line_color="gray", opacity=0.5)
            fig.add_vline(x=median_pop, line_dash="dash", line_color="gray", opacity=0.5)

            fig.add_annotation(x=75, y=median_votes * 1.5, text="Popular Hits",
                             showarrow=False, font=dict(size=PLOTLY_FONT_SIZES['annotation'], color="#7f8c8d"))
            fig.add_annotation(x=25, y=median_votes * 1.5, text="Obscure Bangers",
                             showarrow=False, font=dict(size=PLOTLY_FONT_SIZES['annotation'], color="#7f8c8d"))
            fig.add_annotation(x=75, y=median_votes * 0.5, text="Popular Flops",
                             showarrow=False, font=dict(size=PLOTLY_FONT_SIZES['annotation'], color="#7f8c8d"))
            fig.add_annotation(x=25, y=median_votes * 0.5, text="Obscure Flops",
                             showarrow=False, font=dict(size=PLOTLY_FONT_SIZES['annotation'], color="#7f8c8d"))

            apply_plotly_theme(fig, title="Mainstream vs. Underground", height=600)

            return fig
        else:
            fig, ax = plt.subplots(figsize=(12, 8))
            scatter = ax.scatter(
                song_df['spotify_popularity'],
                song_df['total_points'],
                s=song_df['total_points'] * 10,
                alpha=0.6,
                c=song_df['total_points'],
                cmap='viridis'
            )
            ax.axhline(median_votes, linestyle='--', color='gray', alpha=0.5)
            ax.axvline(median_pop, linestyle='--', color='gray', alpha=0.5)
            ax.set_xlabel('Spotify Popularity')
            ax.set_ylabel('Total Votes')
            ax.set_title('Mainstream vs. Underground')
            ax.text(75, median_votes * 1.3, 'Popular Hits', fontsize=12, color='gray')
            ax.text(20, median_votes * 1.3, 'Obscure Bangers', fontsize=12, color='gray')
            plt.colorbar(scatter, ax=ax, label='Total Points')
            plt.tight_layout()
            return fig

    @staticmethod
    def obscurity_score_chart(
        data: "MusicLeagueData",
        round_id: Optional[str] = None,
        top_n: int = 10,
        interactive: bool = True
    ):
        """
        Horizontal bar chart of hidden gems (high obscurity score).
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            top_n: Number of top songs to show
            interactive: If True, return Plotly figure; else Matplotlib
            
        Returns:
            Plotly or Matplotlib figure
        """
        song_df = SongMetrics.get_all_song_metrics(data, round_id)

        if len(song_df) == 0:
            print("No songs found")
            return None

        top_songs = song_df.nlargest(top_n, 'obscurity_score')

        if interactive:
            fig = go.Figure(go.Bar(
                x=top_songs['obscurity_score'],
                y=top_songs['song_name'] + ' - ' + top_songs['artist'],
                orientation='h',
                marker=dict(color=COLORS_DICT['green']),
                text=top_songs['spotify_popularity'],
                texttemplate='Pop: %{text}',
                textposition='outside'
            ))

            apply_plotly_theme(
                fig,
                title=f"Top {top_n} Hidden Gems (Obscurity Score)",
                xaxis_title="Obscurity Score (Votes / Popularity)",
                yaxis_title="Song",
                height=500,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )

            return fig
        else:
            fig, ax = plt.subplots(figsize=(16, 9), dpi=200)
            y_pos = np.arange(len(top_songs))
            ax.barh(y_pos, top_songs['obscurity_score'], color=COLORS_DICT['green'])
            ax.set_yticks(y_pos)
            ax.set_yticklabels(top_songs['song_name'] + ' - ' + top_songs['artist'])
            configure_axes(ax, f'Top {top_n} Hidden Gems', 'Obscurity Score', 'Song')
            plt.tight_layout()
            return fig

