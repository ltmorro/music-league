"""
Narrative generation for the dashboard.
Generates colorful, engaging commentary with personality.
"""

import pandas as pd
from typing import Dict, Optional, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from musicleague.data.loader import MusicLeagueData


# Phrase banks for variety
CLOSE_MATCH_PHRASES = [
    "A photo finish—these two couldn't be more evenly matched.",
    "Separated by a hair. This one came down to the wire.",
    "Too close to call without a recount.",
    "The musical equivalent of a tie-breaker.",
]

BLOWOUT_PHRASES = [
    "Not even close. One league ran away with it.",
    "A commanding lead that was never in doubt.",
    "Complete domination from start to finish.",
    "The kind of gap that makes you double-check the math.",
]

CONTROVERSY_PHRASES = [
    "This one split the room right down the middle.",
    "Love it or hate it—there was no middle ground.",
    "A polarizing pick that sparked debate.",
    "The votes were scattered like confetti.",
]

RISING_PLAYER_PHRASES = [
    "catching fire lately",
    "hitting their stride",
    "building serious momentum",
    "on a hot streak",
]

FALLING_PLAYER_PHRASES = [
    "cooling off after a strong start",
    "losing steam in recent rounds",
    "struggling to recapture early magic",
    "in a bit of a slump",
]


def _pick(phrases: list) -> str:
    """Pick a random phrase from a list for variety."""
    return random.choice(phrases)


def generate_champion_commentary(
    data1: "MusicLeagueData",
    data2: "MusicLeagueData",
    league1_name: str,
    league2_name: str
) -> str:
    """
    Generate colorful commentary comparing winning players from both leagues.
    """
    from musicleague.dashboard.helpers import get_player_champion

    champ1 = get_player_champion(data1)
    champ2 = get_player_champion(data2)

    if not champ1 or not champ2:
        return "Not enough data to crown a champion just yet."

    point_diff = abs(champ1['total_points'] - champ2['total_points'])

    lines = []
    lines.append(f"**{champ1['name']}** dominated {league1_name} with **{champ1['total_points']} total pts**.")
    lines.append(f"**{champ2['name']}** ruled {league2_name} with **{champ2['total_points']} pts**.")

    if point_diff < 20:
        lines.append(_pick(CLOSE_MATCH_PHRASES))
    elif point_diff > 50:
        winner = champ1['name'] if champ1['total_points'] > champ2['total_points'] else champ2['name']
        lines.append(f"{winner} pulled ahead by {point_diff} points. {_pick(BLOWOUT_PHRASES)}")

    # Add flavor based on round wins
    if champ1['round_wins'] > 3 and champ2['round_wins'] > 3:
        lines.append("Both champions racked up multiple round wins—consistent excellence.")
    elif champ1['round_wins'] > champ2['round_wins'] + 2:
        lines.append(f"{champ1['name']} was the round-by-round assassin with {champ1['round_wins']} wins.")
    elif champ2['round_wins'] > champ1['round_wins'] + 2:
        lines.append(f"{champ2['name']} stacked up {champ2['round_wins']} round wins along the way.")

    # Comment on efficiency
    if champ1['avg_points'] > 10 and champ2['avg_points'] > 10:
        lines.append("Both champions averaged over 10 pts per song. Elite curation.")
    elif champ1['avg_points'] > champ2['avg_points'] + 2:
        lines.append(f"{champ1['name']} was more efficient at {champ1['avg_points']} pts/song.")
    elif champ2['avg_points'] > champ1['avg_points'] + 2:
        lines.append(f"{champ2['name']} showed sharper taste at {champ2['avg_points']} pts/song.")

    return " ".join(lines)


def generate_submitter_commentary(
    data1: "MusicLeagueData",
    data2: "MusicLeagueData",
    league1_name: str,
    league2_name: str
) -> str:
    """
    Generate commentary about top submitters with personality.
    """
    from musicleague.metrics.submitters import SubmitterMetrics

    submitters1 = []
    for sid, sdata in data1.competitors.items():
        avg = SubmitterMetrics.average_points_per_submission(data1, sid)
        if avg > 0:
            submitters1.append((sdata['name'], avg))

    submitters2 = []
    for sid, sdata in data2.competitors.items():
        avg = SubmitterMetrics.average_points_per_submission(data2, sid)
        if avg > 0:
            submitters2.append((sdata['name'], avg))

    submitters1.sort(key=lambda x: x[1], reverse=True)
    submitters2.sort(key=lambda x: x[1], reverse=True)

    if not submitters1 or not submitters2:
        return "The submitter data is still warming up."

    top1_name, top1_score = submitters1[0]
    top2_name, top2_score = submitters2[0]

    lines = []
    lines.append(f"**{league1_name}**'s top curator: **{top1_name}** averaging {top1_score:.1f} pts per submission")
    lines.append(f"**{league2_name}**'s finest: **{top2_name}** with {top2_score:.1f} pts per submission")

    diff = abs(top1_score - top2_score)
    if diff > 3:
        leader = top1_name if top1_score > top2_score else top2_name
        lines.append(f"{leader} has the clear edge—their taste is resonating.")
    elif diff > 1:
        lines.append("Both are reading their audience well.")
    else:
        lines.append("A statistical dead heat between these two tastemakers.")

    return " · ".join(lines)


def generate_voter_shift_commentary(
    data1: "MusicLeagueData",
    data2: "MusicLeagueData",
    league1_name: str,
    league2_name: str,
    metric: str = 'hipster'
) -> str:
    """
    Generate commentary about shifts in voter behavior between leagues.
    """
    from musicleague.metrics.voters import VoterMetrics

    if metric == 'hipster':
        scores1 = {
            data1.competitors[vid]['name']: VoterMetrics.hipster_score(data1, vid)
            for vid in data1.competitors.keys()
        }
        scores2 = {
            data2.competitors[vid]['name']: VoterMetrics.hipster_score(data2, vid)
            for vid in data2.competitors.keys()
        }

        common_voters = set(scores1.keys()) & set(scores2.keys())

        if not common_voters:
            return "Different crowds, different vibes—no voters in common."

        changes = {
            voter: scores2[voter] - scores1[voter]
            for voter in common_voters if scores1[voter] > 0
        }

        if not changes:
            return "Not enough overlap to track the evolution."

        biggest_drop = min(changes.items(), key=lambda x: x[1])
        biggest_gain = max(changes.items(), key=lambda x: x[1])

        lines = []
        if abs(biggest_drop[1]) > 10:
            lines.append(f"**{biggest_drop[0]}** discovered the Top 40—their hipster cred dropped {abs(biggest_drop[1]):.0f} pts")

        if biggest_gain[1] > 10:
            lines.append(f"**{biggest_gain[0]}** went full crate-digger (+{biggest_gain[1]:.0f} pts into the obscure)")

        avg_change = sum(changes.values()) / len(changes)
        if abs(avg_change) > 5:
            if avg_change < 0:
                lines.append(f"The group is drifting toward the mainstream (avg shift: {avg_change:+.1f})")
            else:
                lines.append(f"Collective taste is getting weirder in the best way (avg shift: {avg_change:+.1f})")

        return " · ".join(lines) if lines else "Voting patterns held steady—creatures of habit."

    return ""


def generate_controversy_commentary(songs_df: pd.DataFrame, league_name: str) -> str:
    """
    Generate colorful commentary about controversial songs.
    """
    if len(songs_df) == 0:
        return "Surprisingly, no songs caused a stir. Everyone's getting along."

    top = songs_df.iloc[0]

    song_desc = f"'{top['Song']}' by {top['Artist']}"

    if top['Controversy σ'] > 3.5:
        return f"The lightning rod: {song_desc} (σ = {top['Controversy σ']:.2f}). Voters couldn't agree if this was genius or garbage—the ultimate love-it-or-leave-it pick."
    elif top['Controversy σ'] > 2.5:
        return f"Most divisive: {song_desc} (σ = {top['Controversy σ']:.2f}). {_pick(CONTROVERSY_PHRASES)}"
    elif top['Controversy σ'] > 1.5:
        return f"The mild provocateur: {song_desc} (σ = {top['Controversy σ']:.2f}). Enough disagreement to keep things interesting."
    else:
        return f"Even the 'controversial' pick, {song_desc}, barely raised an eyebrow (σ = {top['Controversy σ']:.2f}). This league votes as a bloc."


def generate_hidden_gem_commentary(gems_df: pd.DataFrame, league_name: str) -> str:
    """
    Generate commentary about hidden gems that feels like a discovery.
    """
    if len(gems_df) == 0:
        return "No hidden gems surfaced—the league stuck to familiar territory."

    top = gems_df.iloc[0]

    lines = []
    lines.append(f"**The Find**: '{top['Song']}' by {top['Artist']}")

    if top['Spotify Pop'] < 10:
        lines.append(f"With just **{top['Spotify Pop']}** Spotify popularity, this was practically unknown to the algorithm—yet it pulled in **{top['Points']} pts**.")
    elif top['Spotify Pop'] < 30:
        lines.append(f"Flying under the radar at **{top['Spotify Pop']}** popularity, it earned **{top['Points']} pts** from voters who knew quality when they heard it.")
    else:
        lines.append(f"Not exactly obscure ({top['Spotify Pop']} popularity), but still outperformed expectations with **{top['Points']} pts**.")

    lines.append(f"Credit to **{top['Submitted By']}** for digging this one up.")

    return " ".join(lines)


def generate_final_verdict(
    league1_name: str,
    league2_name: str,
    score1: float,
    score2: float,
    weights: Dict[str, float]
) -> str:
    """
    Generate the final verdict with appropriate drama.
    """
    winner = league1_name if score1 > score2 else league2_name
    loser = league2_name if score1 > score2 else league1_name
    winner_score = max(score1, score2)
    loser_score = min(score1, score2)

    margin = winner_score - loser_score

    top_metric = max(weights.items(), key=lambda x: x[1])
    metric_name = top_metric[0].replace('_', ' ').title()

    lines = []

    # The headline
    if margin > 25:
        lines.append(f"**{winner} takes it decisively** ({winner_score:.1f} to {loser_score:.1f})")
        lines.append("This wasn't close. One league simply brought more heat.")
    elif margin > 15:
        lines.append(f"**{winner} pulls ahead** ({winner_score:.1f} to {loser_score:.1f})")
        lines.append("A comfortable margin, though not a runaway.")
    elif margin > 5:
        lines.append(f"**{winner} edges out {loser}** ({winner_score:.1f} to {loser_score:.1f})")
        lines.append("A competitive showing from both sides.")
    else:
        lines.append(f"**{winner} by a whisker** ({winner_score:.1f} to {loser_score:.1f})")
        lines.append("This could've gone either way. Adjust those weights and the story might change.")

    lines.append(f"The deciding factor: **{metric_name}** (weighted at {top_metric[1]}%)")

    # Weight breakdown
    active_weights = [(k.replace('_', ' ').title(), v) for k, v in weights.items() if v > 0]
    active_weights.sort(key=lambda x: x[1], reverse=True)

    weight_str = ", ".join([f"{name}: {val}%" for name, val in active_weights])
    lines.append(f"*Your scoring breakdown: {weight_str}*")

    return "\n\n".join(lines)


def generate_network_commentary(data: "MusicLeagueData", league_name: str) -> str:
    """
    Generate commentary about network/influence dynamics.
    """
    from musicleague.metrics.network import NetworkMetrics

    influence = NetworkMetrics.influence_score(data)

    if not influence:
        return "The influence web hasn't formed yet—need more voting data."

    top_influencers = sorted(influence.items(), key=lambda x: x[1], reverse=True)[:3]

    lines = [f"**Who shapes the vote in {league_name}?**"]

    top_name, top_score = top_influencers[0]
    lines.append(f"**{top_name}** leads the influence rankings ({top_score:.4f})—when they vote high, others tend to follow.")

    if len(top_influencers) > 1:
        others = [f"{name} ({score:.4f})" for name, score in top_influencers[1:]]
        lines.append(f"Also wielding influence: {', '.join(others)}")

    return " ".join(lines)


def generate_wordsmith_commentary(
    data1: "MusicLeagueData",
    data2: "MusicLeagueData",
    league1_name: str,
    league2_name: str
) -> str:
    """
    Generate commentary comparing comment engagement between leagues.
    """
    from musicleague.metrics.comments import CommentMetrics

    stats1 = CommentMetrics.get_all_submitter_comment_stats(data1)
    stats2 = CommentMetrics.get_all_submitter_comment_stats(data2)

    if len(stats1) == 0 or len(stats2) == 0:
        return "Comment data is too sparse for a proper comparison."

    # Calculate league-wide averages
    avg_len1 = stats1['avg_length'].mean()
    avg_len2 = stats2['avg_length'].mean()
    avg_rate1 = stats1['comment_rate'].mean()
    avg_rate2 = stats2['comment_rate'].mean()

    lines = []

    # Compare wordiness with personality
    if avg_len1 > avg_len2 * 1.5:
        lines.append(f"**{league1_name}** brings the essays ({avg_len1:.0f} chars avg vs {avg_len2:.0f})")
    elif avg_len2 > avg_len1 * 1.5:
        lines.append(f"**{league2_name}** writes full reviews ({avg_len2:.0f} chars avg vs {avg_len1:.0f})")
    elif avg_len1 > avg_len2 * 1.2:
        lines.append(f"**{league1_name}** is a bit more verbose ({avg_len1:.0f} vs {avg_len2:.0f} avg chars)")
    elif avg_len2 > avg_len1 * 1.2:
        lines.append(f"**{league2_name}** has more to say ({avg_len2:.0f} vs {avg_len1:.0f} avg chars)")
    else:
        lines.append(f"Both leagues are equally chatty ({avg_len1:.0f} vs {avg_len2:.0f} chars)")

    # Compare engagement rate
    if avg_rate1 > avg_rate2 + 15:
        lines.append(f"**{league1_name}** rarely lets a submission go uncommented ({avg_rate1:.0f}% comment rate vs {avg_rate2:.0f}%)")
    elif avg_rate2 > avg_rate1 + 15:
        lines.append(f"**{league2_name}** shows up with opinions ({avg_rate2:.0f}% comment rate vs {avg_rate1:.0f}%)")
    elif avg_rate1 > avg_rate2 + 5:
        lines.append(f"**{league1_name}** comments slightly more often ({avg_rate1:.0f}% vs {avg_rate2:.0f}%)")
    elif avg_rate2 > avg_rate1 + 5:
        lines.append(f"**{league2_name}** is a touch more engaged ({avg_rate2:.0f}% vs {avg_rate1:.0f}%)")

    # Find top wordsmith in each league
    if len(stats1) > 0:
        top1 = stats1.iloc[0]
        lines.append(f"**{league1_name}**'s wordsmith: **{top1['submitter_name']}** ({top1['avg_length']:.0f} avg chars)")
    if len(stats2) > 0:
        top2 = stats2.iloc[0]
        lines.append(f"**{league2_name}**'s wordsmith: **{top2['submitter_name']}** ({top2['avg_length']:.0f} avg chars)")

    return " · ".join(lines) if lines else "Both leagues keep their thoughts to themselves."


def generate_best_comment_showcase(data: "MusicLeagueData", league_name: str) -> str:
    """
    Highlight the best/longest comments like a greatest hits collection.
    """
    from musicleague.metrics.comments import CommentMetrics

    notable = CommentMetrics.get_notable_comments(data, min_length=50, top_n=3)

    if len(notable) == 0:
        return f"**{league_name}** kept it brief—no standout comments to feature."

    lines = [f"**Quotable moments from {league_name}:**"]

    for i, (_, row) in enumerate(notable.iterrows()):
        truncated = row['comment'][:150] + "..." if len(row['comment']) > 150 else row['comment']
        lines.append(f"**{row['person']}** on '{row['song']}': \"{truncated}\"")

    return "\n\n".join(lines)


def generate_momentum_commentary(
    data1: "MusicLeagueData",
    data2: "MusicLeagueData",
    league1_name: str,
    league2_name: str
) -> str:
    """
    Generate commentary comparing momentum between leagues with narrative flair.
    """
    from musicleague.metrics.comparisons import CrossRoundMetrics

    momentum1 = CrossRoundMetrics.get_all_momentum_scores(data1)
    momentum2 = CrossRoundMetrics.get_all_momentum_scores(data2)

    if len(momentum1) == 0 or len(momentum2) == 0:
        return "Need more rounds to spot the trends."

    lines = []

    # Count rising vs falling players
    rising1 = len(momentum1[momentum1['trend'] == 'Rising'])
    falling1 = len(momentum1[momentum1['trend'] == 'Falling'])
    rising2 = len(momentum2[momentum2['trend'] == 'Rising'])
    falling2 = len(momentum2[momentum2['trend'] == 'Falling'])

    # Characterize each league's vibe
    if rising1 > falling1 * 2:
        lines.append(f"**{league1_name}** has the wind at its back—{rising1} players trending up vs {falling1} cooling off")
    elif falling1 > rising1 * 2:
        lines.append(f"**{league1_name}** is in flux—{falling1} players losing steam while only {rising1} are rising")
    else:
        lines.append(f"**{league1_name}**: {rising1} rising, {falling1} falling—a stable field")

    if rising2 > falling2 * 2:
        lines.append(f"**{league2_name}** is surging—{rising2} players on the upswing")
    elif falling2 > rising2 * 2:
        lines.append(f"**{league2_name}** sees more slumps than streaks—{falling2} falling, {rising2} rising")
    else:
        lines.append(f"**{league2_name}**: {rising2} rising, {falling2} falling—holding steady")

    # Find hottest player in each
    if len(momentum1) > 0:
        hot1 = momentum1.iloc[0]
        if hot1['momentum'] > 0:
            lines.append(f"**{hot1['submitter']}** is {_pick(RISING_PLAYER_PHRASES)} in {league1_name} (+{hot1['momentum']:.2f})")
    if len(momentum2) > 0:
        hot2 = momentum2.iloc[0]
        if hot2['momentum'] > 0:
            lines.append(f"**{hot2['submitter']}** is {_pick(RISING_PLAYER_PHRASES)} in {league2_name} (+{hot2['momentum']:.2f})")

    return " · ".join(lines)


# Arc type icons for display
ARC_ICONS = {
    "Headliner": "🎤",
    "Opening Act": "🎬",
    "Encore": "🔥",
    "Crowd Favorite": "👏",
    "One-Hit Wonder": "💥",
    "Wild Card": "🎲",
}

# Arc type descriptions for narrative
ARC_DESCRIPTIONS = {
    "Headliner": ["dominated the stage", "commanded the spotlight", "owned every round"],
    "Opening Act": ["started hot but faded", "peaked early", "couldn't maintain the heat"],
    "Encore": ["saved the best for last", "finished on fire", "came back strong"],
    "Crowd Favorite": ["stayed in the pocket", "delivered consistency", "never missed a beat"],
    "One-Hit Wonder": ["had that one magic moment", "struck gold once", "caught lightning in a bottle"],
    "Wild Card": ["kept everyone guessing", "defied prediction", "rode the rollercoaster"],
}


def generate_arc_commentary(
    data1: "MusicLeagueData",
    data2: "MusicLeagueData",
    league1_name: str,
    league2_name: str
) -> str:
    """
    Generate commentary comparing player arcs between leagues.
    """
    from musicleague.metrics.comparisons import CrossRoundMetrics

    arcs1 = CrossRoundMetrics.get_all_player_arcs(data1)
    arcs2 = CrossRoundMetrics.get_all_player_arcs(data2)

    if len(arcs1) == 0 or len(arcs2) == 0:
        return "Need more data to analyze player arcs."

    lines = []

    # Count arc types per league
    arc_counts1 = arcs1['arc_type'].value_counts().to_dict()
    arc_counts2 = arcs2['arc_type'].value_counts().to_dict()

    # Find dominant arc type for each league
    dominant1 = max(arc_counts1, key=arc_counts1.get) if arc_counts1 else None
    dominant2 = max(arc_counts2, key=arc_counts2.get) if arc_counts2 else None

    if dominant1:
        count1 = arc_counts1[dominant1]
        icon1 = ARC_ICONS.get(dominant1, "")
        lines.append(
            f"**{league1_name}** is a league of {icon1} **{dominant1}s** "
            f"({count1} players)"
        )

    if dominant2:
        count2 = arc_counts2[dominant2]
        icon2 = ARC_ICONS.get(dominant2, "")
        lines.append(
            f"**{league2_name}** skews toward {icon2} **{dominant2}s** "
            f"({count2} players)"
        )

    # Highlight the top player from each league with their arc
    if len(arcs1) > 0:
        top1 = arcs1.iloc[0]
        desc1 = _pick(ARC_DESCRIPTIONS.get(top1['arc_type'], ["performed"]))
        lines.append(
            f"**{top1['submitter']}** ({top1['arc_type']}) {desc1} in {league1_name}"
        )

    if len(arcs2) > 0:
        top2 = arcs2.iloc[0]
        desc2 = _pick(ARC_DESCRIPTIONS.get(top2['arc_type'], ["performed"]))
        lines.append(
            f"**{top2['submitter']}** ({top2['arc_type']}) {desc2} in {league2_name}"
        )

    # Look for interesting Encore stories (biggest comeback)
    encores1 = arcs1[arcs1['arc_type'] == 'Encore']
    encores2 = arcs2[arcs2['arc_type'] == 'Encore']

    if len(encores1) > 0:
        best_encore1 = encores1.loc[encores1['finishing_strength'].idxmax()]
        if best_encore1['finishing_strength'] > 0:
            lines.append(
                f"Comeback story: **{best_encore1['submitter']}** improved by "
                f"+{best_encore1['finishing_strength']:.0f} pts/round in the second half"
            )

    return " · ".join(lines)


def generate_round_highlight(data: "MusicLeagueData", round_index: int) -> str:
    """
    Generate commentary for a specific round's results.
    """
    from musicleague.metrics.comparisons import CrossRoundMetrics

    rankings_df = CrossRoundMetrics.round_rankings(data)

    if len(rankings_df) == 0:
        return "Round data hasn't loaded yet."

    round_ids = data.rounds
    if round_index < 0 or round_index >= len(round_ids):
        return "That round doesn't exist."

    round_id = round_ids[round_index]
    round_data = rankings_df[rankings_df['round_id'] == round_id]

    if len(round_data) == 0:
        return "No submissions recorded for this round."

    winner = round_data.iloc[0]
    runner_up = round_data.iloc[1] if len(round_data) > 1 else None

    lines = []
    lines.append(f"**Round {round_index + 1}**: '{winner['song']}' by {winner['artist']} took the crown")
    lines.append(f"**{winner['submitter']}** brought it home with **{winner['points']} pts**")

    if runner_up is not None:
        margin = winner['points'] - runner_up['points']
        if margin <= 1:
            lines.append(f"Edged out '{runner_up['song']}' by just {margin} pt—a nail-biter")
        elif margin <= 3:
            lines.append(f"Squeaked past '{runner_up['song']}' by {margin} pts—close enough to feel it")
        elif margin >= 15:
            lines.append(f"Crushed the competition—runner-up '{runner_up['song']}' trailed by {margin} pts")
        elif margin >= 10:
            lines.append(f"A strong showing—{margin} pts clear of the runner-up")
        else:
            lines.append(f"Won by {margin} pts over '{runner_up['song']}'")

    return " · ".join(lines)