__author__ = "qiao"

"""
Rank the trials given the matching and aggregation results
"""

import json
import sys

eps = 1e-9

def get_matching_score(matching):
    included = not_inc = na_inc = no_info_inc = 0
    excluded = not_exc = na_exc = no_info_exc = 0

    for _, info in matching["inclusion"].items():
        if len(info) != 3:
            continue
        if info[2] == "included":
            included += 1
        elif info[2] == "not included":
            not_inc += 1
        elif info[2] == "not applicable":
            na_inc += 1
        elif info[2] == "not enough information":
            no_info_inc += 1

    for _, info in matching["exclusion"].items():
        if len(info) != 3:
            continue
        if info[2] == "excluded":
            excluded += 1
        elif info[2] == "not excluded":
            not_exc += 1
        elif info[2] == "not applicable":
            na_exc += 1
        elif info[2] == "not enough information":
            no_info_exc += 1

    score = included / (included + not_inc + no_info_inc + eps)
    if not_inc > 0:
        score -= 1
    if excluded > 0:
        score -= 1

    return score

def get_agg_score(assessment):
    try:
        rel_score = float(assessment["relevance_score_R"])
        eli_score = float(assessment["eligibility_score_E"])
    except:
        rel_score = 0
        eli_score = 0
    return (rel_score + eli_score) / 100

if __name__ == "__main__":
    matching_results_path = sys.argv[1]
    agg_results_path = sys.argv[2]
    output_file = "dataset/data/1_FINAL_ranking_results.txt"

    matching_results = json.load(open(matching_results_path))
    agg_results = json.load(open(agg_results_path))

    with open(output_file, "w") as f:
        for patient_id, label2trial2results in matching_results.items():
            trial2score = {}

            for _, trial2results in label2trial2results.items():
                for trial_id, results in trial2results.items():
                    matching_score = get_matching_score(results)
                    agg_score = get_agg_score(agg_results.get(patient_id, {}).get(trial_id, {}))
                    trial_score = matching_score + agg_score
                    trial2score[trial_id] = trial_score

            sorted_trial2score = sorted(trial2score.items(), key=lambda x: -x[1])

            f.write(f"\nPatient ID: {patient_id}\n")
            f.write("Clinical trial ranking:\n")
            for trial, score in sorted_trial2score:
                trial_link = f"[ {trial} ](https://clinicaltrials.gov/study/{trial})"
                f.write(f"{trial_link} {score}\n")
            f.write("===\n\n")
