"""
Music League Dashboard - Entry Point

This is the main entry point for the Streamlit multipage app.
Uses st.navigation() for explicit control over page names and order.
"""

import streamlit as st

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Music League Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Define pages with explicit titles (no filename-based naming)
pages = [
    st.Page("pages/0_🏠_Home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/1_🎵_Songs.py", title="Songs", icon="🎵"),
    st.Page("pages/2_🌟_Players.py", title="Players", icon="🌟"),
    st.Page("pages/4_📈_Trends.py", title="Trends", icon="📈"),
    st.Page("pages/3_💬_Commentary_Booth.py", title="Commentary", icon="💬"),
    st.Page("pages/5_🕸️_Connections.py", title="Connections", icon="🕸️"),
    st.Page("pages/6_⚖️_Final_Scorecard.py", title="Scorecard", icon="⚖️"),
]

# Create navigation and run the selected page
nav = st.navigation(pages)
nav.run()
