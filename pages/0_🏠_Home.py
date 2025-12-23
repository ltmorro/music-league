"""
Home Page - The Soundwave Smackdown
An engaging landing page that hooks users immediately.
"""

import streamlit as st
from musicleague.dashboard import (
    setup_page, LEAGUE_COLORS, ACCENT_COLORS,
    load_league_data, get_league_summary_stats, get_player_champion,
    get_most_controversial_songs, get_hidden_gems,
    get_player_arcs, get_influence_rankings, ARC_ICONS,
    generate_champion_commentary,
    DEFAULT_LEAGUES, format_league_name,
)

# Page setup
setup_page()

# Use default leagues from config
league1, league2 = DEFAULT_LEAGUES
league1_display = format_league_name(league1)
league2_display = format_league_name(league2)

# Store leagues in session state for other pages
st.session_state.league1 = league1
st.session_state.league2 = league2

# ============================================================================
# HERO SECTION - Big, bold, attention-grabbing
# ============================================================================

# CSS is loaded centrally via setup_page() from theme.py

# Hero title
st.markdown('<h1 class="hero-title">The Soundwave Smackdown</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Two leagues. One question. Who actually has good taste?</p>', unsafe_allow_html=True)

# Load data
try:
    with st.spinner("Loading the battle data..."):
        data1 = load_league_data(league1)
        data2 = load_league_data(league2)
        stats1 = get_league_summary_stats(data1)
        stats2 = get_league_summary_stats(data2)
except Exception as e:
    st.error(f"Error loading league data: {e}")
    st.stop()

# ============================================================================
# THE MATCHUP - League vs League cards
# ============================================================================

col1, col_vs, col2 = st.columns([5, 2, 5])

with col1:
    st.markdown(f"""
    <div class="league-card" style="--bg-start: #2980b9; --bg-end: #1a5276;">
        <h2>{league1_display}</h2>
        <div class="stat-big">{stats1['total_competitors']}</div>
        <div class="stat-label">Players in the arena</div>
        <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
            <span style="font-size: 1.5rem; font-weight: 700;">{stats1['total_submissions']}</span> tracks
            &nbsp;·&nbsp;
            <span style="font-size: 1.5rem; font-weight: 700;">{stats1['total_rounds']}</span> rounds
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_vs:
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
        <span class="vs-badge">VS</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="league-card" style="--bg-start: #c0392b; --bg-end: #922b21;">
        <h2>{league2_display}</h2>
        <div class="stat-big">{stats2['total_competitors']}</div>
        <div class="stat-label">Players in the arena</div>
        <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
            <span style="font-size: 1.5rem; font-weight: 700;">{stats2['total_submissions']}</span> tracks
            &nbsp;·&nbsp;
            <span style="font-size: 1.5rem; font-weight: 700;">{stats2['total_rounds']}</span> rounds
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# CHAMPION SPOTLIGHT - The winning players
# ============================================================================

champ1 = get_player_champion(data1)
champ2 = get_player_champion(data2)

st.markdown("## The Reigning Champions")

champ_col1, champ_col2 = st.columns(2)

with champ_col1:
    if champ1:
        st.markdown(f"""
        <div class="champion-spotlight">
            <h3>{league1_display}</h3>
            <div style="font-size: 2rem; font-weight: 700; margin-bottom: 1rem;">
                {champ1['name']}
            </div>
            <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                <div>
                    <div style="font-size: 2rem; font-weight: 900; color: #FFC864;">{champ1['total_points']}</div>
                    <div style="font-size: 0.75rem; opacity: 0.7; text-transform: uppercase;">Total Points</div>
                </div>
                <div>
                    <div style="font-size: 2rem; font-weight: 900;">{champ1['round_wins']}</div>
                    <div style="font-size: 0.75rem; opacity: 0.7; text-transform: uppercase;">Round Wins</div>
                </div>
                <div>
                    <div style="font-size: 2rem; font-weight: 900;">{champ1['avg_points']}</div>
                    <div style="font-size: 0.75rem; opacity: 0.7; text-transform: uppercase;">Avg/Song</div>
                </div>
            </div>
            <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.7;">
                {champ1['submissions']} tracks submitted
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No champion data available")

with champ_col2:
    if champ2:
        st.markdown(f"""
        <div class="champion-spotlight">
            <h3>{league2_display}</h3>
            <div style="font-size: 2rem; font-weight: 700; margin-bottom: 1rem;">
                {champ2['name']}
            </div>
            <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                <div>
                    <div style="font-size: 2rem; font-weight: 900; color: #FFC864;">{champ2['total_points']}</div>
                    <div style="font-size: 0.75rem; opacity: 0.7; text-transform: uppercase;">Total Points</div>
                </div>
                <div>
                    <div style="font-size: 2rem; font-weight: 900;">{champ2['round_wins']}</div>
                    <div style="font-size: 0.75rem; opacity: 0.7; text-transform: uppercase;">Round Wins</div>
                </div>
                <div>
                    <div style="font-size: 2rem; font-weight: 900;">{champ2['avg_points']}</div>
                    <div style="font-size: 0.75rem; opacity: 0.7; text-transform: uppercase;">Avg/Song</div>
                </div>
            </div>
            <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.7;">
                {champ2['submissions']} tracks submitted
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No champion data available")

# Champion commentary
st.caption(generate_champion_commentary(data1, data2, league1_display, league2_display))

st.markdown("---")

# ============================================================================
# TEASER SECTION - Hook people into other pages
# ============================================================================

st.markdown("## What You'll Discover")

# Get some teaser data
controversial1 = get_most_controversial_songs(data1, n=1)
controversial2 = get_most_controversial_songs(data2, n=1)
gems1 = get_hidden_gems(data1, n=1)
gems2 = get_hidden_gems(data2, n=1)
arcs1 = get_player_arcs(data1)
arcs2 = get_player_arcs(data2)
influence1 = get_influence_rankings(data1, n=1)
influence2 = get_influence_rankings(data2, n=1)

teaser_col1, teaser_col2 = st.columns(2)

with teaser_col1:
    # Most controversial
    if len(controversial1) > 0:
        cont = controversial1.iloc[0]
        st.markdown(f"""
        <div class="teaser-card" style="--accent: #d35400;">
            <h4>Most Divisive Pick</h4>
            <p><strong>"{cont['Song']}"</strong> split the room in {league1_display}. Some gave it everything, others gave it nothing.</p>
        </div>
        """, unsafe_allow_html=True)

    # Hidden gem
    if len(gems1) > 0:
        gem = gems1.iloc[0]
        st.markdown(f"""
        <div class="teaser-card" style="--accent: #16a085;">
            <h4>The Deep Cut</h4>
            <p><strong>"{gem['Song']}"</strong> had just {gem['Spotify Pop']} Spotify popularity but pulled in {gem['Points']} points. Someone knows their stuff.</p>
        </div>
        """, unsafe_allow_html=True)

with teaser_col2:
    # Player arcs
    if len(arcs1) > 0 and len(arcs2) > 0:
        headliners1 = arcs1[arcs1['Arc'] == 'Headliner']
        headliners2 = arcs2[arcs2['Arc'] == 'Headliner']
        encores1 = arcs1[arcs1['Arc'] == 'Encore']
        encores2 = arcs2[arcs2['Arc'] == 'Encore']
        headliner_count = len(headliners1) + len(headliners2)
        encore_count = len(encores1) + len(encores2)
        st.markdown(f"""
        <div class="teaser-card" style="--accent: #8e44ad;">
            <h4>Player Arcs</h4>
            <p><strong>{headliner_count} Headliners</strong> dominated consistently, while <strong>{encore_count} Encore stories</strong> saved the best for last.</p>
        </div>
        """, unsafe_allow_html=True)

    # Influence
    if len(influence1) > 0 and len(influence2) > 0:
        inf1 = influence1.iloc[0]
        inf2 = influence2.iloc[0]
        st.markdown(f"""
        <div class="teaser-card" style="--accent: #2980b9;">
            <h4>The Influencers</h4>
            <p><strong>{inf1['Voter']}</strong> and <strong>{inf2['Voter']}</strong> shape how votes flow. When they vote, others follow.</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# NAVIGATION CARDS - Make it easy to explore
# ============================================================================

st.markdown("## Explore the Dashboard")

# Navigation grid using Streamlit columns and buttons
nav_row1 = st.columns(3)
nav_row2 = st.columns(3)

with nav_row1[0]:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 2.5rem;">🎵</div>
        <div style="font-weight: 600; margin: 0.5rem 0;">Songs</div>
        <div style="font-size: 0.85rem; color: #7f8c8d;">Top tracks, controversial picks, and hidden gems</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Songs", use_container_width=True):
        st.switch_page("pages/1_🎵_Songs.py")

with nav_row1[1]:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 2.5rem;">🌟</div>
        <div style="font-weight: 600; margin: 0.5rem 0;">Players</div>
        <div style="font-size: 0.85rem; color: #7f8c8d;">Who's the best curator? The stats don't lie</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Players", use_container_width=True):
        st.switch_page("pages/2_🌟_Players.py")

with nav_row1[2]:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 2.5rem;">💬</div>
        <div style="font-weight: 600; margin: 0.5rem 0;">Commentary</div>
        <div style="font-size: 0.85rem; color: #7f8c8d;">The wordsmiths and critics</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Commentary", use_container_width=True):
        st.switch_page("pages/3_💬_Commentary_Booth.py")

with nav_row2[0]:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 2.5rem;">📈</div>
        <div style="font-weight: 600; margin: 0.5rem 0;">Trends</div>
        <div style="font-size: 0.85rem; color: #7f8c8d;">Player arcs and performance over time</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Trends", use_container_width=True):
        st.switch_page("pages/4_📈_Trends.py")

with nav_row2[1]:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 2.5rem;">🕸️</div>
        <div style="font-weight: 600; margin: 0.5rem 0;">Connections</div>
        <div style="font-size: 0.85rem; color: #7f8c8d;">Voting network, loyalties, and rivalries</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Connections", use_container_width=True):
        st.switch_page("pages/5_🕸️_Connections.py")

with nav_row2[2]:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 2.5rem;">⚖️</div>
        <div style="font-weight: 600; margin: 0.5rem 0;">Scorecard</div>
        <div style="font-size: 0.85rem; color: #7f8c8d;">Crown the ultimate winner</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Scorecard", use_container_width=True):
        st.switch_page("pages/6_⚖️_Final_Scorecard.py")

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

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

    # Quick stats
    total_tracks = stats1['total_submissions'] + stats2['total_submissions']
    total_votes = stats1['total_votes'] + stats2['total_votes']
    total_rounds = stats1['total_rounds'] + stats2['total_rounds']

    st.markdown("### Combined Stats")
    st.metric("Total Tracks", total_tracks)
    st.metric("Total Votes Cast", total_votes)
    st.metric("Rounds Played", total_rounds)

    st.markdown("---")
    st.caption("Powered by Spotify API")
