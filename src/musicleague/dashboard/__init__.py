"""
Dashboard utilities for the Soundwave Smackdown Streamlit app.
"""

from musicleague.config import DEFAULT_LEAGUES, format_league_name
from musicleague.visualizations.base import (
    apply_plotly_theme,
    get_plotly_layout,
    PLOTLY_FONT_SIZES,
)
from musicleague.dashboard.helpers import (
    load_preprocessed_data,
    load_league_data,
    get_league_summary_stats,
    get_top_songs,
    get_most_controversial_songs,
    get_hidden_gems,
    get_submitter_rankings,
    get_voter_rankings,
    get_influence_rankings,
    create_comparison_metrics,
    calculate_weighted_score,
    get_league_champion,
    get_player_champion,
    # Comment helpers
    get_wordsmith_rankings,
    get_critic_rankings,
    get_best_comments,
    # Trends helpers
    get_round_by_round_performance,
    get_momentum_rankings,
    get_player_arcs,
    get_player_round_scores,
    get_round_champions,
)
from musicleague.dashboard.theme import (
    load_custom_css,
    get_league_color,
    get_metric_display_name,
    get_metric_tooltip,
    create_vs_divider,
    create_league_header,
    setup_page,
    LEAGUE_COLORS,
    ACCENT_COLORS,
    METRIC_NAMES,
    METRIC_TOOLTIPS,
    PAGE_CONFIG,
)
from musicleague.dashboard.narrative import (
    generate_champion_commentary,
    generate_submitter_commentary,
    generate_voter_shift_commentary,
    generate_controversy_commentary,
    generate_hidden_gem_commentary,
    generate_final_verdict,
    generate_network_commentary,
    # Comment narratives
    generate_wordsmith_commentary,
    generate_best_comment_showcase,
    # Trends narratives
    generate_momentum_commentary,
    generate_arc_commentary,
    generate_round_highlight,
    ARC_ICONS,
)

__all__ = [
    # Config
    "DEFAULT_LEAGUES",
    "format_league_name",
    # Plotly Theme
    "apply_plotly_theme",
    "get_plotly_layout",
    "PLOTLY_FONT_SIZES",
    # Helpers
    "load_preprocessed_data",
    "load_league_data",
    "get_league_summary_stats",
    "get_top_songs",
    "get_most_controversial_songs",
    "get_hidden_gems",
    "get_submitter_rankings",
    "get_voter_rankings",
    "get_influence_rankings",
    "create_comparison_metrics",
    "calculate_weighted_score",
    "get_league_champion",
    "get_player_champion",
    # Comment helpers
    "get_wordsmith_rankings",
    "get_critic_rankings",
    "get_best_comments",
    # Trends helpers
    "get_round_by_round_performance",
    "get_momentum_rankings",
    "get_player_arcs",
    "get_player_round_scores",
    "get_round_champions",
    # Theme
    "load_custom_css",
    "get_league_color",
    "get_metric_display_name",
    "get_metric_tooltip",
    "create_vs_divider",
    "create_league_header",
    "setup_page",
    "LEAGUE_COLORS",
    "ACCENT_COLORS",
    "METRIC_NAMES",
    "METRIC_TOOLTIPS",
    "PAGE_CONFIG",
    # Narrative
    "generate_champion_commentary",
    "generate_submitter_commentary",
    "generate_voter_shift_commentary",
    "generate_controversy_commentary",
    "generate_hidden_gem_commentary",
    "generate_final_verdict",
    "generate_network_commentary",
    # Comment narratives
    "generate_wordsmith_commentary",
    "generate_best_comment_showcase",
    # Trends narratives
    "generate_momentum_commentary",
    "generate_arc_commentary",
    "generate_round_highlight",
    "ARC_ICONS",
]

