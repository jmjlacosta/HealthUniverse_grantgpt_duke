import json

# File paths for grant retrieval
queries_file = "dataset/grants/researchers.jsonl"
corpus_file = "dataset/grants/grants.jsonl"
qid2nctids_results_file = "dataset/grants/qid2grantids_results.json"
output_file = "dataset/grants/retrieved_grants.json"

# Load queries.jsonl (line by line)
with open(queries_file, "r") as f:
    queries_data = {
        json.loads(line)['_id']: {'text': json.loads(line)['text']}
        for line in f
    }

# Load corpus.jsonl (line by line)
with open(corpus_file, "r") as f:
    corpus_data = {
        json.loads(line)['grant_id']: {
            k: json.loads(line)[k] for k in json.loads(line) if k != 'grant_id'
        }
        for line in f
    }

# Load qid2nctids_results.json (full JSON file)
with open(qid2nctids_results_file, "r") as f:
    qid2nctids_results = json.load(f)

# Process retrieved trials
retrieved_trials = []

for researcher in qid2nctids_results:
    if researcher in queries_data:
        valid_grants = []

        for gid in qid2nctids_results[researcher]:
            if gid in corpus_data:
                grant_info = corpus_data[gid]
                grant_info['grant_id'] = gid
                valid_grants.append(grant_info)

        researcher_retrieved = {
            "researcher_id": researcher,
            "researcher": queries_data[researcher]['text'],
            "grants": valid_grants
        }
        retrieved_trials.append(researcher_retrieved)

# Save results to retrieved_trials.json
with open(output_file, "w") as f:
    json.dump(retrieved_trials, f, indent=4)

print(f"Results saved to {output_file}")
