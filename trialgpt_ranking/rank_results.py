__author__ = "qiao"

"""
Rank the grants given the matching results.
"""

import json
import sys
from TrialGPT import score_grant_match

if __name__ == "__main__":
    matching_results_path = sys.argv[1]
    output_file = "dataset/grants/grant_rankings.txt"

    matching_results = json.load(open(matching_results_path))

    with open(output_file, "w") as f:
        for researcher_id, grant2results in matching_results.items():
            scores = {}
            for grant_id, result in grant2results.items():
                scores[grant_id] = score_grant_match(result)

            sorted_scores = sorted(scores.items(), key=lambda x: -x[1])

            f.write(f"\nResearcher ID: {researcher_id}\n")
            f.write("Grant ranking:\n")
            for gid, score in sorted_scores:
                f.write(f"{gid} {score}\n")
            f.write("===\n\n")
