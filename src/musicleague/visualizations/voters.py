"""
Voter-specific visualizations for MusicLeague analysis.
"""

from typing import Optional, TYPE_CHECKING

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

if TYPE_CHECKING:
    from musicleague.data.loader import MusicLeagueData

from musicleague.metrics.voters import VoterMetrics
from musicleague.visualizations.base import (
    COLORS_DICT, configure_axes, apply_plotly_theme, PLOTLY_FONT_SIZES
)


class VoterVisualizations:
    """Visualizations for voter-specific metrics."""

    @staticmethod
    def similarity_heatmap(
        data: "MusicLeagueData",
        round_id: Optional[str] = None,
        interactive: bool = True
    ):
        """
        Clustered heatmap showing voter similarity (correlation).
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            interactive: If True, return Plotly figure; else Matplotlib
            
        Returns:
            Plotly or Matplotlib figure
        """
        sim_matrix = VoterMetrics.voter_similarity_matrix(data, round_id)

        if len(sim_matrix) == 0:
            print("No voters found")
            return None

        if interactive:
            fig = go.Figure(data=go.Heatmap(
                z=sim_matrix.values,
                x=sim_matrix.columns,
                y=sim_matrix.index,
                colorscale='RdBu',
                zmid=0,
                text=np.round(sim_matrix.values, 2),
                texttemplate='%{text}',
                textfont={"size": PLOTLY_FONT_SIZES['heatmap_text']}
            ))

            apply_plotly_theme(
                fig,
                title="Voter Similarity Matrix (Spearman Correlation)",
                xaxis_title="Voter",
                yaxis_title="Voter",
                height=700,
                width=700
            )

            return fig
        else:
            fig, ax = plt.subplots(figsize=(12, 10))
            sns.heatmap(
                sim_matrix, annot=True, fmt='.2f', cmap='RdBu_r',
                center=0, ax=ax, square=True
            )
            ax.set_title('Voter Similarity Matrix')
            plt.tight_layout()
            return fig

    @staticmethod
    def golden_ear_chart(
        data: "MusicLeagueData",
        round_id: Optional[str] = None,
        interactive: bool = True
    ):
        """
        Horizontal bar chart of golden ear scores (tastemakers).
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            interactive: If True, return Plotly figure; else Matplotlib
            
        Returns:
            Plotly or Matplotlib figure
        """
        voter_scores = {}
        for voter_id, voter_data in data.competitors.items():
            score = VoterMetrics.golden_ear_score(data, voter_id, round_id)
            voter_scores[voter_data['name']] = score

        sorted_voters = sorted(voter_scores.items(), key=lambda x: x[1], reverse=True)
        names = [v[0] for v in sorted_voters]
        scores = [v[1] for v in sorted_voters]

        if interactive:
            colors = [
                COLORS_DICT['green'] if s > 0 else COLORS_DICT['red']
                for s in scores
            ]

            fig = go.Figure(go.Bar(
                x=scores,
                y=names,
                orientation='h',
                marker=dict(color=colors)
            ))

            apply_plotly_theme(
                fig,
                title="Golden Ear Score (Tastemaker)",
                xaxis_title="Correlation with Final Rankings",
                yaxis_title="Voter",
                height=600,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )

            return fig
        else:
            fig, ax = plt.subplots(figsize=(16, 9), dpi=200)
            colors = [
                COLORS_DICT['green'] if s > 0 else COLORS_DICT['red']
                for s in scores
            ]
            y_pos = np.arange(len(names))
            ax.barh(y_pos, scores, color=colors)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names)
            configure_axes(ax, 'Golden Ear Score (Tastemaker)', 'Correlation Score', 'Voter')
            ax.axvline(0, color='black', linewidth=0.5)
            plt.tight_layout()
            return fig

    @staticmethod
    def hipster_score_chart(
        data: "MusicLeagueData",
        round_id: Optional[str] = None,
        interactive: bool = True
    ):
        """
        Horizontal bar chart of hipster scores.
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            interactive: If True, return Plotly figure; else Matplotlib
            
        Returns:
            Plotly or Matplotlib figure
        """
        voter_scores = {}
        for voter_id, voter_data in data.competitors.items():
            score = VoterMetrics.hipster_score(data, voter_id, round_id)
            voter_scores[voter_data['name']] = score

        sorted_voters = sorted(voter_scores.items(), key=lambda x: x[1], reverse=True)
        names = [v[0] for v in sorted_voters]
        scores = [v[1] for v in sorted_voters]

        if interactive:
            fig = go.Figure(go.Bar(
                x=scores,
                y=names,
                orientation='h',
                marker=dict(color=COLORS_DICT['gold'])
            ))

            apply_plotly_theme(
                fig,
                title="Hipster Score (Obscure Track Preference)",
                xaxis_title="Hipster Score",
                yaxis_title="Voter",
                height=600,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )

            return fig
        else:
            fig, ax = plt.subplots(figsize=(16, 9), dpi=200)
            y_pos = np.arange(len(names))
            ax.barh(y_pos, scores, color=COLORS_DICT['gold'])
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names)
            configure_axes(ax, 'Hipster Score', 'Hipster Score', 'Voter')
            plt.tight_layout()
            return fig

    @staticmethod
    def generosity_chart(
        data: "MusicLeagueData",
        round_id: Optional[str] = None,
        interactive: bool = True
    ):
        """
        Bar chart of generosity scores with error bars.
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            interactive: If True, return Plotly figure; else Matplotlib
            
        Returns:
            Plotly or Matplotlib figure
        """
        voter_stats = {}
        for voter_id, voter_data in data.competitors.items():
            mean, std = VoterMetrics.generosity_score(data, voter_id, round_id)
            voter_stats[voter_data['name']] = (mean, std)

        sorted_voters = sorted(voter_stats.items(), key=lambda x: x[1][0], reverse=True)
        names = [v[0] for v in sorted_voters]
        means = [v[1][0] for v in sorted_voters]
        stds = [v[1][1] for v in sorted_voters]

        if interactive:
            fig = go.Figure()

            fig.add_trace(go.Bar(
                y=names,
                x=means,
                orientation='h',
                marker=dict(color=COLORS_DICT['blue']),
                error_x=dict(type='data', array=stds, visible=True)
            ))

            apply_plotly_theme(
                fig,
                title="Generosity Score (Average Points Given)",
                xaxis_title="Average Points",
                yaxis_title="Voter",
                height=600,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )

            return fig
        else:
            fig, ax = plt.subplots(figsize=(16, 9), dpi=200)
            y_pos = np.arange(len(names))
            ax.barh(y_pos, means, xerr=stds, color=COLORS_DICT['blue'], alpha=0.7)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names)
            configure_axes(ax, 'Generosity Score', 'Average Points Given', 'Voter')
            plt.tight_layout()
            return fig

    @staticmethod
    def loyalty_heatmap(
        data: "MusicLeagueData",
        round_id: Optional[str] = None,
        interactive: bool = True
    ):
        """
        Heatmap showing which voters prefer which submitters.
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            interactive: If True, return Plotly figure; else Matplotlib
            
        Returns:
            Plotly or Matplotlib figure
        """
        voter_ids = list(data.competitors.keys())
        submitter_ids = list(data.competitors.keys())

        matrix_data = []
        voter_names = []

        for voter_id in voter_ids:
            loyalty = VoterMetrics.loyalty_index(data, voter_id, round_id)
            voter_name = data.competitors[voter_id]['name']
            voter_names.append(voter_name)

            row = []
            for submitter_id in submitter_ids:
                submitter_name = data.competitors[submitter_id]['name']
                row.append(loyalty.get(submitter_name, 0.0))

            matrix_data.append(row)

        submitter_names = [data.competitors[sid]['name'] for sid in submitter_ids]
        matrix = np.array(matrix_data)

        if interactive:
            fig = go.Figure(data=go.Heatmap(
                z=matrix,
                x=submitter_names,
                y=voter_names,
                colorscale='YlOrRd',
                text=np.round(matrix, 1),
                texttemplate='%{text}',
                textfont={"size": PLOTLY_FONT_SIZES['heatmap_text']}
            ))

            apply_plotly_theme(
                fig,
                title="Loyalty Index (Avg Points Given to Each Submitter)",
                xaxis_title="Submitter",
                yaxis_title="Voter",
                height=700,
                width=800
            )

            return fig
        else:
            fig, ax = plt.subplots(figsize=(14, 12))
            sns.heatmap(
                matrix, annot=True, fmt='.1f', cmap='YlOrRd',
                xticklabels=submitter_names, yticklabels=voter_names, ax=ax
            )
            ax.set_title('Loyalty Index')
            plt.tight_layout()
            return fig

