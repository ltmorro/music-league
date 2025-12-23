"""
Trends Page - The Arc
Round-by-round performance, momentum, and hot streaks.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from musicleague.dashboard import (
    setup_page, LEAGUE_COLORS,
    load_league_data,
    get_round_by_round_performance, get_player_arcs, get_player_round_scores,
    get_round_champions,
    generate_arc_commentary, ARC_ICONS,
    DEFAULT_LEAGUES, format_league_name,
    apply_plotly_theme, PLOTLY_FONT_SIZES,
)

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
<div class="page-header trends">
    <h1>The Arc</h1>
    <p>Every player has a story. Watch it unfold round by round.</p>
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
arcs_l1 = get_player_arcs(data1)
arcs_l2 = get_player_arcs(data2)
champions_l1 = get_round_champions(data1)
champions_l2 = get_round_champions(data2)

# Quick stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_rounds = len(data1.rounds) + len(data2.rounds)
    st.markdown(f"""
    <div class="stat-highlight">
        <div class="number">{total_rounds}</div>
        <div class="label">Total Rounds</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    headliners_l1 = len(arcs_l1[arcs_l1['Arc'] == 'Headliner']) if len(arcs_l1) > 0 else 0
    headliners_l2 = len(arcs_l2[arcs_l2['Arc'] == 'Headliner']) if len(arcs_l2) > 0 else 0
    st.markdown(f"""
    <div class="stat-highlight green">
        <div class="number">{headliners_l1 + headliners_l2}</div>
        <div class="label">Headliners</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    encores_l1 = len(arcs_l1[arcs_l1['Arc'] == 'Encore']) if len(arcs_l1) > 0 else 0
    encores_l2 = len(arcs_l2[arcs_l2['Arc'] == 'Encore']) if len(arcs_l2) > 0 else 0
    st.markdown(f"""
    <div class="stat-highlight red">
        <div class="number">{encores_l1 + encores_l2}</div>
        <div class="label">Comeback Stories</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    if len(champions_l1) > 0:
        top_winner = champions_l1['Winner'].value_counts().iloc[0]
    else:
        top_winner = 0
    st.markdown(f"""
    <div class="stat-highlight gold">
        <div class="number">{top_winner}</div>
        <div class="label">Most Round Wins</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["Performance Over Time", "Player Arcs", "Round Champions"])

# =============================================================================
# Tab 1: Performance Over Time
# =============================================================================
with tab1:
    st.markdown("""
    <div class="section-header">
        <span class="icon">📈</span>
        <h2>The Race</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Track cumulative points across rounds. Select players to compare their journeys.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)

        perf_l1 = get_round_by_round_performance(data1)

        if len(perf_l1) > 0:
            all_players_l1 = sorted(perf_l1['submitter'].unique().tolist())

            # Initialize session state
            if 'player_select_l1' not in st.session_state:
                st.session_state.player_select_l1 = all_players_l1[:5]

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Select All", key="select_all_l1"):
                    st.session_state.player_select_l1 = all_players_l1
                    st.rerun()
            with col_btn2:
                if st.button("Clear", key="clear_all_l1"):
                    st.session_state.player_select_l1 = []
                    st.rerun()

            selected_l1 = st.multiselect(
                "Select players",
                all_players_l1,
                key="player_select_l1",
                label_visibility="collapsed"
            )

            if selected_l1:
                filtered_l1 = perf_l1[perf_l1['submitter'].isin(selected_l1)]

                fig = px.line(
                    filtered_l1,
                    x='round_index',
                    y='cumulative_points',
                    color='submitter',
                    markers=True,
                    labels={
                        'round_index': 'Round',
                        'cumulative_points': 'Cumulative Points',
                        'submitter': 'Player'
                    }
                )
                apply_plotly_theme(
                    fig,
                    title=f"Cumulative Points Over Time - {league1_display}",
                    height=450,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Select at least one player")
        else:
            st.info("No performance data available")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)

        perf_l2 = get_round_by_round_performance(data2)

        if len(perf_l2) > 0:
            all_players_l2 = sorted(perf_l2['submitter'].unique().tolist())

            if 'player_select_l2' not in st.session_state:
                st.session_state.player_select_l2 = all_players_l2[:5]

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Select All", key="select_all_l2"):
                    st.session_state.player_select_l2 = all_players_l2
                    st.rerun()
            with col_btn2:
                if st.button("Clear", key="clear_all_l2"):
                    st.session_state.player_select_l2 = []
                    st.rerun()

            selected_l2 = st.multiselect(
                "Select players",
                all_players_l2,
                key="player_select_l2",
                label_visibility="collapsed"
            )

            if selected_l2:
                filtered_l2 = perf_l2[perf_l2['submitter'].isin(selected_l2)]

                fig = px.line(
                    filtered_l2,
                    x='round_index',
                    y='cumulative_points',
                    color='submitter',
                    markers=True,
                    labels={
                        'round_index': 'Round',
                        'cumulative_points': 'Cumulative Points',
                        'submitter': 'Player'
                    }
                )
                apply_plotly_theme(
                    fig,
                    title=f"Cumulative Points Over Time - {league2_display}",
                    height=450,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Select at least one player")
        else:
            st.info("No performance data available")

# =============================================================================
# Tab 2: Player Arcs
# =============================================================================
with tab2:
    st.markdown("""
    <div class="section-header">
        <span class="icon">🎭</span>
        <h2>Player Arcs</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Every player has a story. Here's how their journey unfolded.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        if len(arcs_l1) > 0:
            # Show player arc cards
            for _, row in arcs_l1.head(8).iterrows():
                arc_icon = ARC_ICONS.get(row['Arc'], "🎵")
                peak_text = f"Peak: Rd {int(row['Peak Round'])} ({int(row['Peak Points'])} pts)"
                finish_text = f"Finish: {row['Finish Strength']:+.0f}" if row['Finish Strength'] != 0 else ""

                st.markdown(f"""
                <div class="momentum-card">
                    <div class="player-info">
                        <span class="trend-icon">{arc_icon}</span>
                        <div>
                            <div class="name">{row['Player']}</div>
                            <div class="streak">{row['Arc']} · {peak_text}</div>
                        </div>
                    </div>
                    <div class="score">{row['Avg Points']:.1f} avg</div>
                </div>
                """, unsafe_allow_html=True)

            # Arc type distribution chart
            arc_counts = arcs_l1['Arc'].value_counts().reset_index()
            arc_counts.columns = ['Arc Type', 'Count']

            # Add icons to arc types
            arc_counts['Arc Type'] = arc_counts['Arc Type'].apply(
                lambda x: f"{ARC_ICONS.get(x, '')} {x}"
            )

            fig = px.bar(
                arc_counts,
                x='Count',
                y='Arc Type',
                orientation='h',
                color='Arc Type',
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            apply_plotly_theme(
                fig,
                height=300,
                showlegend=False,
                title="Arc Type Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for arc analysis")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        if len(arcs_l2) > 0:
            for _, row in arcs_l2.head(8).iterrows():
                arc_icon = ARC_ICONS.get(row['Arc'], "🎵")
                peak_text = f"Peak: Rd {int(row['Peak Round'])} ({int(row['Peak Points'])} pts)"

                st.markdown(f"""
                <div class="momentum-card">
                    <div class="player-info">
                        <span class="trend-icon">{arc_icon}</span>
                        <div>
                            <div class="name">{row['Player']}</div>
                            <div class="streak">{row['Arc']} · {peak_text}</div>
                        </div>
                    </div>
                    <div class="score">{row['Avg Points']:.1f} avg</div>
                </div>
                """, unsafe_allow_html=True)

            arc_counts = arcs_l2['Arc'].value_counts().reset_index()
            arc_counts.columns = ['Arc Type', 'Count']
            arc_counts['Arc Type'] = arc_counts['Arc Type'].apply(
                lambda x: f"{ARC_ICONS.get(x, '')} {x}"
            )

            fig = px.bar(
                arc_counts,
                x='Count',
                y='Arc Type',
                orientation='h',
                color='Arc Type',
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            apply_plotly_theme(
                fig,
                height=300,
                showlegend=False,
                title="Arc Type Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for arc analysis")

    # -------------------------------------------------------------------------
    # Player Deep Dive Section
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <span class="icon">🔍</span>
        <h2>Player Deep Dive</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Select a player to see their journey in detail.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        if len(arcs_l1) > 0:
            players_l1 = arcs_l1['Player'].tolist()
            selected_player_l1 = st.selectbox(
                "Select player",
                players_l1,
                key="player_detail_l1",
                label_visibility="collapsed"
            )

            if selected_player_l1:
                # Get player arc info
                player_arc = arcs_l1[arcs_l1['Player'] == selected_player_l1].iloc[0]
                arc_icon = ARC_ICONS.get(player_arc['Arc'], "🎵")

                # Display arc info card
                st.markdown(f"""
                <div class="momentum-card" style="margin-bottom: 1rem;">
                    <div class="player-info">
                        <span class="trend-icon" style="font-size: 2rem;">{arc_icon}</span>
                        <div>
                            <div class="name" style="font-size: 1.2rem;">{selected_player_l1}</div>
                            <div class="streak">{player_arc['Arc']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Key stats
                stat_cols = st.columns(4)
                with stat_cols[0]:
                    st.metric("Avg Points", f"{player_arc['Avg Points']:.1f}")
                with stat_cols[1]:
                    st.metric("Consistency", f"±{player_arc['Consistency']:.1f}")
                with stat_cols[2]:
                    finish_delta = player_arc['Finish Strength']
                    st.metric("Finish", f"{finish_delta:+.0f}", delta=f"{'Strong' if finish_delta > 0 else 'Weak' if finish_delta < 0 else 'Even'}")
                with stat_cols[3]:
                    st.metric("Peak Round", f"Rd {int(player_arc['Peak Round'])}", delta=f"{int(player_arc['Peak Points'])} pts")

                # Round-by-round chart
                scores_l1 = get_player_round_scores(data1, selected_player_l1)
                if len(scores_l1) > 0:
                    # Create chart with first/second half coloring
                    fig = go.Figure()

                    # Add bar chart for points per round
                    colors = ['#3498db' if h == 'First Half' else '#e74c3c' for h in scores_l1['half']]
                    fig.add_trace(go.Bar(
                        x=scores_l1['round_num'],
                        y=scores_l1['points'],
                        name='Points',
                        marker_color=colors,
                        text=scores_l1['points'],
                        textposition='outside',
                    ))

                    # Add average line
                    avg_points = scores_l1['points'].mean()
                    fig.add_hline(
                        y=avg_points,
                        line_dash="dash",
                        line_color="gray",
                        annotation_text=f"Avg: {avg_points:.1f}",
                        annotation_position="right"
                    )

                    apply_plotly_theme(
                        fig,
                        title=f"{selected_player_l1}'s Journey",
                        xaxis_title="Round",
                        yaxis_title="Points",
                        height=300,
                        showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("Blue = First Half · Red = Second Half")
        else:
            st.info("No player data available")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        if len(arcs_l2) > 0:
            players_l2 = arcs_l2['Player'].tolist()
            selected_player_l2 = st.selectbox(
                "Select player",
                players_l2,
                key="player_detail_l2",
                label_visibility="collapsed"
            )

            if selected_player_l2:
                player_arc = arcs_l2[arcs_l2['Player'] == selected_player_l2].iloc[0]
                arc_icon = ARC_ICONS.get(player_arc['Arc'], "🎵")

                st.markdown(f"""
                <div class="momentum-card" style="margin-bottom: 1rem;">
                    <div class="player-info">
                        <span class="trend-icon" style="font-size: 2rem;">{arc_icon}</span>
                        <div>
                            <div class="name" style="font-size: 1.2rem;">{selected_player_l2}</div>
                            <div class="streak">{player_arc['Arc']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                stat_cols = st.columns(4)
                with stat_cols[0]:
                    st.metric("Avg Points", f"{player_arc['Avg Points']:.1f}")
                with stat_cols[1]:
                    st.metric("Consistency", f"±{player_arc['Consistency']:.1f}")
                with stat_cols[2]:
                    finish_delta = player_arc['Finish Strength']
                    st.metric("Finish", f"{finish_delta:+.0f}", delta=f"{'Strong' if finish_delta > 0 else 'Weak' if finish_delta < 0 else 'Even'}")
                with stat_cols[3]:
                    st.metric("Peak Round", f"Rd {int(player_arc['Peak Round'])}", delta=f"{int(player_arc['Peak Points'])} pts")

                scores_l2 = get_player_round_scores(data2, selected_player_l2)
                if len(scores_l2) > 0:
                    fig = go.Figure()

                    colors = ['#3498db' if h == 'First Half' else '#e74c3c' for h in scores_l2['half']]
                    fig.add_trace(go.Bar(
                        x=scores_l2['round_num'],
                        y=scores_l2['points'],
                        name='Points',
                        marker_color=colors,
                        text=scores_l2['points'],
                        textposition='outside',
                    ))

                    avg_points = scores_l2['points'].mean()
                    fig.add_hline(
                        y=avg_points,
                        line_dash="dash",
                        line_color="gray",
                        annotation_text=f"Avg: {avg_points:.1f}",
                        annotation_position="right"
                    )

                    apply_plotly_theme(
                        fig,
                        title=f"{selected_player_l2}'s Journey",
                        xaxis_title="Round",
                        yaxis_title="Points",
                        height=300,
                        showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("Blue = First Half · Red = Second Half")
        else:
            st.info("No player data available")

    st.markdown("---")
    st.info(generate_arc_commentary(data1, data2, league1_display, league2_display))

# =============================================================================
# Tab 3: Round Champions
# =============================================================================
with tab3:
    st.markdown("""
    <div class="section-header">
        <span class="icon">🏆</span>
        <h2>Round Winners</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Who won each round?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        if len(champions_l1) > 0:
            for _, row in champions_l1.iterrows():
                st.markdown(f"""
                <div class="champion-row">
                    <div class="round-num">{int(row['Round'])}</div>
                    <div class="song-info">
                        <div class="song-name">{row['Song']}</div>
                        <div class="winner-name">{row['Winner']} · {row['Artist']}</div>
                    </div>
                    <div class="points">{int(row['Points'])} pts</div>
                </div>
                """, unsafe_allow_html=True)

            # Pie chart
            win_counts = champions_l1['Winner'].value_counts().reset_index()
            win_counts.columns = ['Winner', 'Wins']

            fig = px.pie(
                win_counts,
                values='Wins',
                names='Winner',
                title='Round Wins Distribution',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            apply_plotly_theme(fig, height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No round data available")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        if len(champions_l2) > 0:
            for _, row in champions_l2.iterrows():
                st.markdown(f"""
                <div class="champion-row">
                    <div class="round-num">{int(row['Round'])}</div>
                    <div class="song-info">
                        <div class="song-name">{row['Song']}</div>
                        <div class="winner-name">{row['Winner']} · {row['Artist']}</div>
                    </div>
                    <div class="points">{int(row['Points'])} pts</div>
                </div>
                """, unsafe_allow_html=True)

            win_counts = champions_l2['Winner'].value_counts().reset_index()
            win_counts.columns = ['Winner', 'Wins']

            fig = px.pie(
                win_counts,
                values='Wins',
                names='Winner',
                title='Round Wins Distribution',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            apply_plotly_theme(fig, height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No round data available")

    # Most wins comparison
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <span class="icon">👑</span>
        <h2>Most Round Wins</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if len(champions_l1) > 0:
            top_winner_l1 = champions_l1['Winner'].value_counts().iloc[0]
            top_name_l1 = champions_l1['Winner'].value_counts().index[0]
            st.markdown(f"""
            <div class="round-champion-card blue">
                <div class="label">{league1_display} Champion</div>
                <div class="name">{top_name_l1}</div>
                <div class="wins">{top_winner_l1} wins</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if len(champions_l2) > 0:
            top_winner_l2 = champions_l2['Winner'].value_counts().iloc[0]
            top_name_l2 = champions_l2['Winner'].value_counts().index[0]
            st.markdown(f"""
            <div class="round-champion-card red">
                <div class="label">{league2_display} Champion</div>
                <div class="name">{top_name_l2}</div>
                <div class="wins">{top_winner_l2} wins</div>
            </div>
            """, unsafe_allow_html=True)

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

    **Performance** - Cumulative points over rounds

    **Player Arcs** - How each player's journey unfolded

    **Round Champions** - Who won each round

    ---

    **Arc Types:**

    🎤 **Headliner** - Dominated consistently

    🎬 **Opening Act** - Strong start, faded late

    🔥 **Encore** - Saved the best for last

    👏 **Crowd Favorite** - Steady performer

    💥 **One-Hit Wonder** - One standout round

    🎲 **Wild Card** - Unpredictable
    """)
