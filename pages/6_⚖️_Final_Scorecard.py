"""
Final Scorecard Page - The Reckoning
Interactive scoring system to crown the ultimate champion.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from musicleague.dashboard import (
    setup_page, LEAGUE_COLORS,
    load_league_data,
    generate_final_verdict,
    DEFAULT_LEAGUES, format_league_name,
    apply_plotly_theme, PLOTLY_FONT_SIZES,
)
from musicleague.metrics.submitters import SubmitterMetrics
from musicleague.metrics.voters import VoterMetrics
from musicleague.metrics.network import NetworkMetrics
from musicleague.metrics.songs import SongMetrics

# Page setup
setup_page()

# Get leagues from session state
league1 = st.session_state.get('league1', DEFAULT_LEAGUES[0])
league2 = st.session_state.get('league2', DEFAULT_LEAGUES[1])
league1_display = format_league_name(league1)
league2_display = format_league_name(league2)

# CSS is loaded centrally via setup_page() from theme.py

# Page Header
st.markdown("""
<div class="page-header scorecard">
    <h1>The Reckoning</h1>
    <p>Set your priorities. Crown your champion. There can only be one.</p>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    data1 = load_league_data(league1)
    data2 = load_league_data(league2)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()


def normalize_metric(values: list[float]) -> list[float]:
    """Normalize values to 0-100 scale using min-max normalization."""
    if not values:
        return values
    min_val = min(values)
    max_val = max(values)
    if max_val == min_val:
        return [50.0] * len(values)  # All same value -> middle score
    return [((v - min_val) / (max_val - min_val)) * 100 for v in values]


def calculate_player_scores(data, weights):
    """Calculate weighted scores for each player in a league.

    All metrics are normalized to 0-100 using min-max scaling based on
    the actual data range, ensuring each metric contributes equally
    based on its weight regardless of its natural scale.
    """
    total_weight = sum(weights.values())
    if total_weight == 0:
        return pd.DataFrame()

    song_df = SongMetrics.get_all_song_metrics(data)
    influence_scores = NetworkMetrics.influence_score(data)

    # First pass: collect raw metric values for all players
    raw_data = []
    for player_id, player_info in data.competitors.items():
        player_name = player_info['name']

        avg_points = SubmitterMetrics.average_points_per_submission(data, player_id)
        underdog = SubmitterMetrics.underdog_factor(data, player_id)
        golden_ear = VoterMetrics.golden_ear_score(data, player_id)

        player_songs = song_df[song_df['submitter'] == player_name]
        avg_controversy = player_songs['controversy_score'].mean() if len(player_songs) > 0 else 0

        raw_influence = influence_scores.get(player_name, 0)

        raw_data.append({
            'player_name': player_name,
            'avg_points': avg_points,
            'underdog': underdog,
            'golden_ear': golden_ear,
            'avg_controversy': avg_controversy,
            'influence': raw_influence,
        })

    if not raw_data:
        return pd.DataFrame()

    # Extract raw values for normalization
    avg_points_raw = [d['avg_points'] for d in raw_data]
    underdog_raw = [d['underdog'] for d in raw_data]
    golden_ear_raw = [d['golden_ear'] for d in raw_data]
    controversy_raw = [d['avg_controversy'] for d in raw_data]
    influence_raw = [d['influence'] for d in raw_data]

    # Normalize each metric to 0-100 using min-max scaling
    points_norm = normalize_metric(avg_points_raw)
    deepcut_norm = normalize_metric(underdog_raw)
    taste_norm = normalize_metric(golden_ear_raw)
    controversy_norm = normalize_metric(controversy_raw)
    influence_norm = normalize_metric(influence_raw)

    # Second pass: build player data with normalized scores
    player_data = []
    for i, d in enumerate(raw_data):
        metrics = {
            'mainstream_hits': points_norm[i],
            'deep_cuts': deepcut_norm[i],
            'taste': taste_norm[i],
            'controversy': controversy_norm[i],
            'clout': influence_norm[i],
        }

        final_score = 0
        for metric, weight in weights.items():
            if metric in metrics:
                final_score += metrics[metric] * (weight / total_weight)

        player_data.append({
            'Player': d['player_name'],
            'Score': round(final_score, 1),
            'Avg Pts': round(points_norm[i], 1),
            'Deep Cut': round(deepcut_norm[i], 1),
            'Taste': round(taste_norm[i], 1),
            'Controversy': round(controversy_norm[i], 1),
            'Influence': round(influence_norm[i], 1),
        })

    df = pd.DataFrame(player_data)
    if len(df) > 0:
        df = df.sort_values('Score', ascending=False).reset_index(drop=True)
        df['Rank'] = range(1, len(df) + 1)
        df = df[['Rank', 'Player', 'Score', 'Avg Pts', 'Deep Cut', 'Taste', 'Controversy', 'Influence']]

    return df


# Sidebar controls for weighting
with st.sidebar:
    st.markdown("### The Matchup")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #2980b9 0%, #1a5276 100%); color: white; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem; text-align: center; font-weight: 600;">
        {league1_display}
    </div>
    <div style="text-align: center; font-weight: 900; color: #7f8c8d; margin: 0.25rem 0;">vs</div>
    <div style="background: linear-gradient(135deg, #c0392b 0%, #922b21 100%); color: white; padding: 0.75rem; border-radius: 8px; text-align: center; font-weight: 600;">
        {league2_display}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Set Your Weights")
    st.caption("What matters most to you?")

    weight_hits = st.slider("Avg Points/Song", 0, 100, 30, help="High-scoring submissions")
    weight_deep_cuts = st.slider("Deep Cut Cred", 0, 100, 20, help="Success with obscure tracks")
    weight_taste = st.slider("Trendsetter Score", 0, 100, 20, help="Voting for eventual winners")
    weight_controversy = st.slider("Controversy", 0, 100, 15, help="Submitting divisive tracks")
    weight_clout = st.slider("Network Influence", 0, 100, 15, help="Voting influence")

    weights = {
        'mainstream_hits': weight_hits,
        'deep_cuts': weight_deep_cuts,
        'taste': weight_taste,
        'controversy': weight_controversy,
        'clout': weight_clout,
    }

    total_weight = sum(weights.values())

    st.markdown("---")
    if total_weight > 0:
        st.markdown(f"**Total Weight: {total_weight}%**")
    else:
        st.warning("Set at least one weight above 0")

# Main content
if total_weight > 0:
    scores1 = calculate_player_scores(data1, weights)
    scores2 = calculate_player_scores(data2, weights)

    # =========================================================================
    # Champions Section
    # =========================================================================
    st.markdown("""
    <div class="section-header">
        <span class="icon">👑</span>
        <h2>The Champions</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if len(scores1) > 0:
            winner1 = scores1.iloc[0]
            margin1 = winner1['Score'] - scores1.iloc[1]['Score'] if len(scores1) > 1 else 0
            runner_up1 = scores1.iloc[1]['Player'] if len(scores1) > 1 else ""
            st.markdown(f"""
            <div class="champion-card blue">
                <div class="league">{league1_display}</div>
                <div class="name">{winner1['Player']}</div>
                <div class="score">{winner1['Score']:.1f}</div>
                <div class="margin">+{margin1:.1f} over {runner_up1}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No player data available")

    with col2:
        if len(scores2) > 0:
            winner2 = scores2.iloc[0]
            margin2 = winner2['Score'] - scores2.iloc[1]['Score'] if len(scores2) > 1 else 0
            runner_up2 = scores2.iloc[1]['Player'] if len(scores2) > 1 else ""
            st.markdown(f"""
            <div class="champion-card red">
                <div class="league">{league2_display}</div>
                <div class="name">{winner2['Player']}</div>
                <div class="score">{winner2['Score']:.1f}</div>
                <div class="margin">+{margin2:.1f} over {runner_up2}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No player data available")

    # Verdict
    if len(scores1) > 0 and len(scores2) > 0:
        verdict = generate_final_verdict(
            league1_display, league2_display,
            scores1.iloc[0]['Score'], scores2.iloc[0]['Score'],
            weights
        )
        st.markdown(f"""
        <div class="verdict-box">
            <div class="title">The Verdict</div>
            <div class="content">{verdict}</div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # Your Weights Visualization
    # =========================================================================
    st.markdown("""
    <div class="section-header">
        <span class="icon">⚖️</span>
        <h2>Your Scoring Formula</h2>
    </div>
    """, unsafe_allow_html=True)

    weight_data = [
        ("Avg Points/Song", weight_hits, "#667eea"),
        ("Deep Cut Cred", weight_deep_cuts, "#16a085"),
        ("Trendsetter Score", weight_taste, "#9b59b6"),
        ("Controversy", weight_controversy, "#e74c3c"),
        ("Network Influence", weight_clout, "#3498db"),
    ]

    for metric_name, value, color in weight_data:
        pct = value / total_weight * 100 if total_weight > 0 else 0
        st.markdown(f"""
        <div class="weight-card">
            <span class="metric">{metric_name}</span>
            <span class="value" style="color: {color};">{value}% ({pct:.0f}% of total)</span>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # Full Leaderboards
    # =========================================================================
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <span class="icon">📊</span>
        <h2>Full Leaderboards</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        if len(scores1) > 0:
            st.dataframe(
                scores1,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn(width="small"),
                    "Player": st.column_config.TextColumn(width="medium"),
                    "Score": st.column_config.NumberColumn(format="%.1f"),
                    "Avg Pts": st.column_config.NumberColumn(format="%.1f", width="small"),
                    "Deep Cut": st.column_config.NumberColumn(format="%.1f", width="small"),
                    "Taste": st.column_config.NumberColumn(format="%.1f", width="small"),
                    "Controversy": st.column_config.NumberColumn(format="%.1f", width="small"),
                    "Influence": st.column_config.NumberColumn(format="%.1f", width="small"),
                }
            )

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        if len(scores2) > 0:
            st.dataframe(
                scores2,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn(width="small"),
                    "Player": st.column_config.TextColumn(width="medium"),
                    "Score": st.column_config.NumberColumn(format="%.1f"),
                    "Avg Pts": st.column_config.NumberColumn(format="%.1f", width="small"),
                    "Deep Cut": st.column_config.NumberColumn(format="%.1f", width="small"),
                    "Taste": st.column_config.NumberColumn(format="%.1f", width="small"),
                    "Controversy": st.column_config.NumberColumn(format="%.1f", width="small"),
                    "Influence": st.column_config.NumberColumn(format="%.1f", width="small"),
                }
            )

    # =========================================================================
    # Score Distribution Charts
    # =========================================================================
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <span class="icon">📈</span>
        <h2>Score Distribution</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if len(scores1) > 0:
            fig1 = go.Figure(go.Bar(
                x=scores1['Score'],
                y=scores1['Player'],
                orientation='h',
                marker=dict(
                    color=scores1['Score'],
                    colorscale=[[0, '#1a5276'], [1, '#2980b9']],
                    showscale=False
                ),
                text=scores1['Score'].apply(lambda x: f"{x:.1f}"),
                textposition='outside'
            ))
            apply_plotly_theme(
                fig1,
                title=f"Final Scores - {league1_display}",
                height=max(350, len(scores1) * 35),
                xaxis_title="Score",
                yaxis_title="",
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(l=0, r=50, t=20, b=40)
            )
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        if len(scores2) > 0:
            fig2 = go.Figure(go.Bar(
                x=scores2['Score'],
                y=scores2['Player'],
                orientation='h',
                marker=dict(
                    color=scores2['Score'],
                    colorscale=[[0, '#922b21'], [1, '#c0392b']],
                    showscale=False
                ),
                text=scores2['Score'].apply(lambda x: f"{x:.1f}"),
                textposition='outside'
            ))
            apply_plotly_theme(
                fig2,
                title=f"Final Scores - {league2_display}",
                height=max(350, len(scores2) * 35),
                xaxis_title="Score",
                yaxis_title="",
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(l=0, r=50, t=20, b=40)
            )
            st.plotly_chart(fig2, use_container_width=True)

    # =========================================================================
    # Metric Breakdown
    # =========================================================================
    st.markdown("---")
    with st.expander("How Scores Are Calculated", expanded=False):
        st.markdown("""
        Each player is scored on 5 metrics using **min-max normalization** (0-100 scale based on
        the actual range within each league), then weighted by your preferences. This ensures each
        metric contributes equally based on its weight, regardless of its natural scale:
        """)

        metrics_info = [
            ("Avg Pts", "Average points received per submission", "#667eea"),
            ("Deep Cut", "Success with obscure, low-popularity tracks", "#16a085"),
            ("Taste", "Correlation between votes and final rankings (Golden Ear)", "#9b59b6"),
            ("Controversy", "Average controversy score of submitted songs", "#e74c3c"),
            ("Influence", "Network influence based on PageRank", "#3498db"),
        ]

        for name, desc, color in metrics_info:
            st.markdown(f"""
            <div class="metric-explainer" style="border-color: {color};">
                <div class="name">{name}</div>
                <div class="desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.info("Set weights in the sidebar to see player scores.")

    st.markdown("""
    <div class="section-header">
        <span class="icon">📋</span>
        <h2>Available Metrics</h2>
    </div>
    """, unsafe_allow_html=True)

    metrics_info = [
        ("Avg Points/Song", "How well do their submissions score?", "#667eea"),
        ("Deep Cut Cred", "Can they win with obscure tracks?", "#16a085"),
        ("Trendsetter Score", "Do they vote for eventual winners?", "#9b59b6"),
        ("Controversy", "Do they submit polarizing songs?", "#e74c3c"),
        ("Network Influence", "How much weight do their votes carry?", "#3498db"),
    ]

    for name, desc, color in metrics_info:
        st.markdown(f"""
        <div class="metric-explainer" style="border-color: {color};">
            <div class="name">{name}</div>
            <div class="desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
