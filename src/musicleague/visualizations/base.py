"""
Base visualization configuration and utilities.

Provides shared configuration for matplotlib and plotly visualizations.
"""

import os
import matplotlib as mpl
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio

from musicleague.config import VisualizationConfig


# =============================================================================
# Plotly Theme Configuration
# =============================================================================

# Font sizes for Plotly charts (in pixels)
PLOTLY_FONT_SIZES = {
    'title': 24,
    'axis_title': 18,
    'tick_label': 16,
    'legend': 16,
    'annotation': 16,
    'hover': 16,
    'heatmap_text': 12,
}

# Font family for Plotly (SpotifyMix with fallbacks)
PLOTLY_FONT_FAMILY = "SpotifyMix, SpotifyMix-Medium, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

# Colors from theme
PLOTLY_THEME_COLORS = {
    'background': 'rgba(0,0,0,0)',
    'paper': 'rgba(0,0,0,0)',
    'text': '#ecf0f1',
    'grid': 'rgba(127,140,141,0.2)',
    'axis': '#eeeeee',
}


def get_plotly_layout(**overrides) -> dict:
    """
    Get standard Plotly layout configuration with consistent font sizes.

    This ensures all charts have readable fonts that match the dashboard style.

    Args:
        **overrides: Any layout properties to override the defaults

    Returns:
        dict: Layout configuration to pass to fig.update_layout()
    """
    base_layout = {
        # Title styling
        'title': {
            'font': {
                'size': PLOTLY_FONT_SIZES['title'],
                'family': PLOTLY_FONT_FAMILY,
                'color': PLOTLY_THEME_COLORS['text'],
            },
            'x': 0.5,
            'xanchor': 'center',
        },
        # Font defaults (applies to all text not otherwise specified)
        'font': {
            'size': PLOTLY_FONT_SIZES['tick_label'],
            'family': PLOTLY_FONT_FAMILY,
            'color': PLOTLY_THEME_COLORS['text'],
        },
        # X-axis styling
        'xaxis': {
            'title': {
                'font': {
                    'size': PLOTLY_FONT_SIZES['axis_title'],
                    'family': PLOTLY_FONT_FAMILY,
                    'color': PLOTLY_THEME_COLORS['text'],
                }
            },
            'tickfont': {
                'size': PLOTLY_FONT_SIZES['tick_label'],
                'family': PLOTLY_FONT_FAMILY,
                'color': PLOTLY_THEME_COLORS['axis'],
            },
            'gridcolor': PLOTLY_THEME_COLORS['grid'],
        },
        # Y-axis styling
        'yaxis': {
            'title': {
                'font': {
                    'size': PLOTLY_FONT_SIZES['axis_title'],
                    'family': PLOTLY_FONT_FAMILY,
                    'color': PLOTLY_THEME_COLORS['text'],
                }
            },
            'tickfont': {
                'size': PLOTLY_FONT_SIZES['tick_label'],
                'family': PLOTLY_FONT_FAMILY,
                'color': PLOTLY_THEME_COLORS['axis'],
            },
            'gridcolor': PLOTLY_THEME_COLORS['grid'],
        },
        # Legend styling
        'legend': {
            'font': {
                'size': PLOTLY_FONT_SIZES['legend'],
                'family': PLOTLY_FONT_FAMILY,
                'color': PLOTLY_THEME_COLORS['text'],
            },
        },
        # Hover label styling
        'hoverlabel': {
            'font': {
                'size': PLOTLY_FONT_SIZES['hover'],
                'family': PLOTLY_FONT_FAMILY,
            },
        },
        # Background colors (transparent for dashboard integration)
        'plot_bgcolor': PLOTLY_THEME_COLORS['background'],
        'paper_bgcolor': PLOTLY_THEME_COLORS['paper'],
        # Margins
        'margin': {'l': 60, 'r': 30, 't': 50, 'b': 50},
    }

    # Apply overrides
    for key, value in overrides.items():
        if isinstance(value, dict) and key in base_layout and isinstance(base_layout[key], dict):
            # Merge nested dicts
            base_layout[key] = {**base_layout[key], **value}
        else:
            base_layout[key] = value

    return base_layout


def apply_plotly_theme(fig: go.Figure, **overrides) -> go.Figure:
    """
    Apply the standard Plotly theme to a figure.

    Args:
        fig: Plotly figure to style
        **overrides: Any layout properties to override

    Returns:
        The styled figure
    """
    fig.update_layout(**get_plotly_layout(**overrides))
    return fig


# =============================================================================
# Matplotlib Configuration
# =============================================================================

def configure_matplotlib():
    """Configure matplotlib with project styling."""
    # Set base style
    plt.style.use("seaborn-v0_8-whitegrid")

    # Color configuration
    COLOR = "black"
    mpl.rcParams["text.color"] = COLOR
    mpl.rcParams["axes.labelcolor"] = COLOR
    mpl.rcParams["xtick.color"] = COLOR
    mpl.rcParams["ytick.color"] = COLOR

    # Font configuration - check if Spotify fonts are available
    font_path = "resources/SpotifyMix-Medium.otf"
    italic_font_path = "resources/SpotifyMix-ThinItalic.otf"

    if os.path.exists(font_path):
        font_manager.fontManager.addfont(font_path)
        prop = font_manager.FontProperties(fname=font_path)
        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = prop.get_name()

    if os.path.exists(italic_font_path):
        font_manager.fontManager.addfont(italic_font_path)

    plt.rcParams["font.size"] = 18


def configure_axes(
    ax,
    title: str,
    xlabel: str,
    ylabel: str,
    disable_grid: bool = True,
    legend_below: bool = False,
    legend_cols: int = 4
):
    """
    Configure axes according to plotting rules.

    Args:
        ax: Matplotlib axes object
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        disable_grid: Whether to disable grid (default True)
        legend_below: Whether to place legend below plot (default False)
        legend_cols: Number of columns for legend (default 4)
    """
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if disable_grid:
        ax.grid(False)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    if ax.get_legend() is not None:
        if legend_below:
            ax.legend(
                loc='upper center',
                bbox_to_anchor=(0.5, -0.15),
                ncol=legend_cols,
                frameon=False
            )
        else:
            ax.legend(frameon=False)


# Initialize matplotlib configuration
configure_matplotlib()

# Export color palettes for convenience
COLORS = VisualizationConfig.COLORS
COLORS_DICT = VisualizationConfig.COLORS_DICT
PLOTLY_COLORS = COLORS

