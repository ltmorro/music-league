"""
Submitter-specific visualizations for MusicLeague analysis.
"""

from typing import List, Optional, TYPE_CHECKING

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

if TYPE_CHECKING:
    from musicleague.data.loader import MusicLeagueData

from musicleague.metrics.submitters import SubmitterMetrics
from musicleague.metrics.comparisons import CrossRoundMetrics
from musicleague.visualizations.base import (
    COLORS_DICT, configure_axes, apply_plotly_theme, PLOTLY_FONT_SIZES
)


class SubmitterVisualizations:
    """Visualizations for submitter-specific metrics."""

    @staticmethod
    def average_points_chart(
        data: "MusicLeagueData",
        round_id: Optional[str] = None,
        interactive: bool = True
    ):
        """
        Horizontal bar chart of average points per submission.
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            interactive: If True, return Plotly figure; else Matplotlib
            
        Returns:
            Plotly or Matplotlib figure
        """
        submitter_stats = {}
        for submitter_id, submitter_data in data.competitors.items():
            avg_points = SubmitterMetrics.average_points_per_submission(
                data, submitter_id, round_id
            )
            if avg_points > 0:
                submitter_stats[submitter_data['name']] = avg_points

        sorted_submitters = sorted(submitter_stats.items(), key=lambda x: x[1], reverse=True)
        names = [s[0] for s in sorted_submitters]
        avgs = [s[1] for s in sorted_submitters]

        if interactive:
            fig = go.Figure(go.Bar(
                x=avgs,
                y=names,
                orientation='h',
                marker=dict(color=COLORS_DICT['green'])
            ))

            apply_plotly_theme(
                fig,
                title="Average Points Per Submission",
                xaxis_title="Average Points",
                yaxis_title="Submitter",
                height=600,
                showlegend=False
            )

            return fig
        else:
            fig, ax = plt.subplots(figsize=(16, 9), dpi=200)
            y_pos = np.arange(len(names))
            ax.barh(y_pos, avgs, color=COLORS_DICT['green'])
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names)
            configure_axes(ax, 'Average Points Per Submission', 'Average Points', 'Submitter')
            plt.tight_layout()
            return fig

    @staticmethod
    def consistency_scatter(
        data: "MusicLeagueData",
        round_id: Optional[str] = None,
        interactive: bool = True
    ):
        """
        Scatter plot: X=average points, Y=std dev (consistency).
        
        Quadrants show: consistent winners, boom-or-bust, etc.
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            interactive: If True, return Plotly figure; else Matplotlib
            
        Returns:
            Plotly or Matplotlib figure
        """
        submitter_stats = []
        for submitter_id, submitter_data in data.competitors.items():
            avg, std = SubmitterMetrics.consistency_score(data, submitter_id, round_id)
            if avg > 0:
                submitter_stats.append({
                    'name': submitter_data['name'],
                    'avg_points': avg,
                    'std_dev': std
                })

        df = pd.DataFrame(submitter_stats)

        if len(df) == 0:
            print("No submitters found")
            return None

        if interactive:
            fig = px.scatter(
                df,
                x='avg_points',
                y='std_dev',
                text='name',
                labels={
                    'avg_points': 'Average Points',
                    'std_dev': 'Standard Deviation'
                },
                hover_data=['name']
            )

            fig.update_traces(textposition='top center')

            median_avg = df['avg_points'].median()
            median_std = df['std_dev'].median()
            fig.add_vline(x=median_avg, line_dash="dash", line_color="gray", opacity=0.5)
            fig.add_hline(y=median_std, line_dash="dash", line_color="gray", opacity=0.5)

            apply_plotly_theme(
                fig,
                title="Submitter Consistency (Avg vs. Std Dev)",
                height=600
            )

            return fig
        else:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.scatter(df['avg_points'], df['std_dev'], s=100, alpha=0.7)

            for _, row in df.iterrows():
                ax.annotate(
                    row['name'], (row['avg_points'], row['std_dev']),
                    fontsize=8, alpha=0.7
                )

            ax.set_xlabel('Average Points')
            ax.set_ylabel('Standard Deviation')
            ax.set_title('Submitter Consistency')
            plt.tight_layout()
            return fig

    @staticmethod
    def performance_trajectory(
        data: "MusicLeagueData",
        round_ids: List[str],
        interactive: bool = True
    ):
        """
        Slope chart showing submitter performance trajectory across rounds.
        
        Args:
            data: MusicLeagueData object
            round_ids: List of round IDs to compare
            interactive: If True, return Plotly figure; else Matplotlib
            
        Returns:
            Plotly or Matplotlib figure
        """
        submitter_trajectories = []

        for submitter_id, submitter_data in data.competitors.items():
            trajectory = CrossRoundMetrics.submitter_performance_trajectory(
                data, submitter_id, round_ids
            )

            if len(trajectory) >= 2:
                submitter_trajectories.append({
                    'name': submitter_data['name'],
                    'round1': trajectory.get(round_ids[0], 0),
                    'round2': trajectory.get(round_ids[1], 0)
                })

        df = pd.DataFrame(submitter_trajectories)

        if len(df) == 0:
            print("No submitters with multi-round data found")
            return None

        df['change'] = df['round2'] - df['round1']
        df['improved'] = df['change'] > 0

        if interactive:
            fig = go.Figure()

            for _, row in df.iterrows():
                color = (
                    COLORS_DICT['green'] if row['improved']
                    else COLORS_DICT['red']
                )
                fig.add_trace(go.Scatter(
                    x=['Round 1', 'Round 2'],
                    y=[row['round1'], row['round2']],
                    mode='lines+markers+text',
                    name=row['name'],
                    line=dict(color=color),
                    text=['', row['name']],
                    textposition='middle right'
                ))

            apply_plotly_theme(
                fig,
                title="Submitter Performance Trajectory",
                xaxis_title="Round",
                yaxis_title="Average Points",
                height=600,
                showlegend=False
            )

            return fig
        else:
            fig, ax = plt.subplots(figsize=(16, 9), dpi=200)

            for _, row in df.iterrows():
                color = (
                    COLORS_DICT['green'] if row['improved']
                    else COLORS_DICT['red']
                )
                ax.plot([0, 1], [row['round1'], row['round2']],
                       marker='o', color=color, alpha=0.6)
                ax.text(1.05, row['round2'], row['name'], fontsize=8, va='center')

            ax.set_xticks([0, 1])
            ax.set_xticklabels(['Round 1', 'Round 2'])
            configure_axes(ax, 'Submitter Performance Trajectory', 'Round', 'Average Points')
            plt.tight_layout()
            return fig

