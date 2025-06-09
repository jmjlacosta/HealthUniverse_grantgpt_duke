__author__ = "qiao"

"""
Running the TrialGPT matching for three cohorts (sigir, TREC 2021, TREC 2022).
"""

import json
from nltk.tokenize import sent_tokenize
import os
import sys

from TrialGPT import trialgpt_matching 

if __name__ == "__main__":
        model = sys.argv[1]

        dataset = json.load(open("dataset/grants/retrieved_grants.json"))

        output_path = "dataset/grants/matching_results.json"

        # Dict{researcher_id: Dict{grant_id: results}}
        if os.path.exists(output_path):
                output = json.load(open(output_path))
        else:
                output = {}

        for instance in dataset:
                researcher_id = instance["researcher_id"]
                researcher = instance["researcher"]
                sents = sent_tokenize(researcher)
                sents = [f"{idx}. {sent}" for idx, sent in enumerate(sents)]
                researcher = "\n".join(sents)

                if researcher_id not in output:
                        output[researcher_id] = {}

                for grant in instance.get("grants", []):
                        grant_id = grant["grant_id"]

                        if grant_id in output[researcher_id]:
                                continue

                        try:
                                results = trialgpt_matching(grant, researcher, model)
                                output[researcher_id][grant_id] = results

                                with open(output_path, "w") as f:
                                        json.dump(output, f, indent=4)

                        except Exception as e:
                                print(e)
                                continue
