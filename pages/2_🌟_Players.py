"""
Players Page - The Roster
Submitter performance, voting patterns, and taste profiles.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from musicleague.dashboard import (
    setup_page, LEAGUE_COLORS,
    load_league_data, get_submitter_rankings, get_voter_rankings,
    generate_submitter_commentary, generate_voter_shift_commentary,
    DEFAULT_LEAGUES, format_league_name,
    apply_plotly_theme, PLOTLY_FONT_SIZES,
)
from musicleague.visualizations import SubmitterVisualizations, VoterVisualizations

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
<div class="page-header players">
    <h1>The Roster</h1>
    <p>Every player has a style. Here's what the numbers say about theirs.</p>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    data1 = load_league_data(league1)
    data2 = load_league_data(league2)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Get rankings data
submitters_l1 = get_submitter_rankings(data1)
submitters_l2 = get_submitter_rankings(data2)
voters_l1 = get_voter_rankings(data1)
voters_l2 = get_voter_rankings(data2)

# Quick stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_players = len(data1.competitors) + len(data2.competitors)
    st.markdown(f"""
    <div class="stat-highlight">
        <div class="number">{total_players}</div>
        <div class="label">Total Players</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if len(submitters_l1) > 0 and len(submitters_l2) > 0:
        top_score = max(submitters_l1['A&R Score'].max(), submitters_l2['A&R Score'].max())
    else:
        top_score = 0
    st.markdown(f"""
    <div class="stat-highlight green">
        <div class="number">{top_score:.1f}</div>
        <div class="label">Top A&R Score</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if len(voters_l1) > 0 and len(voters_l2) > 0:
        top_trend = max(voters_l1['Trendsetter'].max(), voters_l2['Trendsetter'].max())
    else:
        top_trend = 0
    st.markdown(f"""
    <div class="stat-highlight purple">
        <div class="number">{top_trend:.3f}</div>
        <div class="label">Top Trendsetter</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    if len(voters_l1) > 0 and len(voters_l2) > 0:
        top_hipster = max(voters_l1['Obscurity Cred'].max(), voters_l2['Obscurity Cred'].max())
    else:
        top_hipster = 0
    st.markdown(f"""
    <div class="stat-highlight red">
        <div class="number">{top_hipster:.0f}</div>
        <div class="label">Top Obscurity</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["Submitters", "Voting Patterns", "Taste Profiles"])

# =============================================================================
# Tab 1: Submitters
# =============================================================================
with tab1:
    st.markdown("""
    <div class="section-header">
        <span class="icon">🎤</span>
        <h2>The Curators</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Who picks the songs that resonate? Ranked by average points per submission.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        if len(submitters_l1) > 0:
            # Top 3 as cards
            for _, row in submitters_l1.head(3).iterrows():
                st.markdown(f"""
                <div class="player-card">
                    <span class="rank">#{int(row['Rank'])}</span>
                    <div class="name">{row['Submitter']}</div>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-value">{row['A&R Score']:.1f}</div>
                            <div class="stat-label">A&R Score</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{row['Consistency']:.1f}</div>
                            <div class="stat-label">Consistency</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{row['Deep Cut Cred']:.0f}</div>
                            <div class="stat-label">Deep Cuts</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Chart
            fig = px.bar(
                submitters_l1.head(10),
                x='A&R Score',
                y='Submitter',
                orientation='h',
                color_discrete_sequence=[LEAGUE_COLORS.get(league1, '#2980b9')]
            )
            apply_plotly_theme(
                fig,
                title=f"A&R Score Rankings - {league1_display}",
                height=400,
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No submitter data")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        if len(submitters_l2) > 0:
            # Top 3 as cards
            for _, row in submitters_l2.head(3).iterrows():
                st.markdown(f"""
                <div class="player-card">
                    <span class="rank">#{int(row['Rank'])}</span>
                    <div class="name">{row['Submitter']}</div>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-value">{row['A&R Score']:.1f}</div>
                            <div class="stat-label">A&R Score</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{row['Consistency']:.1f}</div>
                            <div class="stat-label">Consistency</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{row['Deep Cut Cred']:.0f}</div>
                            <div class="stat-label">Deep Cuts</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Chart
            fig = px.bar(
                submitters_l2.head(10),
                x='A&R Score',
                y='Submitter',
                orientation='h',
                color_discrete_sequence=[LEAGUE_COLORS.get(league2, '#c0392b')]
            )
            apply_plotly_theme(
                fig,
                title=f"A&R Score Rankings - {league2_display}",
                height=400,
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No submitter data")

    # Commentary
    st.markdown("---")
    st.info(generate_submitter_commentary(data1, data2, league1_display, league2_display))

    # Consistency scatter
    st.markdown("""
    <div class="section-header">
        <span class="icon">📊</span>
        <h2>Consistency Check</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Average score vs. variance. Bottom-left = reliable. Top-right = volatile.")

    col1, col2 = st.columns(2)

    with col1:
        try:
            fig1 = SubmitterVisualizations.consistency_scatter(data1, interactive=True)
            if fig1:
                fig1.update_traces(marker=dict(color=LEAGUE_COLORS.get(league1, '#2980b9')))
                fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig1, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate chart: {e}")

    with col2:
        try:
            fig2 = SubmitterVisualizations.consistency_scatter(data2, interactive=True)
            if fig2:
                fig2.update_traces(marker=dict(color=LEAGUE_COLORS.get(league2, '#c0392b')))
                fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate chart: {e}")

# =============================================================================
# Tab 2: Voting Patterns
# =============================================================================
with tab2:
    st.markdown("""
    <div class="section-header">
        <span class="icon">🔮</span>
        <h2>The Trendsetters</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Positive correlation with final rankings = they see winners before others do.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        if len(voters_l1) > 0:
            top_trendsetters_l1 = voters_l1.nlargest(10, 'Trendsetter')

            # Highlight top trendsetter
            top = top_trendsetters_l1.iloc[0]
            st.markdown(f"""
            <div class="stat-highlight purple">
                <div class="label">Top Trendsetter</div>
                <div style="font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">{top['Voter']}</div>
                <div class="number">{top['Trendsetter']:.3f}</div>
            </div>
            """, unsafe_allow_html=True)

            fig = px.bar(
                top_trendsetters_l1,
                x='Trendsetter',
                y='Voter',
                orientation='h',
                color_discrete_sequence=[LEAGUE_COLORS.get(league1, '#2980b9')]
            )
            apply_plotly_theme(fig, title=f"Trendsetter Rankings - {league1_display}", height=350, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        if len(voters_l2) > 0:
            top_trendsetters_l2 = voters_l2.nlargest(10, 'Trendsetter')

            top = top_trendsetters_l2.iloc[0]
            st.markdown(f"""
            <div class="stat-highlight purple">
                <div class="label">Top Trendsetter</div>
                <div style="font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">{top['Voter']}</div>
                <div class="number">{top['Trendsetter']:.3f}</div>
            </div>
            """, unsafe_allow_html=True)

            fig = px.bar(
                top_trendsetters_l2,
                x='Trendsetter',
                y='Voter',
                orientation='h',
                color_discrete_sequence=[LEAGUE_COLORS.get(league2, '#c0392b')]
            )
            apply_plotly_theme(fig, title=f"Trendsetter Rankings - {league2_display}", height=350, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

    # Contrarians
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <span class="icon">🎭</span>
        <h2>The Contrarians</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Negative correlation = they vote against the crowd.")

    col1, col2 = st.columns(2)

    with col1:
        if len(voters_l1) > 0:
            rebels_l1 = voters_l1.nsmallest(5, 'Trendsetter')
            for _, row in rebels_l1.iterrows():
                trend_class = "trend-down" if row['Trendsetter'] < 0 else "trend-neutral"
                st.markdown(f"""
                <div class="connection-card" style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="voter">{row['Voter']}</span>
                    <span class="change {trend_class}">{row['Trendsetter']:.3f}</span>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        if len(voters_l2) > 0:
            rebels_l2 = voters_l2.nsmallest(5, 'Trendsetter')
            for _, row in rebels_l2.iterrows():
                trend_class = "trend-down" if row['Trendsetter'] < 0 else "trend-neutral"
                st.markdown(f"""
                <div class="connection-card" style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="voter">{row['Voter']}</span>
                    <span class="change {trend_class}">{row['Trendsetter']:.3f}</span>
                </div>
                """, unsafe_allow_html=True)

    # Generosity
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <span class="icon">🎁</span>
        <h2>Generosity</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Average points given per vote. Who's generous? Who's stingy?")

    col1, col2 = st.columns(2)

    with col1:
        try:
            fig1 = VoterVisualizations.generosity_chart(data1, interactive=True)
            if fig1:
                fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig1, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate chart: {e}")

    with col2:
        try:
            fig2 = VoterVisualizations.generosity_chart(data2, interactive=True)
            if fig2:
                fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate chart: {e}")

# =============================================================================
# Tab 3: Taste Profiles
# =============================================================================
with tab3:
    st.markdown("""
    <div class="section-header">
        <span class="icon">🕵️</span>
        <h2>Obscurity Cred</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Who votes for the deep cuts? High score = preference for low-popularity tracks.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        if len(voters_l1) > 0:
            hipsters_l1 = voters_l1.nlargest(10, 'Obscurity Cred')

            # Top hipster card
            top = hipsters_l1.iloc[0]
            st.markdown(f"""
            <div class="stat-highlight dark">
                <div class="label">Most Obscure Taste</div>
                <div style="font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">{top['Voter']}</div>
                <div class="number text-green">{top['Obscurity Cred']:.0f}</div>
            </div>
            """, unsafe_allow_html=True)

            st.dataframe(hipsters_l1[['Voter', 'Obscurity Cred']], use_container_width=True, hide_index=True)

        try:
            fig1 = VoterVisualizations.hipster_score_chart(data1, interactive=True)
            if fig1:
                fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig1, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate chart: {e}")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        if len(voters_l2) > 0:
            hipsters_l2 = voters_l2.nlargest(10, 'Obscurity Cred')

            top = hipsters_l2.iloc[0]
            st.markdown(f"""
            <div class="stat-highlight dark">
                <div class="label">Most Obscure Taste</div>
                <div style="font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">{top['Voter']}</div>
                <div class="number text-green">{top['Obscurity Cred']:.0f}</div>
            </div>
            """, unsafe_allow_html=True)

            st.dataframe(hipsters_l2[['Voter', 'Obscurity Cred']], use_container_width=True, hide_index=True)

        try:
            fig2 = VoterVisualizations.hipster_score_chart(data2, interactive=True)
            if fig2:
                fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate chart: {e}")

    # Shift commentary
    st.markdown("---")
    st.info(generate_voter_shift_commentary(data1, data2, league1_display, league2_display, metric='hipster'))

    # Voter similarity
    st.markdown("""
    <div class="section-header">
        <span class="icon">🤝</span>
        <h2>Voter Similarity</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Who has similar taste? Darker = more similar voting patterns.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**{league1_display}**")
        try:
            fig1 = VoterVisualizations.similarity_heatmap(data1, interactive=True)
            if fig1:
                st.plotly_chart(fig1, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate heatmap: {e}")

    with col2:
        st.markdown(f"**{league2_display}**")
        try:
            fig2 = VoterVisualizations.similarity_heatmap(data2, interactive=True)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate heatmap: {e}")

# =============================================================================
# Sidebar
# =============================================================================
with st.sidebar:
    st.markdown("### The Matchup")
    st.markdown(f"""
    <div class="matchup-box">
        <div class="league-name blue">{league1_display}</div>
        <div class="vs">vs</div>
        <div class="league-name red">{league2_display}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    **What You're Seeing:**

    **Submitters** - Avg points per submission (A&R Score)

    **Voting Patterns** - Trendsetter scores, generosity

    **Taste Profiles** - Obscurity preferences, voting similarity
    """)
