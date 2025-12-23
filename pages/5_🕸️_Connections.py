"""
Connections Page - The Web
Voting networks, influence scores, and relationship dynamics.
"""

import streamlit as st
import pandas as pd
from musicleague.dashboard import (
    setup_page, LEAGUE_COLORS,
    load_league_data, get_influence_rankings,
    generate_network_commentary,
    DEFAULT_LEAGUES, format_league_name,
    apply_plotly_theme, PLOTLY_FONT_SIZES,
)
from musicleague.visualizations import NetworkVisualizations, VoterVisualizations
from musicleague.metrics import NetworkMetrics

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
<div class="page-header connections">
    <h1>The Web</h1>
    <p>Who influences who? Uncover the hidden connections in the voting network.</p>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    data1 = load_league_data(league1)
    data2 = load_league_data(league2)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Get data
influence_l1 = get_influence_rankings(data1, n=15)
influence_l2 = get_influence_rankings(data2, n=15)

# Build graphs for stats
G1 = NetworkMetrics.build_voting_graph(data1)
G2 = NetworkMetrics.build_voting_graph(data2)

# Quick stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_nodes = len(G1.nodes()) + len(G2.nodes())
    st.markdown(f"""
    <div class="stat-highlight">
        <div class="number">{total_nodes}</div>
        <div class="label">Network Nodes</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_edges = len(G1.edges()) + len(G2.edges())
    st.markdown(f"""
    <div class="stat-highlight purple">
        <div class="number">{total_edges}</div>
        <div class="label">Connections</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if len(influence_l1) > 0:
        top_inf = influence_l1.iloc[0]['Voter']
    else:
        top_inf = "N/A"
    st.markdown(f"""
    <div class="stat-highlight blue">
        <div class="number">{top_inf}</div>
        <div class="label">Top Influencer</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    if len(G1.edges()) > 0:
        avg_weight = sum([d['weight'] for _, _, d in G1.edges(data=True)]) / len(G1.edges())
    else:
        avg_weight = 0
    st.markdown(f"""
    <div class="stat-highlight green">
        <div class="number">{avg_weight:.1f}</div>
        <div class="label">Avg Connection</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["Influence", "Network Graph", "Loyalty & Reciprocity"])

# =============================================================================
# Tab 1: Influence Rankings
# =============================================================================
with tab1:
    st.markdown("""
    <div class="section-header">
        <span class="icon">👑</span>
        <h2>The Influencers</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("PageRank-based influence. Higher score = votes carry more weight in the network.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        if len(influence_l1) > 0:
            # Top influencer card
            top = influence_l1.iloc[0]
            st.markdown(f"""
            <div class="influence-card">
                <div class="rank">Most Influential</div>
                <div class="name">{top['Voter']}</div>
                <div class="score">{top['Clout Score']:.1f}</div>
                <div class="score-label">Clout Score</div>
            </div>
            """, unsafe_allow_html=True)

            st.dataframe(influence_l1, use_container_width=True, hide_index=True)
            st.caption(generate_network_commentary(data1, league1_display))

            try:
                fig1 = NetworkVisualizations.influence_score_chart(data1, interactive=True)
                if fig1:
                    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig1, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not generate chart: {e}")
        else:
            st.info("No influence data available")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        if len(influence_l2) > 0:
            top = influence_l2.iloc[0]
            st.markdown(f"""
            <div class="influence-card">
                <div class="rank">Most Influential</div>
                <div class="name">{top['Voter']}</div>
                <div class="score">{top['Clout Score']:.1f}</div>
                <div class="score-label">Clout Score</div>
            </div>
            """, unsafe_allow_html=True)

            st.dataframe(influence_l2, use_container_width=True, hide_index=True)
            st.caption(generate_network_commentary(data2, league2_display))

            try:
                fig2 = NetworkVisualizations.influence_score_chart(data2, interactive=True)
                if fig2:
                    fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig2, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not generate chart: {e}")
        else:
            st.info("No influence data available")

    # Influence comparison
    if len(influence_l1) > 0 and len(influence_l2) > 0:
        st.markdown("---")
        st.markdown("""
        <div class="section-header">
            <span class="icon">📊</span>
            <h2>Influence Shifts</h2>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Comparing clout between the two leagues.")

        merged = pd.merge(
            influence_l1[['Voter', 'Clout Score']],
            influence_l2[['Voter', 'Clout Score']],
            on='Voter',
            how='outer',
            suffixes=(f'_{league1_display}', f'_{league2_display}')
        )
        merged = merged.fillna(0)
        merged['Change'] = merged[f'Clout Score_{league2_display}'] - merged[f'Clout Score_{league1_display}']
        merged = merged.sort_values('Change', ascending=False)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Biggest Gains**")
            gainers = merged.head(5)
            for _, row in gainers.iterrows():
                change = row['Change']
                st.markdown(f"""
                <div class="influence-change-row positive">
                    <span class="name">{row['Voter']}</span>
                    <span class="change">+{change:.1f}</span>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("**Biggest Drops**")
            losers = merged.tail(5).iloc[::-1]
            for _, row in losers.iterrows():
                change = row['Change']
                st.markdown(f"""
                <div class="influence-change-row negative">
                    <span class="name">{row['Voter']}</span>
                    <span class="change">{change:.1f}</span>
                </div>
                """, unsafe_allow_html=True)

# =============================================================================
# Tab 2: Network Graph
# =============================================================================
with tab2:
    st.markdown("""
    <div class="section-header">
        <span class="icon">🕸️</span>
        <h2>Voting Network</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Node size = influence. Edge thickness = points exchanged.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        try:
            fig1 = NetworkVisualizations.voting_network(data1, interactive=True)
            if fig1:
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("Could not generate network graph")
        except Exception as e:
            st.warning(f"Error: {e}")

        # Network stats
        st.markdown("**Network Stats**")
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.markdown(f"""
            <div class="network-stat">
                <div class="value">{len(G1.nodes())}</div>
                <div class="label">Nodes</div>
            </div>
            """, unsafe_allow_html=True)
        with stat_col2:
            st.markdown(f"""
            <div class="network-stat">
                <div class="value">{len(G1.edges())}</div>
                <div class="label">Edges</div>
            </div>
            """, unsafe_allow_html=True)
        with stat_col3:
            if len(G1.edges()) > 0:
                avg_w = sum([d['weight'] for _, _, d in G1.edges(data=True)]) / len(G1.edges())
            else:
                avg_w = 0
            st.markdown(f"""
            <div class="network-stat">
                <div class="value">{avg_w:.1f}</div>
                <div class="label">Avg Weight</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        try:
            fig2 = NetworkVisualizations.voting_network(data2, interactive=True)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Could not generate network graph")
        except Exception as e:
            st.warning(f"Error: {e}")

        # Network stats
        st.markdown("**Network Stats**")
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.markdown(f"""
            <div class="network-stat">
                <div class="value">{len(G2.nodes())}</div>
                <div class="label">Nodes</div>
            </div>
            """, unsafe_allow_html=True)
        with stat_col2:
            st.markdown(f"""
            <div class="network-stat">
                <div class="value">{len(G2.edges())}</div>
                <div class="label">Edges</div>
            </div>
            """, unsafe_allow_html=True)
        with stat_col3:
            if len(G2.edges()) > 0:
                avg_w = sum([d['weight'] for _, _, d in G2.edges(data=True)]) / len(G2.edges())
            else:
                avg_w = 0
            st.markdown(f"""
            <div class="network-stat">
                <div class="value">{avg_w:.1f}</div>
                <div class="label">Avg Weight</div>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# Tab 3: Loyalty & Reciprocity
# =============================================================================
with tab3:
    st.markdown("""
    <div class="section-header">
        <span class="icon">💝</span>
        <h2>Loyalty Heatmap</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Average points given from voters (rows) to submitters (columns).")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        try:
            fig1 = VoterVisualizations.loyalty_heatmap(data1, interactive=True)
            if fig1:
                st.plotly_chart(fig1, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate heatmap: {e}")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        try:
            fig2 = VoterVisualizations.loyalty_heatmap(data2, interactive=True)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate heatmap: {e}")

    # Reciprocity
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <span class="icon">🤝</span>
        <h2>Strongest Reciprocal Relationships</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Do people vote for those who vote for them?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        try:
            reciprocity_l1 = NetworkMetrics.voting_reciprocity(data1)
            if len(reciprocity_l1) > 0:
                top_reciprocal = reciprocity_l1.nlargest(8, 'reciprocity_score')
                for _, row in top_reciprocal.iterrows():
                    st.markdown(f"""
                    <div class="relationship-row">
                        <div class="pair">{row['voter']} ↔ {row['submitter']}</div>
                        <div class="stats">
                            <span>{int(row['points_given'])} given</span>
                            <span>{int(row['points_received'])} received</span>
                            <span class="reciprocity">{row['reciprocity_score']:.0f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No reciprocity data")
        except Exception as e:
            st.warning(f"Could not calculate: {e}")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        try:
            reciprocity_l2 = NetworkMetrics.voting_reciprocity(data2)
            if len(reciprocity_l2) > 0:
                top_reciprocal = reciprocity_l2.nlargest(8, 'reciprocity_score')
                for _, row in top_reciprocal.iterrows():
                    st.markdown(f"""
                    <div class="relationship-row">
                        <div class="pair">{row['voter']} ↔ {row['submitter']}</div>
                        <div class="stats">
                            <span>{int(row['points_given'])} given</span>
                            <span>{int(row['points_received'])} received</span>
                            <span class="reciprocity">{row['reciprocity_score']:.0f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No reciprocity data")
        except Exception as e:
            st.warning(f"Could not calculate: {e}")

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

    **Influence** - PageRank-based voting influence

    **Network Graph** - Visual voting relationships

    **Loyalty** - Who votes for whom consistently

    **Reciprocity** - Mutual voting relationships
    """)
