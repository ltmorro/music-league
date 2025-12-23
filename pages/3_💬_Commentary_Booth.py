"""
Commentary Booth Page - The Discourse
Who writes the best comments? Hall of Fame quotes and engagement analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from musicleague.dashboard import (
    setup_page, LEAGUE_COLORS,
    load_league_data,
    get_wordsmith_rankings, get_critic_rankings, get_best_comments,
    generate_wordsmith_commentary, generate_best_comment_showcase,
    DEFAULT_LEAGUES, format_league_name,
    apply_plotly_theme, PLOTLY_FONT_SIZES,
)
from musicleague.metrics.comments import CommentMetrics

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
<div class="page-header commentary">
    <h1>The Commentary Booth</h1>
    <p>Words matter. Here's who brings the most flavor to the discourse.</p>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    data1 = load_league_data(league1)
    data2 = load_league_data(league2)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Get rankings
wordsmiths_l1 = get_wordsmith_rankings(data1)
wordsmiths_l2 = get_wordsmith_rankings(data2)
critics_l1 = get_critic_rankings(data1)
critics_l2 = get_critic_rankings(data2)

# Quick stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_comments_l1 = wordsmiths_l1['Total Comments'].sum() if len(wordsmiths_l1) > 0 else 0
    total_comments_l2 = wordsmiths_l2['Total Comments'].sum() if len(wordsmiths_l2) > 0 else 0
    st.markdown(f"""
    <div class="stat-highlight">
        <div class="number">{int(total_comments_l1 + total_comments_l2)}</div>
        <div class="label">Total Comments</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if len(wordsmiths_l1) > 0 and len(wordsmiths_l2) > 0:
        avg_len = (wordsmiths_l1['Avg Length'].mean() + wordsmiths_l2['Avg Length'].mean()) / 2
    else:
        avg_len = 0
    st.markdown(f"""
    <div class="stat-highlight blue">
        <div class="number">{avg_len:.0f}</div>
        <div class="label">Avg Length</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if len(wordsmiths_l1) > 0:
        top_wordsmith = wordsmiths_l1.iloc[0]['Submitter']
    else:
        top_wordsmith = "N/A"
    st.markdown(f"""
    <div class="stat-highlight purple">
        <div class="number">{top_wordsmith}</div>
        <div class="label">Top Wordsmith</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    if len(critics_l1) > 0:
        top_critic = critics_l1.iloc[0]['Voter']
    else:
        top_critic = "N/A"
    st.markdown(f"""
    <div class="stat-highlight red">
        <div class="number">{top_critic}</div>
        <div class="label">Top Critic</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["Wordsmiths", "Critics", "Hall of Fame"])

# =============================================================================
# Tab 1: Wordsmith Rankings
# =============================================================================
with tab1:
    st.markdown("""
    <div class="section-header">
        <span class="icon">✍️</span>
        <h2>The Wordsmiths</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Who writes the most detailed submission comments?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        if len(wordsmiths_l1) > 0:
            # Top wordsmith card
            top = wordsmiths_l1.iloc[0]
            st.markdown(f"""
            <div class="wordsmith-card blue">
                <div class="top-label">Top Wordsmith</div>
                <div class="name">{top['Submitter']}</div>
                <div class="stats">
                    <div>
                        <div class="stat-value">{top['Avg Length']:.0f}</div>
                        <div class="stat-label">Avg Chars</div>
                    </div>
                    <div>
                        <div class="stat-value">{top['Comment Rate %']:.0f}%</div>
                        <div class="stat-label">Comment Rate</div>
                    </div>
                    <div>
                        <div class="stat-value">{int(top['Total Comments'])}</div>
                        <div class="stat-label">Total</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            fig = px.bar(
                wordsmiths_l1.head(10),
                x='Avg Length',
                y='Submitter',
                orientation='h',
                color_discrete_sequence=[LEAGUE_COLORS.get(league1, '#2980b9')]
            )
            apply_plotly_theme(fig, title=f"Wordsmith Rankings - {league1_display}", height=350, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No comment data available")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        if len(wordsmiths_l2) > 0:
            top = wordsmiths_l2.iloc[0]
            st.markdown(f"""
            <div class="wordsmith-card red">
                <div class="top-label">Top Wordsmith</div>
                <div class="name">{top['Submitter']}</div>
                <div class="stats">
                    <div>
                        <div class="stat-value">{top['Avg Length']:.0f}</div>
                        <div class="stat-label">Avg Chars</div>
                    </div>
                    <div>
                        <div class="stat-value">{top['Comment Rate %']:.0f}%</div>
                        <div class="stat-label">Comment Rate</div>
                    </div>
                    <div>
                        <div class="stat-value">{int(top['Total Comments'])}</div>
                        <div class="stat-label">Total</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            fig = px.bar(
                wordsmiths_l2.head(10),
                x='Avg Length',
                y='Submitter',
                orientation='h',
                color_discrete_sequence=[LEAGUE_COLORS.get(league2, '#c0392b')]
            )
            apply_plotly_theme(fig, title=f"Wordsmith Rankings - {league2_display}", height=350, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No comment data available")

    # Commentary comparison
    st.markdown("---")
    st.info(generate_wordsmith_commentary(data1, data2, league1_display, league2_display))

    # Comment vs Points analysis
    st.markdown("""
    <div class="section-header">
        <span class="icon">📈</span>
        <h2>Do Longer Comments = More Votes?</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Does explaining your song choice help it score better?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**{league1_display}**")
        comment_vs_points_l1 = CommentMetrics.submission_comment_vs_points(data1)
        corr_stats_l1 = CommentMetrics.comment_length_correlation(data1)

        if len(comment_vs_points_l1) > 0:
            fig = px.scatter(
                comment_vs_points_l1,
                x='comment_length',
                y='total_points',
                hover_name='song',
                hover_data=['artist', 'submitter'],
                color='has_comment',
                color_discrete_map={True: LEAGUE_COLORS.get(league1, '#2980b9'), False: '#cccccc'},
                labels={'comment_length': 'Comment Length (chars)', 'total_points': 'Points Received'},
            )
            apply_plotly_theme(fig, title=f"Comment Length vs. Points - {league1_display}", height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            # Insight box
            if corr_stats_l1['correlation'] > 0.1:
                st.markdown(f"""
                <div class="insight-box positive">
                    <strong>Longer comments don't really correlate with higher scores!</strong><br>
                    +{corr_stats_l1['difference']:.1f} pts avg difference · r = {corr_stats_l1['correlation']:.3f}
                </div>
                """, unsafe_allow_html=True)
            elif corr_stats_l1['correlation'] < -0.1:
                st.markdown(f"""
                <div class="insight-box negative">
                    <strong>Shorter comments actually score better here</strong><br>
                    {corr_stats_l1['difference']:.1f} pts difference · r = {corr_stats_l1['correlation']:.3f}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="insight-box neutral">
                    <strong>No strong relationship</strong> between comment length and points.
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"**{league2_display}**")
        comment_vs_points_l2 = CommentMetrics.submission_comment_vs_points(data2)
        corr_stats_l2 = CommentMetrics.comment_length_correlation(data2)

        if len(comment_vs_points_l2) > 0:
            fig = px.scatter(
                comment_vs_points_l2,
                x='comment_length',
                y='total_points',
                hover_name='song',
                hover_data=['artist', 'submitter'],
                color='has_comment',
                color_discrete_map={True: LEAGUE_COLORS.get(league2, '#c0392b'), False: '#cccccc'},
                labels={'comment_length': 'Comment Length (chars)', 'total_points': 'Points Received'},
            )
            apply_plotly_theme(fig, title=f"Comment Length vs. Points - {league2_display}", height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            if corr_stats_l2['correlation'] > 0.1:
                st.markdown(f"""
                <div class="insight-box positive">
                    <strong>Longer comments don't really correlate with higher scores!</strong><br>
                    +{corr_stats_l2['difference']:.1f} pts avg difference · r = {corr_stats_l2['correlation']:.3f}
                </div>
                """, unsafe_allow_html=True)
            elif corr_stats_l2['correlation'] < -0.1:
                st.markdown(f"""
                <div class="insight-box negative">
                    <strong>Shorter comments actually score better here</strong><br>
                    {corr_stats_l2['difference']:.1f} pts difference · r = {corr_stats_l2['correlation']:.3f}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="insight-box neutral">
                    <strong>No strong relationship</strong> between comment length and points.
                </div>
                """, unsafe_allow_html=True)

# =============================================================================
# Tab 2: Critic Rankings
# =============================================================================
with tab2:
    st.markdown("""
    <div class="section-header">
        <span class="icon">🎭</span>
        <h2>The Critics</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Who leaves the most detailed vote comments?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        if len(critics_l1) > 0:
            top = critics_l1.iloc[0]
            st.markdown(f"""
            <div class="critic-card">
                <div class="top-label">Top Critic</div>
                <div class="name">{top['Voter']}</div>
                <div class="score">{top['Avg Length']:.0f} <span class="unit">avg chars</span></div>
            </div>
            """, unsafe_allow_html=True)

            fig = px.bar(
                critics_l1.head(10),
                x='Avg Length',
                y='Voter',
                orientation='h',
                color_discrete_sequence=[LEAGUE_COLORS.get(league1, '#2980b9')]
            )
            apply_plotly_theme(fig, title=f"Critic Rankings - {league1_display}", height=350, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No comment data available")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        if len(critics_l2) > 0:
            top = critics_l2.iloc[0]
            st.markdown(f"""
            <div class="critic-card">
                <div class="top-label">Top Critic</div>
                <div class="name">{top['Voter']}</div>
                <div class="score">{top['Avg Length']:.0f} <span class="unit">avg chars</span></div>
            </div>
            """, unsafe_allow_html=True)

            fig = px.bar(
                critics_l2.head(10),
                x='Avg Length',
                y='Voter',
                orientation='h',
                color_discrete_sequence=[LEAGUE_COLORS.get(league2, '#c0392b')]
            )
            apply_plotly_theme(fig, title=f"Critic Rankings - {league2_display}", height=350, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No comment data available")

    # Comment engagement by points
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <span class="icon">💬</span>
        <h2>Do Higher Points = More Comments?</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Do voters comment more when giving high points?")

    col1, col2 = st.columns(2)

    with col1:
        engagement_l1 = CommentMetrics.comment_engagement_by_points(data1)
        if len(engagement_l1) > 0:
            fig = px.scatter(
                engagement_l1,
                x='points',
                y='comment_rate',
                size='count',
                color_discrete_sequence=[LEAGUE_COLORS.get(league1, '#2980b9')],
                labels={'points': 'Points Given', 'comment_rate': 'Comment Rate %'}
            )
            apply_plotly_theme(fig, title=f"{league1_display}", height=350)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        engagement_l2 = CommentMetrics.comment_engagement_by_points(data2)
        if len(engagement_l2) > 0:
            fig = px.scatter(
                engagement_l2,
                x='points',
                y='comment_rate',
                size='count',
                color_discrete_sequence=[LEAGUE_COLORS.get(league2, '#c0392b')],
                labels={'points': 'Points Given', 'comment_rate': 'Comment Rate %'}
            )
            apply_plotly_theme(fig, title=f"{league2_display}", height=350)
            st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# Tab 3: Hall of Fame
# =============================================================================
with tab3:
    st.markdown("""
    <div class="section-header">
        <span class="icon">🏆</span>
        <h2>Hall of Fame</h2>
    </div>
    """, unsafe_allow_html=True)
    st.caption("The longest, most passionate comments from each league.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<span class="league-badge blue">{league1_display}</span>', unsafe_allow_html=True)
        best_l1 = get_best_comments(data1, n=8)

        if len(best_l1) > 0:
            for _, row in best_l1.iterrows():
                comment_preview = row['comment'][:200] + "..." if len(row['comment']) > 200 else row['comment']
                comment_type = "Submission" if row['type'] == 'submission' else "Vote"
                st.markdown(f"""
                <div class="quote-card">
                    <div class="quote-text">{comment_preview}</div>
                    <div class="quote-meta">
                        <span class="quote-author">{row['person']}</span> on "{row['song']}"
                        <br><span style="opacity: 0.5;">{comment_type} · {row['length']} chars</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No notable comments found")

    with col2:
        st.markdown(f'<span class="league-badge red">{league2_display}</span>', unsafe_allow_html=True)
        best_l2 = get_best_comments(data2, n=8)

        if len(best_l2) > 0:
            for _, row in best_l2.iterrows():
                comment_preview = row['comment'][:200] + "..." if len(row['comment']) > 200 else row['comment']
                comment_type = "Submission" if row['type'] == 'submission' else "Vote"
                st.markdown(f"""
                <div class="quote-card">
                    <div class="quote-text">{comment_preview}</div>
                    <div class="quote-meta">
                        <span class="quote-author">{row['person']}</span> on "{row['song']}"
                        <br><span style="opacity: 0.5;">{comment_type} · {row['length']} chars</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No notable comments found")

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

    **Wordsmiths** - Submitters who write detailed song explanations

    **Critics** - Voters who leave thoughtful feedback

    **Hall of Fame** - The most notable comments

    ---

    **Metrics:**

    **Avg Length** - Average characters per comment

    **Comment Rate** - % of submissions/votes with comments
    """)
