"""
Songs Page - The Track Record
Top tracks, controversial picks, and deep cuts across both leagues.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from musicleague.dashboard import (
    setup_page, LEAGUE_COLORS,
    load_league_data, get_top_songs, get_most_controversial_songs,
    get_hidden_gems,
    generate_controversy_commentary, generate_hidden_gem_commentary,
    DEFAULT_LEAGUES, format_league_name,
    apply_plotly_theme, PLOTLY_FONT_SIZES,
)
from musicleague.metrics import SongMetrics

# Page setup
setup_page()

# Get leagues from session state or use defaults
league1 = st.session_state.get('league1', DEFAULT_LEAGUES[0])
league2 = st.session_state.get('league2', DEFAULT_LEAGUES[1])
league1_display = format_league_name(league1)
league2_display = format_league_name(league2)

# CSS is loaded centrally via setup_page() from theme.py

# Page Header
st.markdown("""
<div class="page-header songs">
    <h1>The Track Record</h1>
    <p>Every song tells a story. Here's how they scored.</p>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    data1 = load_league_data(league1)
    data2 = load_league_data(league2)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Quick stats row
song_df_1 = SongMetrics.get_all_song_metrics(data1)
song_df_2 = SongMetrics.get_all_song_metrics(data2)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-highlight">
        <div class="number">{len(song_df_1) + len(song_df_2)}</div>
        <div class="label">Total Tracks</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_pts = (song_df_1['total_points'].mean() + song_df_2['total_points'].mean()) / 2
    st.markdown(f"""
    <div class="stat-highlight green">
        <div class="number">{avg_pts:.1f}</div>
        <div class="label">Avg Points</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    max_pts = max(song_df_1['total_points'].max(), song_df_2['total_points'].max())
    st.markdown(f"""
    <div class="stat-highlight gold">
        <div class="number">{int(max_pts)}</div>
        <div class="label">Highest Score</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_cont = (song_df_1['controversy_score'].mean() + song_df_2['controversy_score'].mean()) / 2
    st.markdown(f"""
    <div class="stat-highlight red">
        <div class="number">{avg_cont:.2f}</div>
        <div class="label">Avg Controversy</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["Top Tracks", "Controversial", "Deep Cuts"])

# =============================================================================
# Tab 1: Top Songs
# =============================================================================
with tab1:
    st.markdown("""
    <div class="section-header">
        <span class="icon">🏆</span>
        <h2>The Leaderboard</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("The songs that dominated. Ranked by total points.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        top_songs_l1 = get_top_songs(data1, n=10)
        if len(top_songs_l1) > 0:
            # Show top 3 as cards
            for i, (_, row) in enumerate(top_songs_l1.head(3).iterrows()):
                st.markdown(f"""
                <div class="song-card">
                    <span class="rank">#{row['Rank']}</span>
                    <div class="song-title">{row['Song']}</div>
                    <div class="artist">{row['Artist']}</div>
                    <div class="stats">
                        <span class="points">{int(row['Points'])} pts</span>
                        <span>by {row['Submitted By']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Rest as table
            if len(top_songs_l1) > 3:
                st.dataframe(
                    top_songs_l1.iloc[3:][['Rank', 'Song', 'Artist', 'Points', 'Submitted By']],
                    use_container_width=True, hide_index=True
                )
        else:
            st.info("No songs found")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        top_songs_l2 = get_top_songs(data2, n=10)
        if len(top_songs_l2) > 0:
            # Show top 3 as cards
            for i, (_, row) in enumerate(top_songs_l2.head(3).iterrows()):
                st.markdown(f"""
                <div class="song-card">
                    <span class="rank">#{row['Rank']}</span>
                    <div class="song-title">{row['Song']}</div>
                    <div class="artist">{row['Artist']}</div>
                    <div class="stats">
                        <span class="points">{int(row['Points'])} pts</span>
                        <span>by {row['Submitted By']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Rest as table
            if len(top_songs_l2) > 3:
                st.dataframe(
                    top_songs_l2.iloc[3:][['Rank', 'Song', 'Artist', 'Points', 'Submitted By']],
                    use_container_width=True, hide_index=True
                )
        else:
            st.info("No songs found")

    # Comparison chart
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <span class="icon">📊</span>
        <h2>Head to Head: Top 10</h2>
    </div>
    """, unsafe_allow_html=True)

    if len(song_df_1) > 0 and len(song_df_2) > 0:
        top10_l1 = song_df_1.head(10).copy()
        top10_l2 = song_df_2.head(10).copy()
        top10_l1['League'] = league1_display
        top10_l2['League'] = league2_display
        combined_top = pd.concat([top10_l1, top10_l2])

        fig = px.bar(
            combined_top,
            x='total_points',
            y='song_name',
            color='League',
            orientation='h',
            color_discrete_map={
                league1_display: LEAGUE_COLORS.get(league1, '#2980b9'),
                league2_display: LEAGUE_COLORS.get(league2, '#c0392b')
            },
            labels={'total_points': 'Total Points', 'song_name': ''},
            hover_data=['artist', 'submitter'],
        )
        apply_plotly_theme(
            fig,
            title="Top 10 Songs: Head to Head",
            height=600,
            showlegend=True,
            yaxis={'categoryorder': 'total ascending'},
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# Tab 2: Controversial Tracks
# =============================================================================
with tab2:
    st.markdown("""
    <div class="section-header">
        <span class="icon">🔥</span>
        <h2>Love It or Hate It</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("High vote variance means the room was split. These songs sparked debate.")

    controversial_l1 = get_most_controversial_songs(data1, n=10)
    controversial_l2 = get_most_controversial_songs(data2, n=10)

    # Combined visualization
    if len(controversial_l1) > 0 and len(controversial_l2) > 0:
        c1 = controversial_l1.copy()
        c2 = controversial_l2.copy()
        c1['League'] = league1_display
        c2['League'] = league2_display
        combined_controversy = pd.concat([c1, c2])

        fig = px.bar(
            combined_controversy,
            x='Controversy σ',
            y='Song',
            color='League',
            orientation='h',
            color_discrete_map={
                league1_display: LEAGUE_COLORS.get(league1, '#2980b9'),
                league2_display: LEAGUE_COLORS.get(league2, '#c0392b')
            },
            labels={'Controversy σ': 'Controversy Score (σ)'},
            hover_data=['Artist', 'Points']
        )
        apply_plotly_theme(
            fig,
            title="Most Controversial Songs",
            height=600,
            showlegend=True,
            yaxis={'categoryorder': 'total ascending'},
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Side-by-side analysis
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        if len(controversial_l1) > 0:
            # Highlight top controversial
            top_cont = controversial_l1.iloc[0]
            st.markdown(f"""
            <div class="controversial-card">
                <div class="label">Most Divisive</div>
                <div class="song-name">{top_cont['Song']}</div>
                <div class="artist">{top_cont['Artist']}</div>
                <div class="score">σ = {top_cont['Controversy σ']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(controversial_l1, use_container_width=True, hide_index=True)
            st.caption(generate_controversy_commentary(controversial_l1, league1_display))
        else:
            st.info("No controversial songs found")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        if len(controversial_l2) > 0:
            top_cont = controversial_l2.iloc[0]
            st.markdown(f"""
            <div class="controversial-card">
                <div class="label">Most Divisive</div>
                <div class="song-name">{top_cont['Song']}</div>
                <div class="artist">{top_cont['Artist']}</div>
                <div class="score">σ = {top_cont['Controversy σ']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(controversial_l2, use_container_width=True, hide_index=True)
            st.caption(generate_controversy_commentary(controversial_l2, league2_display))
        else:
            st.info("No controversial songs found")

# =============================================================================
# Tab 3: Deep Cuts
# =============================================================================
with tab3:
    st.markdown("""
    <div class="section-header">
        <span class="icon">💎</span>
        <h2>Hidden Gems</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Low Spotify popularity + high points = someone found something special.")

    # Scatter plot
    st.markdown("#### Popularity vs. Points")

    if len(song_df_1) > 0 and len(song_df_2) > 0:
        df1 = song_df_1.copy()
        df2 = song_df_2.copy()
        df1['League'] = league1_display
        df2['League'] = league2_display
        combined_songs = pd.concat([df1, df2])

        fig = px.scatter(
            combined_songs,
            x='spotify_popularity',
            y='total_points',
            color='League',
            hover_name='song_name',
            hover_data=['artist', 'submitter'],
            size='total_points',
            color_discrete_map={
                league1_display: LEAGUE_COLORS.get(league1, '#2980b9'),
                league2_display: LEAGUE_COLORS.get(league2, '#c0392b')
            },
            labels={'spotify_popularity': 'Spotify Popularity', 'total_points': 'Total Points'}
        )

        # Add quadrant lines
        median_pop = combined_songs['spotify_popularity'].median()
        median_pts = combined_songs['total_points'].median()

        fig.add_hline(y=median_pts, line_dash="dash", line_color="rgba(127,140,141,0.5)")
        fig.add_vline(x=median_pop, line_dash="dash", line_color="rgba(127,140,141,0.5)")

        # Quadrant labels
        max_pop = combined_songs['spotify_popularity'].max()
        max_pts = combined_songs['total_points'].max()

        fig.add_annotation(x=max_pop * 0.15, y=max_pts * 0.9, text="💎 HIDDEN GEMS",
                          showarrow=False, font=dict(size=PLOTLY_FONT_SIZES['annotation'], color="#16a085"))
        fig.add_annotation(x=max_pop * 0.85, y=max_pts * 0.9, text="Popular Hits",
                          showarrow=False, font=dict(size=PLOTLY_FONT_SIZES['annotation'], color="#7f8c8d"))

        apply_plotly_theme(
            fig,
            title="Popularity vs. Points",
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Top Deep Cuts")

    gems_l1 = get_hidden_gems(data1, n=5)
    gems_l2 = get_hidden_gems(data2, n=5)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        if len(gems_l1) > 0:
            for _, gem in gems_l1.iterrows():
                st.markdown(f"""
                <div class="gem-card">
                    <div class="song-name">{gem['Song']}</div>
                    <div class="meta">{gem['Artist']} · by {gem['Submitted By']}</div>
                    <div class="meta" style="margin-top: 0.5rem;">
                        <strong>{int(gem['Points'])} pts</strong> with only <strong>{int(gem['Spotify Pop'])}</strong> Spotify popularity
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.caption(generate_hidden_gem_commentary(gems_l1, league1_display))
        else:
            st.info("No deep cuts found")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        if len(gems_l2) > 0:
            for _, gem in gems_l2.iterrows():
                st.markdown(f"""
                <div class="gem-card">
                    <div class="song-name">{gem['Song']}</div>
                    <div class="meta">{gem['Artist']} · by {gem['Submitted By']}</div>
                    <div class="meta" style="margin-top: 0.5rem;">
                        <strong>{int(gem['Points'])} pts</strong> with only <strong>{int(gem['Spotify Pop'])}</strong> Spotify popularity
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.caption(generate_hidden_gem_commentary(gems_l2, league2_display))
        else:
            st.info("No deep cuts found")

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

    **Top Tracks** - Highest scoring songs across all rounds

    **Controversial** - Songs with high vote variance (some loved, some hated)

    **Deep Cuts** - Low Spotify popularity but high points (hidden gems)
    """)
