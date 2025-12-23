"""
Network and relationship metrics for MusicLeague analysis.

Provides metrics based on voting relationships and network analysis,
including influence scores and reciprocity calculations.
"""

from typing import Dict, Optional, TYPE_CHECKING

import networkx as nx
import pandas as pd

if TYPE_CHECKING:
    from musicleague.data.loader import MusicLeagueData


class NetworkMetrics:
    """Metrics based on voting relationships and network analysis."""

    @staticmethod
    def build_voting_graph(
        data: "MusicLeagueData",
        round_id: Optional[str] = None
    ) -> nx.DiGraph:
        """
        Build directed graph of voting relationships.
        
        Edge weight represents total points from voter to submitter.
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            
        Returns:
            NetworkX DiGraph with competitors as nodes
        """
        G = nx.DiGraph()

        # Add all competitors as nodes
        for comp_id, comp_data in data.competitors.items():
            G.add_node(comp_data['name'], id=comp_id)

        # Add edges for votes
        for vote in data.votes:
            if round_id is None or vote['round_id'] == round_id:
                if vote['points'] > 0:
                    submitter_id = data.get_submitter_for_song(
                        vote['spotify_uri'],
                        vote['round_id']
                    )
                    if submitter_id and submitter_id != vote['voter_id']:
                        voter_name = data.competitors[vote['voter_id']]['name']
                        submitter_name = data.competitors[submitter_id]['name']

                        if G.has_edge(voter_name, submitter_name):
                            G[voter_name][submitter_name]['weight'] += vote['points']
                        else:
                            G.add_edge(voter_name, submitter_name, weight=vote['points'])

        return G

    @staticmethod
    def voting_reciprocity(
        data: "MusicLeagueData",
        round_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Calculate reciprocity between all voter-submitter pairs.
        
        Reciprocity score indicates how balanced the voting relationship is
        between two participants.
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            
        Returns:
            DataFrame with columns: voter, submitter, points_given, 
            points_received, reciprocity_score
        """
        G = NetworkMetrics.build_voting_graph(data, round_id)

        reciprocity_data = []

        for node_a in G.nodes():
            for node_b in G.nodes():
                if node_a != node_b:
                    points_a_to_b = (
                        G[node_a][node_b]['weight']
                        if G.has_edge(node_a, node_b) else 0
                    )
                    points_b_to_a = (
                        G[node_b][node_a]['weight']
                        if G.has_edge(node_b, node_a) else 0
                    )

                    if points_a_to_b > 0 or points_b_to_a > 0:
                        max_points = max(points_a_to_b, points_b_to_a)
                        reciprocity = (
                            min(points_a_to_b, points_b_to_a) / max_points
                            if max_points > 0 else 0
                        )

                        reciprocity_data.append({
                            'voter': node_a,
                            'submitter': node_b,
                            'points_given': points_a_to_b,
                            'points_received': points_b_to_a,
                            'reciprocity_score': reciprocity
                        })

        return pd.DataFrame(reciprocity_data)

    @staticmethod
    def influence_score(
        data: "MusicLeagueData",
        round_id: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate PageRank-based influence score for each voter.
        
        Higher influence indicates a voter whose preferences tend to
        align with or predict group preferences.
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            
        Returns:
            Dictionary mapping voter names to influence scores
        """
        G = NetworkMetrics.build_voting_graph(data, round_id)

        if len(G.nodes()) == 0:
            return {}

        try:
            pagerank = nx.pagerank(G, weight='weight')
            return {node: float(score) for node, score in pagerank.items()}
        except nx.NetworkXError:
            # If PageRank fails (e.g., empty graph), return equal scores
            return {node: 1.0 / len(G.nodes()) for node in G.nodes()}

    @staticmethod
    def detect_cliques(
        data: "MusicLeagueData",
        round_id: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Detect voting communities/cliques using community detection.
        
        Args:
            data: MusicLeagueData object
            round_id: Optional round ID to filter by
            
        Returns:
            Dictionary mapping voter names to community IDs
        """
        G = NetworkMetrics.build_voting_graph(data, round_id)
        G_undirected = G.to_undirected()

        try:
            # Try to use python-louvain for community detection
            import community as community_louvain
            return community_louvain.best_partition(G_undirected, weight='weight')
        except ImportError:
            # Fallback to simple connected components
            components = list(nx.connected_components(G_undirected))
            community_map = {}
            for i, component in enumerate(components):
                for node in component:
                    community_map[node] = i
            return community_map

