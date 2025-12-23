"""
Theme configuration for the Soundwave Smackdown dashboard.
Defines colors, styling, and branding for consistent visual identity.
"""

import streamlit as st
from typing import Optional

from musicleague.config import VisualizationConfig

# Page configuration constants
PAGE_CONFIG = {
    "page_title": "Music League Dashboard",
    "page_icon": "🎵",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Re-export from config for backwards compatibility and convenience
LEAGUE_COLORS = VisualizationConfig.LEAGUE_COLORS
ACCENT_COLORS = VisualizationConfig.COLORS_DICT
METRIC_NAMES = VisualizationConfig.METRIC_NAMES
COLORS = VisualizationConfig.COLORS_DICT
COLORS_DARK = VisualizationConfig.COLORS_DARK
BG_COLORS = VisualizationConfig.BG_COLORS
SEMANTIC = VisualizationConfig.SEMANTIC

# Tooltip descriptions for metrics
METRIC_TOOLTIPS = {
    'total_votes': "How many fans showed up to the gig? This is pure crowd energy.",
    'total_competitors': "How deep is the bench? More players means more variety... or more duds.",
    'total_submissions': "The total number of songs thrown into the ring. A sheer wall of sound!",
    'avg_points_per_submission': "Who's the best talent scout? This is the average score for a player's picks.",
    'controversy_score': "Based on vote standard deviation (σ). A high score means the crowd was fighting in the aisles over this track.",
    'obscurity_score': "Our 'Obscurity Score.' Did this song score big points while having zero Spotify fame? That's cred.",
    'golden_ear_score': "This player's votes line up with the final winners. They're not just a fan; they're a prophet.",
    'hipster_score': "Who only votes for tracks nobody's ever heard of? This is their badge of honor.",
    'influence_score': "Who's the real MVP? This score shows who's the most influential player in the league's voting network.",
    'generosity_score': "How freely does this voter hand out points? Generous or stingy?",
}


def load_custom_css():
    """Load custom CSS for dashboard styling.

    This is the single source of truth for all dashboard CSS.
    All pages should use setup_page() which calls this function.
    Do NOT add inline CSS to individual page files.
    """
    # Get colors from config
    blue = VisualizationConfig.COLORS_DICT['blue']          # #2980b9
    blue_dark = VisualizationConfig.COLORS_DARK['blue']     # #1a5276
    red = VisualizationConfig.COLORS_DICT['red']            # #c0392b
    red_dark = VisualizationConfig.COLORS_DARK['red']       # #922b21
    green = VisualizationConfig.COLORS_DICT['green']        # #16a085
    green_dark = VisualizationConfig.COLORS_DARK['green']   # #0e6655
    purple = VisualizationConfig.COLORS_DICT['purple']      # #8e44ad
    purple_dark = VisualizationConfig.COLORS_DARK['purple'] # #6c3483
    orange = VisualizationConfig.COLORS_DICT['orange']      # #d35400
    orange_dark = VisualizationConfig.COLORS_DARK['orange'] # #a04000
    gray = VisualizationConfig.COLORS_DICT['gray']          # #7f8c8d
    gray_dark = VisualizationConfig.COLORS_DARK['gray']     # #566573
    white = VisualizationConfig.COLORS_DICT['white']        # #ecf0f1
    gold = VisualizationConfig.COLORS_DICT['gold']          # #FFC864

    bg_dark = VisualizationConfig.BG_COLORS['dark']         # #1f1f1f
    bg_card = VisualizationConfig.BG_COLORS['card']         # #2a2a2a

    # Semantic background colors for positive/negative states
    bg_positive = '#1a3a2a'
    bg_positive_end = '#1f2f1f'
    bg_negative = '#3a1a1a'
    bg_negative_end = '#2f1f1f'

    st.markdown(f"""
    <style>
    /* ==========================================================================
       CSS CUSTOM PROPERTIES (Design Tokens)
       Centralized color and spacing values for consistency
       ========================================================================== */
    :root {{
        /* Primary colors */
        --color-blue: {blue};
        --color-blue-dark: {blue_dark};
        --color-red: {red};
        --color-red-dark: {red_dark};
        --color-green: {green};
        --color-green-dark: {green_dark};
        --color-purple: {purple};
        --color-purple-dark: {purple_dark};
        --color-orange: {orange};
        --color-orange-dark: {orange_dark};
        --color-gray: {gray};
        --color-gray-dark: {gray_dark};
        --color-gold: {gold};
        --color-white: {white};

        /* Background colors */
        --bg-dark: {bg_dark};
        --bg-card: {bg_card};

        /* Semantic backgrounds */
        --bg-positive: {bg_positive};
        --bg-positive-end: {bg_positive_end};
        --bg-negative: {bg_negative};
        --bg-negative-end: {bg_negative_end};

        /* Common gradients */
        --gradient-dark: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-card) 100%);
        --gradient-dark-reverse: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-dark) 100%);
        --gradient-blue: linear-gradient(135deg, var(--color-blue) 0%, var(--color-blue-dark) 100%);
        --gradient-red: linear-gradient(135deg, var(--color-red) 0%, var(--color-red-dark) 100%);
        --gradient-green: linear-gradient(135deg, var(--color-green) 0%, var(--color-green-dark) 100%);
        --gradient-purple: linear-gradient(135deg, var(--color-purple) 0%, var(--color-purple-dark) 100%);
        --gradient-orange: linear-gradient(135deg, var(--color-orange) 0%, var(--color-orange-dark) 100%);
        --gradient-gold: linear-gradient(135deg, var(--color-gold) 0%, var(--color-orange) 100%);
        --gradient-positive: linear-gradient(135deg, var(--bg-positive) 0%, var(--bg-positive-end) 100%);
        --gradient-negative: linear-gradient(135deg, var(--bg-negative) 0%, var(--bg-negative-end) 100%);

        /* Spacing */
        --spacing-xs: 0.25rem;
        --spacing-sm: 0.5rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;

        /* Border radius */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-pill: 20px;
        --radius-round: 50%;
    }}

    /* ==========================================================================
       BASE UTILITY CLASSES
       Reusable patterns to reduce duplication
       ========================================================================== */

    /* Gradient text effect - apply to any element needing gradient text */
    .gradient-text {{
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    /* Card base - common card styling */
    .card-base {{
        color: white;
        padding: var(--spacing-lg);
        border-radius: var(--radius-md);
        margin-bottom: var(--spacing-md);
    }}

    /* Left-border accent card base */
    .accent-card {{
        background: var(--gradient-dark-reverse);
        border-left: 4px solid var(--color-blue);
        padding: var(--spacing-md) 1.25rem;
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        margin-bottom: 0.75rem;
    }}
    .accent-card.positive {{ border-color: var(--color-green); background: var(--gradient-positive); }}
    .accent-card.negative {{ border-color: var(--color-red); background: var(--gradient-negative); }}
    .accent-card.neutral {{ border-color: var(--color-gray); }}
    .accent-card.purple {{ border-color: var(--color-purple); }}
    .accent-card.green {{ border-color: var(--color-green); }}

    /* Common child element patterns */
    .card-name {{
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: var(--spacing-sm);
    }}
    .card-score {{
        font-size: 2rem;
        font-weight: 900;
        color: var(--color-gold);
    }}
    .card-label {{
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.8;
    }}
    .card-stats {{
        display: flex;
        gap: var(--spacing-lg);
    }}

    /* Color modifier classes for gradients */
    .bg-gradient-blue {{ background: var(--gradient-blue); }}
    .bg-gradient-red {{ background: var(--gradient-red); }}
    .bg-gradient-green {{ background: var(--gradient-green); }}
    .bg-gradient-purple {{ background: var(--gradient-purple); }}
    .bg-gradient-orange {{ background: var(--gradient-orange); }}
    .bg-gradient-gold {{ background: var(--gradient-gold); color: var(--bg-dark); }}
    .bg-gradient-dark {{ background: var(--gradient-dark); }}
    .bg-gradient-dark-reverse {{ background: var(--gradient-dark-reverse); }}

    /* ==========================================================================
       MAIN CONTAINER
       ========================================================================== */
    .main {{
        padding: 0rem 1rem;
    }}

    /* ==========================================================================
       PAGE HEADERS - Gradient titles for each page
       ========================================================================== */
    .page-header {{
        text-align: center;
        margin-bottom: var(--spacing-xl);
    }}
    .page-header h1 {{
        font-size: 2.5rem;
        font-weight: 900;
        margin-bottom: var(--spacing-sm);
    }}
    .page-header p {{
        color: var(--color-gray);
        font-size: 1.1rem;
    }}

    /* Page-specific header gradients - background-clip must be with background */
    .page-header.songs h1 {{
        background: linear-gradient(135deg, {green} 0%, {bg_dark} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .page-header.players h1 {{
        background: linear-gradient(135deg, {orange} 0%, {red} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .page-header.commentary h1 {{
        background: linear-gradient(135deg, {blue} 0%, {purple} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .page-header.trends h1 {{
        background: linear-gradient(135deg, {green} 0%, {green_dark} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .page-header.connections h1 {{
        background: linear-gradient(135deg, {purple} 0%, {blue} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .page-header.scorecard h1 {{
        background: linear-gradient(135deg, {gold} 0%, {orange} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .page-header.home h1 {{
        background: linear-gradient(135deg, {blue} 0%, {purple} 50%, {red} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    /* ==========================================================================
       STAT HIGHLIGHTS - Big number cards
       ========================================================================== */
    .stat-highlight {{
        background: linear-gradient(135deg, {blue} 0%, {purple} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
    }}
    .stat-highlight .number {{
        font-size: 2.5rem;
        font-weight: 900;
    }}
    .stat-highlight .label {{
        font-size: 0.85rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* Stat highlight color variants */
    .stat-highlight.blue {{ background: linear-gradient(135deg, {blue} 0%, {blue_dark} 100%); }}
    .stat-highlight.red {{ background: linear-gradient(135deg, {red} 0%, {red_dark} 100%); }}
    .stat-highlight.green {{ background: linear-gradient(135deg, {green} 0%, {green_dark} 100%); }}
    .stat-highlight.purple {{ background: linear-gradient(135deg, {purple} 0%, {purple_dark} 100%); }}
    .stat-highlight.orange {{ background: linear-gradient(135deg, {orange} 0%, {orange_dark} 100%); }}
    .stat-highlight.gold {{ background: linear-gradient(135deg, {gold} 0%, {orange} 100%); color: {bg_dark}; }}
    .stat-highlight.dark {{ background: linear-gradient(135deg, {bg_dark} 0%, {bg_card} 100%); }}

    /* ==========================================================================
       SECTION HEADERS - Icon + title combos
       ========================================================================== */
    .section-header {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2rem 0 1rem 0;
    }}
    .section-header .icon {{
        font-size: 2rem;
    }}
    .section-header h2 {{
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
    }}

    /* ==========================================================================
       LEAGUE BADGES - Small colored pills
       ========================================================================== */
    .league-badge {{
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        color: white;
    }}
    .league-badge.blue {{ background: linear-gradient(135deg, {blue} 0%, {blue_dark} 100%); }}
    .league-badge.red {{ background: linear-gradient(135deg, {red} 0%, {red_dark} 100%); }}

    /* ==========================================================================
       PLAYER CARDS - Individual player stat cards
       ========================================================================== */
    .player-card {{
        background: linear-gradient(135deg, {bg_dark} 0%, {bg_card} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }}
    .player-card .rank {{
        position: absolute;
        top: 0.75rem;
        right: 1rem;
        font-size: 2rem;
        font-weight: 900;
        color: rgba(255, 200, 100, 0.3);
    }}
    .player-card .name {{
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }}
    .player-card .stats {{
        display: flex;
        gap: 1.5rem;
    }}
    .player-card .stat {{
        text-align: center;
    }}
    .player-card .stat-value {{
        font-size: 1.5rem;
        font-weight: 900;
        color: {gold};
    }}
    .player-card .stat-label {{
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.7;
    }}

    /* ==========================================================================
       TRAIT BADGES - Small colored pills for player traits
       ========================================================================== */
    .trait-badge {{
        display: inline-block;
        padding: 0.3rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }}
    .trait-badge.gold {{ background: {gold}; color: {bg_dark}; }}
    .trait-badge.green {{ background: {green}; color: white; }}
    .trait-badge.purple {{ background: {purple}; color: white; }}
    .trait-badge.orange {{ background: {orange}; color: white; }}
    .trait-badge.blue {{ background: {blue}; color: white; }}
    .trait-badge.red {{ background: {red}; color: white; }}

    /* ==========================================================================
       INSIGHT CARDS - Bordered info cards
       ========================================================================== */
    .insight-card {{
        background: linear-gradient(135deg, {bg_card} 0%, {bg_dark} 100%);
        border-left: 4px solid {blue};
        padding: 1.25rem;
        border-radius: 0 12px 12px 0;
        margin-bottom: 1rem;
    }}
    .insight-card h4 {{
        margin: 0 0 0.5rem 0;
        color: white;
    }}
    .insight-card p {{
        margin: 0;
        color: {gray};
        font-size: 0.95rem;
    }}
    .insight-card.positive {{ border-color: var(--color-green); background: var(--gradient-positive); }}
    .insight-card.negative {{ border-color: var(--color-red); background: var(--gradient-negative); }}
    .insight-card.neutral {{ border-color: {gray}; }}

    /* ==========================================================================
       COMMENT CARDS - For commentary booth
       ========================================================================== */
    .comment-card {{
        background: linear-gradient(135deg, {bg_card} 0%, {bg_dark} 100%);
        border-left: 4px solid {blue};
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.75rem;
    }}
    .comment-card .author {{
        color: white;
        font-weight: 600;
    }}
    .comment-card .text {{
        color: white;
        margin-top: 0.5rem;
    }}
    .comment-card.positive {{ border-color: var(--color-green); background: var(--gradient-positive); }}
    .comment-card.negative {{ border-color: var(--color-red); background: var(--gradient-negative); }}

    /* ==========================================================================
       WORDSMITH CARDS - For commentary stats
       ========================================================================== */
    .wordsmith-card {{
        background: linear-gradient(135deg, {blue} 0%, {blue_dark} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }}
    .wordsmith-card.blue {{ background: linear-gradient(135deg, {blue} 0%, {blue_dark} 100%); }}
    .wordsmith-card.red {{ background: linear-gradient(135deg, {red} 0%, {red_dark} 100%); }}
    .wordsmith-card .top-label {{
        font-size: 0.75rem;
        text-transform: uppercase;
        opacity: 0.8;
        letter-spacing: 1px;
    }}
    .wordsmith-card .name {{
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    .wordsmith-card .stats {{
        display: flex;
        gap: 1.5rem;
        margin-top: 0.75rem;
    }}
    .wordsmith-card .stat-value {{
        font-size: 1.5rem;
        font-weight: 900;
    }}
    .wordsmith-card .stat-label {{
        font-size: 0.7rem;
        text-transform: uppercase;
        opacity: 0.8;
    }}

    /* ==========================================================================
       MATCHUP CARDS - For league comparisons
       ========================================================================== */
    .matchup-box {{
        text-align: center;
        padding: 0.5rem;
    }}
    .matchup-box .league-name {{
        padding: 0.75rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        color: white;
        margin-bottom: 0.5rem;
    }}
    .matchup-box .league-name.blue {{ background: linear-gradient(135deg, {blue} 0%, {blue_dark} 100%); }}
    .matchup-box .league-name.red {{ background: linear-gradient(135deg, {red} 0%, {red_dark} 100%); }}
    .matchup-box .vs {{
        font-weight: 900;
        color: {gray};
        margin: 0.25rem 0;
    }}

    /* ==========================================================================
       METRIC CARDS - General purpose
       ========================================================================== */
    .metric-card {{
        background: linear-gradient(135deg, {blue} 0%, {purple} 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }}

    /* ==========================================================================
       VS STYLING - For comparison dividers
       ========================================================================== */
    .vs-text {{
        text-align: center;
        font-size: 4rem;
        font-weight: 900;
        color: {gold};
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
        padding: 2rem 0;
    }}

    /* ==========================================================================
       LEAGUE HEADERS - Large titled boxes
       ========================================================================== */
    .league-header-blue {{
        background: linear-gradient(135deg, {blue} 0%, {blue_dark} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(41, 128, 185, 0.3);
    }}
    .league-header-red {{
        background: linear-gradient(135deg, {red} 0%, {red_dark} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(192, 57, 43, 0.3);
    }}

    /* ==========================================================================
       SONG CARDS - For songs page
       ========================================================================== */
    .song-card {{
        background: linear-gradient(135deg, {bg_dark} 0%, {bg_card} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }}
    .song-card .title {{
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    .song-card .artist {{
        color: {gray};
        font-size: 0.9rem;
    }}
    .song-card .points {{
        font-size: 2rem;
        font-weight: 900;
        color: {gold};
    }}

    /* ==========================================================================
       NETWORK/CONNECTION STYLES
       ========================================================================== */
    .connection-card {{
        background: linear-gradient(135deg, {bg_card} 0%, {bg_dark} 100%);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }}
    .connection-card .voter {{
        font-weight: 600;
        color: white;
    }}
    .connection-card .change {{
        font-weight: 700;
    }}
    .connection-card .change.positive {{ color: {green}; }}
    .connection-card .change.negative {{ color: {red}; }}

    /* ==========================================================================
       MOMENTUM CARDS - Trends page player momentum display
       ========================================================================== */
    .momentum-card {{
        background: linear-gradient(135deg, {bg_dark} 0%, {bg_card} 100%);
        color: white;
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .momentum-card .player-info {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    .momentum-card .trend-icon {{
        font-size: 1.5rem;
    }}
    .momentum-card .name {{
        font-weight: 700;
        font-size: 1.1rem;
    }}
    .momentum-card .streak {{
        font-size: 0.85rem;
        opacity: 0.7;
    }}
    .momentum-card .score {{
        font-size: 1.5rem;
        font-weight: 900;
    }}
    .momentum-card .score.rising {{ color: {green}; }}
    .momentum-card .score.falling {{ color: {red}; }}
    .momentum-card .score.steady {{ color: {gray}; }}

    /* ==========================================================================
       CHAMPION ROWS - Round-by-round winners
       ========================================================================== */
    .champion-row {{
        background: linear-gradient(135deg, {bg_card} 0%, {bg_dark} 100%);
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .champion-row .round-num {{
        background: {gold};
        color: {bg_dark};
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
    }}
    .champion-row .song-info {{
        flex: 1;
        margin-left: 1rem;
    }}
    .champion-row .song-name {{
        font-weight: 700;
        color: white;
    }}
    .champion-row .winner-name {{
        font-size: 0.85rem;
        color: #a0a0a0;
    }}
    .champion-row .points {{
        font-weight: 900;
        color: {green};
    }}

    /* ==========================================================================
       CHAMPION CARDS - Final Scorecard winner display
       ========================================================================== */
    .champion-card {{
        background: linear-gradient(135deg, {bg_dark} 0%, {bg_card} 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }}
    .champion-card::before {{
        content: "👑";
        position: absolute;
        top: 1rem;
        right: 1rem;
        font-size: 3rem;
        opacity: 0.2;
    }}
    .champion-card .league {{
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        opacity: 0.7;
        margin-bottom: 0.5rem;
    }}
    .champion-card .name {{
        font-size: 2rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
    }}
    .champion-card .score {{
        font-size: 3.5rem;
        font-weight: 900;
        color: {gold};
    }}
    .champion-card .margin {{
        font-size: 0.9rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }}
    .champion-card.blue {{ background: linear-gradient(135deg, {blue} 0%, {blue_dark} 100%); }}
    .champion-card.red {{ background: linear-gradient(135deg, {red} 0%, {red_dark} 100%); }}

    /* ==========================================================================
       WEIGHT CARDS - Scorecard weight sliders
       ========================================================================== */
    .weight-card {{
        background: linear-gradient(135deg, {bg_card} 0%, {bg_dark} 100%);
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .weight-card .metric {{
        font-weight: 600;
        color: white;
    }}
    .weight-card .value {{
        font-size: 1.2rem;
        font-weight: 900;
        color: {gold};
    }}

    /* ==========================================================================
       VERDICT BOX - Final verdict display
       ========================================================================== */
    .verdict-box {{
        background: linear-gradient(135deg, {bg_dark} 0%, {bg_card} 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin: 2rem 0;
    }}
    .verdict-box .title {{
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        opacity: 0.7;
        margin-bottom: 1rem;
    }}
    .verdict-box .content {{
        font-size: 1.1rem;
        line-height: 1.6;
    }}

    /* ==========================================================================
       METRIC EXPLAINER - Scorecard metric descriptions
       ========================================================================== */
    .metric-explainer {{
        background: linear-gradient(135deg, {bg_card} 0%, {bg_dark} 100%);
        border-left: 4px solid {purple};
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.75rem;
    }}
    .metric-explainer .name {{
        font-weight: 700;
        color: white;
    }}
    .metric-explainer .desc {{
        color: #a0a0a0;
        font-size: 0.9rem;
    }}

    /* ==========================================================================
       INFLUENCE CARDS - Connections page
       ========================================================================== */
    .influence-card {{
        background: linear-gradient(135deg, {bg_dark} 0%, {bg_card} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1rem;
    }}
    .influence-card .rank {{
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.7;
        margin-bottom: 0.5rem;
    }}
    .influence-card .name {{
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    .influence-card .score {{
        font-size: 2.5rem;
        font-weight: 900;
        color: {gold};
    }}
    .influence-card .score-label {{
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.7;
    }}

    /* ==========================================================================
       CONTROVERSIAL CARDS - Most divisive songs
       ========================================================================== */
    .controversial-card {{
        background: linear-gradient(135deg, {red} 0%, {red_dark} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }}
    .controversial-card .label {{
        font-size: 0.8rem;
        text-transform: uppercase;
        opacity: 0.8;
        letter-spacing: 1px;
    }}
    .controversial-card .song-name {{
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }}
    .controversial-card .artist {{
        opacity: 0.85;
    }}
    .controversial-card .score {{
        margin-top: 1rem;
        font-size: 2rem;
        font-weight: 900;
    }}

    /* ==========================================================================
       ROUND CHAMPION CARDS - For trends page champions
       ========================================================================== */
    .round-champion-card {{
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
    }}
    .round-champion-card.blue {{ background: linear-gradient(135deg, {blue} 0%, {blue_dark} 100%); }}
    .round-champion-card.red {{ background: linear-gradient(135deg, {red} 0%, {red_dark} 100%); }}
    .round-champion-card .label {{
        font-size: 0.8rem;
        text-transform: uppercase;
        opacity: 0.8;
        letter-spacing: 1px;
    }}
    .round-champion-card .name {{
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }}
    .round-champion-card .wins {{
        font-size: 2.5rem;
        font-weight: 900;
        color: {gold};
    }}

    /* ==========================================================================
       INFLUENCE CHANGE ROWS - For connections page
       ========================================================================== */
    .influence-change-row {{
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid;
    }}
    .influence-change-row.positive {{
        background: var(--gradient-positive);
        border-color: var(--color-green);
    }}
    .influence-change-row.negative {{
        background: var(--gradient-negative);
        border-color: var(--color-red);
    }}
    .influence-change-row .name {{
        font-weight: 600;
        color: white;
    }}
    .influence-change-row.positive .change {{ color: {green}; font-weight: 700; }}
    .influence-change-row.negative .change {{ color: {red}; font-weight: 700; }}

    /* ==========================================================================
       CRITIC CARDS - For top critic display
       ========================================================================== */
    .critic-card {{
        background: linear-gradient(135deg, {purple} 0%, {purple_dark} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }}
    .critic-card .top-label {{
        font-size: 0.75rem;
        text-transform: uppercase;
        opacity: 0.8;
        letter-spacing: 1px;
    }}
    .critic-card .name {{
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }}
    .critic-card .score {{
        font-size: 2rem;
        font-weight: 900;
    }}
    .critic-card .unit {{
        font-size: 0.9rem;
        opacity: 0.8;
    }}

    /* ==========================================================================
       QUOTE CARDS - Hall of Fame comments
       ========================================================================== */
    .quote-card {{
        background: linear-gradient(135deg, {bg_dark} 0%, {bg_card} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        position: relative;
    }}
    .quote-card::before {{
        content: '"';
        font-size: 4rem;
        position: absolute;
        top: -0.5rem;
        left: 0.5rem;
        opacity: 0.15;
        font-family: Georgia, serif;
    }}
    .quote-card .quote-text {{
        font-style: italic;
        font-size: 1.05rem;
        line-height: 1.5;
        margin-bottom: 1rem;
        padding-left: 1rem;
    }}
    .quote-card .quote-meta {{
        font-size: 0.85rem;
        opacity: 0.7;
    }}
    .quote-card .quote-author {{
        font-weight: 700;
        color: {gold};
    }}

    /* ==========================================================================
       GEM CARDS - Hidden gems display
       ========================================================================== */
    .gem-card {{
        background: linear-gradient(135deg, {bg_dark} 0%, {bg_card} 100%);
        color: white;
        padding: 1.25rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
        border-left: 4px solid {green};
    }}
    .gem-card .song-name {{
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 0.5rem;
    }}
    .gem-card .meta {{
        font-size: 0.85rem;
        color: {gray};
    }}

    /* ==========================================================================
       INSIGHT BOX - Commentary analysis
       ========================================================================== */
    .insight-box {{
        background: linear-gradient(135deg, {bg_card} 0%, {bg_dark} 100%);
        border-left: 4px solid {blue};
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        color: white;
    }}
    .insight-box strong {{ color: white; }}
    .insight-box.positive {{
        border-color: var(--color-green);
        background: var(--gradient-positive);
    }}
    .insight-box.negative {{
        border-color: var(--color-red);
        background: var(--gradient-negative);
    }}
    .insight-box.neutral {{ border-color: {gray}; }}

    /* ==========================================================================
       RELATIONSHIP ROWS - Reciprocity display
       ========================================================================== */
    .relationship-row {{
        background: linear-gradient(135deg, {bg_card} 0%, {bg_dark} 100%);
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .relationship-row .pair {{
        font-weight: 600;
        color: white;
    }}
    .relationship-row .stats {{
        display: flex;
        gap: 1.5rem;
        font-size: 0.9rem;
        color: {gray};
    }}
    .relationship-row .reciprocity {{
        font-weight: 700;
        color: {green};
    }}

    /* ==========================================================================
       NETWORK STATS - Small stat boxes
       ========================================================================== */
    .network-stat {{
        background: linear-gradient(135deg, {bg_card} 0%, {bg_dark} 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }}
    .network-stat .value {{
        font-size: 1.8rem;
        font-weight: 900;
        color: white;
    }}
    .network-stat .label {{
        font-size: 0.75rem;
        color: #a0a0a0;
        text-transform: uppercase;
    }}

    /* ==========================================================================
       HOME PAGE - Hero and navigation
       ========================================================================== */
    .hero-title {{
        text-align: center;
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, {blue} 0%, {purple} 50%, {red} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
    }}
    .hero-subtitle {{
        text-align: center;
        font-size: 1.3rem;
        color: {gray};
        margin-bottom: 2rem;
    }}
    .vs-badge {{
        display: inline-block;
        background: linear-gradient(135deg, {bg_dark} 0%, {bg_card} 100%);
        color: {gold};
        font-size: 1.8rem;
        font-weight: 900;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        letter-spacing: 3px;
    }}
    .league-card {{
        background: linear-gradient(135deg, var(--bg-start) 0%, var(--bg-end) 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        transition: transform 0.2s ease;
    }}
    .league-card:hover {{
        transform: translateY(-4px);
    }}
    .league-card h2 {{
        margin: 0 0 0.5rem 0;
        font-size: 1.8rem;
        color: white !important;
        border: none !important;
    }}
    .league-card .stat-big {{
        font-size: 3rem;
        font-weight: 900;
        margin: 0.5rem 0;
    }}
    .league-card .stat-label {{
        font-size: 0.9rem;
        opacity: 0.85;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .champion-spotlight {{
        background: linear-gradient(135deg, {bg_dark} 0%, {bg_card} 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        position: relative;
        overflow: hidden;
    }}
    .champion-spotlight::before {{
        content: "🏆";
        position: absolute;
        right: 1rem;
        top: 1rem;
        font-size: 4rem;
        opacity: 0.15;
    }}
    .champion-spotlight h3 {{
        color: {gold} !important;
        margin-top: 0;
        border: none !important;
    }}
    .teaser-card {{
        background: linear-gradient(135deg, {bg_card} 0%, {bg_dark} 100%);
        border-left: 4px solid var(--accent);
        padding: 1.5rem;
        border-radius: 0 12px 12px 0;
        margin-bottom: 1rem;
    }}
    .teaser-card h4 {{
        margin: 0 0 0.5rem 0;
        color: white;
    }}
    .teaser-card p {{
        margin: 0;
        color: {gray};
        font-size: 0.95rem;
    }}

    /* ==========================================================================
       TREND INDICATORS
       ========================================================================== */
    .trend-up {{ color: {green}; }}
    .trend-down {{ color: {red}; }}
    .trend-neutral {{ color: {gray}; }}

    /* ==========================================================================
       STREAMLIT COMPONENT OVERRIDES
       ========================================================================== */
    /* Info box styling */
    .stAlert {{
        border-radius: 10px;
    }}

    /* Dataframe styling */
    .dataframe {{
        font-size: 0.9rem;
    }}

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        padding: 0px 24px;
        border-radius: 8px 8px 0px 0px;
        font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        border-bottom: 3px solid {blue};
    }}

    /* Button styling */
    .stButton > button {{
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
    }}

    /* ==========================================================================
       UTILITY CLASSES
       ========================================================================== */
    .text-gold {{ color: {gold}; }}
    .text-green {{ color: {green}; }}
    .text-red {{ color: {red}; }}
    .text-blue {{ color: {blue}; }}
    .text-purple {{ color: {purple}; }}
    .text-gray {{ color: {gray}; }}
    .text-white {{ color: white; }}

    .bg-dark {{ background: {bg_dark}; }}
    .bg-card {{ background: {bg_card}; }}
    </style>
    """, unsafe_allow_html=True)


def get_league_color(league_name: str) -> str:
    """Get the brand color for a specific league."""
    return LEAGUE_COLORS.get(league_name, ACCENT_COLORS['gray'])


def get_metric_display_name(metric_key: str) -> str:
    """Get the branded display name for a metric."""
    return METRIC_NAMES.get(metric_key, metric_key.replace('_', ' ').title())


def get_metric_tooltip(metric_key: str) -> str:
    """Get the tooltip description for a metric."""
    return METRIC_TOOLTIPS.get(metric_key, '')


def create_vs_divider():
    """Create a centered VS divider element."""
    st.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)


def create_league_header(league_name: str, is_blue: bool = True):
    """Create a styled header for a league."""
    header_class = "league-header-blue" if is_blue else "league-header-red"
    corner_text = "In the Blue Corner..." if is_blue else "In the Red Corner..."

    st.markdown(
        f'<div class="{header_class}">{corner_text}<br/>{league_name}</div>',
        unsafe_allow_html=True
    )


def setup_page():
    """
    Common page setup for all dashboard pages.

    Call this at the top of each page file. It handles:
    - Loading custom CSS

    Note: st.set_page_config() is called only in streamlit_app.py.
    In Streamlit multipage apps, set_page_config must be called exactly once
    in the main entry point, not in individual pages.
    """
    load_custom_css()

