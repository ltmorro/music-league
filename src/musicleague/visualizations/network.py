"""
Network visualizations for MusicLeague analysis.
"""

from typing import Optional, TYPE_CHECKING

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import plotly.graph_objects as go

if TYPE_CHECKING:
    from musicleague.data.loader import MusicLeagueData

from musicleague.metrics.network import NetworkMetrics
from musicleague.visualizations.base import (
    COLORS_DICT, configure_axes, apply_plotly_theme, PLOTLY_FONT_SIZES
)


class NetworkVisualizations:
    """Visualizations for network/relationship metrics."""

    @staticmethod
    def voting_network(
        data: "MusicLeagueData",
        round_id: Optional[str] = None,
        interactive: bool = True
    ):
        """
        Network graph showing voting relationships.

        Node size and color represent influence (PageRank).
        Edge width and opacity represent points exchanged.
        Uses a cohesive teal/green color palette.

        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            interactive: If True, return Plotly figure; else Matplotlib

        Returns:
            Plotly or Matplotlib figure
        """
        G = NetworkMetrics.build_voting_graph(data, round_id)

        if len(G.nodes()) == 0:
            return None

        # Calculate influence scores for node sizing/coloring
        influence = NetworkMetrics.influence_score(data, round_id)

        # Normalize influence for sizing (min 25, max 60)
        influence_values = list(influence.values())
        if influence_values:
            min_inf = min(influence_values)
            max_inf = max(influence_values)
            inf_range = max_inf - min_inf if max_inf != min_inf else 1
        else:
            min_inf, inf_range = 0, 1

        if interactive:
            # Use Kamada-Kawai for more aesthetic layout
            try:
                pos = nx.kamada_kawai_layout(G)
            except Exception:
                pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)

            # Get edge weights for normalization
            edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
            max_weight = max(edge_weights) if edge_weights else 1
            min_weight = min(edge_weights) if edge_weights else 0
            weight_range = max_weight - min_weight if max_weight != min_weight else 1

            # Create curved edges with varying width/opacity based on weight
            edge_traces = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                weight = G[edge[0]][edge[1]]['weight']
                norm_weight = (weight - min_weight) / weight_range

                # Width: 0.5-4 based on weight
                edge_width = 0.5 + norm_weight * 3.5

                # Opacity: 0.15-0.6 based on weight
                edge_opacity = 0.15 + norm_weight * 0.45

                mid_x = (x0 + x1) / 2
                mid_y = (y0 + y1) / 2
                dx = x1 - x0
                dy = y1 - y0
                length = np.sqrt(dx**2 + dy**2)
                if length > 0:
                    offset = 0.1 * length
                    ctrl_x = mid_x - dy / length * offset
                    ctrl_y = mid_y + dx / length * offset
                else:
                    ctrl_x, ctrl_y = mid_x, mid_y

                t_vals = np.linspace(0, 1, 15)
                curve_x = (1-t_vals)**2 * x0 + 2*(1-t_vals)*t_vals * ctrl_x + t_vals**2 * x1
                curve_y = (1-t_vals)**2 * y0 + 2*(1-t_vals)*t_vals * ctrl_y + t_vals**2 * y1

                edge_traces.append(go.Scatter(
                    x=list(curve_x) + [None],
                    y=list(curve_y) + [None],
                    mode='lines',
                    line=dict(
                        width=edge_width,
                        color=f'rgba(29, 185, 184, {edge_opacity})',
                    ),
                    hoverinfo='text',
                    hovertext=f"{edge[0]} → {edge[1]}<br><b>{int(weight)} pts</b>",
                    showlegend=False,
                ))

            # Build node data with influence-based sizing and coloring
            node_x = []
            node_y = []
            node_sizes = []
            node_colors = []
            node_text = []
            hover_text = []

            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)

                node_influence = influence.get(node, min_inf)
                norm_inf = (node_influence - min_inf) / inf_range

                # Size: 25-55 based on influence
                size = 25 + norm_inf * 30
                node_sizes.append(size)
                node_colors.append(norm_inf)
                node_text.append(node)

                # Calculate node stats for hover
                in_edges = G.in_edges(node, data=True) if G.is_directed() else []
                out_edges = G.out_edges(node, data=True) if G.is_directed() else []
                pts_received = sum(d['weight'] for _, _, d in in_edges) if in_edges else 0
                pts_given = sum(d['weight'] for _, _, d in out_edges) if out_edges else 0

                hover_text.append(
                    f"<b>{node}</b><br>"
                    f"Influence: {node_influence:.3f}<br>"
                    f"Received: {int(pts_received)} pts<br>"
                    f"Given: {int(pts_given)} pts"
                )

            # Node trace with clean teal gradient
            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers+text',
                text=node_text,
                textposition="top center",
                textfont=dict(
                    size=11,
                    color='rgba(236, 240, 241, 0.9)',
                    family="SpotifyMix, sans-serif",
                ),
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    colorscale=[
                        [0, '#1a5276'],      # Dark blue (low influence)
                        [0.5, '#1db954'],    # Spotify green (mid)
                        [1, '#1ed760'],      # Bright green (high influence)
                    ],
                    showscale=True,
                    colorbar=dict(
                        title=dict(
                            text="Influence",
                            font=dict(size=12, color='#ecf0f1'),
                        ),
                        tickfont=dict(size=10, color='#bdc3c7'),
                        thickness=12,
                        len=0.4,
                        x=1.02,
                        outlinewidth=0,
                    ),
                    line=dict(width=2, color='rgba(255, 255, 255, 0.6)'),
                ),
                hoverinfo='text',
                hovertext=hover_text,
            )

            fig = go.Figure(data=edge_traces + [node_trace])

            apply_plotly_theme(
                fig,
                title="Voting Network",
                showlegend=False,
                hovermode='closest',
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                    scaleanchor="y",
                    scaleratio=1,
                ),
                yaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                ),
                height=700,
            )

            return fig
        else:
            fig, ax = plt.subplots(figsize=(12, 12))
            try:
                pos = nx.kamada_kawai_layout(G)
            except Exception:
                pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)

            # Node sizes based on influence
            node_sizes = []
            node_colors = []
            for node in G.nodes():
                node_inf = influence.get(node, min_inf)
                norm_inf = (node_inf - min_inf) / inf_range
                node_sizes.append(400 + norm_inf * 1000)
                node_colors.append(norm_inf)

            edges = G.edges()
            weights = [G[u][v]['weight'] for u, v in edges]
            max_w = max(weights) if weights else 1

            # Draw edges with teal color, varying alpha
            for (u, v), w in zip(edges, weights):
                norm_w = w / max_w
                alpha = 0.15 + norm_w * 0.45
                nx.draw_networkx_edges(
                    G, pos, edgelist=[(u, v)],
                    width=0.5 + norm_w * 3,
                    alpha=alpha,
                    edge_color='#1db954',
                    ax=ax,
                    connectionstyle="arc3,rad=0.1",
                )

            # Custom colormap: dark blue to green
            from matplotlib.colors import LinearSegmentedColormap
            colors_list = ['#1a5276', '#1db954', '#1ed760']
            cmap = LinearSegmentedColormap.from_list('influence', colors_list)

            nx.draw_networkx_nodes(
                G, pos,
                node_size=node_sizes,
                node_color=node_colors,
                cmap=cmap,
                alpha=0.95,
                edgecolors='white',
                linewidths=1.5,
                ax=ax
            )

            nx.draw_networkx_labels(G, pos, font_size=9, font_color='#ecf0f1', ax=ax)

            ax.set_title('Voting Network', fontsize=14)
            ax.axis('off')
            plt.tight_layout()
            return fig

    @staticmethod
    def influence_score_chart(
        data: "MusicLeagueData",
        round_id: Optional[str] = None,
        interactive: bool = True
    ):
        """
        Horizontal bar chart of influence scores (PageRank).
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            interactive: If True, return Plotly figure; else Matplotlib
            
        Returns:
            Plotly or Matplotlib figure
        """
        influence = NetworkMetrics.influence_score(data, round_id)

        sorted_voters = sorted(influence.items(), key=lambda x: x[1], reverse=True)
        names = [v[0] for v in sorted_voters[:15]]
        scores = [v[1] for v in sorted_voters[:15]]

        if interactive:
            fig = go.Figure(go.Bar(
                x=scores,
                y=names,
                orientation='h',
                marker=dict(color=COLORS_DICT['gold'])
            ))

            apply_plotly_theme(
                fig,
                title="Influence Score (PageRank)",
                xaxis_title="Influence Score",
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
            configure_axes(ax, 'Influence Score (PageRank)', 'Influence Score', 'Voter')
            plt.tight_layout()
            return fig

