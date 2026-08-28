from typing import List, Dict, Any

def assign_panels_to_teams(panels: List[Dict[str, Any]], teams: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    FCFS Panel assignment logic:
    - Track with most teams is assigned exclusively to Panel 4.
    - Remaining tracks are distributed across Panels 1-3.
    """
    if not teams:
        return []

    p_ids = [p["panel_id"] for p in panels]
    if len(p_ids) < 4:
        # Fallback if fewer than 4 panels exist: simple round-robin
        return [
            {"team_id": t["team_id"], "panel_id": p_ids[i % len(p_ids)]}
            for i, t in enumerate(teams)
        ]

    p1, p2, p3, p4 = p_ids[0], p_ids[1], p_ids[2], p_ids[3]

    track_counts = {}
    first_idx = {}
    for i, t in enumerate(teams):
        tk = t["track_id"]
        track_counts[tk] = track_counts.get(tk, 0) + 1
        if tk not in first_idx:
            first_idx[tk] = i

    max_track = max(
        track_counts.keys(),
        key=lambda tk: (track_counts[tk], -first_idx[tk])
    )

    remaining_tracks = [t for t in track_counts.keys() if t != max_track]
    remaining_tracks.sort(key=lambda t: (-track_counts[t], first_idx[t]))

    track_to_panel = {max_track: p4}
    panel_slots = [p1, p1, p2, p2, p3, p3]

    for idx, track in enumerate(remaining_tracks):
        if idx < len(panel_slots):
            track_to_panel[track] = panel_slots[idx]
        else:
            track_to_panel[track] = [p1, p2, p3][idx % 3]

    return [
        {"team_id": t["team_id"], "panel_id": track_to_panel[t["track_id"]]}
        for t in teams
    ]
