"""Utility functions for ranking grants."""


def score_grant_match(match_result: dict) -> float:
    """Convert a matching result into a numeric score."""
    label = str(match_result.get("label", "")).lower()
    if label == "eligible":
        return 1.0
    if label == "not eligible":
        return -1.0
    return 0.0
